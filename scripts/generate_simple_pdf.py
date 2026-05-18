from __future__ import annotations

import argparse
import textwrap
from pathlib import Path


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
LEFT = 50
RIGHT = 50
TOP = 60
BOTTOM = 55
TITLE_SIZE = 18
H1_SIZE = 15
H2_SIZE = 12
BODY_SIZE = 10
LINE_GAP = 4
MAX_CHARS = 92


def escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def parse_markdown(md_text: str) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    for raw in md_text.splitlines():
        stripped = raw.rstrip()
        if not stripped:
            lines.append(("blank", ""))
        elif stripped.startswith("# "):
            lines.append(("title", stripped[2:].strip()))
        elif stripped.startswith("## "):
            lines.append(("h1", stripped[3:].strip()))
        elif stripped.startswith("### "):
            lines.append(("h2", stripped[4:].strip()))
        elif stripped.startswith("- "):
            lines.append(("bullet", stripped[2:].strip()))
        else:
            lines.append(("body", stripped))
    return lines


def wrap_line(kind: str, text: str) -> list[tuple[str, str]]:
    if kind == "blank":
        return [("blank", "")]
    if kind in {"title", "h1", "h2"}:
        width = 70 if kind == "title" else 82
        return [(kind, part) for part in textwrap.wrap(text, width=width) or [""]]
    if kind == "bullet":
        wrapped = textwrap.wrap(text, width=MAX_CHARS - 4) or [""]
        result = [("bullet", f"- {wrapped[0]}")]
        result.extend([("body", f"  {part}") for part in wrapped[1:]])
        return result
    wrapped = textwrap.wrap(text, width=MAX_CHARS) or [""]
    return [(kind, part) for part in wrapped]


def flatten_lines(md_text: str) -> list[tuple[str, str]]:
    flat: list[tuple[str, str]] = []
    for kind, text in parse_markdown(md_text):
        flat.extend(wrap_line(kind, text))
    return flat


def line_metrics(kind: str) -> tuple[str, int, int]:
    if kind == "title":
        return "Courier-Bold", TITLE_SIZE, TITLE_SIZE + 8
    if kind == "h1":
        return "Courier-Bold", H1_SIZE, H1_SIZE + 6
    if kind == "h2":
        return "Courier-Bold", H2_SIZE, H2_SIZE + 5
    if kind == "blank":
        return "Courier", BODY_SIZE, BODY_SIZE + LINE_GAP
    return "Courier", BODY_SIZE, BODY_SIZE + LINE_GAP


def paginate(lines: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    pages: list[list[tuple[str, str]]] = []
    current: list[tuple[str, str]] = []
    remaining = PAGE_HEIGHT - TOP - BOTTOM

    for kind, text in lines:
        _, _, step = line_metrics(kind)
        if current and remaining - step < 0:
            pages.append(current)
            current = []
            remaining = PAGE_HEIGHT - TOP - BOTTOM
        current.append((kind, text))
        remaining -= step

    if current:
        pages.append(current)
    return pages


def page_stream(page_lines: list[tuple[str, str]]) -> str:
    y = PAGE_HEIGHT - TOP
    chunks = ["BT", f"{LEFT} {y} Td"]
    first = True

    for kind, text in page_lines:
        font, size, step = line_metrics(kind)
        if not first:
            chunks.append(f"0 -{step} Td")
            y -= step
        first = False
        if kind == "blank":
            continue
        chunks.append(f"/{font} {size} Tf")
        chunks.append(f"({escape_pdf_text(text)}) Tj")

    chunks.append("ET")
    return "\n".join(chunks)


def build_pdf(pages: list[list[tuple[str, str]]]) -> bytes:
    objects: list[bytes] = []

    catalog_id = 1
    pages_id = 2
    font_regular_id = 3
    font_bold_id = 4

    page_object_ids: list[int] = []
    content_object_ids: list[int] = []
    next_id = 5
    for _ in pages:
        page_object_ids.append(next_id)
        content_object_ids.append(next_id + 1)
        next_id += 2

    def add(obj: str | bytes) -> None:
        objects.append(obj.encode("latin-1") if isinstance(obj, str) else obj)

    add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")

    kids = " ".join(f"{pid} 0 R" for pid in page_object_ids)
    add(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_ids)} >>")

    add("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    add("<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold >>")

    for page_id, content_id, page in zip(page_object_ids, content_object_ids, pages):
        add(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /Courier {font_regular_id} 0 R /Courier-Bold {font_bold_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        stream = page_stream(page).encode("latin-1")
        add(
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{index} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")

    xref_start = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        out.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    out.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_markdown", type=Path)
    parser.add_argument("output_pdf", type=Path)
    args = parser.parse_args()

    md_text = args.input_markdown.read_text()
    lines = flatten_lines(md_text)
    pages = paginate(lines)
    pdf_bytes = build_pdf(pages)
    args.output_pdf.write_bytes(pdf_bytes)
    print(f"Wrote {args.output_pdf} with {len(pages)} pages")


if __name__ == "__main__":
    main()
