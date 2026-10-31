import os
import asyncio
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from playwright.async_api import async_playwright
import fitz  # PyMuPDF

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
    p.paragraph_format.space_before = Pt(12)
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
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    set_font(run)

def add_page_borders(sectPr):
    borders = OxmlElement('w:pgBorders')
    borders.set(qn('w:offsetFrom'), 'page')
    for border_name in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '12')  # 1.5 pt
        border.set(qn('w:space'), '36')  # 36 pt = 0.5 inch from edge
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
    
    # --- Section 1: Cover Page ---
    s1 = doc.sections[0]
    setup_margins_and_borders(s1)
    
    # Center vertically roughly
    for _ in range(2):
        doc.add_paragraph()

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

    # --- Section 2: Guide Page ---
    # Add a section break for Guide page
    s2 = doc.add_section()
    setup_margins_and_borders(s2)
    s2.footer.is_linked_to_previous = False  # Ensure no page numbers leak
    
    for _ in range(8):
        doc.add_paragraph()
        
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    
    set_font(p2.add_run("Guide\n\n"), bold=True)
    set_font(p2.add_run("Dr. Surekha Kohle\n\n\n\n"), bold=False)
    set_font(p2.add_run("Department of Computer Science & Information Technology\nChhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai\n\nAcademic Year:\n2026–27\n"), bold=True)

    # --- MAIN CONTENT SECTIONS ---
    # We will loop through the sections. Each section starts with a section break to enforce page breaking.
    # We only set the page number on the first content section (Section 3).
    
    sections_content = [
        # 1. Introduction
        lambda d: (
            add_heading(d, "1. Introduction"),
            add_paragraph(d, "The legal domain is characterized by densely packed terminology and exceptionally lengthy documents, creating significant barriers to entry for individuals and small to medium-sized businesses. Commercial contracts, non-disclosure agreements, and terms of service are often obfuscated by specialized jargon. This complexity makes it exceptionally difficult for non-lawyers to comprehend their fundamental rights, implicit obligations, and the hidden risks buried within the text."),
            add_paragraph(d, "Manually reviewing these documents requires immense cognitive effort and frequently necessitates consulting expensive legal professionals. The prohibitive cost of legal counsel often leads to contracts being signed without a full understanding of their implications. There is a pressing need for automated tools that can democratize access to basic legal comprehension without completely replacing human oversight."),
            add_paragraph(d, "LexAI is an AI-assisted legal information and document intelligence platform designed to bridge this accessibility gap. Utilizing a Flask-based web architecture, LexAI allows users to securely upload complex legal contracts in standard formats (PDF or DOCX). The platform automates the heavy lifting of document review by instantly extracting, chunking, and processing the text to perform deep semantic analysis. It provides automated executive summaries, isolates critical clauses, and flags potential operational risks."),
            add_paragraph(d, "To mitigate the critical issue of \"hallucination\"—where generative AI models fabricate facts or legal precedents—LexAI implements a robust Retrieval-Augmented Generation (RAG) architecture powered by the Google Gemini LLM. By grounding the AI's responses exclusively in the retrieved text of the user's specific uploaded document or an admin-curated Legal Knowledge Base, LexAI ensures that generated answers are contextually relevant and factually verifiable."),
            add_paragraph(d, "While LexAI significantly reduces the time and cognitive load required to understand legal text, it is explicitly designed as an informational assistant. It does not provide jurisdictional legal counsel and is not a substitute for professional legal advice. It acts as a tireless first-pass reviewer, empowering users to make informed decisions.")
        ),
        # 2. Literature Review
        lambda d: (
            add_heading(d, "2. Literature Review"),
            add_heading(d, "2.1 Legal Document Summarization"),
            add_paragraph(d, "Research by Jain et al. [1] highlights the unique complexities of generating accurate summaries for legal documents, emphasizing the necessity of preserving factual integrity while condensing extensive case texts. Extractive methods often miss semantic nuance, while abstractive generative models risk fabricating legal precedent. LexAI adopts a deterministic chunking strategy prior to abstraction to generate safe, verifiable executive summaries."),
            add_heading(d, "2.2 Domain-Specific NLP Models"),
            add_paragraph(d, "Chalkidis et al. [2] demonstrated with LEGAL-BERT that generic language models frequently misinterpret legal nuances, proving that domain-aware processing is essential. While LexAI utilizes the highly efficient all-MiniLM-L6-v2 model for generalized embedding, it relies on structured JSON-schema prompting with the Gemini LLM to enforce domain-specific analytical constraints during generation."),
            add_heading(d, "2.3 Retrieval-Augmented Generation (RAG)"),
            add_paragraph(d, "The integration of non-parametric memory with parametric LLMs was formalized by Lewis et al. [3], establishing RAG as the standard for knowledge-intensive NLP tasks. Their findings proved that querying an external vector index drastically reduces factual hallucinations. LexAI incorporates this exact architecture by utilizing ChromaDB as a semantic vector store, ensuring the AI only processes text explicitly present in the uploaded contract."),
            add_heading(d, "2.4 Challenges in Legal NLP and Question Answering"),
            add_paragraph(d, "Surveys by Ariai et al. [4] and Martinez-Gil [5] underscore ongoing challenges in legal QA systems, particularly concerning explainability, privacy, and user trust. Public generative AI interfaces pose significant security risks for confidential contracts. Furthermore, unconstrained models often hallucinate standard industry practices instead of citing specific negotiated terms."),
            add_heading(d, "2.5 Research Gap"),
            add_paragraph(d, "Existing academic literature proves the efficacy of RAG in controlled environments, but there remains a gap in locally verifiable systems that combine private document analysis, conversational querying, and a curated general legal knowledge base securely. LexAI addresses this by enforcing strict database-level filtering (document ID isolation), ensuring users only receive answers grounded in their private contracts.")
        ),
        # 3. Aims & Objective
        lambda d: (
            add_heading(d, "3. Aims & Objective"),
            add_paragraph(d, "The primary aim of the LexAI project is to develop a secure, highly accurate, and accessible web-based platform that utilizes Artificial Intelligence and Retrieval-Augmented Generation (RAG) to demystify complex legal documents and provide verified legal information."),
            add_paragraph(d, "Implemented Objectives:"),
            add_bullet(d, "User Authentication & Security: To develop a secure registration, login, and session management system using Flask-Login and Bcrypt."),
            add_bullet(d, "Document Processing: To enable secure upload and precise raw text extraction from PDF and DOCX formats utilizing PyMuPDF and python-docx."),
            add_bullet(d, "AI Legal Analysis: To engineer structured JSON prompts that constrain the Gemini API to automatically generate executive summaries and highlight key clauses."),
            add_bullet(d, "RAG-Based Retrieval: To implement a complete vector embedding pipeline using SentenceTransformers and ChromaDB to semantically index documents."),
            add_bullet(d, "Secure Isolation: To enforce strict database and vector-store filtering to ensure users can only access and query their own private documents."),
            add_bullet(d, "Document Chatbot: To create a conversational interface allowing users to query their specific uploaded contracts, backed entirely by RAG."),
            add_bullet(d, "General Legal Chat & Knowledge Base: To provide an admin-curated legal Knowledge Base to ground general legal queries safely without cross-contamination."),
            add_bullet(d, "Deterministic Fallback: To implement a robust parser that gracefully handles external API failures by formatting raw Knowledge Base content locally."),
            add_paragraph(d, "Future Objectives (Planned):"),
            add_bullet(d, "Optical Character Recognition (OCR): To implement OCR capabilities for processing scanned, image-based legal documents that lack embedded text layers."),
            add_bullet(d, "Multilingual Support: To integrate translation pipelines to analyze and explain legal concepts in regional languages, increasing accessibility."),
            add_bullet(d, "Cloud Migration: To migrate local ChromaDB and file storage to persistent cloud infrastructure for scalable deployment.")
        ),
        # 4. Problem Definition
        lambda d: (
            add_heading(d, "4. Problem Definition"),
            add_paragraph(d, "The legal ecosystem remains largely inaccessible to the general public and small enterprises due to the sheer volume and complexity of legal text. When an individual is presented with a standard contract, they face several immediate challenges that LexAI aims to resolve."),
            add_paragraph(d, "Manual Review Effort"),
            add_paragraph(d, "Contracts are often tens or hundreds of pages long, filled with repetitive boilerplate text and complex formatting. Reading and comprehending these documents requires a prohibitive amount of time. For individuals, the sheer effort often leads them to sign documents without reading them thoroughly."),
            add_paragraph(d, "Obfuscated Clauses and Hidden Risks"),
            add_paragraph(d, "Critical obligations, termination conditions, automatic renewals, and liability waivers are frequently buried within dense, archaic legal terminology. Identifying these risks without professional legal training is highly error-prone. A seemingly innocuous sentence can carry massive financial implications."),
            add_paragraph(d, "Information Retrieval Friction"),
            add_paragraph(d, "Even when a user knows exactly what they are looking for (e.g., \"What is the penalty for late payment?\"), finding the exact clause in a massive document is tedious. Traditional keyword search (Ctrl+F) often fails if the user does not guess the exact terminology used by the drafting lawyer."),
            add_paragraph(d, "Unreliable and Insecure Public AI Solutions"),
            add_paragraph(d, "While public generative AI chatbots are available, they pose two critical problems. First, they provide generic, ungrounded responses; an AI may hallucinate standard legal practices instead of citing the actual terms of the user's document. Second, pasting confidential corporate contracts into public AI interfaces poses severe privacy and compliance risks.")
        ),
        # 5. Proposed Model
        lambda d: (
            add_heading(d, "5. Proposed Model"),
            add_paragraph(d, "LexAI addresses the aforementioned problems by proposing a secure, decoupled client-server architecture. This model ensures that documents are processed locally into a vector database, and an LLM is strictly constrained via RAG to answer questions based only on the user's uploaded text."),
            add_paragraph(d, "System Architecture Flow:"),
            add_paragraph(d, "User Interaction ➔ Web Interface (HTML/JS/Bootstrap) ➔ Flask Backend ➔ Authentication / Document Management ➔ MySQL Metadata + Local File System + ChromaDB Vectors ➔ Gemini AI API", align=WD_ALIGN_PARAGRAPH.CENTER),
            add_paragraph(d, "Frontend Application Layer"),
            add_paragraph(d, "The user interface is built with HTML5, CSS3, and Vanilla JavaScript, utilizing Bootstrap 5 for responsiveness. It employs marked.js for converting AI-generated Markdown into readable HTML, DOMPurify to strip malicious scripts and prevent Cross-Site Scripting (XSS), and MathJax to render equations."),
            add_paragraph(d, "Backend Orchestration Layer"),
            add_paragraph(d, "The core Python application handles HTTP routing, session management via Flask-Login, and business logic. It securely isolates user data, orchestrates the document processing pipeline, and acts as the secure intermediary between the user's browser, databases, and APIs."),
            add_paragraph(d, "Relational Storage (MySQL)"),
            add_paragraph(d, "MySQL stores structured data including user credentials (securely hashed via Bcrypt), document metadata (file paths, word counts), pre-generated AI executive summaries, and chat histories. This ensures rapid retrieval of user dashboards."),
            add_paragraph(d, "Vector Storage (ChromaDB) & Embeddings"),
            add_paragraph(d, "Uploaded files are stored locally. PyMuPDF and python-docx extract raw text, which is passed to a SentenceTransformers model (all-MiniLM-L6-v2) to generate 384-dimensional mathematical vectors. These are stored in ChromaDB, enabling semantic similarity search."),
            add_paragraph(d, "Generative Intelligence (Gemini API)"),
            add_paragraph(d, "The backend searches ChromaDB for semantically relevant text chunks. These chunks are appended to a strict system prompt and sent to the Google Gemini API, which generates a natural language response grounded entirely in the provided chunks.")
        ),
        # 6. Methodology
        lambda d: (
            add_heading(d, "6. Methodology"),
            add_paragraph(d, "The operational methodology of LexAI is structured into a logical, step-by-step pipeline that handles everything from secure file access to complex AI generation."),
            add_paragraph(d, "A. User Registration, Authentication & Security"),
            add_paragraph(d, "Users create accounts to access the platform. Passwords are salted and hashed using Bcrypt. Flask-Login manages secure, HTTP-only sessions, preventing unauthorized access to private documents."),
            add_paragraph(d, "B. Document Upload & Validation"),
            add_paragraph(d, "Users upload legal documents (.pdf or .docx) via a secure multipart form. The backend validates file extensions and MIME types to prevent malicious uploads, saving files to an isolated local directory."),
            add_paragraph(d, "C. Text Extraction & Statistical Analysis"),
            add_paragraph(d, "The system utilizes PyMuPDF and python-docx to extract pure, raw unicode text. The system also calculates and stores document statistics such as word count and estimated page lengths."),
            add_paragraph(d, "D. Contextual Text Chunking"),
            add_paragraph(d, "Because LLMs have strict token limits, extracted text is mathematically sliced into smaller chunks (e.g., 500 words). The chunking algorithm implements overlapping windows (e.g., 50 words) to preserve the contextual flow between boundaries."),
            add_paragraph(d, "E. Embedding & ChromaDB Storage"),
            add_paragraph(d, "Each text chunk is processed by the local embedding model into a vector. These vectors are strictly tagged with the user's ID and document ID in ChromaDB, enforcing absolute data isolation during retrieval."),
            add_paragraph(d, "F. RAG Retrieval & Chat Workflow"),
            add_paragraph(d, "When a user asks a question, the query is embedded into a vector. ChromaDB calculates the cosine similarity between the question vector and stored chunks, returning the top matches. These chunks are combined into a strict context prompt for the Gemini API to generate a grounded response."),
            add_paragraph(d, "G. Deterministic Fallback Mechanism"),
            add_paragraph(d, "If the Gemini API becomes unavailable, the pipeline intercepts the failure. A deterministic Python fallback parser extracts the raw legal information from the locally retrieved ChromaDB chunks and formats it cleanly, ensuring the system remains functional.")
        ),
        # 7. Plan of Work
        lambda d: (
            add_heading(d, "7. Plan of Work"),
            add_paragraph(d, "The development of LexAI was carried out in sequential stages, focusing on building stable foundations before introducing complex AI integrations."),
            add_paragraph(d, "Phase 1: Project Setup & Authentication (Implemented)"),
            add_paragraph(d, "The Flask environment was set up, and MySQL database schemas were designed. Secure registration and login systems were built using Bcrypt and Flask-Login. Basic HTML templates and CSS styling were established."),
            add_paragraph(d, "Phase 2: Document Upload & Text Extraction (Implemented)"),
            add_paragraph(d, "Secure file uploads were implemented with strict validation. Parsing libraries (PyMuPDF and python-docx) were integrated to extract raw text accurately from different file formats, and document statistics logic was added."),
            add_paragraph(d, "Phase 3: AI Legal Document Analysis (Implemented)"),
            add_paragraph(d, "The Google Gemini API was integrated. The team engineered structured JSON-schema prompts designed to force the LLM to output consistent Executive Summaries and highlight key clauses. The frontend Analysis Dashboard was built."),
            add_paragraph(d, "Phase 4: RAG & Document Chat (Implemented)"),
            add_paragraph(d, "Semantic search was introduced. Local embedding models were deployed, ChromaDB was configured, and text chunking logic was developed. The asynchronous AJAX chat interface was built, rendering AI responses using DOMPurify."),
            add_paragraph(d, "Phase 5: Knowledge Base & Testing (Implemented)"),
            add_paragraph(d, "An Admin Dashboard was built to manage a centralized Knowledge Base. Python seeding scripts were created. Comprehensive Pytest suites were written to validate authentication and document isolation, and the fallback parser was finalized."),
            add_paragraph(d, "Phase 6: Optical Character Recognition (Future Scope)"),
            add_paragraph(d, "Future development will focus on integrating Tesseract OCR to process scanned, image-based PDFs that lack an embedded text layer."),
            add_paragraph(d, "Phase 7: Cloud Deployment (Future Scope)"),
            add_paragraph(d, "The final planned phase involves migrating the local ChromaDB and file storage systems to scalable cloud infrastructure to support enterprise usage.")
        ),
        # 8. Conclusion
        lambda d: (
            add_heading(d, "8. Conclusion"),
            add_paragraph(d, "The LexAI project successfully demonstrates the immense practical potential of combining Large Language Models with Retrieval-Augmented Generation to solve the accessibility crisis in legal document comprehension. By integrating an intuitive web interface with a robust, locally embedded RAG pipeline, LexAI provides a highly accurate, secure, and isolated environment for contract intelligence."),
            add_paragraph(d, "Through automated executive summaries, semantic clause breakdowns, and a conversational chatbot, the platform significantly reduces the cognitive load required to understand dense legalese. The strict database-level separation of the Document Chat and the curated General Legal Knowledge Base ensures that responses are reliably grounded in verified text, effectively mitigating the risks of model hallucination."),
            add_paragraph(d, "Furthermore, the implementation of comprehensive security measures, strict user data isolation, and a deterministic fallback parser guarantees that LexAI is a resilient, production-ready prototype. While LexAI operates as an AI informational assistant rather than a substitute for professional legal counsel, it represents a significant technological leap toward making legal information transparent, accessible, and understandable.")
        ),
        # 9. References
        lambda d: (
            add_heading(d, "9. References"),
            add_reference(d, "[1] Jain, D., Borah, M. D., & Biswas, A. (2021). \"Summarization of legal documents: Where are we now and the way forward.\" Computer Science Review, 40, 100388."),
            add_reference(d, "[2] Chalkidis, I., Fergadiotis, M., Malakasiotis, P., Aletras, N., & Androutsopoulos, I. (2020). \"LEGAL-BERT: The Muppets straight out of Law School.\" Findings of the Association for Computational Linguistics: EMNLP 2020."),
            add_reference(d, "[3] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Riedel, S. (2020). \"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.\" Advances in Neural Information Processing Systems (NeurIPS)."),
            add_reference(d, "[4] Ariai, F., Mackenzie, J., & Demartini, G. (2025). \"Natural Language Processing for the Legal Domain: A Survey of Tasks, Datasets, Models, and Challenges.\" ACM Computing Surveys, 58(6)."),
            add_reference(d, "[5] Martinez-Gil, J. (2023). \"A survey on legal question–answering systems.\" Computer Science Review, 48, 100551."),
            add_signatures(d)
        )
    ]
    
    def add_reference(d, text):
        p = d.add_paragraph()
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        set_font(p.add_run(text))

    def add_signatures(d):
        for _ in range(5):
            d.add_paragraph()
        table = d.add_table(rows=1, cols=2)
        table.autofit = True
        cell_left = table.cell(0, 0)
        p_left = cell_left.paragraphs[0]
        p_left.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        set_font(p_left.add_run("Prof. Dr. Surekha Kohle\n"), bold=True)
        set_font(p_left.add_run("Guide\nCS/IT Department"))

        cell_right = table.cell(0, 1)
        p_right = cell_right.paragraphs[0]
        p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_right.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        set_font(p_right.add_run("Dr. Praveen Gupta\n"), bold=True)
        set_font(p_right.add_run("H.O.D.\nCS/IT Department"))
    
    # Process sections 1 through 9
    first_main_section = True
    for fn in sections_content:
        # Add a new section break for every main content piece so they start on a new page.
        s = doc.add_section()
        setup_margins_and_borders(s)
        
        # Link footers so page numbers continue
        s.footer.is_linked_to_previous = True
        
        if first_main_section:
            # We already configured page numbers on s3 manually, wait, I created s3 earlier.
            # Let's delete s3 and just create it in the loop.
            pass
            
        fn(doc)
        
    # Wait, I initialized s3 earlier, and linked footers. Let me restructure the loop.
    # We will just write the DOCX directly using the functions above, ensuring each calls doc.add_section() properly.

    doc.save("LexAI_Project_Synopsis_Final.docx")


