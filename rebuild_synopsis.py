import os
import asyncio
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from playwright.async_api import async_playwright
import pymupdf as fitz

def set_font(run, name='Bookman Old Style', size=12, bold=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    r = run._r
    rPr = r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)
    rPr.append(rFonts)

def add_heading(doc, text, page_break_before=False):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(12)
    if page_break_before:
        p.paragraph_format.page_break_before = True
    run = p.add_run(text)
    set_font(run, bold=True)
    return p

def add_paragraph(doc, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.space_after = Pt(12)
    run = p.add_run(text)
    set_font(run)
    return p

def add_bullet(doc, text):
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    set_font(run)

def add_page_borders(sectPr):
    borders = OxmlElement('w:pgBorders')
    borders.set(qn('w:offsetFrom'), 'page')
    for border_name in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')  # 0.5 pt for a thin visible border
        border.set(qn('w:space'), '36')  # 0.5 inch from edge
        border.set(qn('w:color'), '000000')
        borders.append(border)
    sectPr.append(borders)

def setup_margins_and_borders(section):
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    add_page_borders(section._sectPr)

def create_docx():
    doc = Document()
    
    # SECTION 1: Cover and Guide Page
    s1 = doc.sections[0]
    setup_margins_and_borders(s1)
    s1.header.is_linked_to_previous = False
    s1.footer.is_linked_to_previous = False
    
    # Cover Page
    for _ in range(3): doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_font(p.add_run("PROJECT SYNOPSIS\nOn\n\n"), bold=True)
    set_font(p.add_run("“LexAI – AI-Powered Legal Assistant & Contract Intelligence Platform”\n\n\n"), bold=True)
    set_font(p.add_run("Submitted to\n"), bold=True)
    set_font(p.add_run("Chhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai\n\n"), bold=True)
    if os.path.exists("csmu_logo.png"):
        p.add_run().add_picture("csmu_logo.png", width=Inches(1.5))
        p.add_run("\n\n")
    else:
        p.add_run("\n\n")
    set_font(p.add_run("for the partial fulfillment of requirement for the Degree of\n"), bold=False)
    set_font(p.add_run("MASTER OF COMPUTER APPLICATION\n\n\n"), bold=True)
    set_font(p.add_run("Submitted By\n\n"), bold=True)
    set_font(p.add_run("Rohan Bongane\nHarsh Jha\nAishwariya Bhunia\nNitu Sharma\n"), bold=False)
    
    doc.add_page_break()
    
    # Guide Page
    for _ in range(8): doc.add_paragraph()
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_font(p2.add_run("Guide\n\n"), bold=True)
    set_font(p2.add_run("Dr. Surekha Kohle\n\n\n\n"), bold=False)
    set_font(p2.add_run("Department of Computer Science & Information Technology\nChhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai\n\nAcademic Year:\n2026–27\n"), bold=True)

    # SECTION 2: Main Content (Page 3 onwards)
    s2 = doc.add_section(WD_SECTION.NEW_PAGE)
    setup_margins_and_borders(s2)
    s2.footer.is_linked_to_previous = False
    s2.header.is_linked_to_previous = False
    
    # Start page numbering at 1
    sectPr = s2._sectPr
    pgNumType = OxmlElement('w:pgNumType')
    pgNumType.set(qn('w:start'), '1')
    sectPr.append(pgNumType)

    # Add page number to footer
    footer = s2.footer
    footer_p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    r_f = OxmlElement('w:r')
    rPr_f = OxmlElement('w:rPr')
    rFonts_f = OxmlElement('w:rFonts')
    rFonts_f.set(qn('w:ascii'), 'Bookman Old Style')
    rPr_f.append(rFonts_f)
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), '24')
    rPr_f.append(sz)
    r_f.append(rPr_f)
    fldSimple.append(r_f)
    footer_p._p.append(fldSimple)

    # 1. Introduction
    add_heading(doc, "1. Introduction")
    add_paragraph(doc, "The legal domain is characterized by densely packed terminology and lengthy documents, creating significant barriers for individuals and small businesses. Contracts and terms of service are often obfuscated by specialized jargon, making it difficult for non-lawyers to comprehend their rights, obligations, and hidden risks.")
    add_paragraph(doc, "Manually reviewing these documents requires immense cognitive effort and frequently necessitates consulting legal professionals. The high cost of legal counsel often leads to contracts being signed without a full understanding of their implications. There is a pressing need for automated tools that can democratize access to basic legal comprehension.")
    add_paragraph(doc, "LexAI is an AI-assisted legal information platform designed to bridge this gap. Utilizing a Flask-based web architecture, LexAI allows users to securely upload legal contracts (PDF or DOCX). The platform extracts and processes text to perform semantic analysis, providing executive summaries and identifying critical clauses.")
    add_paragraph(doc, "To mitigate the \"hallucination\" risks associated with generative models, LexAI implements a Retrieval-Augmented Generation (RAG) architecture using the Google Gemini LLM. Grounding responses exclusively in the retrieved text of the user's specific document or a curated Knowledge Base helps reduce the likelihood of inaccurate claims. While LexAI assists in comprehension, it does not replace professional legal advice and acts primarily as an informational tool to aid preliminary review.")
    
    doc.add_page_break()

    # 2. Literature Review
    add_heading(doc, "2. Literature Review")
    add_paragraph(doc, "Jain et al. [1] highlight the complexities of summarizing legal documents, emphasizing the necessity of preserving factual integrity. Traditional extractive methods miss semantic nuance, while abstractive generative models risk fabricating legal precedent. LexAI adopts a deterministic chunking strategy prior to abstraction to generate verifiable summaries.")
    add_paragraph(doc, "Chalkidis et al. [2] demonstrated with LEGAL-BERT that generic language models frequently misinterpret legal nuances, necessitating domain-aware processing. LexAI addresses this by combining the efficient all-MiniLM-L6-v2 embedding model with strict JSON-schema prompting via the Gemini LLM to enforce analytical constraints.")
    add_paragraph(doc, "Lewis et al. [3] established Retrieval-Augmented Generation (RAG) as a standard for knowledge-intensive NLP tasks, proving that querying an external vector index reduces factual hallucinations. LexAI incorporates this by utilizing ChromaDB as a semantic vector store, ensuring the AI processes text explicitly present in the uploaded document.")
    add_paragraph(doc, "Surveys by Ariai et al. [4] and Martinez-Gil [5] underscore challenges in legal QA systems concerning privacy and trust. Public generative AI interfaces pose security risks for confidential contracts, and unconstrained models may hallucinate standard practices instead of citing negotiated terms.")
    add_heading(doc, "Research Gap")
    add_paragraph(doc, "While existing literature supports RAG in controlled settings, there is a gap in accessible systems that combine private document analysis with a securely isolated environment. LexAI addresses this by enforcing database-level filtering (document ID isolation), ensuring users only query their private contracts safely.")

    doc.add_page_break()

    # 3. Aims & Objective
    add_heading(doc, "3. Aims & Objective")
    add_paragraph(doc, "The primary aim of LexAI is to develop a secure, accessible web-based platform that utilizes Artificial Intelligence and RAG to demystify complex legal documents.")
    add_paragraph(doc, "Implemented Objectives:")
    add_bullet(doc, "User Authentication & Security: Develop secure registration and session management using Flask-Login and Bcrypt.")
    add_bullet(doc, "Document Processing: Enable secure upload and raw text extraction from PDF/DOCX using PyMuPDF and python-docx.")
    add_bullet(doc, "AI Legal Analysis: Engineer JSON prompts that constrain the Gemini API to generate executive summaries and highlight key clauses.")
    add_bullet(doc, "RAG-Based Retrieval: Implement a vector embedding pipeline using SentenceTransformers and ChromaDB.")
    add_bullet(doc, "Secure Isolation: Enforce database filtering so users can only access their own private documents.")
    add_bullet(doc, "Document Chatbot: Create a conversational interface for users to query their specific uploaded contracts.")
    add_bullet(doc, "Knowledge Base: Provide an admin-curated Knowledge Base for general legal queries.")
    add_bullet(doc, "Deterministic Fallback: Implement a robust parser to handle external API failures by formatting local content.")
    add_paragraph(doc, "Future Objectives (Planned):")
    add_bullet(doc, "Optical Character Recognition (OCR): Process scanned, image-based legal documents lacking embedded text.")
    add_bullet(doc, "Cloud Migration: Migrate local ChromaDB and file storage to persistent cloud infrastructure.")

    doc.add_page_break()

    # 4. Problem Definition
    add_heading(doc, "4. Problem Definition")
    add_paragraph(doc, "The legal ecosystem remains largely inaccessible to the general public and small enterprises due to the volume and complexity of legal text. When an individual faces a standard contract, they encounter several immediate challenges:")
    add_paragraph(doc, "Manual Review Effort:\nContracts are often filled with repetitive boilerplate text and complex formatting. Reading these documents requires significant time. For many, this effort leads to signing documents without thorough review.")
    add_paragraph(doc, "Obfuscated Clauses and Hidden Risks:\nCritical obligations, termination conditions, and liability waivers are frequently buried within archaic terminology. Identifying these risks without training is highly error-prone, carrying potential financial implications.")
    add_paragraph(doc, "Information Retrieval Friction:\nFinding specific clauses (e.g., late payment penalties) in a massive document is tedious. Traditional keyword search often fails if the user does not guess the exact terminology used by the drafting lawyer.")
    add_paragraph(doc, "Unreliable Public AI Solutions:\nWhile public generative AI chatbots are available, they provide generic, ungrounded responses. Furthermore, pasting confidential contracts into public interfaces poses severe privacy and compliance risks.")

    doc.add_page_break()

    # 5. Proposed Model
    add_heading(doc, "5. Proposed Model")
    add_paragraph(doc, "LexAI proposes a decoupled client-server architecture ensuring documents are processed locally, and an LLM is strictly constrained via RAG to answer based only on the user's uploaded text.")
    add_paragraph(doc, "System Architecture Flow:\nUser Interaction ➔ Web Interface ➔ Flask Backend ➔ Metadata / Vector Storage ➔ Gemini API", align=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "Frontend Layer:\nThe interface is built with HTML5, CSS3, and JavaScript, utilizing Bootstrap 5. It employs marked.js for Markdown rendering and DOMPurify to prevent Cross-Site Scripting (XSS).")
    add_paragraph(doc, "Backend Orchestration Layer:\nThe Python Flask application handles routing, session management, and business logic. It securely isolates user data and orchestrates the processing pipeline.")
    add_paragraph(doc, "Relational Storage (MySQL):\nMySQL stores structured data, including Bcrypt-hashed credentials, document metadata, and chat histories, ensuring rapid retrieval of session states.")
    add_paragraph(doc, "Vector Storage & Embeddings:\nUploaded files are parsed to extract raw text, which a SentenceTransformers model converts into mathematical vectors. These are stored in ChromaDB for semantic similarity search.")
    add_paragraph(doc, "Generative Intelligence:\nThe backend retrieves semantically relevant text chunks from ChromaDB. These are appended to a strict prompt and sent to the Gemini API, which generates a natural language response grounded in the chunks.")

    doc.add_page_break()

    # 6. Methodology
    add_heading(doc, "6. Methodology")
    add_paragraph(doc, "The operational methodology is structured into a logical pipeline handling everything from secure file access to AI generation.")
    add_paragraph(doc, "A. Authentication & Upload Validation:\nUsers create accounts protected by Bcrypt hashing and Flask-Login. Uploaded files undergo MIME type and extension validation before being securely saved to an isolated local directory.")
    add_paragraph(doc, "B. Text Extraction:\nThe system utilizes PyMuPDF and python-docx to extract pure unicode text. Document statistics, such as word counts, are calculated simultaneously.")
    add_paragraph(doc, "C. Contextual Chunking:\nTo respect LLM token limits, extracted text is sliced into smaller chunks (e.g., 500 words). Overlapping windows (e.g., 50 words) preserve the contextual flow between boundaries.")
    add_paragraph(doc, "D. Embedding & Storage:\nEach chunk is processed by the local embedding model. The resulting vectors are strictly tagged with the user's ID in ChromaDB, enforcing absolute data isolation during future retrieval.")
    add_paragraph(doc, "E. RAG Retrieval & Chat Workflow:\nUser queries are embedded into vectors. ChromaDB calculates cosine similarity against stored chunks, returning the top matches. These chunks are combined into a strict context prompt for the Gemini API.")
    add_paragraph(doc, "F. Deterministic Fallback:\nIf the Gemini API becomes unavailable, the pipeline intercepts the failure. A deterministic Python fallback parser formats the raw legal information retrieved from ChromaDB, ensuring basic system functionality.")

    doc.add_page_break()

    # 7. Plan of Work
    add_heading(doc, "7. Plan of Work")
    add_paragraph(doc, "The development of LexAI was executed in sequential stages to ensure stability before integrating AI components. The structured timeline is outlined below:")
    
    # Use a neat table for the Plan of Work
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Phase'
    hdr_cells[1].text = 'Task Description'
    hdr_cells[2].text = 'Status'
    
    for cell in hdr_cells:
        for p in cell.paragraphs:
            for r in p.runs:
                set_font(r, bold=True)
                
    phases = [
        ("Phase 1", "Project Setup, MySQL Database Design, Flask-Login & Bcrypt Authentication", "Implemented"),
        ("Phase 2", "Secure Document Upload, MIME Validation, PyMuPDF Text Extraction", "Implemented"),
        ("Phase 3", "Gemini API Integration, JSON-schema Prompt Engineering", "Implemented"),
        ("Phase 4", "RAG Pipeline, SentenceTransformers Embedding, ChromaDB Indexing, Chat UI", "Implemented"),
        ("Phase 5", "Admin Knowledge Base, Testing Suites, Deterministic Fallback Parser", "Implemented"),
        ("Phase 6", "Optical Character Recognition (OCR) for scanned PDFs", "Future Scope"),
        ("Phase 7", "Cloud Migration for Persistent Vector Storage and Scalability", "Future Scope")
    ]
    
    for phase, desc, status in phases:
        row_cells = table.add_row().cells
        row_cells[0].text = phase
        row_cells[1].text = desc
        row_cells[2].text = status
        for cell in row_cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    set_font(r)

    doc.add_page_break()

    # 8. Conclusion
    add_heading(doc, "8. Conclusion")
    add_paragraph(doc, "The LexAI project demonstrates the practical application of combining Large Language Models with Retrieval-Augmented Generation to address accessibility issues in legal document comprehension. By integrating an intuitive web interface with a locally embedded RAG pipeline, LexAI provides a secure, isolated environment for contract analysis.")
    add_paragraph(doc, "Through automated executive summaries and a conversational chatbot, the platform reduces the cognitive load required to understand dense legalese. The strict database-level separation of the user's Document Chat and the General Legal Knowledge Base helps ensure that responses are reliably grounded in verified text, aiming to minimize the risks of model hallucination.")
    add_paragraph(doc, "While LexAI does not eliminate all risks of AI inaccuracy and is not a substitute for professional legal counsel, it represents a functional prototype. The implementation of security measures, user data isolation, and a deterministic fallback parser ensures that LexAI acts as a resilient and transparent informational assistant for individuals and small businesses.")

    doc.add_page_break()

    # 9. References
    add_heading(doc, "9. References")
    def add_reference(d, text):
        p = d.add_paragraph()
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.paragraph_format.space_after = Pt(12)
        set_font(p.add_run(text))

    add_reference(doc, "[1] Jain, D., Borah, M. D., & Biswas, A. (2021). \"Summarization of legal documents: Where are we now and the way forward.\" Computer Science Review, 40, 100388.")
    add_reference(doc, "[2] Chalkidis, I., Fergadiotis, M., Malakasiotis, P., Aletras, N., & Androutsopoulos, I. (2020). \"LEGAL-BERT: The Muppets straight out of Law School.\" Findings of the Association for Computational Linguistics: EMNLP 2020.")
    add_reference(doc, "[3] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Riedel, S. (2020). \"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.\" Advances in Neural Information Processing Systems (NeurIPS).")
    add_reference(doc, "[4] Ariai, F., Mackenzie, J., & Demartini, G. (2025). \"Natural Language Processing for the Legal Domain: A Survey of Tasks, Datasets, Models, and Challenges.\" ACM Computing Surveys, 58(6).")
    add_reference(doc, "[5] Martinez-Gil, J. (2023). \"A survey on legal question–answering systems.\" Computer Science Review, 48, 100551.")

    for _ in range(4): doc.add_paragraph()

    table_sig = doc.add_table(rows=1, cols=2)
    table_sig.autofit = True
    cell_left = table_sig.cell(0, 0)
    p_left = cell_left.paragraphs[0]
    p_left.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_font(p_left.add_run("Prof. Dr. Surekha Kohle\n"), bold=True)
    set_font(p_left.add_run("Guide\nCS/IT Department"))

    cell_right = table_sig.cell(0, 1)
    p_right = cell_right.paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_right.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_font(p_right.add_run("Dr. Praveen Gupta\n"), bold=True)
    set_font(p_right.add_run("H.O.D.\nCS/IT Department"))

    doc.save("LexAI_Project_Synopsis_Final.docx")


