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

def set_para_format(p, line_spacing=1.5, space_before=2, space_after=4, align=WD_ALIGN_PARAGRAPH.JUSTIFY, keep_with_next=False):
    p.alignment = align
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = keep_with_next

def add_heading(doc, text, space_before=6, space_after=2, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.15, space_before=space_before, space_after=space_after, align=align, keep_with_next=True)
    run = p.add_run(text)
    set_run_font(run, name='Bookman Old Style', size=12, bold=True)
    return p

def add_subheading(doc, text, space_before=4, space_after=2, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.15, space_before=space_before, space_after=space_after, align=align, keep_with_next=True)
    run = p.add_run(text)
    set_run_font(run, name='Bookman Old Style', size=12, bold=True)
    return p

def add_body(doc, text, space_before=0, space_after=4, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.5, space_before=space_before, space_after=space_after, align=align)
    run = p.add_run(text)
    set_run_font(run, name='Bookman Old Style', size=12, bold=False)
    return p

def add_bullet(doc, bold_prefix, text, space_before=0, space_after=3):
    p = doc.add_paragraph()
    set_para_format(p, line_spacing=1.5, space_before=space_before, space_after=space_after, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    p.paragraph_format.left_indent = Inches(0.2)
    r1 = p.add_run(bold_prefix + " ")
    set_run_font(r1, name='Bookman Old Style', size=12, bold=True)
    r2 = p.add_run(text)
    set_run_font(r2, name='Bookman Old Style', size=12, bold=False)
    return p

def add_numbered(doc, num_str, text, space_before=0, space_after=3):
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

def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
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

def build_8page_synopsis():
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
    r_ftr2_title = p_ftr2.add_run("Enhancing Legal Efficiency Through Artificial Intelligence\t")
    set_run_font(r_ftr2_title, name='Bookman Old Style', size=10, bold=False, color_rgb=RGBColor(80, 80, 80))
    r_ftr2_page = p_ftr2.add_run()
    set_run_font(r_ftr2_page, name='Bookman Old Style', size=10, bold=True, color_rgb=RGBColor(80, 80, 80))
    add_page_number_field(r_ftr2_page)
    
    # ---------------- PAGE 1: COVER PAGE ----------------
    p_top_sp = doc.add_paragraph()
    set_para_format(p_top_sp, line_spacing=1.0, space_before=0, space_after=8, align=WD_ALIGN_PARAGRAPH.CENTER)
    
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
    set_para_format(p_sub, line_spacing=1.15, space_before=14, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_sub = p_sub.add_run("Submitted to")
    set_run_font(r_sub, name='Bookman Old Style', size=12, bold=False)
    
    # University Name
    p_uni = doc.add_paragraph()
    set_para_format(p_uni, line_spacing=1.15, space_before=2, space_after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_uni = p_uni.add_run("Chhatrapati Shivaji Maharaj University,\nPanvel, Navi Mumbai")
    set_run_font(r_uni, name='Bookman Old Style', size=14, bold=True)
    
    # Logo
    if os.path.exists("csmu_logo.png"):
        p_logo = doc.add_paragraph()
        set_para_format(p_logo, line_spacing=1.0, space_before=4, space_after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
        p_logo.add_run().add_picture("csmu_logo.png", width=Inches(1.55))
    
    # Degree info
    p_deg_req = doc.add_paragraph()
    set_para_format(p_deg_req, line_spacing=1.15, space_before=6, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_deg_req = p_deg_req.add_run("for the partial fulfillment of requirement for the Degree of")
    set_run_font(r_deg_req, name='Bookman Old Style', size=11, bold=False)
    
    p_deg = doc.add_paragraph()
    set_para_format(p_deg, line_spacing=1.15, space_before=2, space_after=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_deg = p_deg.add_run("Master of Computer Application")
    set_run_font(r_deg, name='Bookman Old Style', size=13, bold=True)
    
    # Submitted By
    p_by_lbl = doc.add_paragraph()
    set_para_format(p_by_lbl, line_spacing=1.15, space_before=4, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_by_lbl = p_by_lbl.add_run("Submitted By")
    set_run_font(r_by_lbl, name='Bookman Old Style', size=12, bold=False)
    
    p_by_name = doc.add_paragraph()
    set_para_format(p_by_name, line_spacing=1.15, space_before=2, space_after=16, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_by_name = p_by_name.add_run("Rohan Bongane")
    set_run_font(r_by_name, name='Bookman Old Style', size=13, bold=True)
    
    # Guide & Head of Dept Label
    p_gh_lbl = doc.add_paragraph()
    set_para_format(p_gh_lbl, line_spacing=1.15, space_before=4, space_after=10, align=WD_ALIGN_PARAGRAPH.CENTER)
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
    set_para_format(p_yr, line_spacing=1.15, space_before=16, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_yr = p_yr.add_run("2026-27")
    set_run_font(r_yr, name='Bookman Old Style', size=12, bold=True)
    
    doc.add_page_break()
    
    # ---------------- PAGE 2: SYNOPSIS, ABSTRACT, 1. INTRODUCTION, 2. PROBLEM STATEMENT ----------------
    p_syn = doc.add_paragraph()
    set_para_format(p_syn, line_spacing=1.15, space_before=0, space_after=6, align=WD_ALIGN_PARAGRAPH.CENTER, keep_with_next=True)
    r_syn = p_syn.add_run("SYNOPSIS")
    set_run_font(r_syn, name='Bookman Old Style', size=12, bold=True)
    
    add_heading(doc, "ABSTRACT", space_before=2, space_after=2)
    add_body(doc, "The legal sector relies heavily on processing voluminous textual records, including statutes, judicial precedents, commercial contracts, and litigation dockets. Managing this information overload manually creates substantial administrative overhead and severe case backlogs. This seminar examines how Artificial Intelligence (AI) enhances operational efficiency within legal workflows. Using Natural Language Processing (NLP) and Large Language Models (LLMs), AI automates routine document analysis, clause extraction, and semantic precedent retrieval. We examine five foundational empirical studies: LegalBench for legal reasoning benchmarks, Magesh et al. for hallucination audits in commercial Retrieval-Augmented Generation (RAG) tools, CUAD for contract due diligence, Better Call GPT for human-AI efficiency differentials, and LexGLUE for multi-task legal understanding. Specialized Indian initiatives, including SUVAS and SUPACE under the e-Courts Project, are reviewed alongside critical challenges surrounding hallucination risks, client data confidentiality, algorithmic bias, and ethical accountability. This literature-based technical study synthesizes state-of-the-art methods into a defensible operational framework.", space_after=4)
    
    add_heading(doc, "1. INTRODUCTION", space_before=6, space_after=2)
    add_body(doc, "The legal profession is inherently knowledge-intensive, requiring practitioners and judicial officers to analyze intricate statutory frameworks, examine extensive case law, and draft precise transactional instruments. Traditionally, legal information retrieval and contract due diligence have depended upon manual reading, physical filing, and boolean keyword searching. These conventional workflows impose significant cognitive fatigue, long turnaround times, and severe institutional backlogs that hinder access to justice. In India alone, over forty million cases remain pending across subordinate courts, high courts, and the Supreme Court, underscoring the critical need for scalable operational efficiency.", space_after=3)
    add_body(doc, "Artificial Intelligence serves as a vital catalyst in resolving these procedural bottlenecks. By leveraging Natural Language Processing (NLP), domain-adapted transformer architectures, and Large Language Models (LLMs), AI systems can comprehend specialized legal vocabulary, extract high-stakes contractual liabilities, and identify relevant precedents based on semantic meaning rather than exact word matching. When properly grounded in verified legal authorities through Retrieval-Augmented Generation (RAG), AI empowers practitioners to transition from repetitive manual sorting to analytical reasoning, case strategy, and client advocacy.", space_after=4)
    
    add_heading(doc, "2. PROBLEM STATEMENT", space_before=6, space_after=2)
    add_body(doc, "Legal documents are characterized by extreme structural complexity, archaic jargon, and jurisdiction-specific statutory references. Traditional computational search methods suffer from keyword brittleness, failing to retrieve authoritative precedents when varied phrasing or synonyms are used. While modern generative AI tools offer rapid document drafting and summarization, their ungrounded deployment creates acute legal and ethical hazards—most notably legal hallucinations, where models invent fictitious judicial citations or misinterpret statutory holdings. Commercial platforms marketed as 'hallucination-free' lack standardized, public auditing, exposing practitioners to professional sanctions. The central problem is how to design, evaluate, and govern AI-assisted workflows that maximize legal operational efficiency while ensuring rigorous doctrinal accuracy, client data confidentiality, and verifiable compliance.", space_after=0)
    
    doc.add_page_break()
    
    # ---------------- PAGE 3: 3. AIM, 4. OBJECTIVES, 5. SCOPE, 6. LITERATURE REVIEW (INTRO) ----------------
    add_heading(doc, "3. AIM", space_before=0, space_after=2)
    add_body(doc, "To study the principles, model architectures, operational workflows, empirical benchmarks, and ethical limitations of Artificial Intelligence in legal workflows, and to understand how these methods support automated analysis of legal documents while maintaining doctrinal accuracy.", space_after=4)
    
    add_heading(doc, "4. OBJECTIVES", space_before=6, space_after=2)
    add_numbered(doc, "1.", "Explain the relationship between AI, deep learning, NLP, and legal information workflows.", space_after=2)
    add_numbered(doc, "2.", "Describe domain-adapted legal transformers (Legal-BERT, Longformer) for long document analysis.", space_after=2)
    add_numbered(doc, "3.", "Differentiate legal classification, contract extraction, semantic search, and generation tasks.", space_after=2)
    add_numbered(doc, "4.", "Examine empirical benchmarks (LegalBench, CUAD, LexGLUE) measuring legal reasoning and accuracy.", space_after=2)
    add_numbered(doc, "5.", "Evaluate human-AI productivity differentials (Better Call GPT) in contract review speed and cost.", space_after=2)
    add_numbered(doc, "6.", "Audit commercial legal RAG tools (Magesh et al.) regarding hallucination rates and citation validity.", space_after=2)
    add_numbered(doc, "7.", "Discuss practical applications, Indian judicial initiatives (SUPACE, SUVAS), and ethical safeguards.", space_after=4)
    
    add_heading(doc, "5. SCOPE OF THE SEMINAR", space_before=6, space_after=2)
    add_body(doc, "The seminar covers major AI-assisted legal tasks across the document lifecycle: text ingestion, semantic chunking, vector indexing, retrieval-augmented generation, and human-in-the-loop verification. It evaluates domain-adapted transformers and generative models across transactional contract review and litigation research. It explores common-law benchmarks and Indian judicial digitization initiatives (SUPACE, SUVAS, e-Courts Project). As a literature-based academic seminar, the scope focuses on rigorous synthesis and comparative analysis of peer-reviewed benchmarks without assuming an unverified custom software implementation.", space_after=4)
    
    add_heading(doc, "6. LITERATURE REVIEW", space_before=6, space_after=2)
    add_body(doc, "To rigorously examine legal efficiency, this seminar reviews five genuine, highly cited, peer-reviewed academic publications across top AI conferences (NeurIPS, ACL), prominent empirical legal journals (Journal of Empirical Legal Studies), and quantitative benchmark archives. Guha et al. (2023) introduce LegalBench, a collaborative benchmark evaluating 162 legal reasoning tasks across foundation models. Magesh et al. (2025) provide the first preregistered empirical audit of commercial legal RAG tools (Lexis+ AI, Westlaw AI), measuring real-world hallucination rates. Hendrycks et al. (2021) present CUAD, an expert-annotated corpus of 13,000+ labels across 510 contracts for due diligence automation. Martin et al. (2024) compare LLMs against lawyers in Better Call GPT, quantifying operational speed and cost reductions. Chalkidis et al. (2022) present LexGLUE, demonstrating that domain pre-training is essential for legal language comprehension.", space_after=0)
    
    doc.add_page_break()
    
    # ---------------- PAGE 4: 6. LITERATURE REVIEW (CONTD.) - COMPARATIVE TABLE & SYNTHESIS ----------------
    add_heading(doc, "6. LITERATURE REVIEW (Contd.)", space_before=0, space_after=2)
    add_body(doc, "The following comparative matrix synthesizes the methodology, findings, and stated research gaps across the five reviewed studies:", space_after=3)
    
    # Concise Comparative Table (5 rows, 5 columns)
    comp_table = doc.add_table(rows=6, cols=5)
    comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(comp_table, color="A0A0A0", sz="4", val="single")
    
    col_widths = [Inches(1.2), Inches(1.1), Inches(1.4), Inches(1.4), Inches(1.4)]
    headers = ["Study & Authors", "Venue & Year", "Method & Tech", "Key Findings", "Primary Research Gap"]
    hdr_row = comp_table.rows[0]
    for idx, heading in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.width = col_widths[idx]
        set_cell_margins(cell, top=40, bottom=40, left=60, right=60)
        set_cell_background(cell, "F0F4F8")
        p = cell.paragraphs[0]
        set_para_format(p, line_spacing=1.0, space_before=1, space_after=1, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(heading)
        set_run_font(r, name='Bookman Old Style', size=9, bold=True)
        
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
            set_cell_margins(cell, top=30, bottom=30, left=60, right=60)
            if r_idx % 2 == 1:
                set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]
            align = WD_ALIGN_PARAGRAPH.CENTER if c_idx < 2 else WD_ALIGN_PARAGRAPH.LEFT
            set_para_format(p, line_spacing=1.0, space_before=1, space_after=1, align=align)
            r = p.add_run(val)
            set_run_font(r, name='Bookman Old Style', size=8, bold=(c_idx == 0))
            
    add_subheading(doc, "Common Thematic Agreements Across Studies", space_before=6, space_after=2)
    add_body(doc, "The literature exhibits strong consensus on three principles: (1) Automated Triage Drives Massive Efficiency: AI achieves substantial speedups in routine clause extraction, metadata categorization, and initial contract issue-spotting (Hendrycks et al., Martin et al.). (2) Domain Adaptation is Essential: Generic AI models underperform when applied naively; domain-specific pre-training on legal corpora (Chalkidis et al.) or tailored legal prompt scaffolding (Guha et al.) is necessary for doctrinal accuracy. (3) The Human-in-the-Loop Imperative: No study supports autonomous legal practice; AI must operate strictly as an assistive tool under qualified legal oversight.", space_after=3)
    
    add_subheading(doc, "Crucial Disagreements and Conflicts in Literature", space_before=4, space_after=2)
    add_body(doc, "The literature highlights two key tensions: (1) Vendor Claims vs. Empirical Reality: Commercial vendors market legal RAG tools as 'hallucination-free,' yet independent empirical auditing by Magesh et al. proves hallucination rates between 17% and 33%, demonstrating a significant gap between marketing and reality. (2) Task-Level Accuracy vs. Real-World Utility: Benchmarks like LegalBench report notable AI failure rates on complex statutory logic puzzles, whereas empirical trials like Better Call GPT find that LLMs match junior attorneys on routine corporate contract reviews, showing that standardized benchmarks often underestimate practical transactional utility.", space_after=0)
    
    doc.add_page_break()
    
    # ---------------- PAGE 5: DEFENSIBLE RESEARCH GAP, 7. METHODOLOGY, 8. CORE TECHNIQUES ----------------
    add_heading(doc, "The Overall Defensible Research Gap in Legal AI", space_before=0, space_after=2)
    add_body(doc, "Synthesizing the empirical findings reveals a critical research gap at the intersection of retrieval speed and legal accuracy:", space_after=2)
    add_bullet(doc, "• What Prior Research Has Addressed:", "Prior literature proves that deep learning models can automate high-volume legal extraction (CUAD), classify complex rulings across multi-task benchmarks (LexGLUE), and perform fast first-pass contract issue spotting at over 90% cost savings (Better Call GPT). Furthermore, benchmarks have mapped the cognitive boundaries of raw LLMs (LegalBench) and quantified hallucination rates in commercial vector-based RAG platforms (Magesh et al.).", space_after=2)
    add_bullet(doc, "• What Remains Insufficiently Studied (The Research Gap):", "While existing studies prove that AI accelerates discrete sub-tasks, there is a fundamental absence of verified, neuro-symbolic verification frameworks that integrate probabilistic vector retrieval with deterministic legal validation. Current legal RAG systems rely exclusively on semantic vector similarity, which frequently retrieves overruled or inapplicable precedents. The literature lacks hybrid architectures combining vector embeddings with active citation validation graphs (e.g., automated Shepard's/KeyCite checking). Moreover, multi-turn conversational interaction latency and the cognitive load of verifying AI drafts remain unquantified. Crucially, landmark research remains overwhelmingly US/UK centric, leaving emerging multilingual legal systems—such as India's transition to BNS, BNSS, and BSA—critically unaddressed.", space_after=3)
    
    add_heading(doc, "7. PROPOSED METHODOLOGY", space_before=6, space_after=2)
    add_body(doc, "To resolve the identified research gaps, this seminar outlines a literature-grounded, multi-layered architectural methodology designed to achieve reliable legal efficiency while systematically preventing hallucination risks. The framework couples dense semantic retrieval with deterministic verification layers across five sequential steps:", space_after=2)
    add_numbered(doc, "Step 1—Define Task & Ingest Data:", "Ingest legal texts (contracts, case laws) using structure-aware OCR and semantic parsers that preserve clause hierarchies.", space_after=2)
    add_numbered(doc, "Step 2—Chunk & Index:", "Partition texts into coherent legal clauses (1,000-word windows with 150-word overlap) and embed using domain-adapted dense models.", space_after=2)
    add_numbered(doc, "Step 3—Retrieve with RAG:", "Execute hybrid dense-sparse retrieval with strict jurisdictional metadata filtering.", space_after=2)
    add_numbered(doc, "Step 4—Verify & Guardrail:", "Cross-reference retrieved precedents against active statutory databases using deterministic rule checkers.", space_after=2)
    add_numbered(doc, "Step 5—Supervise & Audit:", "Render AI-generated drafts with direct source attribution and confidence indicators for mandatory attorney review.", space_after=3)
    
    add_heading(doc, "8. CORE TECHNIQUES AND ARCHITECTURES", space_before=6, space_after=2)
    add_body(doc, "Key techniques include: (1) Domain Transformers: Legal-BERT captures statutory syntax, while Longformer processes 100-page dockets via sliding-window attention. (2) Dense Semantic Search: Continuous vector embeddings retrieve precedents based on legal meaning rather than exact keywords. (3) Retrieval-Augmented Generation (RAG): Grounds generative models by injecting retrieved statutory passages into prompts. (4) Neuro-Symbolic Validation: Combines statistical fluency with deterministic statutory rule engines to eliminate citation hallucinations.", space_after=0)
    
    doc.add_page_break()
    
    # ---------------- PAGE 6: 9. EVALUATION METRICS, 10. APPLICATIONS, 11. CHALLENGES & ETHICS ----------------
    add_heading(doc, "9. EVALUATION METRICS AND BENCHMARKING", space_before=0, space_after=2)
    add_body(doc, "Rigorous evaluation of legal AI systems requires a balanced combination of technical information retrieval metrics, generation faithfulness metrics, and operational efficiency indicators:", space_after=2)
    add_bullet(doc, "Information Retrieval Metrics:", "Precision, Recall@K, and Mean Reciprocal Rank (MRR) evaluate whether relevant statutory provisions and precedents appear in top retrieval positions. High recall is essential to avoid omitting vital legal authorities.", space_after=2)
    add_bullet(doc, "RAG Triad Faithfulness:", "Measures Context Relevance (retrieved passages pertain directly to query), Groundedness (all response claims derive strictly from context), and Answer Faithfulness (absence of fabricated citations).", space_after=2)
    add_bullet(doc, "Doctrinal Reasoning Evaluation:", "LegalBench's 162-task cognitive taxonomy evaluates multi-tiered reasoning, including issue-spotting, rule application, statutory interpretation, and counterfactual analysis.", space_after=2)
    add_bullet(doc, "Operational Efficiency Indicators:", "Measures turnaround time reductions (from hours to seconds), cost-per-review metrics, and practitioner agreement rates against human baselines established by Martin et al.", space_after=3)
    
    add_heading(doc, "10. APPLICATIONS", space_before=6, space_after=2)
    add_bullet(doc, "Contract Due Diligence:", "AI automatically extracts standardized covenants (indemnity, non-compete, liability caps) across hundreds of commercial agreements during corporate mergers, compressing weeks of manual reading into minutes.", space_after=2)
    add_bullet(doc, "Litigation E-Discovery:", "Semantic search models rapidly filter millions of internal communications, identifying relevant evidentiary records and relevant precedents with high contextual accuracy.", space_after=2)
    add_bullet(doc, "Indian Judicial Modernization:", "The Supreme Court of India has deployed SUPACE to process case facts for judges, while SUVAS utilizes neural translation to translate judgments into regional Indian languages, advancing access to justice under the e-Courts Project.", space_after=2)
    add_bullet(doc, "Citizen Legal Literacy:", "AI-driven informational interfaces empower small businesses and citizens to comprehend complex legal contracts and navigate procedural filing requirements before incurring heavy legal fees.", space_after=3)
    
    add_heading(doc, "11. CHALLENGES AND ETHICAL CONSIDERATIONS", space_before=6, space_after=2)
    add_body(doc, "Deploying AI in legal workflows introduces profound technical, ethical, and regulatory challenges:", space_after=2)
    add_bullet(doc, "Hallucination Risks & Judicial Ethics:", "LLMs can generate fabricated case citations with high confidence. Submitting unverified AI citations has led to formal judicial sanctions under court ethics rules (e.g., Mata v. Avianca), highlighting the necessity of mandatory verification.", space_after=2)
    add_bullet(doc, "Client Confidentiality & Privilege:", "Transmitting sensitive client contracts to public commercial LLM APIs risks breaching attorney-client privilege. Enterprise architectures must utilize on-premises deployments or zero-retention encryption pipelines.", space_after=2)
    add_bullet(doc, "Algorithmic Bias & Fairness:", "AI models trained on historical case law risk perpetuating historical societal disparities if deployed in predictive justice or bail recommendation systems without continuous bias auditing.", space_after=2)
    add_bullet(doc, "Unauthorized Practice of Law (UPL):", "AI tools must function strictly as informational decision-support systems for licensed attorneys, accompanied by clear disclaimers that they do not constitute formal legal counsel.", space_after=0)
    
    doc.add_page_break()
    
    # ---------------- PAGE 7: 12. FUTURE SCOPE, 13. EXPECTED OUTCOMES, 14. CONCLUSION, REFERENCES ----------------
    add_heading(doc, "12. FUTURE SCOPE", space_before=0, space_after=2)
    add_body(doc, "Future research directions in legal AI include: (1) Neuro-symbolic integration combining deep language models with formal statutory knowledge graphs and automated Shepard's/KeyCite validation pipelines. (2) Autonomous agentic workflows capable of multi-turn legal research, interactive document drafting, and procedural docket tracking. (3) Expansion to multilingual legal corpora in emerging jurisdictions, particularly supporting India's transition to the new criminal law codes (Bharatiya Nyaya Sanhita, Bharatiya Nagarik Suraksha Sanhita, and Bharatiya Sakshya Adhiniyam).", space_after=3)
    
    add_heading(doc, "13. EXPECTED OUTCOMES", space_before=5, space_after=2)
    add_body(doc, "This seminar provides a comprehensive conceptual and technical foundation in legal AI. Students and practitioners will understand how domain-adapted transformers and RAG architectures enhance operational efficiency, how to evaluate commercial tool reliability using empirical benchmarks, and how to implement responsible, human-in-the-loop safeguards that uphold professional integrity and legal ethics.", space_after=3)
    
    add_heading(doc, "14. CONCLUSION", space_before=5, space_after=2)
    add_body(doc, "Artificial Intelligence is fundamentally modernizing the legal profession, transforming traditional, labor-intensive workflows into streamlined, technology-assisted operations. When integrated with semantic search, domain-adapted language models, and Retrieval-Augmented Generation, AI delivers order-of-magnitude reductions in contract review duration, speeds up case law discovery, and significantly lowers operational costs. However, empirical literature conclusively demonstrates that AI cannot replace the indispensable human faculties of moral reasoning, contextual empathy, ethical accountability, and courtroom advocacy. Furthermore, the persistent reality of citation hallucinations and client privacy risks requires that AI be deployed strictly as an assistive cognitive amplifier supervised by qualified practitioners. By pairing high-speed machine retrieval with rigorous human oversight and deterministic verification safeguards, the legal profession can achieve unprecedented efficiency while safeguarding the fundamental integrity of justice.", space_after=4)
    
    add_heading(doc, "REFERENCES", space_before=5, space_after=2)
    
    def add_ref_entry(doc, ref_num, text):
        p = doc.add_paragraph()
        set_para_format(p, line_spacing=1.1, space_before=1, space_after=2, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        r_num = p.add_run(f"[{ref_num}] ")
        set_run_font(r_num, name='Bookman Old Style', size=9.5, bold=True)
        r_txt = p.add_run(text)
        set_run_font(r_txt, name='Bookman Old Style', size=9, bold=False)
        return p
        
    add_ref_entry(doc, 1, 'N. Guha, J. Nyarko, D. E. Ho, C. Ré, A. Chilton, K. Tobia, J. R. Nay, et al., "LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models," in Proc. NeurIPS 2023 Track on Datasets and Benchmarks, New Orleans, USA, Dec. 2023. DOI: 10.48550/arXiv.2308.11462.')
    add_ref_entry(doc, 2, 'V. Magesh, F. Surani, M. Dahl, M. Suzgun, C. D. Manning, and D. E. Ho, "Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools," Journal of Empirical Legal Studies, Wiley, 2025. Preprint: arXiv:2405.20362. DOI: 10.1111/jels.12413.')
    add_ref_entry(doc, 3, 'D. Hendrycks, C. Burns, A. Chen, and S. Ball, "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review," in Proc. NeurIPS 2021 Track on Datasets and Benchmarks, Dec. 2021. DOI: 10.48550/arXiv.2103.06268.')
    add_ref_entry(doc, 4, 'L. Martin, N. Whitehouse, S. Yiu, L. Catterson, and R. Perera, "Better Call GPT, Comparing Large Language Models Against Lawyers," arXiv preprint arXiv:2401.16212, Jan. 2024. DOI: 10.48550/arXiv.2401.16212.')
    add_ref_entry(doc, 5, 'I. Chalkidis, A. Jana, D. Hartung, M. Bommarito, I. Androutsopoulos, D. M. Katz, and N. Aletras, "LexGLUE: A Benchmark Dataset for Legal Language Understanding in English," in Proc. 60th Annual Meeting of the ACL (ACL 2022), Dublin, Ireland, May 2022, pp. 4310–4330. DOI: 10.18653/v1/2022.acl-long.297.')
    add_ref_entry(doc, 6, 'P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in Advances in Neural Information Processing Systems (NeurIPS 2020), vol. 33, 2020, pp. 9459–9474.')
    add_ref_entry(doc, 7, 'Supreme Court of India, "AI in the Indian Judiciary: An Overview of SUPACE and SUVAS Initiatives," Official Reports of the Supreme Court of India Artificial Intelligence Committee, New Delhi, India, 2021–2023. Available: https://main.sci.gov.in/')
    
    doc.add_page_break()
    
    # ---------------- PAGE 8: APPROVAL & SIGN-OFF (CERTIFICATE PAGE) ----------------
    p_sep1 = doc.add_paragraph()
    set_para_format(p_sep1, line_spacing=1.0, space_before=14, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
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
    set_para_format(p_cand, line_spacing=1.5, space_before=6, space_after=40, align=WD_ALIGN_PARAGRAPH.LEFT)
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
    print(f"Building 8-page document: {out_docx}...")
    doc = build_8page_synopsis()
    doc.save(out_docx)
    print("DOCX successfully generated.")
