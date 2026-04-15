#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from pathlib import Path

BASE_DIR = Path("/home/amil/beauty/site-mirror/beauty.hotpepper.jp/slnH000702503/review")
OUT_DIR = Path("/home/amil/beauty/output")
OUT_FILE = OUT_DIR / "hotpepper_reviews.md"


class ReviewLiExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.li_depth = 0
        self.capture = False
        self.capture_depth = 0
        self.current: list[str] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "li":
            self.li_depth += 1

        if not self.capture and tag == "li":
            attrs_dict = dict(attrs)
            class_attr = attrs_dict.get("class", "") or ""
            classes = set(class_attr.split())
            if "reportCassette" in classes or "reportDetailCassette" in classes:
                self.capture = True
                self.capture_depth = self.li_depth

        if self.capture:
            self.current.append(self.get_starttag_text() or f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        if self.capture:
            self.current.append(f"</{tag}>")

        if tag == "li":
            if self.capture and self.li_depth == self.capture_depth:
                self.blocks.append("".join(self.current))
                self.current = []
                self.capture = False
                self.capture_depth = 0
            self.li_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.current.append(data)

    def handle_entityref(self, name: str) -> None:
        if self.capture:
            self.current.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self.capture:
            self.current.append(f"&#{name};")


def strip_tags(fragment: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_from_block(block: str) -> dict[str, str]:
    name_match = re.search(r'<span class="b">(.*?)</span>', block, flags=re.S)
    date_match = re.search(r"\[投稿日\]\s*([0-9]{4}/[0-9]{1,2}/[0-9]{1,2})", block)
    rating_match = re.search(r"総合\s*<span[^>]*>\s*([0-9](?:\.[0-9])?)\s*</span>", block, flags=re.S)

    review_match = re.search(
        r'<p class="mT10 wwbw">(.*?)<dl class="mT25">',
        block,
        flags=re.S,
    )

    reply_match = re.search(
        r"からの返信コメント</p>.*?<p class=\"mT10 wwbw\">(.*?)</div>",
        block,
        flags=re.S,
    )

    menu_match = re.search(
        r"予約時のクーポン・メニュー\s*</dt>\s*<dd[^>]*>\s*<p>\s*(.*?)\s*</p>",
        block,
        flags=re.S,
    )

    return {
        "name": strip_tags(name_match.group(1)) if name_match else "(unknown)",
        "date": date_match.group(1) if date_match else "(unknown)",
        "rating": rating_match.group(1) if rating_match else "(unknown)",
        "review": strip_tags(review_match.group(1)) if review_match else "",
        "reply": strip_tags(reply_match.group(1)) if reply_match else "",
        "menu": strip_tags(menu_match.group(1)) if menu_match else "",
    }


def page_sort_key(path: Path) -> tuple[int, str]:
    if path.name == "index.html":
        return (1, path.name)
    match = re.match(r"PN(\d+)\.html$", path.name)
    if match:
        return (int(match.group(1)), path.name)
    return (10_000, path.name)


def main() -> None:
    pages = sorted(BASE_DIR.glob("*.html"), key=page_sort_key)
    if not pages:
        raise SystemExit(f"No HTML files found in {BASE_DIR}")

    all_reviews: list[dict[str, str]] = []
    page_index: list[tuple[str, int]] = []

    for page in pages:
        parser = ReviewLiExtractor()
        parser.feed(page.read_text(encoding="utf-8", errors="ignore"))
        extracted = [extract_from_block(block) for block in parser.blocks]
        extracted = [r for r in extracted if r.get("review")]
        page_index.append((page.name, len(extracted)))
        all_reviews.extend(extracted)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Hot Pepper Reviews Export")
    lines.append("")
    lines.append("Source: https://beauty.hotpepper.jp/slnH000702503/review/")
    lines.append(f"Pages processed: {len(pages)}")
    lines.append(f"Reviews extracted: {len(all_reviews)}")
    lines.append("")
    lines.append("## Page Breakdown")
    lines.append("")
    for page_name, count in page_index:
        lines.append(f"- {page_name}: {count} reviews")

    lines.append("")
    lines.append("## Reviews")
    lines.append("")

    for i, review in enumerate(all_reviews, start=1):
        lines.append(f"### {i}. {review['name']}")
        lines.append(f"- Date: {review['date']}")
        lines.append(f"- Rating: {review['rating']}")
        if review["menu"]:
            lines.append(f"- Menu: {review['menu']}")
        lines.append("")
        lines.append("**Review**")
        lines.append("")
        lines.append(review["review"])
        if review["reply"]:
            lines.append("")
            lines.append("**Salon Reply**")
            lines.append("")
            lines.append(review["reply"])
        lines.append("")

    OUT_FILE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {OUT_FILE}")
    print(f"Pages: {len(pages)} | Reviews: {len(all_reviews)}")


if __name__ == "__main__":
    main()