html_head = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page { size: A4; margin: 1in; }
        body {
            font-family: "Bookman Old Style", serif; font-size: 12pt;
            line-height: 1.5; color: black; text-align: justify;
            margin: 0; padding: 0;
        }
        .page-border {
            position: fixed; top: -0.5in; left: -0.5in; right: -0.5in; bottom: -0.5in;
            border: 1px solid black; z-index: -100; pointer-events: none;
        }
        h2, h3 { font-size: 12pt; font-weight: bold; margin-top: 0; margin-bottom: 12px; }
        p { margin-bottom: 12px; margin-top: 0; }
        ul { margin-top: 0; margin-bottom: 12px; padding-left: 20px; }
        li { margin-bottom: 6px; }
        .main-section { page-break-before: always; }
        .main-section:first-of-type { page-break-before: auto; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 12px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { font-weight: bold; }
        .cover-page, .guide-page { page-break-after: always; }
        .cover-page img { width: 1.5in; height: auto; margin: 20px 0; }
        .cover-page p, .guide-page p { text-align: center; margin: 0; }
        .bold { font-weight: bold; }
        .signatures { width: 100%; margin-top: 60px; page-break-inside: avoid; border: none; }
        .signatures td { border: none; padding: 0; }
        .sig-right { text-align: right; }
    </style>
</head>
<body>
    <div class="page-border"></div>
"""

html_part1 = html_head + """
    <div class="cover-page">
        <br><br><br>
        <p class="bold">PROJECT SYNOPSIS</p>
        <p class="bold">On</p><br>
        <p class="bold">“LexAI – AI-Powered Legal Assistant & Contract Intelligence Platform”</p><br><br><br>
        <p class="bold">Submitted to</p><br>
        <p class="bold">Chhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai</p><br><br>
        <p style="text-align:center;"><img src="csmu_logo.png" alt="CSMU Logo"></p><br><br>
        <p>for the partial fulfillment of requirement for the Degree of</p><br>
        <p class="bold">MASTER OF COMPUTER APPLICATION</p><br><br><br>
        <p class="bold">Submitted By</p><br>
        <p>Rohan Bongane</p>
        <p>Harsh Jha</p>
        <p>Aishwariya Bhunia</p>
        <p>Nitu Sharma</p>
    </div>
    <div class="guide-page">
        <br><br><br><br><br><br><br><br><br><br><br>
        <p class="bold">Guide</p><br>
        <p>Dr. Surekha Kohle</p><br><br><br><br><br><br>
        <p class="bold">Department of Computer Science & Information Technology</p>
        <p class="bold">Chhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai</p><br><br>
        <p class="bold">Academic Year:</p>
        <p class="bold">2026–27</p>
    </div>
</body></html>
"""

html_part2 = html_head + """
    <div class="main-section">
        <h2>1. Introduction</h2>
        <p>The legal domain is characterized by densely packed terminology and lengthy documents, creating significant barriers for individuals and small businesses. Contracts and terms of service are often obfuscated by specialized jargon, making it difficult for non-lawyers to comprehend their rights, obligations, and hidden risks.</p>
        <p>Manually reviewing these documents requires immense cognitive effort and frequently necessitates consulting legal professionals. The high cost of legal counsel often leads to contracts being signed without a full understanding of their implications. There is a pressing need for automated tools that can democratize access to basic legal comprehension.</p>
        <p>LexAI is an AI-assisted legal information platform designed to bridge this gap. Utilizing a Flask-based web architecture, LexAI allows users to securely upload legal contracts (PDF or DOCX). The platform extracts and processes text to perform semantic analysis, providing executive summaries and identifying critical clauses.</p>
        <p>To mitigate the "hallucination" risks associated with generative models, LexAI implements a Retrieval-Augmented Generation (RAG) architecture using the Google Gemini LLM. Grounding responses exclusively in the retrieved text of the user's specific document or a curated Knowledge Base helps reduce the likelihood of inaccurate claims. While LexAI assists in comprehension, it does not replace professional legal advice and acts primarily as an informational tool to aid preliminary review.</p>
    </div>

    <div class="main-section">
        <h2>2. Literature Review</h2>
        <p>Jain et al. [1] highlight the complexities of summarizing legal documents, emphasizing the necessity of preserving factual integrity. Traditional extractive methods miss semantic nuance, while abstractive generative models risk fabricating legal precedent. LexAI adopts a deterministic chunking strategy prior to abstraction to generate verifiable summaries.</p>
        <p>Chalkidis et al. [2] demonstrated with LEGAL-BERT that generic language models frequently misinterpret legal nuances, necessitating domain-aware processing. LexAI addresses this by combining the efficient all-MiniLM-L6-v2 embedding model with strict JSON-schema prompting via the Gemini LLM to enforce analytical constraints.</p>
        <p>Lewis et al. [3] established Retrieval-Augmented Generation (RAG) as a standard for knowledge-intensive NLP tasks, proving that querying an external vector index reduces factual hallucinations. LexAI incorporates this by utilizing ChromaDB as a semantic vector store, ensuring the AI processes text explicitly present in the uploaded document.</p>
        <p>Surveys by Ariai et al. [4] and Martinez-Gil [5] underscore challenges in legal QA systems concerning privacy and trust. Public generative AI interfaces pose security risks for confidential contracts, and unconstrained models may hallucinate standard practices instead of citing negotiated terms.</p>
        <h2>Research Gap</h2>
        <p>While existing literature supports RAG in controlled settings, there is a gap in accessible systems that combine private document analysis with a securely isolated environment. LexAI addresses this by enforcing database-level filtering (document ID isolation), ensuring users only query their private contracts safely.</p>
    </div>

    <div class="main-section">
        <h2>3. Aims & Objective</h2>
        <p>The primary aim of LexAI is to develop a secure, accessible web-based platform that utilizes Artificial Intelligence and RAG to demystify complex legal documents.</p>
        <p>Implemented Objectives:</p>
        <ul>
            <li><strong>User Authentication & Security:</strong> Develop secure registration and session management using Flask-Login and Bcrypt.</li>
            <li><strong>Document Processing:</strong> Enable secure upload and raw text extraction from PDF/DOCX using PyMuPDF and python-docx.</li>
            <li><strong>AI Legal Analysis:</strong> Engineer JSON prompts that constrain the Gemini API to generate executive summaries and highlight key clauses.</li>
            <li><strong>RAG-Based Retrieval:</strong> Implement a vector embedding pipeline using SentenceTransformers and ChromaDB.</li>
            <li><strong>Secure Isolation:</strong> Enforce database filtering so users can only access their own private documents.</li>
            <li><strong>Document Chatbot:</strong> Create a conversational interface for users to query their specific uploaded contracts.</li>
            <li><strong>Knowledge Base:</strong> Provide an admin-curated Knowledge Base for general legal queries.</li>
            <li><strong>Deterministic Fallback:</strong> Implement a robust parser to handle external API failures by formatting local content.</li>
        </ul>
        <p>Future Objectives (Planned):</p>
        <ul>
            <li><strong>Optical Character Recognition (OCR):</strong> Process scanned, image-based legal documents lacking embedded text.</li>
            <li><strong>Cloud Migration:</strong> Migrate local ChromaDB and file storage to persistent cloud infrastructure.</li>
        </ul>
    </div>

    <div class="main-section">
        <h2>4. Problem Definition</h2>
        <p>The legal ecosystem remains largely inaccessible to the general public and small enterprises due to the volume and complexity of legal text. When an individual faces a standard contract, they encounter several immediate challenges:</p>
        <p class="bold">Manual Review Effort</p>
        <p>Contracts are often filled with repetitive boilerplate text and complex formatting. Reading these documents requires significant time. For many, this effort leads to signing documents without thorough review.</p>
        <p class="bold">Obfuscated Clauses and Hidden Risks</p>
        <p>Critical obligations, termination conditions, and liability waivers are frequently buried within archaic terminology. Identifying these risks without training is highly error-prone, carrying potential financial implications.</p>
        <p class="bold">Information Retrieval Friction</p>
        <p>Finding specific clauses (e.g., late payment penalties) in a massive document is tedious. Traditional keyword search often fails if the user does not guess the exact terminology used by the drafting lawyer.</p>
        <p class="bold">Unreliable Public AI Solutions</p>
        <p>While public generative AI chatbots are available, they provide generic, ungrounded responses. Furthermore, pasting confidential contracts into public interfaces poses severe privacy and compliance risks.</p>
    </div>

    <div class="main-section">
        <h2>5. Proposed Model</h2>
        <p>LexAI proposes a decoupled client-server architecture ensuring documents are processed locally, and an LLM is strictly constrained via RAG to answer based only on the user's uploaded text.</p>
        <p style="text-align: center; font-style: italic;" class="bold">System Architecture Flow:<br>User Interaction ➔ Web Interface ➔ Flask Backend ➔ Metadata / Vector Storage ➔ Gemini API</p>
        <p class="bold">Frontend Layer</p>
        <p>The interface is built with HTML5, CSS3, and JavaScript, utilizing Bootstrap 5. It employs marked.js for Markdown rendering and DOMPurify to prevent Cross-Site Scripting (XSS).</p>
        <p class="bold">Backend Orchestration Layer</p>
        <p>The Python Flask application handles routing, session management, and business logic. It securely isolates user data and orchestrates the processing pipeline.</p>
        <p class="bold">Relational Storage (MySQL)</p>
        <p>MySQL stores structured data, including Bcrypt-hashed credentials, document metadata, and chat histories, ensuring rapid retrieval of session states.</p>
        <p class="bold">Vector Storage & Embeddings</p>
        <p>Uploaded files are parsed to extract raw text, which a SentenceTransformers model converts into mathematical vectors. These are stored in ChromaDB for semantic similarity search.</p>
        <p class="bold">Generative Intelligence</p>
        <p>The backend retrieves semantically relevant text chunks from ChromaDB. These are appended to a strict prompt and sent to the Gemini API, which generates a natural language response grounded in the chunks.</p>
    </div>

    <div class="main-section">
        <h2>6. Methodology</h2>
        <p>The operational methodology is structured into a logical pipeline handling everything from secure file access to AI generation.</p>
        <p class="bold">A. Authentication & Upload Validation</p>
        <p>Users create accounts protected by Bcrypt hashing and Flask-Login. Uploaded files undergo MIME type and extension validation before being securely saved to an isolated local directory.</p>
        <p class="bold">B. Text Extraction</p>
        <p>The system utilizes PyMuPDF and python-docx to extract pure unicode text. Document statistics, such as word counts, are calculated simultaneously.</p>
        <p class="bold">C. Contextual Chunking</p>
        <p>To respect LLM token limits, extracted text is sliced into smaller chunks (e.g., 500 words). Overlapping windows (e.g., 50 words) preserve the contextual flow between boundaries.</p>
        <p class="bold">D. Embedding & Storage</p>
        <p>Each chunk is processed by the local embedding model. The resulting vectors are strictly tagged with the user's ID in ChromaDB, enforcing absolute data isolation during future retrieval.</p>
        <p class="bold">E. RAG Retrieval & Chat Workflow</p>
        <p>User queries are embedded into vectors. ChromaDB calculates cosine similarity against stored chunks, returning the top matches. These chunks are combined into a strict context prompt for the Gemini API.</p>
        <p class="bold">F. Deterministic Fallback</p>
        <p>If the Gemini API becomes unavailable, the pipeline intercepts the failure. A deterministic Python fallback parser formats the raw legal information retrieved from ChromaDB, ensuring basic system functionality.</p>
    </div>

    <div class="main-section">
        <h2>7. Plan of Work</h2>
        <p>The development of LexAI was executed in sequential stages to ensure stability before integrating AI components. The structured timeline is outlined below:</p>
        <table>
            <tr>
                <th>Phase</th>
                <th>Task Description</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Phase 1</td>
                <td>Project Setup, MySQL Database Design, Flask-Login & Bcrypt Authentication</td>
                <td>Implemented</td>
            </tr>
            <tr>
                <td>Phase 2</td>
                <td>Secure Document Upload, MIME Validation, PyMuPDF Text Extraction</td>
                <td>Implemented</td>
            </tr>
            <tr>
                <td>Phase 3</td>
                <td>Gemini API Integration, JSON-schema Prompt Engineering</td>
                <td>Implemented</td>
            </tr>
            <tr>
                <td>Phase 4</td>
                <td>RAG Pipeline, SentenceTransformers Embedding, ChromaDB Indexing, Chat UI</td>
                <td>Implemented</td>
            </tr>
            <tr>
                <td>Phase 5</td>
                <td>Admin Knowledge Base, Testing Suites, Deterministic Fallback Parser</td>
                <td>Implemented</td>
            </tr>
            <tr>
                <td>Phase 6</td>
                <td>Optical Character Recognition (OCR) for scanned PDFs</td>
                <td>Future Scope</td>
            </tr>
            <tr>
                <td>Phase 7</td>
                <td>Cloud Migration for Persistent Vector Storage and Scalability</td>
                <td>Future Scope</td>
            </tr>
        </table>
    </div>

    <div class="main-section">
        <h2>8. Conclusion</h2>
        <p>The LexAI project demonstrates the practical application of combining Large Language Models with Retrieval-Augmented Generation to address accessibility issues in legal document comprehension. By integrating an intuitive web interface with a locally embedded RAG pipeline, LexAI provides a secure, isolated environment for contract analysis.</p>
        <p>Through automated executive summaries and a conversational chatbot, the platform reduces the cognitive load required to understand dense legalese. The strict database-level separation of the user's Document Chat and the General Legal Knowledge Base helps ensure that responses are reliably grounded in verified text, aiming to minimize the risks of model hallucination.</p>
        <p>While LexAI does not eliminate all risks of AI inaccuracy and is not a substitute for professional legal counsel, it represents a functional prototype. The implementation of security measures, user data isolation, and a deterministic fallback parser ensures that LexAI acts as a resilient and transparent informational assistant for individuals and small businesses.</p>
    </div>

    <div class="main-section">
        <h2>9. References</h2>
        <p>[1] Jain, D., Borah, M. D., & Biswas, A. (2021). "Summarization of legal documents: Where are we now and the way forward." <span class="bold">Computer Science Review</span>, 40, 100388.</p>
        <p>[2] Chalkidis, I., Fergadiotis, M., Malakasiotis, P., Aletras, N., & Androutsopoulos, I. (2020). "LEGAL-BERT: The Muppets straight out of Law School." <span class="bold">Findings of the Association for Computational Linguistics: EMNLP 2020</span>.</p>
        <p>[3] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Riedel, S. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." <span class="bold">Advances in Neural Information Processing Systems (NeurIPS)</span>.</p>
        <p>[4] Ariai, F., Mackenzie, J., & Demartini, G. (2025). "Natural Language Processing for the Legal Domain: A Survey of Tasks, Datasets, Models, and Challenges." <span class="bold">ACM Computing Surveys</span>, 58(6).</p>
        <p>[5] Martinez-Gil, J. (2023). "A survey on legal question–answering systems." <span class="bold">Computer Science Review</span>, 48, 100551.</p>
        
        <table class="signatures">
            <tr>
                <td class="sig-left">
                    <p class="bold">Prof. Dr. Surekha Kohle</p>
                    <p>Guide</p>
                    <p>CS/IT Department</p>
                </td>
                <td class="sig-right">
                    <p class="bold">Dr. Praveen Gupta</p>
                    <p>H.O.D.</p>
                    <p>CS/IT Department</p>
                </td>
            </tr>
        </table>
    </div>
</body></html>
"""

async def generate_pdf():
    with open('synopsis_part1.html', 'w', encoding='utf-8') as f:
        f.write(html_part1)
    with open('synopsis_part2.html', 'w', encoding='utf-8') as f:
        f.write(html_part2)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # Pass 1
        page1 = await browser.new_page()
        await page1.goto(f"file://{os.path.abspath('synopsis_part1.html')}")
        await page1.pdf(
            path="part1.pdf",
            format="A4",
            margin={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
            display_header_footer=False
        )
        await page1.close()
        
        # Pass 2
        page2 = await browser.new_page()
        await page2.goto(f"file://{os.path.abspath('synopsis_part2.html')}")
        await page2.pdf(
            path="part2.pdf",
            format="A4",
            margin={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
            display_header_footer=True,
            header_template="<span></span>",
            footer_template="""
            <div style="width: 100%; font-size: 11pt; text-align: center; font-family: 'Bookman Old Style', serif;">
                <span class="pageNumber"></span>
            </div>
            """
        )
        await page2.close()
        await browser.close()
        
    merged = fitz.open()
    merged.insert_pdf(fitz.open("part1.pdf"))
    merged.insert_pdf(fitz.open("part2.pdf"))
    merged.save("LexAI_Project_Synopsis_Final.pdf")
    merged.close()

if __name__ == "__main__":
    create_docx()
    asyncio.run(generate_pdf())
