import os
import sys
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_run_font(run, name='Bookman Old Style', size=12, bold=False, italic=False, color_rgb=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb

def set_para_format(p, line_spacing=1.5, space_before=4, space_after=6, align=WD_ALIGN_PARAGRAPH.JUSTIFY, keep_with_next=False):
    p.alignment = align
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = keep_with_next

def add_page_number_field(run):
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

def add_heading_para(doc, text, level=1, space_before=10, space_after=4, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.15, space_before=space_before, space_after=space_after, align=align, keep_with_next=True)
    run = p.add_run(text)
    # User constraint: "All heading and subheading: 12 bold Bookman Old Style"
    set_run_font(run, name='Bookman Old Style', size=12, bold=True)
    return p

def add_body_para(doc, text, space_before=0, space_after=6, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.5, space_before=space_before, space_after=space_after, align=align)
    run = p.add_run(text)
    # User constraint: "Normal Text: Bookman Old Style 12 font"
    set_run_font(run, name='Bookman Old Style', size=12, bold=False)
    return p

def add_bullet_item(doc, bold_prefix, text, space_before=0, space_after=4):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.5, space_before=space_before, space_after=space_after, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    p.paragraph_format.left_indent = Inches(0.25)
    r1 = p.add_run(bold_prefix + " ")
    set_run_font(r1, name='Bookman Old Style', size=12, bold=True)
    r2 = p.add_run(text)
    set_run_font(r2, name='Bookman Old Style', size=12, bold=False)
    return p

def add_numbered_item(doc, num_str, bold_prefix, text, space_before=0, space_after=4):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.5, space_before=space_before, space_after=space_after, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    p.paragraph_format.left_indent = Inches(0.25)
    r_num = p.add_run(num_str + " ")
    set_run_font(r_num, name='Bookman Old Style', size=12, bold=True)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix + ": ")
        set_run_font(r_pre, name='Bookman Old Style', size=12, bold=True)
    r_txt = p.add_run(text)
    set_run_font(r_txt, name='Bookman Old Style', size=12, bold=False)
    return p

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

print("Helper definitions loaded successfully.")
