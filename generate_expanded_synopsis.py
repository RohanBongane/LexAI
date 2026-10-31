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

def add_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(12)
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
        border.set(qn('w:sz'), '4')  # 0.5 pt thin border
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

    # SECTION 2: Main Content
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
    add_paragraph(doc, "LexAI addresses the aforementioned problems by proposing a secure, decoupled client-server architecture. This model ensures that documents are processed locally into a vector database, and an LLM is strictly constrained via RAG to answer questions based only on the user's uploaded text or the curated Knowledge Base.")
    
    add_heading(doc, "5.1 System Architecture Overview")
    add_paragraph(doc, "The system follows a modular architecture separating the user interface, backend orchestration, data storage, and external AI services. The data flow proceeds as follows:")
    add_paragraph(doc, "User → Web Interface → Flask Backend → Authentication and Document Processing → MySQL / Local File Storage / ChromaDB → Gemini API → Response to User", align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_heading(doc, "5.2 Frontend Application")
    add_paragraph(doc, "The presentation layer is built utilizing HTML5, CSS3, and JavaScript, with Bootstrap 5 ensuring a responsive layout across devices. It handles user authentication forms, document uploads, and asynchronous chat interactions. To securely render AI-generated Markdown responses, the frontend employs marked.js for formatting and DOMPurify to sanitize outputs against Cross-Site Scripting (XSS) vulnerabilities.")
    
    add_heading(doc, "5.3 Backend Processing Layer")
    add_paragraph(doc, "A Python-based Flask application serves as the core backend orchestration layer. It is responsible for routing HTTP requests, managing user sessions, processing uploaded documents, executing retrieval logic, and handling communication with the external Gemini API. This layer acts as a secure intermediary, ensuring that raw data is processed before any AI integration occurs.")
    
    add_heading(doc, "5.4 Relational Database and File Storage")
    add_paragraph(doc, "MySQL, managed via Flask-SQLAlchemy, acts as the primary relational database. It stores securely hashed user credentials, document metadata (such as file paths and upload timestamps), generated executive summaries, and chat conversation histories. Uploaded PDF and DOCX files are stored directly on the local server file system in isolated, user-specific directories.")
    
    add_heading(doc, "5.5 Semantic Vector Storage")
    add_paragraph(doc, "To enable semantic search, extracted document text is processed by a local SentenceTransformers model (all-MiniLM-L6-v2) to generate mathematical embeddings. These vectors, along with document chunk metadata, are indexed in ChromaDB, an open-source embedding database optimized for local RAG pipelines.")
    
    add_heading(doc, "5.6 AI Analysis and RAG Integration")
    add_paragraph(doc, "When a query is made, the retrieved text chunks from ChromaDB are supplied to the Google Gemini API. The API is constrained by structured system prompts to generate contextual answers or executive summaries grounded solely in the provided text. The architecture strictly separates Document-Specific Chat (querying private uploads) from the General Legal Knowledge Base (querying an admin-curated repository).")
    
    add_heading(doc, "5.7 Security and Reliability")
    add_paragraph(doc, "Security is enforced at multiple levels. Authentication relies on Flask-Login and Bcrypt password hashing. ChromaDB queries are explicitly filtered by user ID and document ID to prevent cross-contamination of private data. While these mechanisms aim to minimize unauthorized access and reduce AI hallucinations, the system relies on a deterministic fallback parser to maintain baseline functionality if the external Gemini API becomes temporarily unavailable.")

    doc.add_page_break()

    # 6. Methodology
    add_heading(doc, "6. Methodology")
    add_paragraph(doc, "The operational methodology of LexAI is structured into a chronological processing pipeline, transforming raw document uploads into interactive, semantically searchable data.")
    
    add_heading(doc, "6.1 User Registration and Authentication")
    add_paragraph(doc, "Users initiate their session by registering an account. Passwords are mathematically salted and hashed using the Bcrypt algorithm before database insertion. The Flask-Login extension manages secure, HTTP-only session cookies, verifying user identity during subsequent requests and preventing unauthorized access to protected routes.")
    
    add_heading(doc, "6.2 Document Upload and Validation")
    add_paragraph(doc, "Authenticated users upload legal contracts in PDF or DOCX formats via a secure multipart form. The backend strictly validates the file extension and MIME type to reject malicious payloads. Validated files are saved to the local filesystem within a designated upload directory.")
    
    add_heading(doc, "6.3 Text Extraction")
    add_paragraph(doc, "The system invokes PyMuPDF to parse PDF files and python-docx for Word documents. These libraries extract pure unicode text while discarding visual formatting. Currently, the methodology relies on embedded text layers; scanned, image-based PDFs cannot be fully processed as Optical Character Recognition (OCR) is not yet implemented.")
    
    add_heading(doc, "6.4 Text Preprocessing and Chunking")
    add_paragraph(doc, "Because Large Language Models are constrained by token limits, the extracted text is divided into smaller, manageable chunks. To ensure that continuous legal clauses are not arbitrarily split, the algorithm utilizes overlapping windows (e.g., a short overlap between consecutive chunks). This preserves the semantic context across chunk boundaries.")
    
    add_heading(doc, "6.5 Embedding Generation and Vector Indexing")
    add_paragraph(doc, "Each text chunk is passed through the local all-MiniLM-L6-v2 SentenceTransformers model to generate a high-dimensional mathematical vector. These vectors are ingested into ChromaDB. Crucially, each vector is appended with metadata containing the specific document ID and user ID to ensure strict indexing.")
    
    add_heading(doc, "6.6 Semantic Retrieval")
    add_paragraph(doc, "During a chat interaction, the user's natural language question is converted into an embedding using the identical SentenceTransformers model. ChromaDB performs a cosine similarity search between the question vector and the indexed document chunks. The retrieval is strictly filtered by the authenticated user's ID, returning only the most relevant chunks.")
    
    add_heading(doc, "6.7 AI-Based Document Analysis")
    add_paragraph(doc, "For automated analysis, the retrieved document content is supplied to the Gemini API alongside a restrictive JSON-schema prompt. The prompt instructs the model to extract key clauses, summarize obligations, and identify potential risks based exclusively on the provided text, returning a structured summary for the user dashboard.")
    
    add_heading(doc, "6.8 Document-Specific Chat and General Legal Chat")
    add_paragraph(doc, "The methodology employs two distinct retrieval paths. The Document-Specific Chat filters vector searches exclusively against the user's private uploaded file. Conversely, the General Legal Chat bypasses user documents entirely, querying a separate ChromaDB collection populated only with an administrator-curated Knowledge Base, ensuring private data is never mixed with general inquiries.")
    
    add_heading(doc, "6.9 Fallback and Error Handling")
    add_paragraph(doc, "In the event of a Gemini API outage (e.g., quota limits or network errors), a deterministic Python fallback mechanism is triggered for Knowledge Base queries. This parser bypasses the LLM entirely, retrieving the most relevant raw text chunks from ChromaDB, formatting them into Markdown, and presenting them directly to the user to maintain system availability.")
    
    add_heading(doc, "6.10 Testing and Validation")
    add_paragraph(doc, "System reliability is verified using the Pytest framework. The testing methodology includes unit tests for the authentication flows, ensuring registration validations and login route protections function correctly. Database isolation tests verify that users cannot access records or vectors belonging to other accounts, utilizing separate test databases to prevent corruption of production data.")

    doc.add_page_break()

    # 7. Plan of Work
    add_heading(doc, "7. Plan of Work")
    add_paragraph(doc, "The development of LexAI was executed in sequential phases, prioritizing core infrastructure and security before integrating advanced artificial intelligence components. The structured timeline and outcomes are detailed below.")
    
    # Table creation
    table = doc.add_table(rows=1, cols=5)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    headers = ['Phase', 'Development Activity', 'Tools / Technologies', 'Status', 'Expected Outcome']
    for i, text in enumerate(headers):
        hdr_cells[i].text = text
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                set_font(r, bold=True)
                r.font.size = Pt(10)
                
    phases = [
        ("Phase 1", "Project setup and authentication.", "Flask, MySQL, Bcrypt, Flask-Login", "Implemented", "Secure user accounts and isolated sessions."),
        ("Phase 2", "Document upload and text extraction.", "PyMuPDF, python-docx, werkzeug", "Implemented", "Reliable ingestion of raw text from PDF and DOCX files."),
        ("Phase 3", "AI-powered legal document analysis.", "Google Gemini API, JSON-Schema", "Implemented", "Automated generation of structured executive summaries."),
        ("Phase 4", "RAG pipeline and document chat.", "SentenceTransformers, ChromaDB, AJAX", "Implemented", "Semantic search enabling context-aware chat interaction."),
        ("Phase 5", "Knowledge Base, fallback mechanism, and testing.", "Flask, Pytest, Python Parsers", "Implemented", "Curated legal chat and resilient external API error handling."),
        ("Phase 6", "OCR support for scanned documents.", "Tesseract OCR, Vision APIs", "Future Scope", "Ability to analyze image-based PDFs lacking text layers."),
        ("Phase 7", "Multilingual support or cloud deployment.", "Translation Pipelines, AWS S3", "Future Scope", "Scalable enterprise deployment and broader language accessibility.")
    ]
    
    for row_data in phases:
        row_cells = table.add_row().cells
        for i, text in enumerate(row_data):
            row_cells[i].text = text
            for p in row_cells[i].paragraphs:
                for r in p.runs:
                    set_font(r)
                    r.font.size = Pt(10)

    add_paragraph(doc, "These phases build logically upon one another; foundational authentication and file handling (Phases 1 and 2) were strict prerequisites for the RAG pipeline (Phases 3 and 4). Future enhancements, such as OCR and cloud migration (Phases 6 and 7), will extend the system's capabilities without disrupting the core architecture established in the implemented phases.")

    doc.add_page_break()

    # 8. Conclusion
    add_heading(doc, "8. Conclusion")
    add_paragraph(doc, "The LexAI project successfully addresses the significant accessibility barrier posed by dense legal terminology and lengthy contracts. By developing a secure, web-based platform that automates the extraction and semantic analysis of legal documents, the system provides individuals and small enterprises with a practical tool for preliminary contract review. The integration of local vector indexing with Retrieval-Augmented Generation (RAG) ensures that the artificial intelligence is firmly grounded in the user's actual document, aiming to minimize the likelihood of hallucinatory or inaccurate responses.")
    add_paragraph(doc, "A critical achievement of the project is the robust implementation of two distinct conversational interfaces. The Document-Specific Chat allows users to interrogate their private uploads securely, enforced by strict database-level filtering that isolates user data. Simultaneously, the General Legal Knowledge Base provides access to curated legal concepts without cross-contaminating private records. Furthermore, the inclusion of a deterministic fallback mechanism ensures that the platform maintains baseline functionality and provides uninterrupted access to its curated repository even during external API outages.")
    add_paragraph(doc, "Despite these advancements, LexAI possesses acknowledged limitations. The current text extraction methodology relies on embedded text layers; therefore, scanned or image-based documents cannot be processed, as Optical Character Recognition (OCR) is not yet implemented. Additionally, the system currently lacks multilingual capabilities, and while RAG significantly reduces factual errors, it does not completely eliminate the risk of AI inaccuracy. LexAI is explicitly designed as an informational assistant and does not replace the necessity for qualified legal professionals.")
    add_paragraph(doc, "Future improvements will focus on expanding the platform's accessibility and scalability. The planned integration of OCR will allow for the processing of legacy scanned contracts, while multilingual support would democratize legal comprehension across broader demographics. Ultimately, LexAI represents a functional, verifiable prototype that makes significant practical contributions toward rendering complex legal information transparent and accessible.")

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
        table { width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 10pt; }
        th, td { border: 1px solid black; padding: 6px; text-align: left; }
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
        <p>LexAI addresses the aforementioned problems by proposing a secure, decoupled client-server architecture. This model ensures that documents are processed locally into a vector database, and an LLM is strictly constrained via RAG to answer questions based only on the user's uploaded text or the curated Knowledge Base.</p>
        
        <h3>5.1 System Architecture Overview</h3>
        <p>The system follows a modular architecture separating the user interface, backend orchestration, data storage, and external AI services. The data flow proceeds as follows:</p>
        <p style="text-align: center; font-style: italic;" class="bold">User ➔ Web Interface ➔ Flask Backend ➔ Authentication and Document Processing ➔ MySQL / Local File Storage / ChromaDB ➔ Gemini API ➔ Response to User</p>
        
        <h3>5.2 Frontend Application</h3>
        <p>The presentation layer is built utilizing HTML5, CSS3, and JavaScript, with Bootstrap 5 ensuring a responsive layout across devices. It handles user authentication forms, document uploads, and asynchronous chat interactions. To securely render AI-generated Markdown responses, the frontend employs marked.js for formatting and DOMPurify to sanitize outputs against Cross-Site Scripting (XSS) vulnerabilities.</p>
        
        <h3>5.3 Backend Processing Layer</h3>
        <p>A Python-based Flask application serves as the core backend orchestration layer. It is responsible for routing HTTP requests, managing user sessions, processing uploaded documents, executing retrieval logic, and handling communication with the external Gemini API. This layer acts as a secure intermediary, ensuring that raw data is processed before any AI integration occurs.</p>
        
        <h3>5.4 Relational Database and File Storage</h3>
        <p>MySQL, managed via Flask-SQLAlchemy, acts as the primary relational database. It stores securely hashed user credentials, document metadata (such as file paths and upload timestamps), generated executive summaries, and chat conversation histories. Uploaded PDF and DOCX files are stored directly on the local server file system in isolated, user-specific directories.</p>
        
        <h3>5.5 Semantic Vector Storage</h3>
        <p>To enable semantic search, extracted document text is processed by a local SentenceTransformers model (all-MiniLM-L6-v2) to generate mathematical embeddings. These vectors, along with document chunk metadata, are indexed in ChromaDB, an open-source embedding database optimized for local RAG pipelines.</p>
        
        <h3>5.6 AI Analysis and RAG Integration</h3>
        <p>When a query is made, the retrieved text chunks from ChromaDB are supplied to the Google Gemini API. The API is constrained by structured system prompts to generate contextual answers or executive summaries grounded solely in the provided text. The architecture strictly separates Document-Specific Chat (querying private uploads) from the General Legal Knowledge Base (querying an admin-curated repository).</p>
        
        <h3>5.7 Security and Reliability</h3>
        <p>Security is enforced at multiple levels. Authentication relies on Flask-Login and Bcrypt password hashing. ChromaDB queries are explicitly filtered by user ID and document ID to prevent cross-contamination of private data. While these mechanisms aim to minimize unauthorized access and reduce AI hallucinations, the system relies on a deterministic fallback parser to maintain baseline functionality if the external Gemini API becomes temporarily unavailable.</p>
    </div>

    <div class="main-section">
        <h2>6. Methodology</h2>
        <p>The operational methodology of LexAI is structured into a chronological processing pipeline, transforming raw document uploads into interactive, semantically searchable data.</p>
        
        <h3>6.1 User Registration and Authentication</h3>
        <p>Users initiate their session by registering an account. Passwords are mathematically salted and hashed using the Bcrypt algorithm before database insertion. The Flask-Login extension manages secure, HTTP-only session cookies, verifying user identity during subsequent requests and preventing unauthorized access to protected routes.</p>
        
        <h3>6.2 Document Upload and Validation</h3>
        <p>Authenticated users upload legal contracts in PDF or DOCX formats via a secure multipart form. The backend strictly validates the file extension and MIME type to reject malicious payloads. Validated files are saved to the local filesystem within a designated upload directory.</p>
        
        <h3>6.3 Text Extraction</h3>
        <p>The system invokes PyMuPDF to parse PDF files and python-docx for Word documents. These libraries extract pure unicode text while discarding visual formatting. Currently, the methodology relies on embedded text layers; scanned, image-based PDFs cannot be fully processed as Optical Character Recognition (OCR) is not yet implemented.</p>
        
        <h3>6.4 Text Preprocessing and Chunking</h3>
        <p>Because Large Language Models are constrained by token limits, the extracted text is divided into smaller, manageable chunks. To ensure that continuous legal clauses are not arbitrarily split, the algorithm utilizes overlapping windows (e.g., a short overlap between consecutive chunks). This preserves the semantic context across chunk boundaries.</p>
        
        <h3>6.5 Embedding Generation and Vector Indexing</h3>
        <p>Each text chunk is passed through the local all-MiniLM-L6-v2 SentenceTransformers model to generate a high-dimensional mathematical vector. These vectors are ingested into ChromaDB. Crucially, each vector is appended with metadata containing the specific document ID and user ID to ensure strict indexing.</p>
        
        <h3>6.6 Semantic Retrieval</h3>
        <p>During a chat interaction, the user's natural language question is converted into an embedding using the identical SentenceTransformers model. ChromaDB performs a cosine similarity search between the question vector and the indexed document chunks. The retrieval is strictly filtered by the authenticated user's ID, returning only the most relevant chunks.</p>
        
        <h3>6.7 AI-Based Document Analysis</h3>
        <p>For automated analysis, the retrieved document content is supplied to the Gemini API alongside a restrictive JSON-schema prompt. The prompt instructs the model to extract key clauses, summarize obligations, and identify potential risks based exclusively on the provided text, returning a structured summary for the user dashboard.</p>
        
        <h3>6.8 Document-Specific Chat and General Legal Chat</h3>
        <p>The methodology employs two distinct retrieval paths. The Document-Specific Chat filters vector searches exclusively against the user's private uploaded file. Conversely, the General Legal Chat bypasses user documents entirely, querying a separate ChromaDB collection populated only with an administrator-curated Knowledge Base, ensuring private data is never mixed with general inquiries.</p>
        
        <h3>6.9 Fallback and Error Handling</h3>
        <p>In the event of a Gemini API outage (e.g., quota limits or network errors), a deterministic Python fallback mechanism is triggered for Knowledge Base queries. This parser bypasses the LLM entirely, retrieving the most relevant raw text chunks from ChromaDB, formatting them into Markdown, and presenting them directly to the user to maintain system availability.</p>
        
        <h3>6.10 Testing and Validation</h3>
        <p>System reliability is verified using the Pytest framework. The testing methodology includes unit tests for the authentication flows, ensuring registration validations and login route protections function correctly. Database isolation tests verify that users cannot access records or vectors belonging to other accounts, utilizing separate test databases to prevent corruption of production data.</p>
    </div>

    <div class="main-section">
        <h2>7. Plan of Work</h2>
        <p>The development of LexAI was executed in sequential phases, prioritizing core infrastructure and security before integrating advanced artificial intelligence components. The structured timeline and outcomes are detailed below.</p>
        
        <table>
            <tr>
                <th>Phase</th>
                <th>Development Activity</th>
                <th>Tools / Technologies</th>
                <th>Status</th>
                <th>Expected Outcome</th>
            </tr>
            <tr>
                <td>Phase 1</td>
                <td>Project setup and authentication.</td>
                <td>Flask, MySQL, Bcrypt, Flask-Login</td>
                <td>Implemented</td>
                <td>Secure user accounts and isolated sessions.</td>
            </tr>
            <tr>
                <td>Phase 2</td>
                <td>Document upload and text extraction.</td>
                <td>PyMuPDF, python-docx, werkzeug</td>
                <td>Implemented</td>
                <td>Reliable ingestion of raw text from PDF and DOCX files.</td>
            </tr>
            <tr>
                <td>Phase 3</td>
                <td>AI-powered legal document analysis.</td>
                <td>Google Gemini API, JSON-Schema</td>
                <td>Implemented</td>
                <td>Automated generation of structured executive summaries.</td>
            </tr>
            <tr>
                <td>Phase 4</td>
                <td>RAG pipeline and document chat.</td>
                <td>SentenceTransformers, ChromaDB, AJAX</td>
                <td>Implemented</td>
                <td>Semantic search enabling context-aware chat interaction.</td>
            </tr>
            <tr>
                <td>Phase 5</td>
                <td>Knowledge Base, fallback mechanism, and testing.</td>
                <td>Flask, Pytest, Python Parsers</td>
                <td>Implemented</td>
                <td>Curated legal chat and resilient external API error handling.</td>
            </tr>
            <tr>
                <td>Phase 6</td>
                <td>OCR support for scanned documents.</td>
                <td>Tesseract OCR, Vision APIs</td>
                <td>Future Scope</td>
                <td>Ability to analyze image-based PDFs lacking text layers.</td>
            </tr>
            <tr>
                <td>Phase 7</td>
                <td>Multilingual support or cloud deployment.</td>
                <td>Translation Pipelines, AWS S3</td>
                <td>Future Scope</td>
                <td>Scalable enterprise deployment and broader language accessibility.</td>
            </tr>
        </table>
        
        <p>These phases build logically upon one another; foundational authentication and file handling (Phases 1 and 2) were strict prerequisites for the RAG pipeline (Phases 3 and 4). Future enhancements, such as OCR and cloud migration (Phases 6 and 7), will extend the system's capabilities without disrupting the core architecture established in the implemented phases.</p>
    </div>

    <div class="main-section">
        <h2>8. Conclusion</h2>
        <p>The LexAI project successfully addresses the significant accessibility barrier posed by dense legal terminology and lengthy contracts. By developing a secure, web-based platform that automates the extraction and semantic analysis of legal documents, the system provides individuals and small enterprises with a practical tool for preliminary contract review. The integration of local vector indexing with Retrieval-Augmented Generation (RAG) ensures that the artificial intelligence is firmly grounded in the user's actual document, aiming to minimize the likelihood of hallucinatory or inaccurate responses.</p>
        <p>A critical achievement of the project is the robust implementation of two distinct conversational interfaces. The Document-Specific Chat allows users to interrogate their private uploads securely, enforced by strict database-level filtering that isolates user data. Simultaneously, the General Legal Knowledge Base provides access to curated legal concepts without cross-contaminating private records. Furthermore, the inclusion of a deterministic fallback mechanism ensures that the platform maintains baseline functionality and provides uninterrupted access to its curated repository even during external API outages.</p>
        <p>Despite these advancements, LexAI possesses acknowledged limitations. The current text extraction methodology relies on embedded text layers; therefore, scanned or image-based documents cannot be processed, as Optical Character Recognition (OCR) is not yet implemented. Additionally, the system currently lacks multilingual capabilities, and while RAG significantly reduces factual errors, it does not completely eliminate the risk of AI inaccuracy. LexAI is explicitly designed as an informational assistant and does not replace the necessity for qualified legal professionals.</p>
        <p>Future improvements will focus on expanding the platform's accessibility and scalability. The planned integration of OCR will allow for the processing of legacy scanned contracts, while multilingual support would democratize legal comprehension across broader demographics. Ultimately, LexAI represents a functional, verifiable prototype that makes significant practical contributions toward rendering complex legal information transparent and accessible.</p>
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