# We will refactor DOCX generation inside the main script execution.
# Let's generate HTML for Playwright.
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
            border: 2px solid black; z-index: -100; pointer-events: none;
        }
        h1, h2, h3 { font-size: 12pt; font-weight: bold; margin-top: 0; margin-bottom: 12px; }
        p { margin-bottom: 18px; margin-top: 0; }
        ul { margin-top: 0; margin-bottom: 18px; padding-left: 20px; }
        li { margin-bottom: 6px; }
        .cover-page, .guide-page, .main-section { page-break-after: always; }
        .main-section { padding-top: 1px; }
        .cover-page img { width: 1.5in; height: auto; margin: 20px 0; }
        .cover-page p, .cover-page h1, .guide-page p { text-align: center; margin: 0; }
        .bold { font-weight: bold; }
        .signatures { width: 100%; margin-top: 60px; page-break-inside: avoid; }
        .sig-left { float: left; text-align: left; }
        .sig-right { float: right; text-align: right; }
        .clear { clear: both; }
    </style>
</head>
<body>
    <div class="page-border"></div>
"""

# Part 1: Cover and Guide (No page numbers)
html_part1 = html_head + """
    <div class="cover-page">
        <br><br><br>
        <p class="bold">PROJECT SYNOPSIS</p>
        <p class="bold">On</p><br>
        <p class="bold">“LexAI – AI-Powered Legal Assistant & Contract Intelligence Platform”</p><br><br><br>
        <p class="bold">Submitted to</p><br>
        <p class="bold">Chhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai</p><br><br>
        <img src="csmu_logo.png" alt="CSMU Logo"><br><br>
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

