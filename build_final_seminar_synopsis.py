import os
import sys
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def create_element(name):
    return OxmlElement(name)

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

def add_heading_para(doc, text, space_before=8, space_after=3, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.15, space_before=space_before, space_after=space_after, align=align, keep_with_next=True)
    run = p.add_run(text)
    set_run_font(run, name='Bookman Old Style', size=12, bold=True)
    return p

def add_subheading_para(doc, text, space_before=6, space_after=2, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.15, space_before=space_before, space_after=space_after, align=align, keep_with_next=True)
    run = p.add_run(text)
    set_run_font(run, name='Bookman Old Style', size=12, bold=True)
    return p

def add_body_para(doc, text, space_before=0, space_after=6, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.5, space_before=space_before, space_after=space_after, align=align)
    run = p.add_run(text)
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

def add_page_number_field(run):
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
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

def set_table_borders(table, color="B0B0B0", sz="4", val="single"):
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

def build_synopsis_document():
    doc = Document()
    
    # Page setup - 1 inch all around (72 pt)
    s1 = doc.sections[0]
    s1.top_margin = Inches(1.0)
    s1.bottom_margin = Inches(1.0)
    s1.left_margin = Inches(1.0)
    s1.right_margin = Inches(1.0)
    s1.page_width = Inches(8.5)
    s1.page_height = Inches(11.0)
    s1.different_first_page_header_footer = True
    
    # Cover page header
    hdr_first = s1.first_page_header
    p_hdr1 = hdr_first.paragraphs[0]
    p_hdr1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_para_format(p_hdr1, line_spacing=1.0, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.RIGHT)
    r_hdr1 = p_hdr1.add_run("MCA | Seminar Synopsis")
    set_run_font(r_hdr1, name='Bookman Old Style', size=10, bold=False, color_rgb=RGBColor(80, 80, 80))
    
    # Cover page footer
    ftr_first = s1.first_page_footer
    p_ftr1 = ftr_first.paragraphs[0]
    set_para_format(p_ftr1, line_spacing=1.0, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_ftr1 = p_ftr1.add_run("Enhancing Legal Efficiency Through Artificial Intelligence")
    set_run_font(r_ftr1, name='Bookman Old Style', size=10, bold=False, color_rgb=RGBColor(80, 80, 80))
    
    # Normal Header & Footer for Subsequent Pages
    hdr_normal = s1.header
    p_hdr2 = hdr_normal.paragraphs[0]
    set_para_format(p_hdr2, line_spacing=1.0, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.RIGHT)
    r_hdr2 = p_hdr2.add_run("MCA | Seminar Synopsis")
    set_run_font(r_hdr2, name='Bookman Old Style', size=10, bold=False, color_rgb=RGBColor(80, 80, 80))
    
    ftr_normal = s1.footer
    p_ftr2 = ftr_normal.paragraphs[0]
    set_para_format(p_ftr2, line_spacing=1.0, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    # Left part: Seminar Title, Right part (tabbed): Page Number
    r_ftr2_title = p_ftr2.add_run("Enhancing Legal Efficiency Through Artificial Intelligence\t")
    set_run_font(r_ftr2_title, name='Bookman Old Style', size=10, bold=False, color_rgb=RGBColor(80, 80, 80))
    r_ftr2_page = p_ftr2.add_run()
    set_run_font(r_ftr2_page, name='Bookman Old Style', size=10, bold=True, color_rgb=RGBColor(80, 80, 80))
    add_page_number_field(r_ftr2_page)
    
    # ---------------- PAGE 1: COVER PAGE ----------------
    # Top spacing
    p_top_sp = doc.add_paragraph()
    set_para_format(p_top_sp, line_spacing=1.0, space_before=0, space_after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    # Boxed Title Table (matching friend's reference PDF)
    title_table = doc.add_table(rows=1, cols=1)
    title_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    title_cell = title_table.cell(0, 0)
    title_cell.width = Inches(6.5)
    set_cell_margins(title_cell, top=140, bottom=140, left=180, right=180)
    
    tcPr = title_cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:right w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p_box = title_cell.paragraphs[0]
    set_para_format(p_box, line_spacing=1.2, space_before=4, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_box = p_box.add_run("“Enhancing Legal Efficiency Through Artificial Intelligence”")
    set_run_font(r_box, name='Bookman Old Style', size=13, bold=True)
    
    # Submitted to
    p_sub = doc.add_paragraph()
    set_para_format(p_sub, line_spacing=1.2, space_before=16, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_sub = p_sub.add_run("Submitted to")
    set_run_font(r_sub, name='Bookman Old Style', size=12, bold=False)
    
    # University Name
    p_uni = doc.add_paragraph()
    set_para_format(p_uni, line_spacing=1.2, space_before=2, space_after=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_uni = p_uni.add_run("Chhatrapati Shivaji Maharaj University,\nPanvel, Navi Mumbai")
    set_run_font(r_uni, name='Bookman Old Style', size=14, bold=True)
    
    # Logo
    if os.path.exists("csmu_logo.png"):
        p_logo = doc.add_paragraph()
        set_para_format(p_logo, line_spacing=1.0, space_before=6, space_after=14, align=WD_ALIGN_PARAGRAPH.CENTER)
        p_logo.add_run().add_picture("csmu_logo.png", width=Inches(1.6))
    
    # Degree info
    p_deg_req = doc.add_paragraph()
    set_para_format(p_deg_req, line_spacing=1.15, space_before=8, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_deg_req = p_deg_req.add_run("for the partial fulfillment of requirement for the Degree of")
    set_run_font(r_deg_req, name='Bookman Old Style', size=11, bold=False)
    
    p_deg = doc.add_paragraph()
    set_para_format(p_deg, line_spacing=1.15, space_before=2, space_after=16, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_deg = p_deg.add_run("Master of Computer Application")
    set_run_font(r_deg, name='Bookman Old Style', size=13, bold=True)
    
    # Submitted By
    p_by_lbl = doc.add_paragraph()
    set_para_format(p_by_lbl, line_spacing=1.15, space_before=6, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_by_lbl = p_by_lbl.add_run("Submitted By")
    set_run_font(r_by_lbl, name='Bookman Old Style', size=12, bold=False)
    
    p_by_name = doc.add_paragraph()
    set_para_format(p_by_name, line_spacing=1.15, space_before=2, space_after=18, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_by_name = p_by_name.add_run("Rohan Bongane")
    set_run_font(r_by_name, name='Bookman Old Style', size=13, bold=True)
    
    # Guide & Head of Dept Label
    p_gh_lbl = doc.add_paragraph()
    set_para_format(p_gh_lbl, line_spacing=1.15, space_before=6, space_after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_gh_lbl = p_gh_lbl.add_run("GUIDE & HEAD OF DEPARTMENT")
    set_run_font(r_gh_lbl, name='Bookman Old Style', size=12, bold=True)
    
    # Guide & HOD Signature Table
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_guide = sig_table.cell(0, 0)
    cell_hod = sig_table.cell(0, 1)
    cell_guide.width = Inches(3.25)
    cell_hod.width = Inches(3.25)
    
    p_g = cell_guide.paragraphs[0]
    set_para_format(p_g, line_spacing=1.15, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_g = p_g.add_run("_________________________\nDr. Surekha Kohle\nProject Guide\nDepartment of CS & IT, CSMU")
    set_run_font(r_g, name='Bookman Old Style', size=11, bold=True)
    
    p_h = cell_hod.paragraphs[0]
    set_para_format(p_h, line_spacing=1.15, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_h = p_h.add_run("__________________________\nDr. Praveen Gupta\nHead of Department\nDepartment of CS & IT, CSMU")
    set_run_font(r_h, name='Bookman Old Style', size=11, bold=True)
    
    # Academic Year
    p_yr = doc.add_paragraph()
    set_para_format(p_yr, line_spacing=1.15, space_before=20, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_yr = p_yr.add_run("2026-27")
    set_run_font(r_yr, name='Bookman Old Style', size=12, bold=True)
    
    doc.add_page_break()
    
    # ---------------- PAGE 2: SYNOPSIS, ABSTRACT, 1. INTRODUCTION, 2. PROBLEM STATEMENT ----------------
    p_syn = doc.add_paragraph()
    set_para_format(p_syn, line_spacing=1.15, space_before=0, space_after=8, align=WD_ALIGN_PARAGRAPH.CENTER, keep_with_next=True)
    r_syn = p_syn.add_run("SYNOPSIS")
    set_run_font(r_syn, name='Bookman Old Style', size=12, bold=True)
    
    add_heading_para(doc, "ABSTRACT", space_before=4, space_after=3)
    add_body_para(doc, "The legal sector relies heavily on processing massive volumes of textual data, including statutory codes, judicial precedents, commercial contracts, and litigation evidence. Handling this information overload manually leads to substantial administrative overhead, prolonged research cycles, and severe case backlogs. This seminar reviews how Artificial Intelligence (AI) enhances operational efficiency across modern legal workflows. Drawing upon foundational literature, we analyze the architectural progression from traditional keyword search to transformer-based language models, dense semantic retrieval, and Retrieval-Augmented Generation (RAG). Five prominent benchmark studies are systematically examined: LegalBench for multi-tiered legal reasoning, Magesh et al. for empirical hallucination auditing in commercial legal tools, CUAD for automated contract due diligence, Better Call GPT for human-AI efficiency differentials, and LexGLUE for multi-task legal understanding. In addition, practical modernization initiatives in India—including SUPACE and SUVAS under the e-Courts Project—are evaluated alongside critical challenges surrounding hallucination risks, client data confidentiality, algorithmic bias, and ethical compliance. This is a literature-based academic study synthesizing state-of-the-art research into a coherent operational framework.")
    
    add_heading_para(doc, "1. INTRODUCTION", space_before=8, space_after=3)
    add_body_para(doc, "The legal domain is inherently text-intensive and knowledge-driven. Legal professionals and judicial officers are required to interpret multi-tiered statutory frameworks, synthesize extensive case law, and draft precise transactional documents under strict temporal constraints. Traditionally, legal information retrieval and contract due diligence have depended upon manual reading, physical filing, and boolean keyword searching. These conventional workflows impose significant cognitive fatigue, long turnaround times, and severe institutional backlogs that hinder access to justice. In India alone, over forty million cases remain pending across subordinate courts, high courts, and the Supreme Court, underscoring the critical need for scalable operational efficiency.")
    add_body_para(doc, "Artificial Intelligence serves as a vital catalyst in resolving these procedural bottlenecks. By leveraging Natural Language Processing (NLP), domain-adapted transformer architectures, and Large Language Models (LLMs), AI systems can comprehend specialized legal vocabulary, extract high-stakes contractual liabilities, and identify relevant precedents based on semantic meaning rather than exact word matching. When properly grounded in verified legal authorities through Retrieval-Augmented Generation (RAG), AI empowers practitioners to transition from repetitive manual sorting to analytical reasoning, case strategy, and client advocacy.")
    
    add_heading_para(doc, "2. PROBLEM STATEMENT", space_before=8, space_after=3)
    add_body_para(doc, "Legal documents are characterized by extreme structural complexity, archaic jargon, and jurisdiction-specific statutory references. Traditional computational search methods suffer from keyword brittleness, failing to retrieve authoritative precedents when varied phrasing or synonyms are used. While modern generative AI tools offer rapid document drafting and summarization, their ungrounded deployment creates acute legal and ethical hazards—most notably legal hallucinations, where models invent fictitious judicial citations or misinterpret statutory holdings. Commercial platforms marketed as 'hallucination-free' lack standardized, public auditing, exposing practitioners to professional sanctions. The central problem is how to design, evaluate, and govern AI-assisted workflows that maximize legal operational efficiency while ensuring rigorous doctrinal accuracy, client data confidentiality, and verifiable compliance.")
    
    doc.add_page_break()
    
    # ---------------- PAGE 3: 3. AIM, 4. OBJECTIVES, 5. SCOPE, 6. LITERATURE REVIEW (INTRO) ----------------
    add_heading_para(doc, "3. AIM", space_before=0, space_after=3)
    add_body_para(doc, "To study the foundational principles, model architectures, operational workflows, empirical benchmarks, and ethical limitations of Artificial Intelligence in legal workflows, and to synthesize how these technologies enhance operational efficiency while preserving doctrinal accuracy and professional integrity.")
    
    add_heading_para(doc, "4. OBJECTIVES", space_before=8, space_after=3)
    add_numbered_item(doc, "1.", "Explain Foundational Relationships", "Examine the relationship between Artificial Intelligence, Natural Language Processing, and legal information workflows.")
    add_numbered_item(doc, "2.", "Analyze Legal Transformer Architectures", "Describe domain-adapted models (Legal-BERT, Longformer) and evaluate their capacity to parse lengthy judicial decisions.")
    add_numbered_item(doc, "3.", "Assess Empirical Benchmarks", "Analyze standardized benchmarks (LegalBench, CUAD, LexGLUE) that quantify legal reasoning, clause extraction, and classification.")
    add_numbered_item(doc, "4.", "Examine Human-AI Efficiency Differentials", "Evaluate empirical studies (Better Call GPT) measuring speed, cost, and accuracy differentials between LLMs and lawyers.")
    add_numbered_item(doc, "5.", "Audit Commercial Reliability", "Investigate empirical audits (Magesh et al.) regarding hallucination rates and citation accuracy in commercial legal RAG tools.")
    add_numbered_item(doc, "6.", "Review Indian Legal Modernization", "Examine institutional initiatives in India, including SUPACE (judicial research) and SUVAS (vernacular translation).")
    add_numbered_item(doc, "7.", "Identify Research Gaps & Ethical Safeguards", "Formulate an architectural framework addressing data confidentiality, hallucination mitigation, algorithmic bias, and human oversight.")
    
    add_heading_para(doc, "5. SCOPE OF THE SEMINAR", space_before=8, space_after=3)
    add_body_para(doc, "The seminar covers the end-to-end lifecycle of AI-assisted legal workflows, including legal text ingestion, semantic chunking, vector indexing, retrieval-augmented generation, and human-in-the-loop verification. It evaluates domain-adapted transformers and generative language models across contract due diligence, litigation e-discovery, and judicial research. The study explores both global common-law benchmarks and specific Indian institutional frameworks (SUPACE, SUVAS, e-Courts Project). As a literature-based academic seminar, the scope is focused on comparative analysis, architectural evaluation, and research gap identification without assuming an unverified custom software implementation.")
    
    add_heading_para(doc, "6. LITERATURE REVIEW", space_before=8, space_after=3)
    add_body_para(doc, "To rigorously examine legal efficiency, this seminar reviews five genuine, highly cited, peer-reviewed academic publications spanning top-tier AI venues (NeurIPS, ACL), prominent empirical legal journals (Journal of Empirical Legal Studies, Wiley), and quantitative benchmark archives. Each paper addresses a foundational pillar of legal efficiency:")
    add_bullet_item(doc, "1. LegalBench (Guha et al., 2023):", "A collaborative benchmark of 162 hand-crafted legal tasks across 6 cognitive types evaluating reasoning capabilities across 20 foundation models.")
    add_bullet_item(doc, "2. Hallucination-Free? (Magesh et al., 2025):", "The first preregistered empirical audit evaluating hallucination rates in commercial legal RAG tools (Lexis+ AI, Westlaw AI).")
    add_bullet_item(doc, "3. CUAD Dataset (Hendrycks et al., 2021):", "An expert-annotated corpus of 13,000+ legal labels across 510 contracts designed to benchmark transformer models on 41 clause types.")
    add_bullet_item(doc, "4. Better Call GPT (Martin et al., 2024):", "A quantitative empirical trial comparing LLMs against junior attorneys and legal process outsourcers on contract issue-spotting.")
    add_bullet_item(doc, "5. LexGLUE (Chalkidis et al., 2022):", "A standardized multi-task evaluation suite across seven legal text comprehension and classification benchmarks.")
    
    doc.add_page_break()
    
    # ---------------- PAGE 4: 6. LITERATURE REVIEW (CONTD.) - COMPARATIVE TABLE & SYNTHESIS ----------------
    add_heading_para(doc, "6. LITERATURE REVIEW (Contd.)", space_before=0, space_after=3)
    add_body_para(doc, "The following comparative matrix synthesizes the methodology, findings, stated research gaps, and inherent limitations across all five foundational studies:")
    
    # Concise Comparative Table (5 rows, 5 columns)
    comp_table = doc.add_table(rows=6, cols=5)
    comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(comp_table, color="B0B0B0", sz="4", val="single")
    
    col_widths = [Inches(1.2), Inches(1.1), Inches(1.4), Inches(1.4), Inches(1.4)]
    
    headers = ["Study & Authors", "Venue & Year", "Method & Tech", "Key Findings", "Primary Research Gap"]
    hdr_row = comp_table.rows[0]
    for idx, heading in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.width = col_widths[idx]
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        set_cell_background(cell, "F0F4F8")
        p = cell.paragraphs[0]
        set_para_format(p, line_spacing=1.0, space_before=2, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(heading)
        set_run_font(r, name='Bookman Old Style', size=9.5, bold=True)
        
    table_data = [
        ("LegalBench\n(Guha et al., 2023)", "NeurIPS 2023\n(Datasets Track)", "162 legal tasks; evaluated 20 LLMs (GPT-4, Claude, LLaMA)", "High accuracy on clause extraction; sharp degradation on multi-step statutory interpretation.", "Lack of multi-hop legal reasoning and cross-jurisdictional benchmarks."),
        ("Hallucination-Free?\n(Magesh et al., 2025)", "J. Empir. Legal Stud.\n(Wiley, 2025)", "Preregistered empirical audit of Lexis+ AI, Westlaw AI & GPT-4", "Commercial RAG tools still hallucinate 17%–33% of the time, often citing overturned precedents.", "Absence of independent continuous public auditing protocols for legal RAG."),
        ("CUAD Dataset\n(Hendrycks et al., 2021)", "NeurIPS 2021\n(Datasets Track)", "13,000+ annotations on 510 contracts; RoBERTa, DeBERTa", "Deep transformers automate extraction of 41 clause types, accelerating M&A due diligence.", "Scarcity of training data for complex, non-standardized multi-clause covenants."),
        ("Better Call GPT\n(Martin et al., 2024)", "arXiv:2401.16212\n(Empirical Trial)", "Randomized trial: GPT-4 vs. junior attorneys on contract review", "LLMs matched junior lawyers in issue-spotting; reduced review time by 90%+ at 99% cost reduction.", "Lack of studies on organizational liability and junior mentorship impacts."),
        ("LexGLUE\n(Chalkidis et al., 2022)", "ACL 2022\n(Main Conference)", "7 legal tasks (ECtHR, SCOTUS, etc.); Legal-BERT, Longformer", "Domain-specific pre-training (Legal-BERT) significantly outperforms generic foundation models.", "Absence of multilingual legal benchmarks and generative task evaluation.")
    ]
    
    for r_idx, row_data in enumerate(table_data, start=1):
        row = comp_table.rows[r_idx]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            if r_idx % 2 == 1:
                set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]
            align = WD_ALIGN_PARAGRAPH.CENTER if c_idx < 2 else WD_ALIGN_PARAGRAPH.LEFT
            set_para_format(p, line_spacing=1.05, space_before=1, space_after=1, align=align)
            r = p.add_run(val)
            set_run_font(r, name='Bookman Old Style', size=8.5, bold=(c_idx == 0))
            
    add_subheading_para(doc, "Common Thematic Agreements Across Studies", space_before=8, space_after=2)
    add_body_para(doc, "A systematic synthesis reveals three points of agreement: (1) Automated Triage Drives Massive Efficiency: AI achieves order-of-magnitude speedups in routine clause extraction, metadata categorization, and initial contract issue-spotting (Hendrycks et al., Martin et al.). (2) Domain Adaptation is Essential: Generic AI models underperform when applied naively; domain-specific pre-training on legal corpora (Chalkidis et al.) or tailored legal prompt scaffolding (Guha et al.) is necessary for doctrinal accuracy. (3) The Human-in-the-Loop Imperative: No study supports fully autonomous legal decision-making; AI must serve strictly as an assistive tool under qualified legal oversight.")
    
    add_subheading_para(doc, "Crucial Disagreements and Conflicts in Literature", space_before=6, space_after=2)
    add_body_para(doc, "The literature exposes two major tensions: (1) Vendor Claims vs. Empirical Reality: Commercial providers market legal RAG tools as 'hallucination-free,' yet independent empirical auditing by Magesh et al. proves hallucination rates between 17% and 33%, demonstrating a significant gap between marketing and reality. (2) Task-Level Accuracy vs. Real-World Utility: Benchmarks like LegalBench report notable AI failure rates on complex statutory logic puzzles, whereas empirical trials like Better Call GPT find that LLMs match junior attorneys on routine corporate contract reviews, showing that standardized benchmarks often underestimate practical transactional utility.")
    
    doc.add_page_break()
    
    # ---------------- PAGE 5: DEFENSIBLE RESEARCH GAP & 7. PROPOSED METHODOLOGY (OVERVIEW) ----------------
    add_heading_para(doc, "The Overall Defensible Research Gap in Legal AI", space_before=0, space_after=3)
    add_body_para(doc, "Synthesizing the empirical findings across the five landmark studies reveals a critical, defensible research gap at the core of AI-driven legal efficiency:")
    
    add_subheading_para(doc, "1. What Prior Research Has Successfully Addressed", space_before=4, space_after=2)
    add_body_para(doc, "Prior literature demonstrates that deep learning architectures can automate high-volume legal extraction (CUAD), classify complex judicial rulings across multi-task benchmarks (LexGLUE), and perform fast first-pass contract issue spotting at over 90% cost savings (Better Call GPT). Furthermore, researchers have established rigorous methodologies to benchmark raw LLM reasoning boundaries (LegalBench) and quantify hallucination rates in commercial vector-based RAG platforms (Magesh et al.).")
    
    add_subheading_para(doc, "2. What Remains Insufficiently Studied and Unresolved (The Gap)", space_before=6, space_after=2)
    add_body_para(doc, "While existing studies prove that AI accelerates discrete sub-tasks, there is a fundamental absence of verified, neuro-symbolic verification frameworks that integrate probabilistic vector retrieval with deterministic legal validation to ensure certified reliability. Specifically:")
    add_bullet_item(doc, "• Lack of Deterministic Validation Safeguards:", "Current legal RAG systems rely exclusively on semantic vector similarity, which frequently retrieves overruled, outdated, or jurisdictionally inapplicable precedents. The literature lacks hybrid architectures combining vector embeddings with active citation validation graphs (e.g., automated Shepard's/KeyCite checking).")
    add_bullet_item(doc, "• Unmeasured Multi-Turn Interactive Latency:", "Existing benchmarks evaluate static, one-shot queries. In practice, legal analysis is an iterative, multi-turn dialogue. The cognitive load, verification latency, and interactive efficiency of human-AI collaboration remain largely unquantified.")
    add_bullet_item(doc, "• Scarcity of Non-Western & Multilingual Research:", "Almost all landmark benchmarks focus exclusively on US Federal and UK common law. Developing, multilingual jurisdictions—such as India's dual statutory transition to BNS, BNSS, and BSA—remain critically unaddressed in academic AI research.")
    
    add_subheading_para(doc, "3. Why Bridging This Research Gap Matters", space_before=6, space_after=2)
    add_body_para(doc, "Bridging this gap is crucial across institutional domains: (1) For Courts & Judges: Enables trustworthy docket summarization (e.g., India's SUPACE) to alleviate immense backlogs without risking judicial misdirection. (2) For Law Firms: Allows senior partners to rely on AI-assisted junior drafts with confidence. (3) For Citizens: Democratizes preliminary legal comprehension while safeguarding against fabricated legal advice.")
    
    add_heading_para(doc, "7. PROPOSED METHODOLOGY", space_before=8, space_after=3)
    add_body_para(doc, "To resolve the identified research gaps, this seminar outlines a literature-grounded, multi-layered architectural methodology designed to achieve reliable legal efficiency while systematically preventing hallucination risks. The framework couples dense semantic retrieval with deterministic verification layers.")
    
    doc.add_page_break()
    
    # ---------------- PAGE 6: 7. METHODOLOGY (CONTD.) & 8. CORE TECHNIQUES AND ARCHITECTURES ----------------
    add_heading_para(doc, "7. PROPOSED METHODOLOGY (Contd.)", space_before=0, space_after=3)
    add_body_para(doc, "The proposed workflow consists of five sequential operational phases:")
    add_numbered_item(doc, "Step 1 —", "Legal Document Ingestion & Structure-Aware Parsing", "Ingest heterogeneous legal documents (contracts, court judgments, statutory acts) utilizing layout-aware OCR and semantic parsers that preserve hierarchical clause structures, numbering, and schedules.")
    add_numbered_item(doc, "Step 2 —", "Semantic Chunking & Domain Vector Indexing", "Partition texts into coherent legal clauses (1,000-word windows with 150-word overlap) rather than arbitrary sentence splits. Embed chunks using domain-tuned dense models (e.g., SentenceTransformers) and store in indexed vector databases.")
    add_numbered_item(doc, "Step 3 —", "Knowledge-Grounded RAG Retrieval", "Execute user queries using hybrid dense-sparse retrieval. Enforce strict metadata filtering by jurisdiction, court hierarchy, and enactment year to eliminate extraneous precedents.")
    add_numbered_item(doc, "Step 4 —", "Neuro-Symbolic Rule Checking & Deterministic Fallback", "Validate retrieved context through deterministic rule-based checkers. Cross-reference case citations against active statutory databases; if confidence falls below threshold, trigger deterministic offline fallback parsers.")
    add_numbered_item(doc, "Step 5 —", "Human-in-the-Loop Supervisory Interface", "Present synthesized outputs accompanied by direct source attribution, highlighted clause citations, and explicit confidence scores, ensuring licensed attorneys retain final validation authority.")
    
    add_heading_para(doc, "8. CORE TECHNIQUES AND ARCHITECTURES", space_before=8, space_after=3)
    add_bullet_item(doc, "Transformer-Based Legal Language Models:", "Models like Legal-BERT incorporate domain pre-training on legal codes, capturing statutory grammar far better than generic models. Longformer models utilize sliding-window local attention with global tokens to process 100-page court dockets without context truncation.")
    add_bullet_item(doc, "Dense Vector Retrieval & Semantic Search:", "Unlike rigid boolean search, dense retrieval maps legal queries and precedents into continuous semantic embedding spaces. This enables retrieval based on conceptual legal meaning, overcoming keyword brittleness across varied terminology.")
    add_bullet_item(doc, "Retrieval-Augmented Generation (RAG):", "RAG separates static model parameters from dynamic legal knowledge. By injecting retrieved statutory sections into the LLM's prompt context, RAG grounds generated summaries in authoritative texts, substantially reducing speculative hallucinations.")
    add_bullet_item(doc, "Neuro-Symbolic Validation Pipelines:", "Combines the natural language fluency of deep learning with the deterministic precision of statutory knowledge graphs and legal rule engines, enforcing strict judicial validity before answers are displayed.")
    
    doc.add_page_break()
    
    # ---------------- PAGE 7: 9. EVALUATION METRICS & 10. PRACTICAL APPLICATIONS ----------------
    add_heading_para(doc, "9. EVALUATION METRICS AND BENCHMARKING", space_before=0, space_after=3)
    add_body_para(doc, "Rigorous evaluation of legal AI systems requires a balanced combination of technical information retrieval metrics, generation faithfulness metrics, and operational efficiency indicators:")
    add_bullet_item(doc, "Information Retrieval Metrics:", "Precision, Recall@K, and Mean Reciprocal Rank (MRR) evaluate whether relevant statutory provisions and case precedents appear within top retrieval ranks. In legal domains, high recall is vital to ensure critical precedents are not omitted.")
    add_bullet_item(doc, "RAG Triad Faithfulness Metrics:", "Evaluates three core dimensions: Context Relevance (retrieved excerpts are pertinent to the query), Groundedness (all claims in the output derive strictly from retrieved context), and Answer Faithfulness (absence of fabricated holdings or citations).")
    add_bullet_item(doc, "Doctrinal Reasoning Evaluation:", "Utilizes LegalBench's 162-task taxonomy to measure multi-tiered legal logic, including rule application, issue-spotting, statutory interpretation, and counterfactual argumentation.")
    add_bullet_item(doc, "Operational Efficiency Indicators:", "Measures turnaround time reductions (from hours to seconds), cost-per-review metrics, and practitioner agreement rates against human baselines, as established by Martin et al.")
    
    add_heading_para(doc, "10. APPLICATIONS", space_before=8, space_after=3)
    add_body_para(doc, "Artificial Intelligence demonstrates diverse, high-impact applications across corporate, litigation, and judicial settings:")
    add_bullet_item(doc, "Automated Contract Due Diligence:", "AI systems extract critical covenants (indemnification, non-compete, change-of-control, liability caps) across hundreds of commercial agreements during merger and acquisition reviews, compressing weeks of manual reading into minutes.")
    add_bullet_item(doc, "Litigation E-Discovery & Precedent Retrieval:", "Semantic search models rapidly filter millions of internal communications, identifying relevant evidentiary records and relevant precedents with high contextual accuracy.")
    add_bullet_item(doc, "Indian Judicial Modernization Initiatives:", "Specialized AI platforms are actively transforming the Indian legal landscape under the e-Courts Project: SUVAS (Supreme Court Vidhik Anuvaad Software) uses neural machine translation to convert Supreme Court judgments into scheduled Indian regional languages; SUPACE (Supreme Court Portal for Assistance in Court's Efficiency) operates as an AI research assistant extracting facts and points of law to assist judges in accelerating docket disposal.")
    add_bullet_item(doc, "Citizen Legal Literacy & Self-Help Triage:", "AI-driven informational interfaces empower small business owners and ordinary citizens to comprehend complex legal contracts and navigate procedural filing requirements before incurring heavy legal fees.")
    
    doc.add_page_break()
    
    # ---------------- PAGE 8: 11. CHALLENGES & ETHICS, 12. FUTURE SCOPE, 13. EXPECTED OUTCOMES ----------------
    add_heading_para(doc, "11. CHALLENGES AND ETHICAL CONSIDERATIONS", space_before=0, space_after=3)
    add_body_para(doc, "While AI unlocks massive operational efficiencies, its deployment in legal contexts introduces profound technical, ethical, and regulatory challenges that demand rigorous safeguards:")
    add_bullet_item(doc, "Hallucination Risks & Judicial Sanctions:", "LLMs can generate fabricated case citations with high confidence. Submitting unverified AI citations has led to formal judicial sanctions under court ethics rules (e.g., Mata v. Avianca), highlighting the necessity of mandatory verification.")
    add_bullet_item(doc, "Client Confidentiality & Privilege:", "Transmitting sensitive client contracts to public commercial LLM APIs risks breaching attorney-client privilege and data privacy regulations. Enterprise architectures must utilize on-premises deployments or zero-retention encryption pipelines.")
    add_bullet_item(doc, "Algorithmic Bias & Jurisprudential Fairness:", "AI models trained on historical case law risk perpetuating historical societal and socioeconomic disparities if deployed in predictive justice or bail recommendation systems without bias auditing.")
    add_bullet_item(doc, "Unauthorized Practice of Law (UPL):", "AI tools must function strictly as informational and research decision-support systems for licensed attorneys, accompanied by clear disclaimers that they do not constitute formal legal counsel.")
    
    add_heading_para(doc, "12. FUTURE SCOPE", space_before=8, space_after=3)
    add_body_para(doc, "Future research directions in legal AI include: (1) Neuro-symbolic integration combining deep language models with formal statutory knowledge graphs and automated Shepard's/KeyCite validation pipelines. (2) Autonomous agentic workflows capable of multi-turn legal research, interactive document drafting, and procedural docket tracking. (3) Expansion to multilingual legal corpora in emerging jurisdictions, particularly supporting India's transition to the new criminal law codes (Bharatiya Nyaya Sanhita, Bharatiya Nagarik Suraksha Sanhita, and Bharatiya Sakshya Adhiniyam).")
    
    add_heading_para(doc, "13. EXPECTED OUTCOMES", space_before=8, space_after=3)
    add_body_para(doc, "This seminar provides a comprehensive conceptual and technical foundation in legal AI. Students and practitioners will understand how domain-adapted transformers and RAG architectures enhance operational efficiency, how to evaluate commercial tool reliability using empirical benchmarks, and how to implement responsible, human-in-the-loop safeguards that uphold professional integrity and legal ethics.")
    
    doc.add_page_break()
    
    # ---------------- PAGE 9: 14. CONCLUSION & REFERENCES ----------------
    add_heading_para(doc, "14. CONCLUSION", space_before=0, space_after=3)
    add_body_para(doc, "Artificial Intelligence represents the most transformative technological advancement in the legal profession since the digitization of legal libraries. When powered by domain-adapted language models, semantic vector retrieval, and Retrieval-Augmented Generation, AI delivers order-of-magnitude reductions in contract review duration, speeds up case law discovery, and significantly lowers operational costs. However, empirical literature conclusively demonstrates that AI cannot replace the indispensable human faculties of moral reasoning, contextual empathy, ethical accountability, and courtroom advocacy. Furthermore, the persistent reality of citation hallucinations and client privacy risks requires that AI be deployed strictly as an assistive cognitive amplifier supervised by qualified practitioners. By pairing high-speed machine retrieval with rigorous human oversight and deterministic verification safeguards, the legal profession can achieve unprecedented efficiency while safeguarding the fundamental integrity of justice.")
    
    add_heading_para(doc, "REFERENCES", space_before=8, space_after=3)
    
    def add_ref_entry(doc, ref_num, text):
        p = doc.add_paragraph()
        set_para_format(p, line_spacing=1.15, space_before=1, space_after=4, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)
        r_num = p.add_run(f"[{ref_num}] ")
        set_run_font(r_num, name='Bookman Old Style', size=10, bold=True)
        r_txt = p.add_run(text)
        set_run_font(r_txt, name='Bookman Old Style', size=9.5, bold=False)
        return p
        
    add_ref_entry(doc, 1, 'N. Guha, J. Nyarko, D. E. Ho, C. Ré, A. Chilton, K. Tobia, J. R. Nay, et al., "LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models," in Proceedings of the 37th Conference on Neural Information Processing Systems (NeurIPS 2023) Track on Datasets and Benchmarks, New Orleans, LA, USA, Dec. 2023. DOI: 10.48550/arXiv.2308.11462.')
    add_ref_entry(doc, 2, 'V. Magesh, F. Surani, M. Dahl, M. Suzgun, C. D. Manning, and D. E. Ho, "Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools," Journal of Empirical Legal Studies, Wiley, 2025. Preprint: arXiv:2405.20362. DOI: 10.1111/jels.12413.')
    add_ref_entry(doc, 3, 'D. Hendrycks, C. Burns, A. Chen, and S. Ball, "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review," in Proceedings of the 35th Conference on Neural Information Processing Systems (NeurIPS 2021) Track on Datasets and Benchmarks, Dec. 2021. DOI: 10.48550/arXiv.2103.06268.')
    add_ref_entry(doc, 4, 'L. Martin, N. Whitehouse, S. Yiu, L. Catterson, and R. Perera, "Better Call GPT, Comparing Large Language Models Against Lawyers," arXiv preprint arXiv:2401.16212, Jan. 2024. DOI: 10.48550/arXiv.2401.16212.')
    add_ref_entry(doc, 5, 'I. Chalkidis, A. Jana, D. Hartung, M. Bommarito, I. Androutsopoulos, D. M. Katz, and N. Aletras, "LexGLUE: A Benchmark Dataset for Legal Language Understanding in English," in Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL 2022), Dublin, Ireland, May 2022, pp. 4310–4330. DOI: 10.18653/v1/2022.acl-long.297.')
    add_ref_entry(doc, 6, 'P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in Advances in Neural Information Processing Systems (NeurIPS 2020), vol. 33, 2020, pp. 9459–9474.')
    add_ref_entry(doc, 7, 'Supreme Court of India, "AI in the Indian Judiciary: An Overview of SUPACE and SUVAS Initiatives," Official Reports of the Supreme Court of India Artificial Intelligence Committee, New Delhi, India, 2021–2023. [Online]. Available: https://main.sci.gov.in/')
    
    doc.add_page_break()
    
    # ---------------- PAGE 10: APPROVAL & SIGN-OFF (CERTIFICATE PAGE) ----------------
    p_sep1 = doc.add_paragraph()
    set_para_format(p_sep1, line_spacing=1.0, space_before=16, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_sep1 = p_sep1.add_run("=============================================================================")
    set_run_font(r_sep1, name='Bookman Old Style', size=11, bold=True)
    
    p_cert_title = doc.add_paragraph()
    set_para_format(p_cert_title, line_spacing=1.15, space_before=4, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_cert_title = p_cert_title.add_run("APPROVAL & SIGN-OFF")
    set_run_font(r_cert_title, name='Bookman Old Style', size=13, bold=True)
    
    p_sep2 = doc.add_paragraph()
    set_para_format(p_sep2, line_spacing=1.0, space_before=4, space_after=24, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_sep2 = p_sep2.add_run("=============================================================================")
    set_run_font(r_sep2, name='Bookman Old Style', size=11, bold=True)
    
    p_cert_body = doc.add_paragraph()
    set_para_format(p_cert_body, line_spacing=1.5, space_before=12, space_after=20, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    r_cert_body = p_cert_body.add_run(
        "This is to certify that the Seminar Synopsis entitled “Enhancing Legal Efficiency Through Artificial Intelligence” "
        "has been successfully submitted by the following student of Department of Computer Science & Information Technology, "
        "Chhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai for the academic year 2026-27 in partial fulfillment of "
        "the requirements for the Degree of Master of Computer Application:"
    )
    set_run_font(r_cert_body, name='Bookman Old Style', size=12, bold=False)
    
    p_cand = doc.add_paragraph()
    set_para_format(p_cand, line_spacing=1.5, space_before=6, space_after=36, align=WD_ALIGN_PARAGRAPH.LEFT)
    p_cand.paragraph_format.left_indent = Inches(0.5)
    r_cand = p_cand.add_run("1. Rohan Bongane")
    set_run_font(r_cand, name='Bookman Old Style', size=12, bold=True)
    
    # Signature Table for Certificate
    cert_sig_table = doc.add_table(rows=1, cols=2)
    cert_sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_g = cert_sig_table.cell(0, 0)
    c_h = cert_sig_table.cell(0, 1)
    c_g.width = Inches(3.25)
    c_h.width = Inches(3.25)
    
    p_cg = c_g.paragraphs[0]
    set_para_format(p_cg, line_spacing=1.15, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_cg = p_cg.add_run("______________________________\nDr. Surekha Kohle\nProject Guide\nDepartment of CS & IT, CSMU")
    set_run_font(r_cg, name='Bookman Old Style', size=11, bold=True)
    
    p_ch = c_h.paragraphs[0]
    set_para_format(p_ch, line_spacing=1.15, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_ch = p_ch.add_run("_______________________________\nDr. Praveen Gupta\nHead of Department\nDepartment of CS & IT, CSMU")
    set_run_font(r_ch, name='Bookman Old Style', size=11, bold=True)
    
    return doc

if __name__ == "__main__":
    out_docx = "Legal_AI_Seminar_Synopsis_Final.docx"
    print(f"Building document: {out_docx}...")
    doc = build_synopsis_document()
    doc.save(out_docx)
    print("DOCX successfully generated.")
