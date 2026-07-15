#!/usr/bin/env python3
"""Kaizenvest Sector Brief — Snapshot PDF generator.

Turns an edition content JSON (same schema assemble.py uses) into an A4
portrait PDF suitable for LinkedIn document upload and email distribution.

Usage: snapshot.py content.json out.pdf [fonts_dir]
Deps:  pip install fpdf2   (fonts: DejaVu TTFs, default ./assets/fonts)
"""
import json, sys, pathlib
from fpdf import FPDF

CREAM = (244, 241, 234)
INK = (18, 18, 18)
BODY = (61, 61, 61)
META = (122, 122, 122)
RED = (227, 18, 11)
TAG_COLORS = {
    "India": (227, 18, 11), "Vietnam": (4, 120, 87), "Philippines": (29, 78, 216),
    "Thailand": (124, 58, 237), "Singapore": (219, 39, 119), "Indonesia": (180, 83, 9),
    "South Korea": (14, 116, 144), "Japan": (159, 18, 57), "USA": (17, 24, 39),
}
DEFAULT_TAG = (55, 65, 81)
SITE = "lucasvegamazzoni.github.io/kaizenvest-brief"

M = 16  # page margin, mm
W = 210 - 2 * M


class Snapshot(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("serifb", "", 10)
        self.set_text_color(*INK)
        self.set_xy(M, 8)
        self.cell(W / 2, 6, "Kaizenvest Sector Brief — Snapshot")
        self.set_font("sans", "", 8)
        self.set_text_color(*META)
        self.set_xy(M + W / 2, 8)
        self.cell(W / 2, 6, self.week_label, align="R")
        self.set_draw_color(*RED)
        self.set_line_width(0.8)
        self.line(M, 15, 210 - M, 15)
        self.set_y(20)

    def footer(self):
        self.set_y(-12)
        self.set_font("sans", "", 8)
        self.set_text_color(*META)
        self.cell(W / 2, 5, f"Full brief: https://{SITE}/")
        self.cell(W / 2, 5, f"{self.page_no()}/{{nb}}", align="R")


def load_fonts(pdf, fonts_dir):
    d = pathlib.Path(fonts_dir)
    pdf.add_font("sans", "", d / "DejaVuSans.ttf")
    pdf.add_font("sansb", "", d / "DejaVuSans-Bold.ttf")
    pdf.add_font("serif", "", d / "DejaVuSerif.ttf")
    pdf.add_font("serifb", "", d / "DejaVuSerif-Bold.ttf")


def cover(pdf, content, n_stories, n_countries, assets_dir):
    pdf.set_auto_page_break(False)
    pdf.add_page()
    pdf.set_fill_color(*CREAM)
    pdf.rect(0, 0, 210, 297, "F")
    # logos
    kz, em = assets_dir / "kaizenvest-logo.png", assets_dir / "empacta-logo.png"
    if kz.exists() and em.exists():
        pdf.image(str(kz), x=M, y=22, h=11)
        pdf.image(str(em), x=M + 62, y=22, h=11)
        rule_y = 40
    else:
        pdf.set_xy(M, 24)
        pdf.set_font("sansb", "", 12)
        pdf.set_text_color(*INK)
        pdf.cell(W, 8, "K A I Z E N V E S T   ×   E M P A C T A")
        rule_y = 36
    # masthead
    pdf.set_fill_color(*RED)
    pdf.rect(M, rule_y, W, 2.2, "F")
    pdf.set_xy(M, rule_y + 8)
    pdf.set_font("serifb", "", 40)
    pdf.set_text_color(*INK)
    pdf.cell(W, 16, "Sector Brief")
    pdf.set_xy(M, rule_y + 26)
    pdf.set_font("sansb", "", 15)
    pdf.set_text_color(*RED)
    pdf.cell(W, 8, "SNAPSHOT")
    pdf.set_xy(M, rule_y + 38)
    pdf.set_font("sans", "", 10)
    pdf.set_text_color(*META)
    pdf.cell(W, 6, "EDUCATION  ·  EDTECH  ·  SKILLING  ·  WORKFORCE")
    pdf.set_xy(M, rule_y + 45)
    pdf.set_font("sansb", "", 11)
    pdf.set_text_color(*INK)
    pdf.cell(W, 6, f"{content['week_label']}   |   {n_stories} stories   |   {n_countries} countries")
    # intro
    pdf.set_xy(M, rule_y + 58)
    pdf.set_font("serif", "", 11.5)
    pdf.set_text_color(*BODY)
    pdf.multi_cell(W, 6.2, "This week in brief.  " + content["intro"])
    # country chips (tags only, wrapped in rows)
    y = min(pdf.get_y() + 12, 238)
    pdf.set_font("sansb", "", 8.5)
    x = M
    for s in content["sections"]:
        if not s["articles"]:
            continue
        color = TAG_COLORS.get(s["country"], DEFAULT_TAG)
        tag_w = pdf.get_string_width(s["country"].upper()) + 7
        if x + tag_w > 210 - M:
            x, y = M, y + 9
        pdf.set_xy(x, y)
        pdf.set_fill_color(*color)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(tag_w, 6.5, s["country"].upper(), fill=True, align="C")
        x += tag_w + 3
    # footer CTA
    pdf.set_xy(M, 266)
    pdf.set_font("sansb", "", 10.5)
    pdf.set_text_color(*INK)
    pdf.cell(W, 6, "Read the full brief with every source and link:")
    pdf.set_xy(M, 273)
    pdf.set_font("sansb", "", 10.5)
    pdf.set_text_color(*RED)
    pdf.cell(W, 6, f"https://{SITE}/")
    pdf.set_auto_page_break(True, margin=18)


def story_block(pdf, a, color):
    est = 30  # rough block height; break page early if close to bottom
    if pdf.get_y() + est > 280:
        pdf.add_page()
    y = pdf.get_y()
    pdf.set_fill_color(*color)
    pdf.rect(M, y + 1, 1.6, 22, "F")
    x = M + 6
    pdf.set_xy(x, y)
    pdf.set_font("serifb", "", 12.5)
    pdf.set_text_color(*INK)
    pdf.multi_cell(W - 6, 6.2, a["headline"])
    pdf.set_xy(x, pdf.get_y() + 1)
    pdf.set_font("serif", "", 9.5)
    pdf.set_text_color(*BODY)
    desc = a["description"]
    first = desc.split(". ")
    short = ". ".join(first[:2]).rstrip(".") + "."
    pdf.multi_cell(W - 6, 5, short)
    pdf.set_xy(x, pdf.get_y() + 0.5)
    pdf.set_font("sans", "", 7.5)
    pdf.set_text_color(*META)
    pdf.cell(W - 6, 4.5, f"{a['source']}  ·  {a['published_date']}")
    pdf.set_y(pdf.get_y() + 8)


def stories(pdf, content):
    pdf.add_page()
    for s in content["sections"]:
        if not s["articles"]:
            continue
        color = TAG_COLORS.get(s["country"], DEFAULT_TAG)
        if pdf.get_y() + 40 > 280:
            pdf.add_page()
        pdf.set_fill_color(*color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("sansb", "", 10)
        tag_w = pdf.get_string_width(s["country"].upper()) + 8
        pdf.cell(tag_w, 7, s["country"].upper(), fill=True, align="C")
        pdf.ln(10)
        for a in s["articles"]:
            story_block(pdf, a, color)
        pdf.set_y(pdf.get_y() + 2)


def back(pdf):
    pdf.add_page()
    pdf.set_fill_color(*CREAM)
    pdf.rect(0, 0, 210, 297, "F")
    pdf.set_fill_color(*RED)
    pdf.rect(M, 110, W, 2.2, "F")
    pdf.set_xy(M, 122)
    pdf.set_font("serifb", "", 24)
    pdf.set_text_color(*INK)
    pdf.multi_cell(W, 11, "Read the full brief")
    pdf.set_xy(M, 148)
    pdf.set_font("sans", "", 12)
    pdf.set_text_color(*BODY)
    pdf.multi_cell(W, 7, f"Every story, source link and image:\nhttps://{SITE}/")
    pdf.set_xy(M, 175)
    pdf.set_font("sans", "", 9)
    pdf.set_text_color(*META)
    pdf.multi_cell(W, 5.5, "Compiled weekly by the Kaizenvest news agent pipeline.\nEducation · EdTech · Skilling · Workforce — USA, India, Vietnam, Philippines, Thailand, Singapore, Indonesia, South Korea, Japan.")


def main():
    content = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2])
    fonts = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else pathlib.Path(__file__).parent / "assets" / "fonts"
    n_stories = sum(len(s["articles"]) for s in content["sections"])
    n_countries = sum(1 for s in content["sections"] if s["articles"])
    pdf = Snapshot(orientation="P", unit="mm", format="A4")
    pdf.week_label = content["week_label"]
    load_fonts(pdf, fonts)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(True, margin=18)
    cover(pdf, content, n_stories, n_countries, fonts.parent)
    stories(pdf, content)
    back(pdf)
    pdf.output(str(out))
    print(f"wrote {out} ({out.stat().st_size} bytes, {pdf.page_no()} pages)")


if __name__ == "__main__":
    main()