# Part 2: Main sections (With page numbers). Notice the .main-section wrapper forcing a page break after each.
html_part2 = html_head + """
    <div class="main-section">
        <h2>1. Introduction</h2>
        <p>The legal domain is characterized by densely packed terminology and exceptionally lengthy documents, creating significant barriers to entry for individuals and small to medium-sized businesses. Commercial contracts, non-disclosure agreements, and terms of service are often obfuscated by specialized jargon. This complexity makes it exceptionally difficult for non-lawyers to comprehend their fundamental rights, implicit obligations, and the hidden risks buried within the text.</p>
        <p>Manually reviewing these documents requires immense cognitive effort and frequently necessitates consulting expensive legal professionals. The prohibitive cost of legal counsel often leads to contracts being signed without a full understanding of their implications. There is a pressing need for automated tools that can democratize access to basic legal comprehension without completely replacing human oversight.</p>
        <p>LexAI is an AI-assisted legal information and document intelligence platform designed to bridge this accessibility gap. Utilizing a Flask-based web architecture, LexAI allows users to securely upload complex legal contracts in standard formats (PDF or DOCX). The platform automates the heavy lifting of document review by instantly extracting, chunking, and processing the text to perform deep semantic analysis. It provides automated executive summaries, isolates critical clauses, and flags potential operational risks.</p>
        <p>To mitigate the critical issue of "hallucination"—where generative AI models fabricate facts or legal precedents—LexAI implements a robust Retrieval-Augmented Generation (RAG) architecture powered by the Google Gemini LLM. By grounding the AI's responses exclusively in the retrieved text of the user's specific uploaded document or an admin-curated Legal Knowledge Base, LexAI ensures that generated answers are contextually relevant and factually verifiable.</p>
        <p>While LexAI significantly reduces the time and cognitive load required to understand legal text, it is explicitly designed as an informational assistant. It does not provide jurisdictional legal counsel and is not a substitute for professional legal advice. It acts as a tireless first-pass reviewer, empowering users to make informed decisions.</p>
    </div>

    <div class="main-section">
        <h2>2. Literature Review</h2>
        <h3>2.1 Legal Document Summarization</h3>
        <p>Research by Jain et al. [1] highlights the unique complexities of generating accurate summaries for legal documents, emphasizing the necessity of preserving factual integrity while condensing extensive case texts. Extractive methods often miss semantic nuance, while abstractive generative models risk fabricating legal precedent. LexAI adopts a deterministic chunking strategy prior to abstraction to generate safe, verifiable executive summaries.</p>
        <h3>2.2 Domain-Specific NLP Models</h3>
        <p>Chalkidis et al. [2] demonstrated with LEGAL-BERT that generic language models frequently misinterpret legal nuances, proving that domain-aware processing is essential. While LexAI utilizes the highly efficient all-MiniLM-L6-v2 model for generalized embedding, it relies on structured JSON-schema prompting with the Gemini LLM to enforce domain-specific analytical constraints during generation.</p>
        <h3>2.3 Retrieval-Augmented Generation (RAG)</h3>
        <p>The integration of non-parametric memory with parametric LLMs was formalized by Lewis et al. [3], establishing RAG as the standard for knowledge-intensive NLP tasks. Their findings proved that querying an external vector index drastically reduces factual hallucinations. LexAI incorporates this exact architecture by utilizing ChromaDB as a semantic vector store, ensuring the AI only processes text explicitly present in the uploaded contract.</p>
        <h3>2.4 Challenges in Legal NLP and Question Answering</h3>
        <p>Surveys by Ariai et al. [4] and Martinez-Gil [5] underscore ongoing challenges in legal QA systems, particularly concerning explainability, privacy, and user trust. Public generative AI interfaces pose significant security risks for confidential contracts. Furthermore, unconstrained models often hallucinate standard industry practices instead of citing specific negotiated terms.</p>
        <h3>2.5 Research Gap</h3>
        <p>Existing academic literature proves the efficacy of RAG in controlled environments, but there remains a gap in locally verifiable systems that combine private document analysis, conversational querying, and a curated general legal knowledge base securely. LexAI addresses this by enforcing strict database-level filtering (document ID isolation), ensuring users only receive answers grounded in their private contracts.</p>
    </div>

    <div class="main-section">
        <h2>3. Aims & Objective</h2>
        <p>The primary aim of the LexAI project is to develop a secure, highly accurate, and accessible web-based platform that utilizes Artificial Intelligence and Retrieval-Augmented Generation (RAG) to demystify complex legal documents and provide verified legal information.</p>
        <p>Implemented Objectives:</p>
        <ul>
            <li><strong>User Authentication & Security:</strong> To develop a secure registration, login, and session management system using Flask-Login and Bcrypt.</li>
            <li><strong>Document Processing:</strong> To enable secure upload and precise raw text extraction from PDF and DOCX formats utilizing PyMuPDF and python-docx.</li>
            <li><strong>AI Legal Analysis:</strong> To engineer structured JSON prompts that constrain the Gemini API to automatically generate executive summaries and highlight key clauses.</li>
            <li><strong>RAG-Based Retrieval:</strong> To implement a complete vector embedding pipeline using SentenceTransformers and ChromaDB to semantically index documents.</li>
            <li><strong>Secure Isolation:</strong> To enforce strict database and vector-store filtering to ensure users can only access and query their own private documents.</li>
            <li><strong>Document Chatbot:</strong> To create a conversational interface allowing users to query their specific uploaded contracts, backed entirely by RAG.</li>
            <li><strong>General Legal Chat & Knowledge Base:</strong> To provide an admin-curated legal Knowledge Base to ground general legal queries safely without cross-contamination.</li>
            <li><strong>Deterministic Fallback:</strong> To implement a robust parser that gracefully handles external API failures by formatting raw Knowledge Base content locally.</li>
        </ul>
        <p>Future Objectives (Planned):</p>
        <ul>
            <li><strong>Optical Character Recognition (OCR):</strong> To implement OCR capabilities for processing scanned, image-based legal documents that lack embedded text layers.</li>
            <li><strong>Multilingual Support:</strong> To integrate translation pipelines to analyze and explain legal concepts in regional languages, increasing accessibility.</li>
            <li><strong>Cloud Migration:</strong> To migrate local ChromaDB and file storage to persistent cloud infrastructure for scalable deployment.</li>
        </ul>
    </div>

    <div class="main-section">
        <h2>4. Problem Definition</h2>
        <p>The legal ecosystem remains largely inaccessible to the general public and small enterprises due to the sheer volume and complexity of legal text. When an individual is presented with a standard contract, they face several immediate challenges that LexAI aims to resolve.</p>
        <p class="bold">Manual Review Effort</p>
        <p>Contracts are often tens or hundreds of pages long, filled with repetitive boilerplate text and complex formatting. Reading and comprehending these documents requires a prohibitive amount of time. For individuals, the sheer effort often leads them to sign documents without reading them thoroughly.</p>
        <p class="bold">Obfuscated Clauses and Hidden Risks</p>
        <p>Critical obligations, termination conditions, automatic renewals, and liability waivers are frequently buried within dense, archaic legal terminology. Identifying these risks without professional legal training is highly error-prone. A seemingly innocuous sentence can carry massive financial implications.</p>
        <p class="bold">Information Retrieval Friction</p>
        <p>Even when a user knows exactly what they are looking for (e.g., "What is the penalty for late payment?"), finding the exact clause in a massive document is tedious. Traditional keyword search (Ctrl+F) often fails if the user does not guess the exact terminology used by the drafting lawyer.</p>
        <p class="bold">Unreliable and Insecure Public AI Solutions</p>
        <p>While public generative AI chatbots are available, they pose two critical problems. First, they provide generic, ungrounded responses; an AI may hallucinate standard legal practices instead of citing the actual terms of the user's document. Second, pasting confidential corporate contracts into public AI interfaces poses severe privacy and compliance risks.</p>
    </div>

    <div class="main-section">
        <h2>5. Proposed Model</h2>
        <p>LexAI addresses the aforementioned problems by proposing a secure, decoupled client-server architecture. This model ensures that documents are processed locally into a vector database, and an LLM is strictly constrained via RAG to answer questions based only on the user's uploaded text.</p>
        <p class="bold">System Architecture Flow:</p>
        <p style="text-align: center; font-style: italic;">User Interaction ➔ Web Interface (HTML/JS/Bootstrap) ➔ Flask Backend ➔ Authentication / Document Management ➔ MySQL Metadata + Local File System + ChromaDB Vectors ➔ Gemini AI API</p>
        <p class="bold">Frontend Application Layer</p>
        <p>The user interface is built with HTML5, CSS3, and Vanilla JavaScript, utilizing Bootstrap 5 for responsiveness. It employs marked.js for converting AI-generated Markdown into readable HTML, DOMPurify to strip malicious scripts and prevent Cross-Site Scripting (XSS), and MathJax to render equations.</p>
        <p class="bold">Backend Orchestration Layer</p>
        <p>The core Python application handles HTTP routing, session management via Flask-Login, and business logic. It securely isolates user data, orchestrates the document processing pipeline, and acts as the secure intermediary between the user's browser, databases, and APIs.</p>
        <p class="bold">Relational Storage (MySQL)</p>
        <p>MySQL stores structured data including user credentials (securely hashed via Bcrypt), document metadata (file paths, word counts), pre-generated AI executive summaries, and chat histories. This ensures rapid retrieval of user dashboards.</p>
        <p class="bold">Vector Storage (ChromaDB) & Embeddings</p>
        <p>Uploaded files are stored locally. PyMuPDF and python-docx extract raw text, which is passed to a SentenceTransformers model (all-MiniLM-L6-v2) to generate 384-dimensional mathematical vectors. These are stored in ChromaDB, enabling semantic similarity search.</p>
        <p class="bold">Generative Intelligence (Gemini API)</p>
        <p>The backend searches ChromaDB for semantically relevant text chunks. These chunks are appended to a strict system prompt and sent to the Google Gemini API, which generates a natural language response grounded entirely in the provided chunks.</p>
    </div>

    <div class="main-section">
        <h2>6. Methodology</h2>
        <p>The operational methodology of LexAI is structured into a logical, step-by-step pipeline that handles everything from secure file access to complex AI generation.</p>
        <p class="bold">A. User Registration, Authentication & Security</p>
        <p>Users create accounts to access the platform. Passwords are salted and hashed using Bcrypt. Flask-Login manages secure, HTTP-only sessions, preventing unauthorized access to private documents.</p>
        <p class="bold">B. Document Upload & Validation</p>
        <p>Users upload legal documents (.pdf or .docx) via a secure multipart form. The backend validates file extensions and MIME types to prevent malicious uploads, saving files to an isolated local directory.</p>
        <p class="bold">C. Text Extraction & Statistical Analysis</p>
        <p>The system utilizes PyMuPDF and python-docx to extract pure, raw unicode text. The system also calculates and stores document statistics such as word count and estimated page lengths.</p>
        <p class="bold">D. Contextual Text Chunking</p>
        <p>Because LLMs have strict token limits, extracted text is mathematically sliced into smaller chunks (e.g., 500 words). The chunking algorithm implements overlapping windows (e.g., 50 words) to preserve the contextual flow between boundaries.</p>
        <p class="bold">E. Embedding & ChromaDB Storage</p>
        <p>Each text chunk is processed by the local embedding model into a vector. These vectors are strictly tagged with the user's ID and document ID in ChromaDB, enforcing absolute data isolation during retrieval.</p>
        <p class="bold">F. RAG Retrieval & Chat Workflow</p>
        <p>When a user asks a question, the query is embedded into a vector. ChromaDB calculates the cosine similarity between the question vector and stored chunks, returning the top matches. These chunks are combined into a strict context prompt for the Gemini API to generate a grounded response.</p>
        <p class="bold">G. Deterministic Fallback Mechanism</p>
        <p>If the Gemini API becomes unavailable, the pipeline intercepts the failure. A deterministic Python fallback parser extracts the raw legal information from the locally retrieved ChromaDB chunks and formats it cleanly, ensuring the system remains functional.</p>
    </div>

    <div class="main-section">
        <h2>7. Plan of Work</h2>
        <p>The development of LexAI was carried out in sequential stages, focusing on building stable foundations before introducing complex AI integrations.</p>
        <p class="bold">Phase 1: Project Setup & Authentication (Implemented)</p>
        <p>The Flask environment was set up, and MySQL database schemas were designed. Secure registration and login systems were built using Bcrypt and Flask-Login. Basic HTML templates and CSS styling were established.</p>
        <p class="bold">Phase 2: Document Upload & Text Extraction (Implemented)</p>
        <p>Secure file uploads were implemented with strict validation. Parsing libraries (PyMuPDF and python-docx) were integrated to extract raw text accurately from different file formats, and document statistics logic was added.</p>
        <p class="bold">Phase 3: AI Legal Document Analysis (Implemented)</p>
        <p>The Google Gemini API was integrated. The team engineered structured JSON-schema prompts designed to force the LLM to output consistent Executive Summaries and highlight key clauses. The frontend Analysis Dashboard was built.</p>
        <p class="bold">Phase 4: RAG & Document Chat (Implemented)</p>
        <p>Semantic search was introduced. Local embedding models were deployed, ChromaDB was configured, and text chunking logic was developed. The asynchronous AJAX chat interface was built, rendering AI responses using DOMPurify.</p>
        <p class="bold">Phase 5: Knowledge Base & Testing (Implemented)</p>
        <p>An Admin Dashboard was built to manage a centralized Knowledge Base. Python seeding scripts were created. Comprehensive Pytest suites were written to validate authentication and document isolation, and the fallback parser was finalized.</p>
        <p class="bold">Phase 6: Optical Character Recognition (Future Scope)</p>
        <p>Future development will focus on integrating Tesseract OCR to process scanned, image-based PDFs that lack an embedded text layer.</p>
        <p class="bold">Phase 7: Cloud Deployment (Future Scope)</p>
        <p>The final planned phase involves migrating the local ChromaDB and file storage systems to scalable cloud infrastructure to support enterprise usage.</p>
    </div>

    <div class="main-section">
        <h2>8. Conclusion</h2>
        <p>The LexAI project successfully demonstrates the immense practical potential of combining Large Language Models with Retrieval-Augmented Generation to solve the accessibility crisis in legal document comprehension. By integrating an intuitive web interface with a robust, locally embedded RAG pipeline, LexAI provides a highly accurate, secure, and isolated environment for contract intelligence.</p>
        <p>Through automated executive summaries, semantic clause breakdowns, and a conversational chatbot, the platform significantly reduces the cognitive load required to understand dense legalese. The strict database-level separation of the Document Chat and the curated General Legal Knowledge Base ensures that responses are reliably grounded in verified text, effectively mitigating the risks of model hallucination.</p>
        <p>Furthermore, the implementation of comprehensive security measures, strict user data isolation, and a deterministic fallback parser guarantees that LexAI is a resilient, production-ready prototype. While LexAI operates as an AI informational assistant rather than a substitute for professional legal counsel, it represents a significant technological leap toward making legal information transparent, accessible, and understandable.</p>
    </div>

    <div class="main-section" style="page-break-after: auto;">
        <h2>9. References</h2>
        <p>[1] Jain, D., Borah, M. D., & Biswas, A. (2021). "Summarization of legal documents: Where are we now and the way forward." <span class="bold">Computer Science Review</span>, 40, 100388.</p>
        <p>[2] Chalkidis, I., Fergadiotis, M., Malakasiotis, P., Aletras, N., & Androutsopoulos, I. (2020). "LEGAL-BERT: The Muppets straight out of Law School." <span class="bold">Findings of the Association for Computational Linguistics: EMNLP 2020</span>.</p>
        <p>[3] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Riedel, S. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." <span class="bold">Advances in Neural Information Processing Systems (NeurIPS)</span>.</p>
        <p>[4] Ariai, F., Mackenzie, J., & Demartini, G. (2025). "Natural Language Processing for the Legal Domain: A Survey of Tasks, Datasets, Models, and Challenges." <span class="bold">ACM Computing Surveys</span>, 58(6).</p>
        <p>[5] Martinez-Gil, J. (2023). "A survey on legal question–answering systems." <span class="bold">Computer Science Review</span>, 48, 100551.</p>

        <!-- Signatures section -->
        <div class="signatures">
            <div class="sig-left">
                <p class="bold">Prof. Dr. Surekha Kohle</p>
                <p>Guide</p>
                <p>CS/IT Department</p>
            </div>
            <div class="sig-right">
                <p class="bold">Dr. Praveen Gupta</p>
                <p>H.O.D.</p>
                <p>CS/IT Department</p>
            </div>
            <div class="clear"></div>
        </div>
    </div>
</body></html>
"""

async def generate_pdf():
    # Write HTML parts
    with open('synopsis_part1.html', 'w', encoding='utf-8') as f:
        f.write(html_part1)
    with open('synopsis_part2.html', 'w', encoding='utf-8') as f:
        f.write(html_part2)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # Pass 1: Cover and Guide
        page1 = await browser.new_page()
        await page1.goto(f"file://{os.path.abspath('synopsis_part1.html')}")
        await page1.pdf(
            path="part1.pdf",
            format="A4",
            margin={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
            display_header_footer=False
        )
        await page1.close()
        
        # Pass 2: Main sections (1 to 9)
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
        
    # Merge PDFs using PyMuPDF
    merged = fitz.open()
    merged.insert_pdf(fitz.open("part1.pdf"))
    merged.insert_pdf(fitz.open("part2.pdf"))
    merged.save("LexAI_Project_Synopsis_Final.pdf")
    merged.close()
    
    # We also need to fix the DOCX code logic to handle page borders properly.
    # To keep this script clean, I will write the DOCX directly using a simpler script.

if __name__ == "__main__":
    asyncio.run(generate_pdf())
