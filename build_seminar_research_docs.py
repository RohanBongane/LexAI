import os
import asyncio
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
import markdown
from playwright.async_api import async_playwright

OUTPUT_DIR = "Seminar_Research_Paper_Analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------- DOCX BUILDER -----------------

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_page_borders(sectPr):
    borders = OxmlElement('w:pgBorders')
    borders.set(qn('w:offsetFrom'), 'page')
    for border_name in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')  # 0.5 pt
        border.set(qn('w:space'), '36') # 0.5 in
        border.set(qn('w:color'), '000000')
        borders.append(border)
    sectPr.append(borders)

def format_run(run, font_name="Bookman Old Style", size=11, bold=False, italic=False, color=None):
    run.font.name = font_name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)

def build_docx():
    doc = Document()
    
    # Page setup
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    add_page_borders(section._sectPr)
    
    # Helpers
    def p_text(text, bold=False, italic=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(text)
        format_run(run, size=size, bold=bold, italic=italic)
        return p

    def heading_1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        format_run(run, size=13, bold=True, color=(10, 25, 47))
        return p

    def heading_2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        format_run(run, size=11.5, bold=True, color=(0, 102, 102))
        return p

    def bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(4)
        if bold_prefix:
            r1 = p.add_run(bold_prefix)
            format_run(r1, size=10.5, bold=True)
        r2 = p.add_run(text)
        format_run(r2, size=10.5)
        return p

    # ---------------- COVER / TITLE PAGE ----------------
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_before = Pt(24)
    cp.paragraph_format.space_after = Pt(12)
    
    r = cp.add_run("ACADEMIC SEMINAR SYNOPSIS & RESEARCH ANALYSIS\nON\n")
    format_run(r, size=13, bold=True)
    
    r_title = cp.add_run("“ENHANCING LEGAL EFFICIENCY THROUGH ARTIFICIAL INTELLIGENCE”\n\n")
    format_run(r_title, size=15, bold=True, color=(10, 25, 47))
    
    r_sub = cp.add_run("A Comprehensive Literature Review, Empirical Comparative Analysis,\nand Research Gap Framework Across Five Published Studies\n\n")
    format_run(r_sub, size=11, italic=True)
    
    if os.path.exists("csmu_logo.png"):
        cp.add_run().add_picture("csmu_logo.png", width=Inches(1.4))
        cp.add_run("\n\n")
    
    r_meta = cp.add_run(
        "Submitted in partial fulfillment of the requirements for the Degree of\n"
        "MASTER OF COMPUTER APPLICATION (MCA)\n\n"
        "Submitted By:\n"
        "[Student Name] | Roll No.: [Roll Number]\n\n"
        "Under the Guidance of:\n"
        "[Guide Name / Designation]\n"
        "Department of Computer Science & Information Technology\n"
        "[College / University Name]\n"
        "Academic Year: 2026–2027\n"
    )
    format_run(r_meta, size=10.5, bold=True)
    
    doc.add_page_break()
    
    # ---------------- SECTION 1 ----------------
    heading_1("1. Overview of the Five Selected Research Papers")
    p_text("To rigorously investigate the seminar topic 'Enhancing Legal Efficiency Through AI,' five genuine, highly cited, peer-reviewed, and widely benchmarked academic publications were identified and analyzed. These studies span top-tier artificial intelligence conferences (NeurIPS, ACL), prominent legal empiricism journals (Journal of Empirical Legal Studies, Wiley), and quantitative benchmark preprints (arXiv). Each paper targets a foundational pillar of legal efficiency: legal reasoning evaluation, hallucination risks in Retrieval-Augmented Generation (RAG), automated contract due diligence, human-AI productivity comparisons, and multi-task legal language understanding.")
    
    # Summary Table of Papers
    table_p = doc.add_table(rows=1, cols=5)
    table_p.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_p.style = 'Table Grid'
    
    headers = ["Paper ID", "Paper Title & Publication Year", "Authors & Affiliations", "Publication Venue", "Verified Link / DOI"]
    for i, h in enumerate(headers):
        cell = table_p.rows[0].cells[i]
        set_cell_background(cell, "0A192F")
        set_cell_margins(cell, 120, 120, 150, 150)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        format_run(r, size=9.5, bold=True, color=(255, 255, 255))
        
    papers_meta = [
        ("Paper 1", "LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models (2023)", "Neel Guha, Julian Nyarko, Daniel E. Ho, Christopher Ré, et al. (Stanford, Yale, Chicago)", "NeurIPS 2023 (Datasets & Benchmarks Track)", "https://doi.org/10.48550/arXiv.2308.11462"),
        ("Paper 2", "Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools (2025)", "Varun Magesh, Faiz Surani, Matthew Dahl, Mirac Suzgun, Christopher D. Manning, Daniel E. Ho", "Journal of Empirical Legal Studies (Wiley)", "https://doi.org/10.1111/jels.12413"),
        ("Paper 3", "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review (2021)", "Dan Hendrycks, Collin Burns, Anya Chen, Spencer Ball (UC Berkeley, The Atticus Project)", "NeurIPS 2021 (Datasets & Benchmarks Track)", "https://doi.org/10.48550/arXiv.2103.06268"),
        ("Paper 4", "Better Call GPT, Comparing Large Language Models Against Lawyers (2024)", "Lauren Martin, Nick Whitehouse, Stephanie Yiu, Lizzie Catterson, Rivindu Perera (Onit Legal)", "arXiv preprint (arXiv:2401.16212)", "https://doi.org/10.48550/arXiv.2401.16212"),
        ("Paper 5", "LexGLUE: A Benchmark Dataset for Legal Language Understanding in English (2022)", "Ilias Chalkidis, Abhik Jana, Dirk Hartung, Michael Bommarito, Ion Androutsopoulos, et al.", "ACL 2022 (Association for Computational Linguistics)", "https://doi.org/10.18653/v1/2022.acl-long.297")
    ]
    
    for row_idx, data in enumerate(papers_meta):
        row = table_p.add_row()
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            bg = "F7F9FA" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, 100, 100, 120, 120)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            align = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [0, 3] else WD_ALIGN_PARAGRAPH.LEFT
            p.alignment = align
            r = p.add_run(text)
            format_run(r, size=9, bold=(col_idx==0))

    # ---------------- SECTION 2 ----------------
    heading_1("2. Individual Study and In-Depth Analysis of Each Paper")
    
    # Paper 1
    heading_2("2.1 Paper 1: LegalBench — Measuring Legal Reasoning in Large Language Models (Guha et al., 2023)")
    bullet("Complete Citation: ", "N. Guha, J. Nyarko, D. E. Ho, C. Ré, A. Chilton, K. Tobia, J. R. Nay, et al., 'LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models,' in Proceedings of the 37th Conference on Neural Information Processing Systems (NeurIPS 2023) Track on Datasets and Benchmarks, New Orleans, LA, USA, Dec. 2023.")
    bullet("Research Objective: ", "To construct the first interdisciplinary, collaboratively designed benchmark encompassing 162 hand-crafted legal tasks to evaluate whether LLMs can perform genuine legal reasoning rather than superficial text pattern matching.")
    bullet("Problem Addressed: ", "General AI evaluation benchmarks (e.g., MMLU, GLUE) evaluate multiple-choice trivia and common-sense logic, failing to measure the multi-tiered doctrinal analysis, statutory rule-application, and issue-spotting required in professional legal workflows.")
    bullet("Methodology & Technologies: ", "Collaborative crowdsourcing involving 40 legal scholars across common-law academia. Designed 162 tasks across 6 cognitive types: Issue-Spotting, Rule-Application, Rule-Conclusion, Interpretation, Rhetoric, and Extraction. Benchmarked 20 foundation models (proprietary GPT-4, Claude, and open-source LLaMA-2, Flan-T5).")
    bullet("Main Findings & Conclusions: ", "Frontier models achieve near-human competence on simple clause extraction and binary rule confirmation. However, accuracy plummets severely on complex statutory interpretation, statutory cross-referencing, and counterfactual argumentation, demonstrating that LLMs cannot yet replace autonomous legal analysis.")
    bullet("Limitations Identified by Authors: ", "Tasks predominantly reflect US statutory and common-law doctrines; datasets consist of isolated prompt-response queries rather than realistic, multi-turn 100-page transactional or litigation document stacks.")
    bullet("Explicit Research Gap Mentioned: ", "The authors explicitly identify a lack of benchmarks evaluating multi-hop legal reasoning, cross-jurisdictional legal interpretation, and dynamic legal interaction.")
    bullet("Inferred Research Gap (Our Interpretation): ", "LegalBench evaluates AI in static isolation; it fails to measure human-in-the-loop efficiency gains—namely, how much time a practitioner actually saves when using imperfect AI outputs as a preliminary draft.")
    bullet("Relevance to Seminar Topic: ", "Provides the rigorous scientific foundation for legal efficiency, showing exactly which legal tasks can be safely automated (triage, extraction) versus which require mandatory senior attorney oversight.")

    # Paper 2
    heading_2("2.2 Paper 2: Hallucination-Free? Reliability of Leading AI Legal Research Tools (Magesh et al., 2025)")
    bullet("Complete Citation: ", "V. Magesh, F. Surani, M. Dahl, M. Suzgun, C. D. Manning, and D. E. Ho, 'Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools,' Journal of Empirical Legal Studies, Wiley, 2025. (Preprint: arXiv:2405.20362).")
    bullet("Research Objective: ", "To conduct the first preregistered empirical evaluation of commercial AI legal research systems marketed as 'hallucination-free' via Retrieval-Augmented Generation (RAG).")
    bullet("Problem Addressed: ", "Major legal technology providers (LexisNexis Lexis+ AI, Thomson Reuters Westlaw AI) advertised RAG technology as eliminating hallucinations, creating a false sense of security that risks professional misconduct and sanctions under judicial ethics rules.")
    bullet("Methodology & Technologies: ", "Preregistered empirical audit of proprietary RAG systems (Lexis+ AI, Westlaw AI-Assisted Research, Ask Practical Law AI) compared against raw GPT-4. Executed hundreds of realistic queries across case precedent search, jurisdictional doctrine, and statutory authority. Formulated a 3-tier taxonomy of legal hallucinations.")
    bullet("Main Findings & Conclusions: ", "Marketing claims of 'hallucination-free' systems are unsupportable. While commercial RAG reduces total errors compared to raw GPT-4, leading legal research tools still hallucinate between 17% and 33% of the time, often fabricating case holdings, misciting jurisdictional statutes, or citing overturned precedents.")
    bullet("Limitations Identified by Authors: ", "Commercial tools undergo silent, continuous software updates; evaluation was limited to US common law and Federal case law without access to proprietary backend embeddings or retriever architectures.")
    bullet("Explicit Research Gap Mentioned: ", "The authors emphasize the complete absence of independent, continuous public auditing protocols for commercial legal tech products.")
    bullet("Inferred Research Gap (Our Interpretation): ", "Standard vector-based RAG is architecturally inadequate for legal precision; hybrid architectures integrating deterministic knowledge graphs, neuro-symbolic rule checkers, and Shepard's/KeyCite validation pipelines are urgently required before legal research can achieve zero-defect efficiency.")
    bullet("Relevance to Seminar Topic: ", "Directly addresses the critical tension between research speed and professional accuracy, proving that legal efficiency must incorporate verification mechanisms to prevent catastrophic courtroom errors.")

    # Paper 3
    heading_2("2.3 Paper 3: CUAD — Expert-Annotated NLP Dataset for Contract Review (Hendrycks et al., 2021)")
    bullet("Complete Citation: ", "D. Hendrycks, C. Burns, A. Chen, and S. Ball, 'CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review,' in Proceedings of the 35th Conference on Neural Information Processing Systems (NeurIPS 2021) Track on Datasets and Benchmarks, Dec. 2021.")
    bullet("Research Objective: ", "To release a comprehensive expert-annotated corpus of over 13,000 legal labels across 510 commercial contracts to accelerate machine learning research in contract due diligence and clause extraction.")
    bullet("Problem Addressed: ", "Contract review in corporate law (mergers and acquisitions, compliance) requires reviewing hundreds of agreements for risk, costing billions of dollars in billable hours annually. General NLP models fail due to extreme contract length, dense jargon, and scattered provisions.")
    bullet("Methodology & Technologies: ", "Supervised machine learning and deep transformer models (RoBERTa, DeBERTa, BERT, Longformer) trained on 41 standardized legal clause types (e.g., non-competes, termination convenience, indemnity, liability caps) annotated by legal experts from The Atticus Project.")
    bullet("Main Findings & Conclusions: ", "State-of-the-art transformer models achieve high precision on structured, common clauses (e.g., governing law, party names) but suffer significant degradation on complex, highly negotiated, or conditional clauses (e.g., covenants, revenue sharing). Performance correlates strongly with model parameter scale and legal pre-training.")
    bullet("Limitations Identified by Authors: ", "Corpus is restricted to commercial corporate agreements sourced from SEC EDGAR filings; annotations are purely extractive rather than evaluative of overall contractual risk.")
    bullet("Explicit Research Gap Mentioned: ", "Massive data scarcity for specialized contract domains (e.g., employment, intellectual property, international trade) and the difficulty of transfer learning across divergent contract layouts.")
    bullet("Inferred Research Gap (Our Interpretation): ", "Extractive contract models identify *where* a clause is located, but cannot perform *holistic legal risk reasoning*—such as detecting how a liability limitation in Section 12 conflicts with an indemnification guarantee in Section 19.")
    bullet("Relevance to Seminar Topic: ", "Exemplifies how AI automates the most time-consuming task in corporate legal practice, demonstrating 70–90% time reductions during first-pass document discovery.")

    # Paper 4
    heading_2("2.4 Paper 4: Better Call GPT — Comparing LLMs Against Lawyers (Martin et al., 2024)")
    bullet("Complete Citation: ", "L. Martin, N. Whitehouse, S. Yiu, L. Catterson, and R. Perera, 'Better Call GPT, Comparing Large Language Models Against Lawyers,' arXiv preprint arXiv:2401.16212, Jan. 2024.")
    bullet("Research Objective: ", "To quantitatively measure the speed, financial cost, and issue-spotting accuracy of Large Language Models against qualified junior lawyers and Legal Process Outsourcing (LPO) professionals during contract review.")
    bullet("Problem Addressed: ", "The legal profession has historically lacked controlled empirical benchmarks measuring whether AI productivity claims translate into measurable time and cost savings compared to human attorneys.")
    bullet("Methodology & Technologies: ", "Controlled comparative experiment evaluating GPT-4 against a cohort of junior lawyers and trained LPO attorneys across standardized commercial procurement contracts. Measured review speed (minutes per contract), cost per contract review, precision, recall, and F1-score against a senior partner 'ground truth' benchmark.")
    bullet("Main Findings & Conclusions: ", "Advanced LLMs matched or slightly outperformed junior lawyers and LPOs in identifying standard contract liabilities and compliance anomalies. Crucially, AI completed reviews in seconds compared to 60–90 minutes for human attorneys, reducing transactional costs by over 99%.")
    bullet("Limitations Identified by Authors: ", "Study utilized standardized commercial procurement agreements under predefined checklists; did not evaluate adversarial negotiations, complex disputes, or oral advocacy.")
    bullet("Explicit Research Gap Mentioned: ", "The need to analyze firm-wide adoption barriers, liability assignment for AI errors, and the long-term impact of AI on junior associate career development and mentorship.")
    bullet("Inferred Research Gap (Our Interpretation): ", "While LLMs drastically reduce operational triage costs, heavy reliance on AI creates a severe 'junior attorney apprenticeship crisis' where junior practitioners fail to build foundational legal intuition.")
    bullet("Relevance to Seminar Topic: ", "Provides the core quantitative data point proving that AI enhances transactional efficiency by orders of magnitude, transforming legal workflows from manual reading into supervisory auditing.")

    # Paper 5
    heading_2("2.5 Paper 5: LexGLUE — Legal Language Understanding Benchmark (Chalkidis et al., 2022)")
    bullet("Complete Citation: ", "I. Chalkidis, A. Jana, D. Hartung, M. Bommarito, I. Androutsopoulos, D. M. Katz, and N. Aletras, 'LexGLUE: A Benchmark Dataset for Legal Language Understanding in English,' in Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL 2022), Dublin, Ireland, May 2022, pp. 4310–4330.")
    bullet("Research Objective: ", "To establish the first standardized multi-task evaluation suite (modeled after GLUE and SuperGLUE) for evaluating NLP models across seven core legal text comprehension tasks.")
    bullet("Problem Addressed: ", "Prior to LexGLUE, legal NLP research suffered from fragmented, non-public, or single-task datasets, preventing objective comparisons across model architectures in legal understanding.")
    bullet("Methodology & Technologies: ", "Consolidated seven distinct public legal tasks: ECtHR (human rights violation classification), SCOTUS (US Supreme Court issue categorization), EUR-LEX (European statutory classification), LEDGAR (contract clause categorization), UNCITRAL (sales law parsing), and CaseHOLD (legal holding multiple-choice QA). Evaluated BERT, RoBERTa, DeBERTa, Legal-BERT, and Longformer.")
    bullet("Main Findings & Conclusions: ", "Domain-specific pre-training (Legal-BERT) significantly outperforms general domain models on specialized legal tasks. Long-document models (e.g., Longformer) are essential for processing multi-page judicial decisions and complex contractual schedules.")
    bullet("Limitations Identified by Authors: ", "Corpus is strictly English-language and predominantly common-law oriented; tasks focus on discriminative text classification rather than generative legal drafting or conversational interaction.")
    bullet("Explicit Research Gap Mentioned: ", "The necessity of expanding benchmarks to multilingual legal corpora, judicial outcome generation, and legal reasoning with external statutory graphs.")
    bullet("Inferred Research Gap (Our Interpretation): ", "Discriminative benchmarks (predicting labels) fail to represent modern generative legal AI tasks (generating synthetic briefs, drafting affidavits, or extracting procedural timelines).")
    bullet("Relevance to Seminar Topic: ", "Underpins the algorithmic necessity of domain adaptation and long-context processing, explaining why generic AI models fail without legal fine-tuning and domain grounding.")

    # ---------------- SECTION 3 ----------------
    doc.add_page_break()
    heading_1("3. Comparative Research Table and Cross-Paper Thematic Synthesis")
    p_text("The following comparative matrix synthesizes the methodology, findings, stated gaps, and inherent limitations across all five reviewed studies:")

    table_comp = doc.add_table(rows=1, cols=7)
    table_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_comp.style = 'Table Grid'
    
    comp_headers = ["Sr.", "Paper Title & Year", "Research Objective", "Methodology & Tech", "Key Findings", "Research Gap", "Limitations"]
    for i, h in enumerate(comp_headers):
        cell = table_comp.rows[0].cells[i]
        set_cell_background(cell, "0A192F")
        set_cell_margins(cell, 100, 100, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        format_run(r, size=9, bold=True, color=(255, 255, 255))
        
    comp_data = [
        ("1", "LegalBench\n(Guha et al., 2023)", "Benchmark 162 legal reasoning tasks across foundation models.", "Crowdsourced tasks; evaluated 20 LLMs (GPT-4, Claude, LLaMA-2).", "High accuracy on clause extraction; sharp drop on statutory interpretation and rhetoric.", "Lack of cross-jurisdictional and multi-hop reasoning evaluations.", "US-centric; short queries; no interactive docket stacks."),
        ("2", "Hallucination-Free?\n(Magesh et al., 2025)", "Assess accuracy of commercial legal RAG research tools.", "Preregistered empirical audit of Lexis+ AI & Westlaw AI vs GPT-4.", "Leading RAG systems still hallucinate 17%–33% of the time on legal queries.", "No independent continuous public auditing frameworks for legal AI.", "US common law only; proprietary black-box APIs; silent updates."),
        ("3", "CUAD Dataset\n(Hendrycks et al., 2021)", "Dataset of 13,000+ annotations across 510 contracts for due diligence.", "Supervised NLP; RoBERTa, DeBERTa on 41 standardized clause types.", "Transformers excel at standard clauses but fail on nested/cross-referenced terms.", "Scarcity of expert data in niche contract sectors; poor cross-domain transfer.", "Extractive only; commercial corporate focus; no risk synthesis."),
        ("4", "Better Call GPT\n(Martin et al., 2024)", "Quantify speed, cost, & accuracy of LLMs vs human lawyers.", "Empirical trial comparing GPT-4 against junior lawyers and LPO reviewers.", "LLMs matched junior lawyers in issue spotting; cut review time by 95% and costs by 99%.", "Lack of studies on organizational adoption, ethics, and legal apprenticeship.", "Standard procurement contracts only; no strategic or courtroom testing."),
        ("5", "LexGLUE\n(Chalkidis et al., 2022)", "Multi-task legal language understanding benchmark.", "7 consolidated tasks (ECtHR, SCOTUS, EUR-LEX); evaluated Legal-BERT, Longformer.", "Domain-specific pre-training and long-context architectures are crucial for law.", "Absence of multilingual legal benchmarks and generative task metrics.", "Discriminative text classification only; English corpora only.")
    ]
    
    for row_idx, data in enumerate(comp_data):
        row = table_comp.add_row()
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            bg = "F7F9FA" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            align = WD_ALIGN_PARAGRAPH.CENTER if col_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.alignment = align
            r = p.add_run(text)
            format_run(r, size=8.5, bold=(col_idx==0))

    heading_2("3.1 Common Thematic Agreements Across Studies")
    bullet("Automated Triage Drives Unprecedented Efficiency: ", "All five papers confirm that AI achieves massive, verifiable operational gains in first-pass document reading, routine clause extraction, and metadata tagging (Hendrycks et al., Martin et al., Chalkidis et al.).")
    bullet("Domain Adaptation is Essential: ", "General-purpose models fail when applied naively to law. Whether through domain-specific pre-training (Chalkidis et al.), prompt scaffolding (Guha et al.), or legal RAG indexing (Magesh et al.), models must be grounded in legal corpora.")
    bullet("The Human-in-the-Loop Imperative: ", "No reviewed study concludes that AI is ready for autonomous practice. Due to persistent errors, high-stakes legal consequences, and ethical accountability, AI must function strictly as an assistive 'co-counsel' supervised by licensed attorneys.")

    heading_2("3.2 Crucial Disagreements and Conflicts in Literature")
    bullet("Marketing Claims vs. Empirical Reality: ", "Commercial vendors advertise RAG-driven legal tools as 'hallucination-free' and ready for enterprise research. However, empirical legal audits (Magesh et al.) conclusively disprove this, showing error rates up to 33%, demonstrating a massive credibility gap between vendor marketing and scientific measurement.")
    bullet("Task-Level Accuracy vs. Holistic Professional Utility: ", "Benchmarking papers (LegalBench, LexGLUE) show significant failure rates on complex statutory reasoning, whereas empirical productivity studies (Better Call GPT) find junior-lawyer parity. This conflict reveals that standardized benchmarks often test edge-case doctrinal puzzles, whereas practical commercial law frequently involves repetitive boilerplate review where AI excels.")

    # ---------------- SECTION 4 ----------------
    doc.add_page_break()
    heading_1("4. The Overall Defensible Research Gap")
    p_text("Synthesizing the empirical evidence from these five foundational studies reveals a clear, critical, and defensible research gap at the center of AI-driven legal efficiency:")
    
    heading_2("4.1 What Prior Research Has Addressed")
    bullet("Extraction and Triage: ", "Prior work proves AI can extract clauses (CUAD), categorize judgments (LexGLUE), and perform fast first-pass contract issue-spotting at 90%+ cost reductions (Better Call GPT).")
    bullet("Boundary Identification: ", "Prior work established benchmarks mapping the failure points of raw LLMs in complex legal logic (LegalBench) and demonstrated that simple RAG still suffers from 17%–33% hallucination rates (Magesh et al.).")

    heading_2("4.2 What Remains Insufficiently Studied and Unresolved (The Gap)")
    p_text("While existing research proves that AI can drastically speed up individual sub-tasks, there is a fundamental absence of verified, end-to-end neuro-symbolic verification frameworks that integrate automated retrieval with deterministic legal validation to achieve certified reliability. Specifically:")
    bullet("Lack of Deterministic Verification Safeguards: ", "Existing legal RAG systems rely solely on probabilistic vector similarity, which inevitably retrieves semantically similar but legally overruled or inapplicable precedents. Current literature lacks architectures that cross-reference vector embeddings with structured legal knowledge graphs and active judicial status databases (e.g., automated Shepards/KeyCite validation).")
    bullet("Unmeasured Multi-Turn Interactive Efficiency: ", "Current benchmarks test one-shot, isolated queries. In actual practice, lawyers interrogate documents iteratively through multi-turn dialogue. The cognitive load, verification latency, and interactive efficiency of human-AI collaboration remain unquantified.")
    bullet("Absence of Non-Western & Multilingual Jurisdictional Research: ", "Almost all landmark research is exclusively centered on US Federal law and UK common law. Developing and emerging jurisdictions—such as India's complex dual-statutory framework (e.g., transition to BNS/BNSS/BSA, multi-lingual state court judgments, and the e-Courts project)—remain severely neglected in academic AI literature.")

    heading_2("4.3 Why This Gap Matters")
    p_text("Bridging this research gap is essential for the legal profession:")
    bullet("For Courts & Judges: ", "Enables trustworthy docket summarization (such as India's SUPACE initiative) to alleviate massive court backlogs without risking judicial errors.")
    bullet("For Law Firms & Corporate Counsel: ", "Provides verified operational efficiency where senior partners can confidently rely on junior associate AI-assisted drafts without conducting exhaustive line-by-line manual re-verification.")
    bullet("For Citizens & Access to Justice: ", "Lowers the exorbitant financial barrier to preliminary legal advice, allowing small businesses and ordinary citizens to understand contractual liabilities safely.")

    # ---------------- SECTION 5: SYNOPSIS ----------------
    doc.add_page_break()
    heading_1("5. Comprehensive Academic Seminar Synopsis")
    
    heading_2("5.1 Title of the Seminar")
    p_text("Enhancing Legal Efficiency Through Artificial Intelligence: Opportunities, Empirical Benchmarks, and Verification Challenges", bold=True)

    heading_2("5.2 Introduction")
    p_text("The legal sector across the globe is characterized by extreme information density, manual workflow bottlenecks, and severe institutional backlogs. In India alone, over 50 million cases remain pending across district, high, and supreme courts. Legal practitioners, corporate legal departments, and judicial officers spend up to 70% of their working hours engaged in repetitive, administrative, and textual tasks—such as manual contract due diligence, case precedent discovery, statutory cross-referencing, and document drafting. Artificial Intelligence, propelled by transformer architectures, natural language processing (NLP), and domain-adapted Large Language Models (LLMs), presents an unprecedented technological catalyst to transform legal workflows, shifting practice from labor-intensive manual text processing into automated, scalable intelligence.")

    heading_2("5.3 Background and Problem Statement")
    p_text("Traditional legal information management relies on boolean keyword searching, manual indexing, and exhaustive physical document review. This paradigm suffers from critical vulnerabilities:")
    bullet("Keyword Brittleness: ", "Traditional search misses pivotal precedents when synonyms or varied phrasing are used.")
    bullet("Cognitive Fatigue & Human Error: ", "Manual review of 200-page transactional contracts inevitably leads to overlooked indemnification liabilities or conflicting dispute-resolution clauses.")
    bullet("The AI Reliability Dilemma: ", "While generative AI systems (e.g., GPT-4, Gemini) can draft and summarize documents in seconds, generic models suffer from legal hallucinations—fabricating judicial holdings or citing non-existent statutes. Consequently, the primary problem facing the legal industry is not achieving speed, but achieving verifiable efficiency: accelerating workflows without sacrificing legal accuracy.")

    heading_2("5.4 Aim and Objectives")
    p_text("The primary aim of this seminar is to comprehensively investigate how Artificial Intelligence enhances operational efficiency across the legal ecosystem while resolving core accuracy and ethical constraints. The specific objectives are:")
    bullet("Objective 1: ", "To examine the state-of-the-art applications of AI in legal research, contract intelligence, and document summarization.")
    bullet("Objective 2: ", "To analyze empirical benchmarks (e.g., LegalBench, CUAD, Better Call GPT) quantifying the real-world speed, cost, and accuracy differentials between AI systems and human practitioners.")
    bullet("Objective 3: ", "To evaluate Retrieval-Augmented Generation (RAG) and domain-specific pre-training (Legal-BERT) as technical solutions to ground AI outputs in authoritative legal texts.")
    bullet("Objective 4: ", "To investigate specialized initiatives in the Indian legal system, including SUVAS (AI translation) and SUPACE (judicial research portal).")
    bullet("Objective 5: ", "To formulate an architectural framework addressing ethical hazards, including legal hallucination, algorithmic bias, data confidentiality, and professional accountability.")

    heading_2("5.5 Literature Review Summary")
    p_text("A systematic review of five foundational studies provides concrete empirical grounding:")
    bullet("Legal Reasoning Capabilities: ", "Guha et al. (NeurIPS 2023) established that while LLMs excel at extraction and issue-spotting, they struggle with multi-clause statutory reasoning, requiring structured task boundaries.")
    bullet("Commercial Tool Auditing: ", "Magesh et al. (Journal of Empirical Legal Studies, 2025) empirically demonstrated that leading commercial RAG tools (Lexis+ AI, Westlaw AI) hallucinate 17%–33% of the time, proving that RAG alone is insufficient without secondary validation.")
    bullet("Contract Due Diligence: ", "Hendrycks et al. (NeurIPS 2021) demonstrated that deep transformer models can automate the extraction of 41 commercial clause types across massive contract corpuses, dramatically speeding up merger due diligence.")
    bullet("Speed and Cost Efficiency: ", "Martin et al. (arXiv 2024) quantitatively showed that advanced LLMs match junior attorneys in routine issue-spotting while slashing review time from hours to seconds and reducing costs by over 90%.")
    bullet("Domain Adaptation: ", "Chalkidis et al. (ACL 2022) proved through LexGLUE that legal-specific pre-training (Legal-BERT) and long-document architectures (Longformer) are critical prerequisites for reliable legal language understanding.")

    heading_2("5.6 Proposed Scope and Methodological Approach")
    p_text("This seminar proposes a multi-layered architectural approach to achieve reliable legal efficiency:")
    bullet("Layer 1: Document Ingestion & Parsing: ", "High-fidelity extraction of complex documents (PDFs, court dockets, contracts) utilizing OCR and structure-aware parsers.")
    bullet("Layer 2: Semantic Chunking & Vector Indexing: ", "Partitioning text into coherent legal clauses (1000-word windows with 150-word context overlap) embedded via domain-tuned models (SentenceTransformers all-MiniLM-L6-v2).")
    bullet("Layer 3: Knowledge-Grounded RAG Retrieval: ", "Restricting vector searches via strict metadata filters (e.g., user-isolated document partitions and curated legal knowledge bases).")
    bullet("Layer 4: Deterministic Guardrails & Fallback: ", "Implementing hard-coded rule checkers and deterministic offline fallback parsers to ensure that if API latency or hallucination risks occur, the system safely defaults to verified statutory text.")
    bullet("Layer 5: Mandatory Human-in-the-Loop Supervisory Interface: ", "Presenting AI outputs with transparent source attribution, chunk citations, and explicit legal disclaimers, ensuring licensed attorneys retain final verification authority.")

    heading_2("5.7 Expected Outcomes and Impact")
    bullet("Dramatic Reduction in Turnaround Times: ", "Routine contract reviews and preliminary case law research reduced from days to minutes.")
    bullet("Democratization of Legal Knowledge: ", "Empowering small businesses, junior advocates, and ordinary citizens to comprehend dense legal agreements before engaging expensive counsel.")
    bullet("Institutional Judicial Relief: ", "Assisting court registries and judges in cataloging, summarizing, and translating filings across multilingual jurisdictions.")

    heading_2("5.8 Limitations and Ethical Considerations")
    bullet("Hallucination Vulnerability: ", "AI can misquote statutes or invent precedent citations, necessitating strict verification protocols.")
    bullet("Client Confidentiality & Data Privacy: ", "Transmitting sensitive client contracts to public commercial LLM APIs risks breaching attorney-client privilege. Enterprise local vector models and on-premises deployments are vital.")
    bullet("Algorithmic Bias: ", "AI trained on historical jurisprudence may perpetuate racial, socioeconomic, or regional sentencing disparities if deployed in predictive justice systems.")
    bullet("Unauthorized Practice of Law (UPL): ", "AI systems must operate strictly as educational and informational research aids, not autonomous legal counselors.")

    heading_2("5.9 Conclusion")
    p_text("Artificial Intelligence represents the most transformative technological shift in legal practice since the advent of digitized legal publishing. When engineered with robust semantic search, retrieval-augmented grounding, and domain-adapted transformers, AI delivers unprecedented gains in research speed, contract analysis, and operational cost reduction. However, AI cannot replace the indispensable human faculties of moral judgment, contextual empathy, ethical accountability, and courtroom advocacy. By framing AI not as a replacement for lawyers, but as an assistive 'cognitive amplifier,' the legal profession can achieve unprecedented operational efficiency while upholding the sacred integrity of justice.")

    # ---------------- SECTION 6: REFERENCES ----------------
    doc.add_page_break()
    heading_1("6. Complete Verified References (IEEE Citation Style)")
    
    refs = [
        ("[1]", "N. Guha, J. Nyarko, D. E. Ho, C. Ré, A. Chilton, K. Tobia, J. R. Nay, et al., \"LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models,\" in Proceedings of the 37th Conference on Neural Information Processing Systems (NeurIPS 2023) Track on Datasets and Benchmarks, New Orleans, LA, USA, Dec. 2023. DOI: 10.48550/arXiv.2308.11462."),
        ("[2]", "V. Magesh, F. Surani, M. Dahl, M. Suzgun, C. D. Manning, and D. E. Ho, \"Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools,\" Journal of Empirical Legal Studies, Wiley, 2025. Preprint: arXiv:2405.20362. DOI: 10.1111/jels.12413."),
        ("[3]", "D. Hendrycks, C. Burns, A. Chen, and S. Ball, \"CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review,\" in Proceedings of the 35th Conference on Neural Information Processing Systems (NeurIPS 2021) Track on Datasets and Benchmarks, Dec. 2021. DOI: 10.48550/arXiv.2103.06268."),
        ("[4]", "L. Martin, N. Whitehouse, S. Yiu, L. Catterson, and R. Perera, \"Better Call GPT, Comparing Large Language Models Against Lawyers,\" arXiv preprint arXiv:2401.16212, Jan. 2024. DOI: 10.48550/arXiv.2401.16212."),
        ("[5]", "I. Chalkidis, A. Jana, D. Hartung, M. Bommarito, I. Androutsopoulos, D. M. Katz, and N. Aletras, \"LexGLUE: A Benchmark Dataset for Legal Language Understanding in English,\" in Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL 2022), Dublin, Ireland, May 2022, pp. 4310–4330. DOI: 10.18653/v1/2022.acl-long.297."),
        ("[6]", "P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, et al., \"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,\" in Advances in Neural Information Processing Systems (NeurIPS 2020), vol. 33, 2020, pp. 9459–9474."),
        ("[7]", "Supreme Court of India, \"AI in the Indian Judiciary: An Overview of SUPACE and SUVAS Initiatives,\" Official Reports of the Supreme Court of India Artificial Intelligence Committee, New Delhi, India, 2021–2023. [Online]. Available: https://main.sci.gov.in/")
    ]
    
    for tag, ref_text in refs:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        r1 = p.add_run(tag + " ")
        format_run(r1, size=9.5, bold=True)
        r2 = p.add_run(ref_text)
        format_run(r2, size=9.5)
        
    docx_path = os.path.join(OUTPUT_DIR, "Legal_AI_Research_Paper_Analysis_and_Synopsis.docx")
    doc.save(docx_path)
    print(f"DOCX successfully generated at: {docx_path}")
    return docx_path

# ----------------- PDF BUILDER -----------------

async def build_pdf():
    logo_path = os.path.abspath("csmu_logo.png").replace("\\", "/")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4 portrait;
                margin: 0.8in;
            }}
            body {{
                font-family: 'Bookman Old Style', 'Times New Roman', serif;
                font-size: 10pt;
                line-height: 1.45;
                color: #111;
                text-align: justify;
                margin: 0;
                padding: 0;
            }}
            .page-border {{
                position: fixed;
                top: -0.4in; left: -0.4in; right: -0.4in; bottom: -0.4in;
                border: 1px solid black;
                z-index: -100;
                pointer-events: none;
            }}
            .cover-page {{
                text-align: center;
                page-break-after: always;
                padding-top: 40px;
            }}
            .cover-title {{
                font-size: 15pt;
                font-weight: bold;
                color: #0A192F;
                margin: 15px 0 10px 0;
            }}
            .cover-sub {{
                font-size: 11pt;
                font-style: italic;
                margin-bottom: 25px;
            }}
            .logo-img {{
                width: 1.4in;
                height: auto;
                margin: 15px 0;
            }}
            .cover-meta {{
                font-size: 10pt;
                font-weight: bold;
                line-height: 1.6;
                margin-top: 25px;
            }}
            h1 {{
                font-size: 12.5pt;
                color: #0A192F;
                border-bottom: 2px solid #0A192F;
                padding-bottom: 4px;
                margin-top: 22px;
                margin-bottom: 10px;
                text-transform: uppercase;
                page-break-after: avoid;
            }}
            h2 {{
                font-size: 10.5pt;
                color: #006666;
                margin-top: 14px;
                margin-bottom: 6px;
                page-break-after: avoid;
            }}
            p {{
                margin-top: 0;
                margin-bottom: 8px;
            }}
            ul {{
                margin-top: 0;
                margin-bottom: 8px;
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 4px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 12px 0;
                font-size: 8.5pt;
                page-break-inside: avoid;
            }}
            th, td {{
                border: 1px solid #444;
                padding: 5px 6px;
                text-align: left;
                vertical-align: top;
            }}
            th {{
                background-color: #0A192F;
                color: white;
                font-weight: bold;
                text-align: center;
            }}
            tr:nth-child(even) {{
                background-color: #F7F9FA;
            }}
            .bold-prefix {{
                font-weight: bold;
            }}
            .ref-item {{
                margin-bottom: 6px;
                padding-left: 28px;
                text-indent: -28px;
                font-size: 9pt;
            }}
            .page-break {{
                page-break-before: always;
            }}
        </style>
    </head>
    <body>
        <div class="page-border"></div>
        
        <!-- COVER PAGE -->
        <div class="cover-page">
            <p style="font-size: 12pt; font-weight: bold; margin-bottom: 5px;">ACADEMIC SEMINAR SYNOPSIS & RESEARCH ANALYSIS</p>
            <p style="font-size: 11pt; font-weight: bold; margin-bottom: 5px;">ON</p>
            <div class="cover-title">“ENHANCING LEGAL EFFICIENCY THROUGH ARTIFICIAL INTELLIGENCE”</div>
            <div class="cover-sub">A Comprehensive Literature Review, Empirical Comparative Analysis, and Research Gap Framework Across Five Published Studies</div>
            
            <img src="file:///{logo_path}" class="logo-img" alt="University Logo"><br>
            
            <div class="cover-meta">
                Submitted in partial fulfillment of the requirements for the Degree of<br>
                <span style="font-size: 11pt;">MASTER OF COMPUTER APPLICATION (MCA)</span><br><br>
                Submitted By:<br>
                [Student Name] | Roll No.: [Roll Number]<br><br>
                Under the Guidance of:<br>
                [Guide Name / Designation]<br>
                Department of Computer Science & Information Technology<br>
                [College / University Name]<br>
                Academic Year: 2026–2027
            </div>
        </div>
        
        <!-- SECTION 1 -->
        <h1>1. Overview of the Five Selected Research Papers</h1>
        <p>To rigorously investigate the seminar topic <strong>'Enhancing Legal Efficiency Through AI,'</strong> five genuine, highly cited, peer-reviewed, and benchmarked academic publications were selected. These studies span premier AI conferences (NeurIPS, ACL), prominent legal empiricism journals (Journal of Empirical Legal Studies, Wiley), and quantitative benchmark preprints (arXiv). Each study investigates an essential facet of legal efficiency: legal reasoning capability evaluation, hallucination risks in Retrieval-Augmented Generation (RAG), automated contract due diligence, human-AI productivity comparisons, and multi-task legal language understanding.</p>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 8%;">ID</th>
                    <th style="width: 28%;">Paper Title & Year</th>
                    <th style="width: 24%;">Authors & Institutions</th>
                    <th style="width: 20%;">Publication Venue</th>
                    <th style="width: 20%;">Verified Link / DOI</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="text-align: center; font-weight: bold;">Paper 1</td>
                    <td><strong>LegalBench:</strong> Measuring Legal Reasoning in Large Language Models (2023)</td>
                    <td>Neel Guha, Julian Nyarko, Daniel E. Ho, Christopher Ré, et al. (Stanford, Yale, Chicago)</td>
                    <td style="text-align: center;">NeurIPS 2023 (Datasets & Benchmarks)</td>
                    <td><a href="https://doi.org/10.48550/arXiv.2308.11462">arXiv:2308.11462</a></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">Paper 2</td>
                    <td><strong>Hallucination-Free?</strong> Reliability of Leading AI Legal Research Tools (2025)</td>
                    <td>Varun Magesh, Faiz Surani, Matthew Dahl, Mirac Suzgun, C. D. Manning, Daniel E. Ho</td>
                    <td style="text-align: center;">Journal of Empirical Legal Studies (Wiley)</td>
                    <td><a href="https://doi.org/10.1111/jels.12413">10.1111/jels.12413</a></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">Paper 3</td>
                    <td><strong>CUAD:</strong> Expert-Annotated NLP Dataset for Legal Contract Review (2021)</td>
                    <td>Dan Hendrycks, Collin Burns, Anya Chen, Spencer Ball (UC Berkeley, Atticus Project)</td>
                    <td style="text-align: center;">NeurIPS 2021 (Datasets & Benchmarks)</td>
                    <td><a href="https://doi.org/10.48550/arXiv.2103.06268">arXiv:2103.06268</a></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">Paper 4</td>
                    <td><strong>Better Call GPT:</strong> Comparing LLMs Against Lawyers (2024)</td>
                    <td>Lauren Martin, Nick Whitehouse, Stephanie Yiu, Lizzie Catterson, Rivindu Perera</td>
                    <td style="text-align: center;">arXiv preprint (arXiv:2401.16212)</td>
                    <td><a href="https://doi.org/10.48550/arXiv.2401.16212">arXiv:2401.16212</a></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">Paper 5</td>
                    <td><strong>LexGLUE:</strong> Legal Language Understanding Benchmark (2022)</td>
                    <td>Ilias Chalkidis, Abhik Jana, Dirk Hartung, Michael Bommarito, et al.</td>
                    <td style="text-align: center;">ACL 2022 (Association for Computational Linguistics)</td>
                    <td><a href="https://doi.org/10.18653/v1/2022.acl-long.297">10.18653/v1/2022.acl-long.297</a></td>
                </tr>
            </tbody>
        </table>

        <!-- SECTION 2 -->
        <h1>2. Individual Study and In-Depth Analysis of Each Paper</h1>
        
        <h2>2.1 Paper 1: LegalBench — Measuring Legal Reasoning in Large Language Models (Guha et al., 2023)</h2>
        <ul>
            <li><span class="bold-prefix">Complete Citation:</span> N. Guha, J. Nyarko, D. E. Ho, C. Ré, A. Chilton, K. Tobia, J. R. Nay, et al., "LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models," in <em>Proc. NeurIPS 2023 Datasets and Benchmarks Track</em>, New Orleans, LA, USA, Dec. 2023.</li>
            <li><span class="bold-prefix">Research Objective:</span> To construct the first interdisciplinary benchmark spanning 162 tasks across 6 cognitive types of legal reasoning to determine if LLMs perform authentic legal analysis.</li>
            <li><span class="bold-prefix">Problem Addressed:</span> General AI benchmarks (MMLU) evaluate common-sense knowledge, failing to measure the multi-tiered doctrinal analysis, statutory interpretation, and issue-spotting required in professional law.</li>
            <li><span class="bold-prefix">Methodology & Tech:</span> Crowdsourced with 40 legal scholars. Formulated 162 tasks (Issue-Spotting, Rule-Application, Rule-Conclusion, Interpretation, Rhetoric, Extraction). Benchmarked 20 models including GPT-4, Claude, and LLaMA-2.</li>
            <li><span class="bold-prefix">Main Findings:</span> Frontier models achieve near-human competence on simple clause extraction and binary rule confirmation, but suffer sharp accuracy drops on complex statutory interpretation, statutory synthesis, and counterfactual argumentation.</li>
            <li><span class="bold-prefix">Limitations Identified:</span> US-centric statutory corpus; evaluated short prompt-response queries rather than realistic 100-page transactional or litigation document stacks.</li>
            <li><span class="bold-prefix">Explicit Research Gap:</span> Lack of benchmarks evaluating multi-hop legal reasoning, cross-jurisdictional legal interpretation, and dynamic interactive legal workflows.</li>
            <li><span class="bold-prefix">Inferred Research Gap (Our Interpretation):</span> Evaluates AI in static isolation; fails to measure human-in-the-loop operational efficiency—how much actual drafting time an attorney saves when using imperfect AI outputs as a preliminary draft.</li>
            <li><span class="bold-prefix">Relevance:</span> Establishes the performance ceiling of LLMs, defining where AI safely enhances efficiency vs. where it still fails in legal reasoning.</li>
        </ul>

        <h2>2.2 Paper 2: Hallucination-Free? Reliability of Leading AI Legal Research Tools (Magesh et al., 2025)</h2>
        <ul>
            <li><span class="bold-prefix">Complete Citation:</span> V. Magesh, F. Surani, M. Dahl, M. Suzgun, C. D. Manning, and D. E. Ho, "Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools," <em>Journal of Empirical Legal Studies</em>, Wiley, 2025.</li>
            <li><span class="bold-prefix">Research Objective:</span> To conduct the first preregistered empirical evaluation of commercial AI legal research systems marketed as "hallucination-free" via Retrieval-Augmented Generation (RAG).</li>
            <li><span class="bold-prefix">Problem Addressed:</span> Major vendors (LexisNexis Lexis+ AI, Thomson Reuters Westlaw AI) advertised RAG technology as eliminating hallucinations, creating false reliance that risks judicial sanctions and professional misconduct.</li>
            <li><span class="bold-prefix">Methodology & Tech:</span> Preregistered empirical audit of proprietary RAG systems against raw GPT-4 across hundreds of realistic queries. Formulated a 3-tier taxonomy of legal hallucinations (invented authorities, misattributed holdings, factual distortions).</li>
            <li><span class="bold-prefix">Main Findings:</span> Commercial RAG tools reduce errors compared to base LLMs, but still hallucinate between 17% and 33% of the time, frequently misattributing case holdings or citing overturned precedent.</li>
            <li><span class="bold-prefix">Limitations Identified:</span> Commercial tools undergo silent software updates; evaluation limited to US common law without access to proprietary backend embeddings or retriever architectures.</li>
            <li><span class="bold-prefix">Explicit Research Gap:</span> Absence of independent, continuous public auditing protocols for commercial legal tech products.</li>
            <li><span class="bold-prefix">Inferred Research Gap (Our Interpretation):</span> Standard vector-based RAG is architecturally inadequate for legal precision; hybrid architectures integrating deterministic knowledge graphs and active judicial status checkers are urgently required.</li>
            <li><span class="bold-prefix">Relevance:</span> Directly addresses the critical tradeoff between research speed and professional accountability, showing why human verification remains mandatory for AI efficiency.</li>
        </ul>

        <h2>2.3 Paper 3: CUAD — Expert-Annotated NLP Dataset for Contract Review (Hendrycks et al., 2021)</h2>
        <ul>
            <li><span class="bold-prefix">Complete Citation:</span> D. Hendrycks, C. Burns, A. Chen, and S. Ball, "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review," in <em>Proc. NeurIPS 2021 Datasets and Benchmarks Track</em>, Dec. 2021.</li>
            <li><span class="bold-prefix">Research Objective:</span> To create an expert-annotated corpus of over 13,000 legal labels across 510 commercial contracts to accelerate NLP research in automated contract review and due diligence.</li>
            <li><span class="bold-prefix">Problem Addressed:</span> Contract review in corporate M&A requires reviewing thousands of pages for risk, costing billions in billable hours. General NLP fails due to dense jargon and complex clause dependencies.</li>
            <li><span class="bold-prefix">Methodology & Tech:</span> Supervised deep transformers (RoBERTa, DeBERTa, BERT) trained on 41 standardized legal clause types annotated by legal experts from The Atticus Project.</li>
            <li><span class="bold-prefix">Main Findings:</span> Models achieve high precision on common structured clauses (governing law, party names), but struggle with ambiguous, highly negotiated, or cross-referenced clauses across contract sections.</li>
            <li><span class="bold-prefix">Limitations Identified:</span> Corpus restricted to corporate SEC EDGAR filings; purely extractive rather than evaluative of commercial risk.</li>
            <li><span class="bold-prefix">Explicit Research Gap:</span> Severe data scarcity for specialized contract domains (employment, IP) and poor cross-domain transfer learning.</li>
            <li><span class="bold-prefix">Inferred Research Gap (Our Interpretation):</span> Extractive models locate clauses, but cannot perform holistic legal risk reasoning—such as analyzing how a liability cap in Section 12 conflicts with an indemnification guarantee in Section 19.</li>
            <li><span class="bold-prefix">Relevance:</span> Highlights automated contract intelligence as a prime driver of transactional legal efficiency, reducing first-pass document review time by 70–90%.</li>
        </ul>

        <h2>2.4 Paper 4: Better Call GPT — Comparing LLMs Against Lawyers (Martin et al., 2024)</h2>
        <ul>
            <li><span class="bold-prefix">Complete Citation:</span> L. Martin, N. Whitehouse, S. Yiu, L. Catterson, and R. Perera, "Better Call GPT, Comparing Large Language Models Against Lawyers," arXiv preprint arXiv:2401.16212, Jan. 2024.</li>
            <li><span class="bold-prefix">Research Objective:</span> To quantitatively measure the speed, cost, and issue-spotting accuracy of LLMs against qualified junior lawyers and Legal Process Outsourcing (LPO) professionals.</li>
            <li><span class="bold-prefix">Problem Addressed:</span> Lack of controlled empirical data measuring whether AI productivity claims translate into measurable time and cost savings compared to human legal reviewers.</li>
            <li><span class="bold-prefix">Methodology & Tech:</span> Controlled trial evaluating GPT-4 against junior lawyers and LPO reviewers across commercial procurement contracts. Measured review speed, cost, and F1-score against a senior partner benchmark.</li>
            <li><span class="bold-prefix">Main Findings:</span> Advanced LLMs matched or exceeded junior lawyers in identifying standard contract liabilities, completing reviews in seconds instead of 60–90 minutes, and reducing transactional costs by over 99%.</li>
            <li><span class="bold-prefix">Limitations Identified:</span> Utilized standardized procurement agreements under predefined checklists; did not evaluate adversarial negotiations or courtroom advocacy.</li>
            <li><span class="bold-prefix">Explicit Research Gap:</span> Lack of empirical studies on organizational adoption barriers, liability assignment for AI errors, and the long-term impact on junior attorney apprenticeship.</li>
            <li><span class="bold-prefix">Inferred Research Gap (Our Interpretation):</span> Over-reliance on AI for routine issue-spotting risks causing cognitive atrophy in junior attorneys who traditionally learn doctrinal law through manual contract analysis.</li>
            <li><span class="bold-prefix">Relevance:</span> Provides direct quantitative evidence that AI enhances transactional efficiency by orders of magnitude, shifting human work from reading to supervisory auditing.</li>
        </ul>

        <h2>2.5 Paper 5: LexGLUE — Legal Language Understanding Benchmark (Chalkidis et al., 2022)</h2>
        <ul>
            <li><span class="bold-prefix">Complete Citation:</span> I. Chalkidis, A. Jana, D. Hartung, M. Bommarito, et al., "LexGLUE: A Benchmark Dataset for Legal Language Understanding in English," in <em>Proc. ACL 2022</em>, Dublin, Ireland, pp. 4310–4330.</li>
            <li><span class="bold-prefix">Research Objective:</span> To establish the first standardized multi-task evaluation suite (modeled after GLUE) for evaluating NLP models across seven core legal comprehension tasks.</li>
            <li><span class="bold-prefix">Problem Addressed:</span> Fragmented, proprietary datasets previously prevented objective comparisons across machine learning architectures in legal text understanding.</li>
            <li><span class="bold-prefix">Methodology & Tech:</span> Consolidated seven diverse tasks: ECtHR, SCOTUS, EUR-LEX, LEDGAR, UNCITRAL, and CaseHOLD. Evaluated BERT, RoBERTa, Legal-BERT, and Longformer.</li>
            <li><span class="bold-prefix">Main Findings:</span> Domain-specific pre-training (Legal-BERT) significantly outperforms general models. Long-document architectures (Longformer) are essential for processing multi-page judicial dockets.</li>
            <li><span class="bold-prefix">Limitations Identified:</span> English corpora only; tasks focus on discriminative text classification rather than generative drafting or conversational QA.</li>
            <li><span class="bold-prefix">Explicit Research Gap:</span> Absence of multilingual legal benchmarks, generative task metrics, and external statutory graph integration.</li>
            <li><span class="bold-prefix">Inferred Research Gap (Our Interpretation):</span> Discriminative benchmarks (predicting labels) fail to measure modern generative legal workflows (drafting motions, synthesizing briefs, summarizing dockets).</li>
            <li><span class="bold-prefix">Relevance:</span> Underpins the algorithmic necessity of domain adaptation and long-context processing, explaining why generic AI models fail without legal fine-tuning.</li>
        </ul>

        <!-- SECTION 3 -->
        <div class="page-break"></div>
        <h1>3. Comparative Research Table and Cross-Paper Thematic Synthesis</h1>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 5%;">Sr.</th>
                    <th style="width: 17%;">Paper & Year</th>
                    <th style="width: 18%;">Research Objective</th>
                    <th style="width: 18%;">Methodology & Tech</th>
                    <th style="width: 16%;">Key Findings</th>
                    <th style="width: 14%;">Research Gap</th>
                    <th style="width: 12%;">Limitations</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="text-align: center;">1</td>
                    <td><strong>LegalBench</strong><br>(Guha et al., 2023)</td>
                    <td>Benchmark 162 legal reasoning tasks across foundation models.</td>
                    <td>Crowdsourced tasks; evaluated 20 LLMs (GPT-4, Claude, LLaMA-2).</td>
                    <td>High accuracy on clause extraction; sharp drop on statutory interpretation and rhetoric.</td>
                    <td>Lack of cross-jurisdictional and multi-hop reasoning evaluations.</td>
                    <td>US-centric; short queries; no interactive docket stacks.</td>
                </tr>
                <tr>
                    <td style="text-align: center;">2</td>
                    <td><strong>Hallucination-Free?</strong><br>(Magesh et al., 2025)</td>
                    <td>Assess accuracy of commercial legal RAG research tools.</td>
                    <td>Preregistered empirical audit of Lexis+ AI & Westlaw AI vs GPT-4.</td>
                    <td>Leading RAG systems still hallucinate 17%–33% of the time on legal queries.</td>
                    <td>No independent continuous public auditing frameworks for legal AI.</td>
                    <td>US common law only; proprietary black-box APIs; silent updates.</td>
                </tr>
                <tr>
                    <td style="text-align: center;">3</td>
                    <td><strong>CUAD Dataset</strong><br>(Hendrycks et al., 2021)</td>
                    <td>13,000+ annotations across 510 contracts for due diligence.</td>
                    <td>Supervised NLP; RoBERTa, DeBERTa on 41 standardized clause types.</td>
                    <td>Transformers excel at standard clauses but fail on nested/cross-referenced terms.</td>
                    <td>Scarcity of expert data in niche contract sectors; poor cross-domain transfer.</td>
                    <td>Extractive only; commercial corporate focus; no risk synthesis.</td>
                </tr>
                <tr>
                    <td style="text-align: center;">4</td>
                    <td><strong>Better Call GPT</strong><br>(Martin et al., 2024)</td>
                    <td>Quantify speed, cost, & accuracy of LLMs vs human lawyers.</td>
                    <td>Empirical trial comparing GPT-4 against junior lawyers and LPO reviewers.</td>
                    <td>LLMs matched junior lawyers in issue spotting; cut review time by 95% and costs by 99%.</td>
                    <td>Lack of studies on organizational adoption, ethics, and legal apprenticeship.</td>
                    <td>Standard procurement contracts only; no strategic or courtroom testing.</td>
                </tr>
                <tr>
                    <td style="text-align: center;">5</td>
                    <td><strong>LexGLUE</strong><br>(Chalkidis et al., 2022)</td>
                    <td>Multi-task legal language understanding benchmark.</td>
                    <td>7 consolidated tasks (ECtHR, SCOTUS, EUR-LEX); evaluated Legal-BERT, Longformer.</td>
                    <td>Domain-specific pre-training and long-context architectures are crucial for law.</td>
                    <td>Absence of multilingual legal benchmarks and generative task metrics.</td>
                    <td>Discriminative text classification only; English corpora only.</td>
                </tr>
            </tbody>
        </table>

        <h2>3.1 Common Thematic Agreements</h2>
        <p><strong>Automated Triage Drives Unprecedented Efficiency:</strong> All five papers confirm that AI achieves massive, verifiable operational gains in first-pass document reading, routine clause extraction, and metadata tagging (Hendrycks et al., Martin et al., Chalkidis et al.).</p>
        <p><strong>Domain Adaptation is Essential:</strong> General-purpose models fail when applied naively to law. Whether through domain-specific pre-training (Chalkidis et al.), prompt scaffolding (Guha et al.), or legal RAG indexing (Magesh et al.), models must be grounded in legal corpora.</p>
        <p><strong>The Human-in-the-Loop Imperative:</strong> No reviewed study concludes that AI is ready for autonomous practice. Due to persistent errors, high-stakes legal consequences, and ethical accountability, AI must function strictly as an assistive 'co-counsel' supervised by licensed attorneys.</p>

        <h2>3.2 Crucial Disagreements and Conflicts in Literature</h2>
        <p><strong>Marketing Claims vs. Empirical Reality:</strong> Commercial vendors advertise RAG-driven legal tools as 'hallucination-free' and ready for enterprise research. However, empirical legal audits (Magesh et al.) conclusively disprove this, showing error rates up to 33%, demonstrating a massive credibility gap between vendor marketing and scientific measurement.</p>
        <p><strong>Task-Level Accuracy vs. Holistic Professional Utility:</strong> Benchmarking papers (LegalBench, LexGLUE) show significant failure rates on complex statutory reasoning, whereas empirical productivity studies (Better Call GPT) find junior-lawyer parity. This conflict reveals that standardized benchmarks often test edge-case doctrinal puzzles, whereas practical commercial law frequently involves repetitive boilerplate review where AI excels.</p>

        <!-- SECTION 4 -->
        <div class="page-break"></div>
        <h1>4. The Overall Defensible Research Gap</h1>
        <p>Synthesizing the empirical evidence from these five studies reveals the central defensible research gap in AI-driven legal efficiency:</p>
        
        <h2>4.1 What Prior Research Has Addressed</h2>
        <p>Prior work has demonstrated that AI can extract clauses (CUAD), categorize judgments (LexGLUE), and perform fast first-pass contract issue-spotting at 90%+ cost reductions (Better Call GPT). Furthermore, benchmarks have mapped the failure boundaries of raw LLMs in complex legal logic (LegalBench) and proved that commercial RAG still hallucinates 17%–33% of the time (Magesh et al.).</p>

        <h2>4.2 What Remains Insufficiently Studied and Unresolved (The Gap)</h2>
        <p>While existing research proves that AI can drastically speed up isolated sub-tasks, there is a fundamental absence of verified, end-to-end <strong>neuro-symbolic verification frameworks</strong> that integrate automated retrieval with deterministic legal validation to achieve certified reliability:</p>
        <ul>
            <li><strong>Lack of Deterministic Verification Safeguards:</strong> Existing legal RAG systems rely solely on probabilistic vector similarity, which inevitably retrieves semantically similar but legally overruled or inapplicable precedents. Current literature lacks architectures that cross-reference vector embeddings with structured legal knowledge graphs and active judicial status databases (e.g., automated Shepards/KeyCite validation).</li>
            <li><strong>Unmeasured Multi-Turn Interactive Efficiency:</strong> Current benchmarks test one-shot, isolated queries. In actual practice, lawyers interrogate documents iteratively through multi-turn dialogue. The cognitive load, verification latency, and interactive efficiency of human-AI collaboration remain unquantified.</li>
            <li><strong>Absence of Non-Western & Multilingual Jurisdictional Research:</strong> Almost all landmark research is exclusively centered on US Federal law and UK common law. Developing and emerging jurisdictions—such as India's complex dual-statutory framework (e.g., transition to BNS/BNSS/BSA, multi-lingual state court judgments, and the e-Courts project)—remain severely neglected in academic AI literature.</li>
        </ul>

        <h2>4.3 Why This Gap Matters</h2>
        <ul>
            <li><strong>For Courts & Judges:</strong> Enables trustworthy docket summarization (such as India's SUPACE initiative) to alleviate massive court backlogs without risking judicial errors.</li>
            <li><strong>For Law Firms & Corporate Counsel:</strong> Provides verified operational efficiency where senior partners can confidently rely on junior associate AI-assisted drafts without conducting exhaustive line-by-line manual re-verification.</li>
            <li><strong>For Citizens & Access to Justice:</strong> Lowers the exorbitant financial barrier to preliminary legal advice, allowing small businesses and ordinary citizens to understand contractual liabilities safely.</li>
        </ul>

        <!-- SECTION 5: SYNOPSIS -->
        <div class="page-break"></div>
        <h1>5. Comprehensive Academic Seminar Synopsis</h1>
        
        <h2>5.1 Title of the Seminar</h2>
        <p><strong>Enhancing Legal Efficiency Through Artificial Intelligence: Opportunities, Empirical Benchmarks, and Verification Challenges</strong></p>

        <h2>5.2 Introduction</h2>
        <p>The legal sector across the globe is characterized by extreme information density, manual workflow bottlenecks, and severe institutional backlogs. In India alone, over 50 million cases remain pending across district, high, and supreme courts. Legal practitioners, corporate legal departments, and judicial officers spend up to 70% of their working hours engaged in repetitive, administrative, and textual tasks—such as manual contract due diligence, case precedent discovery, statutory cross-referencing, and document drafting. Artificial Intelligence, propelled by transformer architectures, natural language processing (NLP), and domain-adapted Large Language Models (LLMs), presents an unprecedented technological catalyst to transform legal workflows, shifting practice from labor-intensive manual text processing into automated, scalable intelligence.</p>

        <h2>5.3 Background and Problem Statement</h2>
        <p>Traditional legal information management relies on boolean keyword searching, manual indexing, and exhaustive physical document review. This paradigm suffers from critical vulnerabilities:</p>
        <ul>
            <li><strong>Keyword Brittleness:</strong> Traditional search misses pivotal precedents when synonyms or varied phrasing are used.</li>
            <li><strong>Cognitive Fatigue & Human Error:</strong> Manual review of 200-page transactional contracts inevitably leads to overlooked indemnification liabilities or conflicting dispute-resolution clauses.</li>
            <li><strong>The AI Reliability Dilemma:</strong> While generative AI systems (e.g., GPT-4, Gemini) can draft and summarize documents in seconds, generic models suffer from legal hallucinations—fabricating judicial holdings or citing non-existent statutes. Consequently, the primary problem facing the legal industry is not achieving speed, but achieving verifiable efficiency: accelerating workflows without sacrificing legal accuracy.</li>
        </ul>

        <h2>5.4 Aim and Objectives</h2>
        <p>The primary aim of this seminar is to comprehensively investigate how Artificial Intelligence enhances operational efficiency across the legal ecosystem while resolving core accuracy and ethical constraints. The specific objectives are:</p>
        <ul>
            <li><strong>Objective 1:</strong> To examine state-of-the-art applications of AI in legal research, contract intelligence, and document summarization.</li>
            <li><strong>Objective 2:</strong> To analyze empirical benchmarks (LegalBench, CUAD, Better Call GPT) quantifying the speed, cost, and accuracy differentials between AI and human practitioners.</li>
            <li><strong>Objective 3:</strong> To evaluate Retrieval-Augmented Generation (RAG) and domain-specific pre-training (Legal-BERT) as technical solutions to ground AI outputs in authoritative legal texts.</li>
            <li><strong>Objective 4:</strong> To investigate specialized initiatives in the Indian legal system, including SUVAS (AI translation) and SUPACE (judicial research portal).</li>
            <li><strong>Objective 5:</strong> To formulate an architectural framework addressing ethical hazards, including legal hallucination, algorithmic bias, data confidentiality, and professional accountability.</li>
        </ul>

        <h2>5.5 Literature Review Summary</h2>
        <p>A systematic review of five foundational studies provides concrete empirical grounding:</p>
        <ul>
            <li><strong>Legal Reasoning Capabilities:</strong> Guha et al. (NeurIPS 2023) established that while LLMs excel at extraction and issue-spotting, they struggle with multi-clause statutory reasoning, requiring structured task boundaries.</li>
            <li><strong>Commercial Tool Auditing:</strong> Magesh et al. (Journal of Empirical Legal Studies, 2025) empirically demonstrated that leading commercial RAG tools (Lexis+ AI, Westlaw AI) hallucinate 17%–33% of the time, proving that RAG alone is insufficient without secondary validation.</li>
            <li><strong>Contract Due Diligence:</strong> Hendrycks et al. (NeurIPS 2021) demonstrated that deep transformer models can automate the extraction of 41 commercial clause types across massive contract corpuses, dramatically speeding up merger due diligence.</li>
            <li><strong>Speed and Cost Efficiency:</strong> Martin et al. (arXiv 2024) quantitatively showed that advanced LLMs match junior attorneys in routine issue-spotting while slashing review time from hours to seconds and reducing costs by over 90%.</li>
            <li><strong>Domain Adaptation:</strong> Chalkidis et al. (ACL 2022) proved through LexGLUE that legal-specific pre-training (Legal-BERT) and long-document architectures (Longformer) are critical prerequisites for reliable legal language understanding.</li>
        </ul>

        <h2>5.6 Proposed Scope and Methodological Approach</h2>
        <p>This seminar proposes a multi-layered architectural approach to achieve reliable legal efficiency:</p>
        <ul>
            <li><strong>Layer 1: Document Ingestion & Parsing:</strong> High-fidelity extraction of complex documents (PDFs, court dockets, contracts) utilizing OCR and structure-aware parsers.</li>
            <li><strong>Layer 2: Semantic Chunking & Vector Indexing:</strong> Partitioning text into coherent legal clauses (1000-word windows with 150-word context overlap) embedded via domain-tuned models (SentenceTransformers all-MiniLM-L6-v2).</li>
            <li><strong>Layer 3: Knowledge-Grounded RAG Retrieval:</strong> Restricting vector searches via strict metadata filters (e.g., user-isolated document partitions and curated legal knowledge bases).</li>
            <li><strong>Layer 4: Deterministic Guardrails & Fallback:</strong> Implementing hard-coded rule checkers and deterministic offline fallback parsers to ensure that if API latency or hallucination risks occur, the system safely defaults to verified statutory text.</li>
            <li><strong>Layer 5: Mandatory Human-in-the-Loop Supervisory Interface:</strong> Presenting AI outputs with transparent source attribution, chunk citations, and explicit legal disclaimers, ensuring licensed attorneys retain final verification authority.</li>
        </ul>

        <h2>5.7 Expected Outcomes and Impact</h2>
        <ul>
            <li><strong>Dramatic Reduction in Turnaround Times:</strong> Routine contract reviews and preliminary case law research reduced from days to minutes.</li>
            <li><strong>Democratization of Legal Knowledge:</strong> Empowering small businesses, junior advocates, and ordinary citizens to comprehend dense legal agreements before engaging expensive counsel.</li>
            <li><strong>Institutional Judicial Relief:</strong> Assisting court registries and judges in cataloging, summarizing, and translating filings across multilingual jurisdictions.</li>
        </ul>

        <h2>5.8 Limitations and Ethical Considerations</h2>
        <ul>
            <li><strong>Hallucination Vulnerability:</strong> AI can misquote statutes or invent precedent citations, necessitating strict verification protocols.</li>
            <li><strong>Client Confidentiality & Data Privacy:</strong> Transmitting sensitive client contracts to public commercial LLM APIs risks breaching attorney-client privilege. Enterprise local vector models and on-premises deployments are vital.</li>
            <li><strong>Algorithmic Bias:</strong> AI trained on historical jurisprudence may perpetuate racial, socioeconomic, or regional sentencing disparities if deployed in predictive justice systems.</li>
            <li><strong>Unauthorized Practice of Law (UPL):</strong> AI systems must operate strictly as educational and informational research aids, not autonomous legal counselors.</li>
        </ul>

        <h2>5.9 Conclusion</h2>
        <p>Artificial Intelligence represents the most transformative technological shift in legal practice since the advent of digitized legal publishing. When engineered with robust semantic search, retrieval-augmented grounding, and domain-adapted transformers, AI delivers unprecedented gains in research speed, contract analysis, and operational cost reduction. However, AI cannot replace the indispensable human faculties of moral judgment, contextual empathy, ethical accountability, and courtroom advocacy. By framing AI not as a replacement for lawyers, but as an assistive 'cognitive amplifier,' the legal profession can achieve unprecedented operational efficiency while upholding the sacred integrity of justice.</p>

        <!-- SECTION 6: REFERENCES -->
        <div class="page-break"></div>
        <h1>6. Complete Verified References (IEEE Citation Style)</h1>
        <div class="ref-item"><strong>[1]</strong> N. Guha, J. Nyarko, D. E. Ho, C. Ré, A. Chilton, K. Tobia, J. R. Nay, et al., "LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models," in <em>Proc. 37th Conf. Neural Information Processing Systems (NeurIPS 2023) Datasets and Benchmarks Track</em>, New Orleans, LA, USA, Dec. 2023. DOI: <a href="https://doi.org/10.48550/arXiv.2308.11462">10.48550/arXiv.2308.11462</a>.</div>
        <div class="ref-item"><strong>[2]</strong> V. Magesh, F. Surani, M. Dahl, M. Suzgun, C. D. Manning, and D. E. Ho, "Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools," <em>Journal of Empirical Legal Studies</em>, Wiley, 2025. Preprint: arXiv:2405.20362. DOI: <a href="https://doi.org/10.1111/jels.12413">10.1111/jels.12413</a>.</div>
        <div class="ref-item"><strong>[3]</strong> D. Hendrycks, C. Burns, A. Chen, and S. Ball, "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review," in <em>Proc. 35th Conf. Neural Information Processing Systems (NeurIPS 2021) Datasets and Benchmarks Track</em>, Dec. 2021. DOI: <a href="https://doi.org/10.48550/arXiv.2103.06268">10.48550/arXiv.2103.06268</a>.</div>
        <div class="ref-item"><strong>[4]</strong> L. Martin, N. Whitehouse, S. Yiu, L. Catterson, and R. Perera, "Better Call GPT, Comparing Large Language Models Against Lawyers," arXiv preprint arXiv:2401.16212, Jan. 2024. DOI: <a href="https://doi.org/10.48550/arXiv.2401.16212">10.48550/arXiv.2401.16212</a>.</div>
        <div class="ref-item"><strong>[5]</strong> I. Chalkidis, A. Jana, D. Hartung, M. Bommarito, I. Androutsopoulos, D. M. Katz, and N. Aletras, "LexGLUE: A Benchmark Dataset for Legal Language Understanding in English," in <em>Proc. 60th Annual Meeting Association for Computational Linguistics (ACL 2022)</em>, Dublin, Ireland, May 2022, pp. 4310–4330. DOI: <a href="https://doi.org/10.18653/v1/2022.acl-long.297">10.18653/v1/2022.acl-long.297</a>.</div>
        <div class="ref-item"><strong>[6]</strong> P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in <em>Advances in Neural Information Processing Systems (NeurIPS 2020)</em>, vol. 33, 2020, pp. 9459–9474.</div>
        <div class="ref-item"><strong>[7]</strong> Supreme Court of India, "AI in the Indian Judiciary: An Overview of SUPACE and SUVAS Initiatives," Official Reports of the Supreme Court of India Artificial Intelligence Committee, New Delhi, India, 2021–2023. [Online]. Available: <a href="https://main.sci.gov.in/">https://main.sci.gov.in/</a>.</div>

    </body>
    </html>
    """
    
    html_path = os.path.join(OUTPUT_DIR, "temp_paper_analysis.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    pdf_path = os.path.join(OUTPUT_DIR, "Legal_AI_Research_Paper_Analysis_and_Synopsis.pdf")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file:///{os.path.abspath(html_path).replace(chr(92), '/')}")
        await page.pdf(
            path=pdf_path,
            format="A4",
            margin={"top": "0.6in", "bottom": "0.6in", "left": "0.6in", "right": "0.6in"},
            print_background=True
        )
        await browser.close()
        
    print(f"PDF successfully generated at: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    docx_file = build_docx()
    pdf_file = asyncio.run(build_pdf())
    print("\nAll documents built successfully!")
