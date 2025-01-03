from __future__ import annotations

import datetime
import pathlib
import re
from typing import TYPE_CHECKING

import feedparser  # pyright: ignore[reportMissingTypeStubs]

if TYPE_CHECKING:
    from typing import Any

DATETIME_REGEX = re.compile(r"\#\#DATETIME\b")
NEWS_REGEX = re.compile(r"\#\#SKY\b")
LICENSE_YEAR_REGEX = re.compile(r"\d{4}")  # ensure we only override first occurrence

TEMPLATE_FILE = pathlib.Path("README.tpl.md")
README_FILE = pathlib.Path("README.md")
LICENSE_FILE = pathlib.Path("LICENSE")

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
    feed: dict[str, Any] = feedparser.parse(NEWS_URL)  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType] # upstream lack of typing

    top_headline: dict[str, Any] = feed["entries"][0]  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType] # upstream lack of typing
    title: str = top_headline["title"]  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType] # upstream lack of typing
    url: str = top_headline["links"][0]["href"]  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType] # upstream lack of typing

    resolved = f"[{title}]({url})"

    return NEWS_REGEX.sub(resolved, current_content)


def handle_license() -> None:
    content = LICENSE_FILE.read_text()
    new_content = LICENSE_YEAR_REGEX.sub(datetime.datetime.now(datetime.UTC).strftime("%Y"), content, count=1)
    LICENSE_FILE.write_text(new_content)


if __name__ == "__main__":
    content = TEMPLATE_FILE.read_text(encoding="utf8")
    after_dt = generate_dt_content(content)
    after_news = generate_news_content(after_dt)
    README_FILE.write_text(after_news, encoding="utf8")
    handle_license()  # we handle the license file differently to only open it once unless the readme which would be 2
