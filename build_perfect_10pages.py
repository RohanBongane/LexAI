import os
import sys
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_run_font(run, name='Bookman Old Style', size=12, bold=False, italic=False, color_rgb=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb

def set_para_format(p, line_spacing=1.5, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, keep_with_next=False):
    p.alignment = align
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = keep_with_next

def add_heading(doc, text, space_before=2, space_after=1, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.15, space_before=space_before, space_after=space_after, align=align, keep_with_next=True)
    run = p.add_run(text)
    set_run_font(run, name='Bookman Old Style', size=12, bold=True)
    return p

def add_subheading(doc, text, space_before=2, space_after=1, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.15, space_before=space_before, space_after=space_after, align=align, keep_with_next=True)
    run = p.add_run(text)
    set_run_font(run, name='Bookman Old Style', size=12, bold=True)
    return p

def add_body(doc, text, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.5, space_before=space_before, space_after=space_after, align=align)
    run = p.add_run(text)
    set_run_font(run, name='Bookman Old Style', size=12, bold=False)
    return p

def add_bullet(doc, bold_prefix, text, space_before=0, space_after=1):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.5, space_before=space_before, space_after=space_after, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    p.paragraph_format.left_indent = Inches(0.2)
    r1 = p.add_run(bold_prefix + " ")
    set_run_font(r1, name='Bookman Old Style', size=12, bold=True)
    r2 = p.add_run(text)
    set_run_font(r2, name='Bookman Old Style', size=12, bold=False)
    return p

def add_numbered(doc, num_str, text, space_before=0, space_after=1):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.5, space_before=space_before, space_after=space_after, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    p.paragraph_format.left_indent = Inches(0.25)
    r_num = p.add_run(num_str + " ")
    set_run_font(r_num, name='Bookman Old Style', size=12, bold=True)
    r_txt = p.add_run(text)
    set_run_font(r_txt, name='Bookman Old Style', size=12, bold=False)
    return p

def add_page_number_field(run):
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

def set_cell_margins(cell, top=5, bottom=5, left=8, right=8):
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

def set_table_borders(table, color="A0A0A0", sz="4", val="single"):
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

def build_perfect_10page_synopsis():
    doc = Document()
    
    # Page setup: A4 size (8.27 in x 11.69 in = 210 mm x 297 mm)
    # Margins: 1.0 inch all around (72 pt)
    s1 = doc.sections[0]
    s1.page_width = Inches(8.27)
    s1.page_height = Inches(11.69)
    s1.top_margin = Inches(1.0)
    s1.bottom_margin = Inches(1.0)
    s1.left_margin = Inches(1.0)
    s1.right_margin = Inches(1.0)
    s1.different_first_page_header_footer = True
    
    # Cover page header & footer
    hdr_first = s1.first_page_header
    p_hdr1 = hdr_first.paragraphs[0]
    set_para_format(p_hdr1, line_spacing=1.0, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.RIGHT)
    r_hdr1 = p_hdr1.add_run("MCA | Seminar Synopsis")
    set_run_font(r_hdr1, name='Bookman Old Style', size=10, bold=False, color_rgb=RGBColor(80, 80, 80))
    
    ftr_first = s1.first_page_footer
    p_ftr1 = ftr_first.paragraphs[0]
    set_para_format(p_ftr1, line_spacing=1.0, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_ftr1 = p_ftr1.add_run("Enhancing Legal Efficiency Through Artificial Intelligence")
    set_run_font(r_ftr1, name='Bookman Old Style', size=10, bold=False, color_rgb=RGBColor(80, 80, 80))
    
    # Normal Header & Footer for Subsequent Pages (Starting from Introduction)
    hdr_normal = s1.header
    p_hdr2 = hdr_normal.paragraphs[0]
    set_para_format(p_hdr2, line_spacing=1.0, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.RIGHT)
    r_hdr2 = p_hdr2.add_run("MCA | Seminar Synopsis")
    set_run_font(r_hdr2, name='Bookman Old Style', size=10, bold=False, color_rgb=RGBColor(80, 80, 80))
    
    ftr_normal = s1.footer
    p_ftr2 = ftr_normal.paragraphs[0]
    set_para_format(p_ftr2, line_spacing=1.0, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    r_ftr2_title = p_ftr2.add_run("Enhancing Legal Efficiency Through Artificial Intelligence\t")
    set_run_font(r_ftr2_title, name='Bookman Old Style', size=10, bold=False, color_rgb=RGBColor(80, 80, 80))
    r_ftr2_page = p_ftr2.add_run()
    set_run_font(r_ftr2_page, name='Bookman Old Style', size=10, bold=True, color_rgb=RGBColor(80, 80, 80))
    add_page_number_field(r_ftr2_page)
    
    # ======================== PAGE 1: COVER PAGE ========================
    p_top_sp = doc.add_paragraph()
    set_para_format(p_top_sp, line_spacing=1.0, space_before=0, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    title_table = doc.add_table(rows=1, cols=1)
    title_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    title_cell = title_table.cell(0, 0)
    title_cell.width = Inches(6.27)
    set_cell_margins(title_cell, top=100, bottom=100, left=120, right=120)
    
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
    set_para_format(p_box, line_spacing=1.15, space_before=2, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_box = p_box.add_run("“Enhancing Legal Efficiency Through Artificial Intelligence”")
    set_run_font(r_box, name='Bookman Old Style', size=13, bold=True)
    
    p_sub = doc.add_paragraph()
    set_para_format(p_sub, line_spacing=1.15, space_before=10, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_sub = p_sub.add_run("Submitted to")
    set_run_font(r_sub, name='Bookman Old Style', size=12, bold=False)
    
    p_uni = doc.add_paragraph()
    set_para_format(p_uni, line_spacing=1.15, space_before=2, space_after=8, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_uni = p_uni.add_run("Chhatrapati Shivaji Maharaj University,\nPanvel, Navi Mumbai")
    set_run_font(r_uni, name='Bookman Old Style', size=14, bold=True)
    
    if os.path.exists("csmu_logo.png"):
        p_logo = doc.add_paragraph()
        set_para_format(p_logo, line_spacing=1.0, space_before=2, space_after=8, align=WD_ALIGN_PARAGRAPH.CENTER)
        p_logo.add_run().add_picture("csmu_logo.png", width=Inches(1.5))
    
    p_deg_req = doc.add_paragraph()
    set_para_format(p_deg_req, line_spacing=1.15, space_before=4, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_deg_req = p_deg_req.add_run("for the partial fulfillment of requirement for the Degree of")
    set_run_font(r_deg_req, name='Bookman Old Style', size=11, bold=False)
    
    p_deg = doc.add_paragraph()
    set_para_format(p_deg, line_spacing=1.15, space_before=2, space_after=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_deg = p_deg.add_run("Master of Computer Application")
    set_run_font(r_deg, name='Bookman Old Style', size=13, bold=True)
    
    p_by_lbl = doc.add_paragraph()
    set_para_format(p_by_lbl, line_spacing=1.15, space_before=4, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_by_lbl = p_by_lbl.add_run("Submitted By")
    set_run_font(r_by_lbl, name='Bookman Old Style', size=12, bold=False)
    
    p_by_name = doc.add_paragraph()
    set_para_format(p_by_name, line_spacing=1.15, space_before=2, space_after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_by_name = p_by_name.add_run("Rohan Bongane")
    set_run_font(r_by_name, name='Bookman Old Style', size=13, bold=True)
    
    p_gh_lbl = doc.add_paragraph()
    set_para_format(p_gh_lbl, line_spacing=1.15, space_before=4, space_after=6, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_gh_lbl = p_gh_lbl.add_run("GUIDE & HEAD OF DEPARTMENT")
    set_run_font(r_gh_lbl, name='Bookman Old Style', size=12, bold=True)
    
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_guide = sig_table.cell(0, 0)
    cell_hod = sig_table.cell(0, 1)
    cell_guide.width = Inches(3.13)
    cell_hod.width = Inches(3.13)
    
    p_g = cell_guide.paragraphs[0]
    set_para_format(p_g, line_spacing=1.15, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_g = p_g.add_run("_________________________\nDr. Surekha Kohle\nProject Guide\nDepartment of CS & IT, CSMU")
    set_run_font(r_g, name='Bookman Old Style', size=11, bold=True)
    
    p_h = cell_hod.paragraphs[0]
    set_para_format(p_h, line_spacing=1.15, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_h = p_h.add_run("__________________________\nDr. Praveen Gupta\nHead of Department\nDepartment of CS & IT, CSMU")
    set_run_font(r_h, name='Bookman Old Style', size=11, bold=True)
    
    p_yr = doc.add_paragraph()
    set_para_format(p_yr, line_spacing=1.15, space_before=12, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_yr = p_yr.add_run("2026-27")
    set_run_font(r_yr, name='Bookman Old Style', size=12, bold=True)
    
    doc.add_page_break()
    
    # ======================== PAGE 2: SYNOPSIS, ABSTRACT, 1. INTRODUCTION ========================
    p_syn = doc.add_paragraph()
    set_para_format(p_syn, line_spacing=1.15, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER, keep_with_next=True)
    r_syn = p_syn.add_run("SYNOPSIS")
    set_run_font(r_syn, name='Bookman Old Style', size=12, bold=True)
    
    add_heading(doc, "ABSTRACT", space_before=2, space_after=1)
    add_body(doc, "The legal sector relies on processing vast textual volumes, including case precedents, commercial contracts, and statutory codes. Manual processing causes administrative delays, high overhead, and severe judicial backlogs. Maximizing throughput while preserving analytical precision defines legal efficiency. Artificial Intelligence (AI) serves as a vital catalyst by automating routine, standardized tasks. Through Natural Language Processing (NLP) and Large Language Models (LLMs), AI empowers professionals to extract structured insights and focus on complex advocacy and strategic reasoning. This seminar systematically synthesizes five foundational benchmarks: LegalBench, commercial RAG reliability audits by Magesh et al., CUAD, Better Call GPT, and LexGLUE. Practical modernization initiatives in India, such as SUVAS and SUPACE, are critically evaluated alongside essential safeguards concerning hallucination risks, client data confidentiality, and algorithmic fairness.", space_after=2)
    
    add_heading(doc, "1. INTRODUCTION", space_before=2, space_after=1)
    add_body(doc, "The legal domain is inherently text-intensive, requiring practitioners to interpret statutory codes, synthesize precedents, and draft complex transactional instruments. Traditionally, legal research and due diligence relied on manual analysis and rigid keyword searches, causing cognitive fatigue, delayed turnaround, and severe institutional backlogs. In India alone, over forty million cases remain pending across courts, underscoring the urgent need for procedural efficiency.", space_after=2)
    add_body(doc, "Artificial Intelligence addresses these bottlenecks through domain-adapted transformers and Large Language Models. When grounded in verified authorities via Retrieval-Augmented Generation (RAG), AI enables rapid document discovery and synthesis, allowing practitioners to transition from repetitive manual sorting to higher-order legal reasoning while ensuring verifiable accuracy.", space_after=0)
    
    doc.add_page_break()
    
    # ======================== PAGE 3: 2. PROBLEM STATEMENT, 3. AIM, 4. OBJECTIVES ========================
    add_heading(doc, "2. PROBLEM STATEMENT", space_before=0, space_after=1)
    add_body(doc, "Legal documents exhibit intricate structural complexity, archaic terminology, and specialized jurisdictional references. Traditional computational search suffers from keyword brittleness, failing when terminology varies. While generative AI models enable rapid drafting and summarization, ungrounded deployment introduces severe risks—most notably hallucinations where models fabricate fictitious citations. Commercial platforms marketed as 'hallucination-free' lack public auditing. The central problem is how to design, evaluate, and govern AI workflows that maximize operational efficiency while guaranteeing doctrinal accuracy, client confidentiality, and ethical compliance.", space_after=2)
    
    add_heading(doc, "3. AIM", space_before=2, space_after=1)
    add_body(doc, "To study the foundational principles, model architectures, empirical benchmarks, and ethical boundaries of Artificial Intelligence in legal workflows, and to examine how these methods support automated document analysis while maintaining strict doctrinal accuracy.", space_after=2)
    
    add_heading(doc, "4. OBJECTIVES", space_before=2, space_after=1)
    add_numbered(doc, "1.", "Explain the relationship between AI, deep learning, NLP, and legal information workflows.", space_after=1)
    add_numbered(doc, "2.", "Describe domain-adapted legal transformers (Legal-BERT, Longformer) for long document analysis.", space_after=1)
    add_numbered(doc, "3.", "Differentiate legal classification, contract extraction, semantic search, and generation tasks.", space_after=1)
    add_numbered(doc, "4.", "Examine empirical benchmarks (LegalBench, CUAD, LexGLUE) measuring legal reasoning and accuracy.", space_after=1)
    add_numbered(doc, "5.", "Evaluate human-AI productivity differentials (Better Call GPT) in contract review speed and cost.", space_after=1)
    add_numbered(doc, "6.", "Audit commercial legal RAG tools (Magesh et al.) regarding hallucination rates and citation validity.", space_after=1)
    add_numbered(doc, "7.", "Analyze practical applications, Indian judicial initiatives (SUPACE, SUVAS), and ethical safeguards.", space_after=0)
    
    doc.add_page_break()
    
    # ======================== PAGE 4: 5. SCOPE, 6. LITERATURE REVIEW (OVERVIEW OF 5 PAPERS) ========================
    add_heading(doc, "5. SCOPE OF THE SEMINAR", space_before=0, space_after=1)
    add_body(doc, "The seminar covers major AI-assisted legal tasks across the document lifecycle: text ingestion, semantic chunking, vector indexing, retrieval-augmented generation, and human-in-the-loop verification. It evaluates domain-adapted transformers and generative models across transactional contract review and litigation research. It explores common-law benchmarks and Indian judicial digitization initiatives (SUPACE, SUVAS, e-Courts Project). As a literature-based academic seminar, the scope focuses on rigorous synthesis and comparative analysis of peer-reviewed benchmarks without assuming an unverified custom software implementation.", space_after=2)
    
    add_heading(doc, "6. LITERATURE REVIEW", space_before=2, space_after=1)
    add_body(doc, "To rigorously examine legal efficiency, this seminar reviews five genuine, highly cited, peer-reviewed academic publications across top AI conferences (NeurIPS, ACL), prominent empirical legal journals (Journal of Empirical Legal Studies), and quantitative benchmark archives:", space_after=1)
    add_bullet(doc, "1. LegalBench (Guha et al., 2023):", "A collaborative benchmark evaluating 162 legal reasoning tasks across 20 foundation models, testing issue-spotting, rule application, and statutory interpretation.", space_after=1)
    add_bullet(doc, "2. Hallucination-Free? (Magesh et al., 2025):", "The first preregistered empirical audit of commercial legal RAG tools (Lexis+ AI, Westlaw AI), measuring real-world hallucination rates and citation accuracy.", space_after=1)
    add_bullet(doc, "3. CUAD Dataset (Hendrycks et al., 2021):", "An expert-annotated corpus of 13,000+ labels across 510 commercial contracts designed to benchmark deep transformers on 41 standardized clause types.", space_after=1)
    add_bullet(doc, "4. Better Call GPT (Martin et al., 2024):", "A randomized empirical trial comparing LLMs against junior attorneys and legal process outsourcers, quantifying review speed, cost, and accuracy differentials.", space_after=1)
    add_bullet(doc, "5. LexGLUE (Chalkidis et al., 2022):", "A multi-task benchmark across seven legal NLP datasets, demonstrating that domain-specific pre-training (Legal-BERT) is essential for legal language comprehension.", space_after=0)
    
    doc.add_page_break()
    
    # ======================== PAGE 5: 6. LITERATURE REVIEW (CONTD.) - TABLE & SYNTHESIS ========================
    add_heading(doc, "6. LITERATURE REVIEW (Contd.)", space_before=0, space_after=1)
    add_body(doc, "The comparative matrix below synthesizes the five foundational benchmark studies:", space_after=1)
    
    comp_table = doc.add_table(rows=6, cols=5)
    comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(comp_table, color="A0A0A0", sz="4", val="single")
    
    col_widths = [Inches(1.2), Inches(1.05), Inches(1.35), Inches(1.35), Inches(1.32)]
    headers = ["Study & Authors", "Venue & Year", "Method & Tech", "Key Findings", "Primary Research Gap"]
    hdr_row = comp_table.rows[0]
    for idx, heading in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.width = col_widths[idx]
        set_cell_margins(cell, top=5, bottom=5, left=6, right=6)
        set_cell_background(cell, "F0F4F8")
        p = cell.paragraphs[0]
        set_para_format(p, line_spacing=1.0, space_before=1, space_after=1, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(heading)
        set_run_font(r, name='Bookman Old Style', size=8.0, bold=True)
        
    table_data = [
        ("LegalBench\n(Guha et al., 2023)", "NeurIPS 2023\n(Datasets)", "162 legal tasks; evaluated 20 LLMs (GPT-4, Claude)", "High accuracy on clause extraction; sharp drop on multi-step statutory logic.", "Lack of multi-hop legal reasoning and cross-jurisdiction benchmarks."),
        ("Hallucination-Free?\n(Magesh et al., 2025)", "J. Emp. Leg. Stud.\n(Wiley, 2025)", "Preregistered audit of Lexis+ AI, Westlaw AI & GPT-4", "Commercial RAG tools hallucinate 17%–33% of the time; cite bad precedents.", "Absence of independent continuous public auditing protocols."),
        ("CUAD Dataset\n(Hendrycks et al., 2021)", "NeurIPS 2021\n(Datasets)", "13k labels on 510 contracts; RoBERTa, DeBERTa", "Deep transformers automate extraction of 41 clause types in M&A review.", "Scarcity of training data for complex multi-clause covenants."),
        ("Better Call GPT\n(Martin et al., 2024)", "arXiv:2401.16212\n(Trial)", "Randomized trial: GPT-4 vs. junior attorneys", "LLMs matched junior lawyers; reduced review time by 90%+ at 99% cost reduction.", "Lack of studies on organizational liability and junior mentorship."),
        ("LexGLUE\n(Chalkidis et al., 2022)", "ACL 2022\n(Main Conf.)", "7 legal tasks (ECtHR, SCOTUS); Legal-BERT", "Domain-specific pre-training (Legal-BERT) outperforms generic models.", "Absence of multilingual benchmarks and generative task evaluation.")
    ]
    
    for r_idx, row_data in enumerate(table_data, start=1):
        row = comp_table.rows[r_idx]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            set_cell_margins(cell, top=4, bottom=4, left=6, right=6)
            if r_idx % 2 == 1:
                set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]
            align = WD_ALIGN_PARAGRAPH.CENTER if c_idx < 2 else WD_ALIGN_PARAGRAPH.LEFT
            set_para_format(p, line_spacing=1.0, space_before=1, space_after=1, align=align)
            r = p.add_run(val)
            set_run_font(r, name='Bookman Old Style', size=7.0, bold=(c_idx == 0))
            
    add_subheading(doc, "Common Thematic Agreements Across Studies", space_before=2, space_after=1)
    add_body(doc, "The literature exhibits strong consensus on three principles: (1) Automated Triage Drives Massive Efficiency: AI achieves substantial speedups in routine clause extraction and initial contract review (Hendrycks et al., Martin et al.). (2) Domain Adaptation is Essential: Generic models underperform; domain-specific pre-training on legal corpora (Chalkidis et al.) or tailored prompt scaffolding (Guha et al.) is necessary for doctrinal accuracy. (3) The Human-in-the-Loop Imperative: No study supports autonomous legal practice; AI must operate strictly as an assistive tool under qualified legal oversight.", space_after=1)
    
    add_subheading(doc, "Crucial Disagreements and Conflicts in Literature", space_before=2, space_after=1)
    add_body(doc, "The literature highlights two key tensions: (1) Vendor Claims vs. Empirical Reality: Vendors market legal RAG tools as 'hallucination-free,' yet empirical auditing by Magesh et al. proves hallucination rates between 17% and 33%, demonstrating a significant credibility gap. (2) Task-Level Accuracy vs. Real-World Utility: Benchmarks report notable AI failure rates on complex statutory logic puzzles, whereas empirical trials find that LLMs match junior attorneys on routine corporate contract reviews, showing that standardized benchmarks often underestimate practical transactional utility.", space_after=0)
    
    doc.add_page_break()
    
    # ======================== PAGE 6: DEFENSIBLE RESEARCH GAP & 7. PROPOSED METHODOLOGY ========================
    add_heading(doc, "The Overall Defensible Research Gap in Legal AI", space_before=0, space_after=1)
    add_bullet(doc, "• Prior Addressed Foundations:", "Prior literature confirms that deep learning automates contract extraction (CUAD), judicial classification (LexGLUE), and first-pass issue spotting at 90%+ cost savings (Better Call GPT), while benchmarks map LLM reasoning boundaries (LegalBench) and RAG hallucination rates (Magesh et al.).", space_after=1)
    add_bullet(doc, "• Crucial Research Gaps:", "While AI accelerates discrete tasks, literature lacks neuro-symbolic frameworks integrating vector retrieval with deterministic legal validation. Standard RAG relies purely on semantic similarity, frequently retrieving overruled precedents without active citation validation graphs. Furthermore, landmark research remains US/UK-centric, leaving multilingual legal jurisdictions—such as India's transition to BNS, BNSS, and BSA—critically unexamined.", space_after=1)
    add_bullet(doc, "• Significance of Bridging Gaps:", "Bridging these gaps enables trustworthy judicial summarization (e.g., India's SUPACE) to alleviate massive court backlogs, ensures dependable attorney-facing decision support, and democratizes legal literacy safely.", space_after=2)
    
    add_heading(doc, "7. PROPOSED METHODOLOGY", space_before=2, space_after=1)
    add_body(doc, "To address these gaps, this seminar synthesizes a literature-grounded methodology ensuring verifiable efficiency across five steps:", space_after=1)
    add_numbered(doc, "Step 1—Data Ingestion:", "Ingest legal texts using layout-aware OCR and semantic parsers preserving hierarchical clause structures.", space_after=1)
    add_numbered(doc, "Step 2—Semantic Chunking:", "Segment documents into clauses (1,000-word windows, 150-word overlap) embedded via legal dense encoders.", space_after=1)
    add_numbered(doc, "Step 3—Hybrid Retrieval:", "Execute hybrid dense-sparse retrieval combining vector similarity with BM25 and court metadata filters.", space_after=1)
    add_numbered(doc, "Step 4—Rule-Based Guardrails:", "Cross-reference retrieved authorities against active statutory databases using deterministic rule engines.", space_after=1)
    add_numbered(doc, "Step 5—Supervised Output:", "Render drafts with verbatim source citations and confidence metrics for mandatory attorney review.", space_after=0)
    
    doc.add_page_break()
    
    # ======================== PAGE 7: 8. CORE TECHNIQUES & 9. EVALUATION METRICS ========================
    add_heading(doc, "8. CORE TECHNIQUES AND ARCHITECTURES", space_before=0, space_after=1)
    add_bullet(doc, "Transformer Legal Language Models:", "Domain-adapted architectures like Legal-BERT pre-train on specialized legal corpora, capturing statutory grammar accurately. Longformer models employ sliding-window attention to process lengthy contracts without context truncation.", space_after=1)
    add_bullet(doc, "Dense Vector Retrieval & Semantic Search:", "Dense vector retrieval maps legal queries and precedents into continuous embedding spaces, capturing contextual meaning across synonyms and phrasing variations beyond rigid boolean matching.", space_after=1)
    add_bullet(doc, "Retrieval-Augmented Generation (RAG):", "RAG decouples model weights from dynamic legal knowledge. Injecting retrieved factual context grounds LLMs directly in authoritative statutory texts, minimizing speculative hallucinations.", space_after=1)
    add_bullet(doc, "Neuro-Symbolic Validation Engines:", "Integrates statistical language models with deterministic knowledge graphs and statutory rule engines to enforce judicial validity before delivering responses.", space_after=2)
    
    add_heading(doc, "9. EVALUATION METRICS AND BENCHMARKING", space_before=2, space_after=1)
    add_bullet(doc, "Information Retrieval Metrics:", "Precision, Recall@K, and Mean Reciprocal Rank (MRR) evaluate whether relevant statutory authorities appear in top retrieval ranks, preventing omission of critical precedents.", space_after=1)
    add_bullet(doc, "RAG Triad Faithfulness:", "Evaluates Context Relevance (passages match legal query), Groundedness (claims derive strictly from context), and Answer Faithfulness (absence of fabricated citations).", space_after=1)
    add_bullet(doc, "Doctrinal Reasoning Evaluation:", "LegalBench's 162-task cognitive taxonomy evaluates multi-tier reasoning, including issue-spotting, rule application, statutory interpretation, and counterfactual analysis.", space_after=1)
    add_bullet(doc, "Operational Efficiency Indicators:", "Quantifies turnaround time reductions (from hours to minutes), review costs, and practitioner concordance rates against human baselines established by Martin et al.", space_after=0)
    
    doc.add_page_break()
    
    # ======================== PAGE 8: 10. APPLICATIONS & 11. CHALLENGES & ETHICAL CONSIDERATIONS ========================
    add_heading(doc, "10. APPLICATIONS", space_before=0, space_after=1)
    add_bullet(doc, "Contract Due Diligence:", "AI automatically extracts standardized covenants (indemnity, non-compete, liability caps) across hundreds of commercial agreements during corporate mergers, compressing weeks of manual reading into minutes.", space_after=1)
    add_bullet(doc, "Litigation E-Discovery:", "Semantic search models rapidly filter millions of internal communications, identifying relevant evidentiary records and relevant precedents with high contextual accuracy.", space_after=1)
    add_bullet(doc, "Indian Judicial Modernization:", "The Supreme Court of India has deployed SUPACE to process case facts for judges, while SUVAS utilizes neural translation to translate judgments into regional Indian languages, advancing access to justice under the e-Courts Project.", space_after=1)
    add_bullet(doc, "Citizen Legal Literacy:", "AI-driven informational interfaces empower small businesses and citizens to comprehend complex legal contracts and navigate procedural filing requirements before incurring heavy legal fees.", space_after=2)
    
    add_heading(doc, "11. CHALLENGES AND ETHICAL CONSIDERATIONS", space_before=2, space_after=1)
    add_bullet(doc, "Hallucination Risks & Judicial Ethics:", "LLMs can generate fabricated case citations with high confidence. Submitting unverified AI citations has led to formal judicial sanctions under court ethics rules (e.g., Mata v. Avianca), highlighting the necessity of mandatory verification.", space_after=1)
    add_bullet(doc, "Client Confidentiality & Privilege:", "Transmitting sensitive client contracts to public commercial LLM APIs risks breaching attorney-client privilege. Enterprise architectures must utilize on-premises deployments or zero-retention encryption pipelines.", space_after=1)
    add_bullet(doc, "Algorithmic Bias & Fairness:", "AI models trained on historical case law risk perpetuating historical societal disparities if deployed in predictive justice or bail recommendation systems without continuous bias auditing.", space_after=1)
    add_bullet(doc, "Unauthorized Practice of Law (UPL):", "AI tools must function strictly as informational decision-support systems for licensed attorneys, accompanied by clear disclaimers that they do not constitute formal legal counsel.", space_after=0)
    
    doc.add_page_break()
    
    # ======================== PAGE 9: 12. FUTURE SCOPE, 13. EXPECTED OUTCOMES, 14. CONCLUSION, REFERENCES ========================
    add_heading(doc, "12. FUTURE SCOPE", space_before=0, space_after=1)
    add_body(doc, "Future research directions in legal AI include: (1) Neuro-symbolic integration combining deep language models with formal statutory knowledge graphs and automated citation validation pipelines. (2) Autonomous agentic workflows capable of multi-turn legal research and procedural docket tracking. (3) Expansion to multilingual legal corpora, particularly supporting India's transition to new criminal codes (BNS, BNSS, and BSA).", space_after=1)
    
    add_heading(doc, "13. EXPECTED OUTCOMES", space_before=2, space_after=1)
    add_body(doc, "This seminar establishes how domain-adapted transformers and RAG architectures enhance legal workflow speed and cost-efficiency. It equips researchers to benchmark commercial tools objectively and implement human-in-the-loop safeguards that uphold professional integrity and legal ethics.", space_after=1)
    
    add_heading(doc, "14. CONCLUSION", space_before=2, space_after=1)
    add_body(doc, "Artificial Intelligence is modernizing legal practice by transforming labor-intensive tasks into streamlined, technology-assisted operations. When integrated with semantic search and RAG architectures, AI achieves order-of-magnitude reductions in contract review duration and case law discovery costs. However, empirical literature conclusively proves that AI cannot substitute for human moral reasoning, ethical accountability, and courtroom advocacy. By combining automated retrieval with mandatory attorney oversight, the legal profession can achieve unprecedented efficiency while safeguarding the integrity of justice.", space_after=1)
    
    add_heading(doc, "REFERENCES", space_before=2, space_after=1)
    
    def add_ref_entry(doc, ref_num, text):
        p = doc.add_paragraph()
        set_para_format(p, line_spacing=1.0, space_before=1, space_after=1, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.first_line_indent = Inches(-0.2)
        r_num = p.add_run(f"[{ref_num}] ")
        set_run_font(r_num, name='Bookman Old Style', size=7.5, bold=True)
        r_txt = p.add_run(text)
        set_run_font(r_txt, name='Bookman Old Style', size=7.0, bold=False)
        return p
        
    add_ref_entry(doc, 1, 'N. Guha et al., "LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models," in Proc. NeurIPS 2023 Datasets Track, Dec. 2023. DOI: 10.48550/arXiv.2308.11462.')
    add_ref_entry(doc, 2, 'V. Magesh et al., "Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools," Journal of Empirical Legal Studies, Wiley, 2025. DOI: 10.1111/jels.12413.')
    add_ref_entry(doc, 3, 'D. Hendrycks et al., "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review," in Proc. NeurIPS 2021 Datasets Track, Dec. 2021. DOI: 10.48550/arXiv.2103.06268.')
    add_ref_entry(doc, 4, 'L. Martin et al., "Better Call GPT, Comparing Large Language Models Against Lawyers," arXiv preprint arXiv:2401.16212, Jan. 2024. DOI: 10.48550/arXiv.2401.16212.')
    add_ref_entry(doc, 5, 'I. Chalkidis et al., "LexGLUE: A Benchmark Dataset for Legal Language Understanding in English," in Proc. ACL 2022, pp. 4310–4330. DOI: 10.18653/v1/2022.acl-long.297.')
    add_ref_entry(doc, 6, 'P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in Advances in NeurIPS 2020, vol. 33, pp. 9459–9474.')
    add_ref_entry(doc, 7, 'Supreme Court of India, "AI in the Indian Judiciary: Overview of SUPACE and SUVAS Initiatives," Official Reports of SCI AI Committee, 2021–2023. Available: https://main.sci.gov.in/')
    
    doc.add_page_break()
    
    # ======================== PAGE 10: APPROVAL & SIGN-OFF (CERTIFICATE PAGE) ========================
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
    set_para_format(p_cand, line_spacing=1.5, space_before=6, space_after=48, align=WD_ALIGN_PARAGRAPH.LEFT)
    p_cand.paragraph_format.left_indent = Inches(0.5)
    r_cand = p_cand.add_run("1. Rohan Bongane")
    set_run_font(r_cand, name='Bookman Old Style', size=12, bold=True)
    
    cert_sig_table = doc.add_table(rows=1, cols=2)
    cert_sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_g = cert_sig_table.cell(0, 0)
    c_h = cert_sig_table.cell(0, 1)
    c_g.width = Inches(3.13)
    c_h.width = Inches(3.13)
    
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
    print(f"Building strictly calibrated 10-page document: {out_docx}...")
    doc = build_perfect_10page_synopsis()
    doc.save(out_docx)
    print("DOCX successfully generated.")
