import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

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
    
    # ----------------------------------------------------
    # SECTION 1: Cover Page
    # ----------------------------------------------------
    s1 = doc.sections[0]
    setup_margins_and_borders(s1)
    # Remove header/footer link
    s1.header.is_linked_to_previous = False
    s1.footer.is_linked_to_previous = False

    for _ in range(2): doc.add_paragraph()
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
    
    # ----------------------------------------------------
    # SECTION 2: Guide Page
    # ----------------------------------------------------
    s2 = doc.add_section()
    setup_margins_and_borders(s2)
    s2.header.is_linked_to_previous = False
    s2.footer.is_linked_to_previous = False
    
    for _ in range(8): doc.add_paragraph()
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_font(p2.add_run("Guide\n\n"), bold=True)
    set_font(p2.add_run("Dr. Surekha Kohle\n\n\n\n"), bold=False)
    set_font(p2.add_run("Department of Computer Science & Information Technology\nChhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai\n\nAcademic Year:\n2026–27\n"), bold=True)

    # ----------------------------------------------------
    # SECTIONS 3 - 11 (Main Content, Sections 1-9)
    # ----------------------------------------------------
    # The requirement is that *every main numbered section* begins on a new page.
    # To have page numbers start at 1, we must add a section break for Section 3, enable page numbering,
    # and then add section breaks or page breaks for the subsequent sections. We will use page breaks within Section 3 
    # for the subsequent main content pieces to keep continuous page numbering easily.

    s3 = doc.add_section()
    setup_margins_and_borders(s3)
    s3.header.is_linked_to_previous = False
    s3.footer.is_linked_to_previous = False

    # Set page numbering to start at 1 for this section
    sectPr = s3._sectPr
    pgNumType = OxmlElement('w:pgNumType')
    pgNumType.set(qn('w:start'), '1')
    sectPr.append(pgNumType)

    # Add page number to footer
    footer = s3.footer
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

    # Content Pages
    # 1. Introduction
    add_heading(doc, "1. Introduction")
    add_paragraph(doc, "The legal domain is characterized by densely packed terminology and exceptionally lengthy documents, creating significant barriers to entry for individuals and small to medium-sized businesses. Commercial contracts, non-disclosure agreements, and terms of service are often obfuscated by specialized jargon. This complexity makes it exceptionally difficult for non-lawyers to comprehend their fundamental rights, implicit obligations, and the hidden risks buried within the text.")
    add_paragraph(doc, "Manually reviewing these documents requires immense cognitive effort and frequently necessitates consulting expensive legal professionals. The prohibitive cost of legal counsel often leads to contracts being signed without a full understanding of their implications. There is a pressing need for automated tools that can democratize access to basic legal comprehension without completely replacing human oversight.")
    add_paragraph(doc, "LexAI is an AI-assisted legal information and document intelligence platform designed to bridge this accessibility gap. Utilizing a Flask-based web architecture, LexAI allows users to securely upload complex legal contracts in standard formats (PDF or DOCX). The platform automates the heavy lifting of document review by instantly extracting, chunking, and processing the text to perform deep semantic analysis. It provides automated executive summaries, isolates critical clauses, and flags potential operational risks.")
    add_paragraph(doc, "To mitigate the critical issue of \"hallucination\"—where generative AI models fabricate facts or legal precedents—LexAI implements a robust Retrieval-Augmented Generation (RAG) architecture powered by the Google Gemini LLM. By grounding the AI's responses exclusively in the retrieved text of the user's specific uploaded document or an admin-curated Legal Knowledge Base, LexAI ensures that generated answers are contextually relevant and factually verifiable.")
    add_paragraph(doc, "While LexAI significantly reduces the time and cognitive load required to understand legal text, it is explicitly designed as an informational assistant. It does not provide jurisdictional legal counsel and is not a substitute for professional legal advice. It acts as a tireless first-pass reviewer, empowering users to make informed decisions.")

    doc.add_page_break()

    # 2. Literature Review
    add_heading(doc, "2. Literature Review")
    add_heading(doc, "2.1 Legal Document Summarization")
    add_paragraph(doc, "Research by Jain et al. [1] highlights the unique complexities of generating accurate summaries for legal documents, emphasizing the necessity of preserving factual integrity while condensing extensive case texts. Extractive methods often miss semantic nuance, while abstractive generative models risk fabricating legal precedent. LexAI adopts a deterministic chunking strategy prior to abstraction to generate safe, verifiable executive summaries.")
    add_heading(doc, "2.2 Domain-Specific NLP Models")
    add_paragraph(doc, "Chalkidis et al. [2] demonstrated with LEGAL-BERT that generic language models frequently misinterpret legal nuances, proving that domain-aware processing is essential. While LexAI utilizes the highly efficient all-MiniLM-L6-v2 model for generalized embedding, it relies on structured JSON-schema prompting with the Gemini LLM to enforce domain-specific analytical constraints during generation.")
    add_heading(doc, "2.3 Retrieval-Augmented Generation (RAG)")
    add_paragraph(doc, "The integration of non-parametric memory with parametric LLMs was formalized by Lewis et al. [3], establishing RAG as the standard for knowledge-intensive NLP tasks. Their findings proved that querying an external vector index drastically reduces factual hallucinations. LexAI incorporates this exact architecture by utilizing ChromaDB as a semantic vector store, ensuring the AI only processes text explicitly present in the uploaded contract.")
    add_heading(doc, "2.4 Challenges in Legal NLP and Question Answering")
    add_paragraph(doc, "Surveys by Ariai et al. [4] and Martinez-Gil [5] underscore ongoing challenges in legal QA systems, particularly concerning explainability, privacy, and user trust. Public generative AI interfaces pose significant security risks for confidential contracts. Furthermore, unconstrained models often hallucinate standard industry practices instead of citing specific negotiated terms.")
    add_heading(doc, "2.5 Research Gap")
    add_paragraph(doc, "Existing academic literature proves the efficacy of RAG in controlled environments, but there remains a gap in locally verifiable systems that combine private document analysis, conversational querying, and a curated general legal knowledge base securely. LexAI addresses this by enforcing strict database-level filtering (document ID isolation), ensuring users only receive answers grounded in their private contracts.")

    doc.add_page_break()

    # 3. Aims & Objective
    add_heading(doc, "3. Aims & Objective")
    add_paragraph(doc, "The primary aim of the LexAI project is to develop a secure, highly accurate, and accessible web-based platform that utilizes Artificial Intelligence and Retrieval-Augmented Generation (RAG) to demystify complex legal documents and provide verified legal information.")
    add_paragraph(doc, "Implemented Objectives:")
    add_bullet(doc, "User Authentication & Security: To develop a secure registration, login, and session management system using Flask-Login and Bcrypt.")
    add_bullet(doc, "Document Processing: To enable secure upload and precise raw text extraction from PDF and DOCX formats utilizing PyMuPDF and python-docx.")
    add_bullet(doc, "AI Legal Analysis: To engineer structured JSON prompts that constrain the Gemini API to automatically generate executive summaries and highlight key clauses.")
    add_bullet(doc, "RAG-Based Retrieval: To implement a complete vector embedding pipeline using SentenceTransformers and ChromaDB to semantically index documents.")
    add_bullet(doc, "Secure Isolation: To enforce strict database and vector-store filtering to ensure users can only access and query their own private documents.")
    add_bullet(doc, "Document Chatbot: To create a conversational interface allowing users to query their specific uploaded contracts, backed entirely by RAG.")
    add_bullet(doc, "General Legal Chat & Knowledge Base: To provide an admin-curated legal Knowledge Base to ground general legal queries safely without cross-contamination.")
    add_bullet(doc, "Deterministic Fallback: To implement a robust parser that gracefully handles external API failures by formatting raw Knowledge Base content locally.")
    add_paragraph(doc, "Future Objectives (Planned):")
    add_bullet(doc, "Optical Character Recognition (OCR): To implement OCR capabilities for processing scanned, image-based legal documents that lack embedded text layers.")
    add_bullet(doc, "Multilingual Support: To integrate translation pipelines to analyze and explain legal concepts in regional languages, increasing accessibility.")
    add_bullet(doc, "Cloud Migration: To migrate local ChromaDB and file storage to persistent cloud infrastructure for scalable deployment.")

    doc.add_page_break()

    # 4. Problem Definition
    add_heading(doc, "4. Problem Definition")
    add_paragraph(doc, "The legal ecosystem remains largely inaccessible to the general public and small enterprises due to the sheer volume and complexity of legal text. When an individual is presented with a standard contract, they face several immediate challenges that LexAI aims to resolve.")
    add_paragraph(doc, "Manual Review Effort\nContracts are often tens or hundreds of pages long, filled with repetitive boilerplate text and complex formatting. Reading and comprehending these documents requires a prohibitive amount of time. For individuals, the sheer effort often leads them to sign documents without reading them thoroughly.")
    add_paragraph(doc, "Obfuscated Clauses and Hidden Risks\nCritical obligations, termination conditions, automatic renewals, and liability waivers are frequently buried within dense, archaic legal terminology. Identifying these risks without professional legal training is highly error-prone. A seemingly innocuous sentence can carry massive financial implications.")
    add_paragraph(doc, "Information Retrieval Friction\nEven when a user knows exactly what they are looking for (e.g., \"What is the penalty for late payment?\"), finding the exact clause in a massive document is tedious. Traditional keyword search (Ctrl+F) often fails if the user does not guess the exact terminology used by the drafting lawyer.")
    add_paragraph(doc, "Unreliable and Insecure Public AI Solutions\nWhile public generative AI chatbots are available, they pose two critical problems. First, they provide generic, ungrounded responses; an AI may hallucinate standard legal practices instead of citing the actual terms of the user's document. Second, pasting confidential corporate contracts into public AI interfaces poses severe privacy and compliance risks.")

    doc.add_page_break()

    # 5. Proposed Model
    add_heading(doc, "5. Proposed Model")
    add_paragraph(doc, "LexAI addresses the aforementioned problems by proposing a secure, decoupled client-server architecture. This model ensures that documents are processed locally into a vector database, and an LLM is strictly constrained via RAG to answer questions based only on the user's uploaded text.")
    add_paragraph(doc, "System Architecture Flow:\nUser Interaction ➔ Web Interface (HTML/JS/Bootstrap) ➔ Flask Backend ➔ Authentication / Document Management ➔ MySQL Metadata + Local File System + ChromaDB Vectors ➔ Gemini AI API", align=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "Frontend Application Layer\nThe user interface is built with HTML5, CSS3, and Vanilla JavaScript, utilizing Bootstrap 5 for responsiveness. It employs marked.js for converting AI-generated Markdown into readable HTML, DOMPurify to strip malicious scripts and prevent Cross-Site Scripting (XSS), and MathJax to render equations.")
    add_paragraph(doc, "Backend Orchestration Layer\nThe core Python application handles HTTP routing, session management via Flask-Login, and business logic. It securely isolates user data, orchestrates the document processing pipeline, and acts as the secure intermediary between the user's browser, databases, and APIs.")
    add_paragraph(doc, "Relational Storage (MySQL)\nMySQL stores structured data including user credentials (securely hashed via Bcrypt), document metadata (file paths, word counts), pre-generated AI executive summaries, and chat histories. This ensures rapid retrieval of user dashboards.")
    add_paragraph(doc, "Vector Storage (ChromaDB) & Embeddings\nUploaded files are stored locally. PyMuPDF and python-docx extract raw text, which is passed to a SentenceTransformers model (all-MiniLM-L6-v2) to generate 384-dimensional mathematical vectors. These are stored in ChromaDB, enabling semantic similarity search.")
    add_paragraph(doc, "Generative Intelligence (Gemini API)\nThe backend searches ChromaDB for semantically relevant text chunks. These chunks are appended to a strict system prompt and sent to the Google Gemini API, which generates a natural language response grounded entirely in the provided chunks.")

    doc.add_page_break()

    # 6. Methodology
    add_heading(doc, "6. Methodology")
    add_paragraph(doc, "The operational methodology of LexAI is structured into a logical, step-by-step pipeline that handles everything from secure file access to complex AI generation.")
    add_paragraph(doc, "A. User Registration, Authentication & Security\nUsers create accounts to access the platform. Passwords are salted and hashed using Bcrypt. Flask-Login manages secure, HTTP-only sessions, preventing unauthorized access to private documents.")
    add_paragraph(doc, "B. Document Upload & Validation\nUsers upload legal documents (.pdf or .docx) via a secure multipart form. The backend validates file extensions and MIME types to prevent malicious uploads, saving files to an isolated local directory.")
    add_paragraph(doc, "C. Text Extraction & Statistical Analysis\nThe system utilizes PyMuPDF and python-docx to extract pure, raw unicode text. The system also calculates and stores document statistics such as word count and estimated page lengths.")
    add_paragraph(doc, "D. Contextual Text Chunking\nBecause LLMs have strict token limits, extracted text is mathematically sliced into smaller chunks (e.g., 500 words). The chunking algorithm implements overlapping windows (e.g., 50 words) to preserve the contextual flow between boundaries.")
    add_paragraph(doc, "E. Embedding & ChromaDB Storage\nEach text chunk is processed by the local embedding model into a vector. These vectors are strictly tagged with the user's ID and document ID in ChromaDB, enforcing absolute data isolation during retrieval.")
    add_paragraph(doc, "F. RAG Retrieval & Chat Workflow\nWhen a user asks a question, the query is embedded into a vector. ChromaDB calculates the cosine similarity between the question vector and stored chunks, returning the top matches. These chunks are combined into a strict context prompt for the Gemini API to generate a grounded response.")
    add_paragraph(doc, "G. Deterministic Fallback Mechanism\nIf the Gemini API becomes unavailable, the pipeline intercepts the failure. A deterministic Python fallback parser extracts the raw legal information from the locally retrieved ChromaDB chunks and formats it cleanly, ensuring the system remains functional.")

    doc.add_page_break()

    # 7. Plan of Work
    add_heading(doc, "7. Plan of Work")
    add_paragraph(doc, "The development of LexAI was carried out in sequential stages, focusing on building stable foundations before introducing complex AI integrations.")
    add_paragraph(doc, "Phase 1: Project Setup & Authentication (Implemented)\nThe Flask environment was set up, and MySQL database schemas were designed. Secure registration and login systems were built using Bcrypt and Flask-Login. Basic HTML templates and CSS styling were established.")
    add_paragraph(doc, "Phase 2: Document Upload & Text Extraction (Implemented)\nSecure file uploads were implemented with strict validation. Parsing libraries (PyMuPDF and python-docx) were integrated to extract raw text accurately from different file formats, and document statistics logic was added.")
    add_paragraph(doc, "Phase 3: AI Legal Document Analysis (Implemented)\nThe Google Gemini API was integrated. The team engineered structured JSON-schema prompts designed to force the LLM to output consistent Executive Summaries and highlight key clauses. The frontend Analysis Dashboard was built.")
    add_paragraph(doc, "Phase 4: RAG & Document Chat (Implemented)\nSemantic search was introduced. Local embedding models were deployed, ChromaDB was configured, and text chunking logic was developed. The asynchronous AJAX chat interface was built, rendering AI responses using DOMPurify.")
    add_paragraph(doc, "Phase 5: Knowledge Base & Testing (Implemented)\nAn Admin Dashboard was built to manage a centralized Knowledge Base. Python seeding scripts were created. Comprehensive Pytest suites were written to validate authentication and document isolation, and the fallback parser was finalized.")
    add_paragraph(doc, "Phase 6: Optical Character Recognition (Future Scope)\nFuture development will focus on integrating Tesseract OCR to process scanned, image-based PDFs that lack an embedded text layer.")
    add_paragraph(doc, "Phase 7: Cloud Deployment (Future Scope)\nThe final planned phase involves migrating the local ChromaDB and file storage systems to scalable cloud infrastructure to support enterprise usage.")

    doc.add_page_break()

    # 8. Conclusion
    add_heading(doc, "8. Conclusion")
    add_paragraph(doc, "The LexAI project successfully demonstrates the immense practical potential of combining Large Language Models with Retrieval-Augmented Generation to solve the accessibility crisis in legal document comprehension. By integrating an intuitive web interface with a robust, locally embedded RAG pipeline, LexAI provides a highly accurate, secure, and isolated environment for contract intelligence.")
    add_paragraph(doc, "Through automated executive summaries, semantic clause breakdowns, and a conversational chatbot, the platform significantly reduces the cognitive load required to understand dense legalese. The strict database-level separation of the Document Chat and the curated General Legal Knowledge Base ensures that responses are reliably grounded in verified text, effectively mitigating the risks of model hallucination.")
    add_paragraph(doc, "Furthermore, the implementation of comprehensive security measures, strict user data isolation, and a deterministic fallback parser guarantees that LexAI is a resilient, production-ready prototype. While LexAI operates as an AI informational assistant rather than a substitute for professional legal counsel, it represents a significant technological leap toward making legal information transparent, accessible, and understandable.")

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

    for _ in range(3): doc.add_paragraph()

    table = doc.add_table(rows=1, cols=2)
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

    doc.save("LexAI_Project_Synopsis_Final.docx")

if __name__ == "__main__":
    create_docx()
