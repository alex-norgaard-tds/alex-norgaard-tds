import datetime
import pathlib
import re

import feedparser

DATETIME_REGEX = re.compile(r"\#\#DATETIME\b")
NEWS_REGEX = re.compile(r"\#\#SKY\b")
TEMPLATE_FILE = pathlib.Path("README.tpl.md")
README_FILE = pathlib.Path("README.md")
NEWS_URL = "https://feeds.skynews.com/feeds/rss/uk.xml"

if not TEMPLATE_FILE.exists():
    raise RuntimeError("No README found.")


def _ordinal(number: int) -> str:
    return f"{number}{'tsnrhtdd'[(number // 10 % 10 != 1) * (number % 10 < 4) * number % 10 :: 4]}"


def generate_dt_content(current_content: str) -> str:
    now = datetime.datetime.now(datetime.UTC)
    now_date_fmt = now.strftime("%B %Y")
    now_time_fmt = now.strftime("%H:%M (%Z)")
    now_ord_fmt = _ordinal(int(now.strftime("%e")))

    resolved = f"{now_ord_fmt} of {now_date_fmt} at {now_time_fmt}"

    return DATETIME_REGEX.sub(resolved, current_content)


def generate_news_content(current_content: str) -> str:
    feed = feedparser.parse(NEWS_URL)

    top_headline = feed["entries"][0]
    title = top_headline["title"]
    url = top_headline["links"][0]["href"]

    resolved = f"[{title}]({url})"

    return NEWS_REGEX.sub(resolved, current_content)


if __name__ == "__main__":
    content = TEMPLATE_FILE.read_text(encoding="utf8")
    after_dt = generate_dt_content(content)
    after_news = generate_news_content(after_dt)
    README_FILE.write_text(after_news, encoding="utf8")
