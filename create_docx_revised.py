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
    # Force the font name in the XML
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
    p.paragraph_format.space_after = Pt(6)
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
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    run = p.add_run(text)
    set_font(run)

def create_revised_docx():
    doc = Document()
    
    # Set Margins to 1 inch
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # --- COVER PAGE ---
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    
    r = p.add_run("PROJECT SYNOPSIS\nOn\n")
    set_font(r, bold=True)
    r2 = p.add_run("“LexAI – AI-Powered Legal Assistant & Contract Intelligence Platform”\n")
    set_font(r2, bold=True)
    r3 = p.add_run("\nSubmitted to\n")
    set_font(r3, bold=True)
    r4 = p.add_run("Chhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai\n\n")
    set_font(r4, bold=True)

    if os.path.exists("csmu_logo.png"):
        p.add_run().add_picture("csmu_logo.png", width=Inches(1.5))
        p.add_run("\n\n")
    else:
        p.add_run("\n\n")
        
    r5 = p.add_run("for the partial fulfillment of requirement for the Degree of\n")
    set_font(r5)
    r6 = p.add_run("MASTER OF COMPUTER APPLICATION\n\n")
    set_font(r6, bold=True)
    
    r7 = p.add_run("Submitted By\n")
    set_font(r7, bold=True)
    r8 = p.add_run("Rohan Bongane\nHarsh Jha\nAishwariya Bhunia\nNitu Sharma\n\n")
    set_font(r8)
    
    r9 = p.add_run("Guide\n")
    set_font(r9, bold=True)
    r10 = p.add_run("Dr. Surekha Kohle\n\n")
    set_font(r10)
    
    r11 = p.add_run("Department of Computer Science & Information Technology\nChhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai\nAcademic Year:\n2026–27")
    set_font(r11, bold=True)

    doc.add_page_break()

    # Create a new section for the body to start page numbering (if supported natively, but we'll let word handle default numbering)
    # Actually, adding page numbers via python-docx requires oxml manipulation. We'll add a simple footer page number.
    sect = doc.sections[-1]
    footer = sect.footer
    footer_p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # OXML for page number
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

    # --- 1. Introduction ---
    add_heading(doc, "1. Introduction")
    add_paragraph(doc, "The legal domain is characterized by densely packed terminology and exceptionally lengthy documents, creating significant barriers to entry for individuals and small businesses. Commercial contracts, non-disclosure agreements, and terms of service are often obfuscated by specialized jargon. Manually reviewing these documents requires immense cognitive effort and frequently necessitates consulting expensive legal professionals to comprehend basic rights, obligations, and hidden risks.")
    add_paragraph(doc, "LexAI is an AI-assisted legal information and document intelligence platform designed to bridge this accessibility gap. Utilizing a Flask-based web architecture, LexAI allows users to upload complex legal contracts in PDF or DOCX formats. The platform automates the heavy lifting of document review by extracting, chunking, and processing the text to perform deep semantic analysis.")
    add_paragraph(doc, "To mitigate the critical issue of \"hallucination\" commonly associated with Large Language Models (LLMs), LexAI implements a robust Retrieval-Augmented Generation (RAG) architecture powered by the Google Gemini LLM. By grounding the AI's responses exclusively in the retrieved text of the user's specific document or an admin-curated Legal Knowledge Base, LexAI ensures that generated answers are contextually relevant, highly accurate, and factually verifiable. It is explicitly noted that LexAI acts as an informational assistant and does not replace professional, jurisdictional legal counsel.")

    # --- 2. Literature Review ---
    add_heading(doc, "2. Literature Review")
    
    add_heading(doc, "2.1 Legal Document Summarization")
    add_paragraph(doc, "Research by Jain et al. [1] highlights the complexities of generating accurate summaries for legal documents, emphasizing the necessity of preserving factual integrity while condensing extensive case texts. Traditional extractive methods often miss semantic nuance, while generative models risk fabricating legal precedent. This underlines the need for deterministic chunking strategies prior to abstraction, which LexAI adopts to generate safe executive summaries.")

    add_heading(doc, "2.2 Domain-Specific NLP Models")
    add_paragraph(doc, "The uniqueness of legal vocabulary requires specialized NLP approaches. Chalkidis et al. [2] demonstrated with LEGAL-BERT that generic language models frequently misinterpret legal nuances, necessitating domain-aware processing. While LexAI utilizes the all-MiniLM-L6-v2 model for generalized embedding efficiency, it relies on structured JSON-schema prompting with the Gemini LLM to enforce domain-specific analytical constraints during generation.")

    add_heading(doc, "2.3 Retrieval-Augmented Generation (RAG)")
    add_paragraph(doc, "The integration of non-parametric memory with parametric LLMs was formalized by Lewis et al. [3], establishing RAG as the standard for knowledge-intensive NLP tasks. Their findings proved that querying an external vector index drastically reduces factual hallucinations. LexAI incorporates this exact architecture by utilizing ChromaDB as a semantic vector store, ensuring the AI only processes text explicitly present in the uploaded contract.")

    add_heading(doc, "2.4 Challenges in Legal NLP and Question Answering")
    add_paragraph(doc, "Recent surveys by Ariai et al. [4] and Martinez-Gil [5] underscore the ongoing challenges in legal QA systems, particularly concerning model explainability, privacy, and user trust. Public generative AI interfaces pose significant security risks for confidential contracts. Furthermore, unconstrained models often hallucinate standard practices instead of citing specific contractual terms.")

    add_heading(doc, "2.5 Research Gap")
    add_paragraph(doc, "While existing literature proves the efficacy of RAG and domain-specific LLMs, there remains a gap in accessible, locally verifiable systems that combine private document analysis, conversational querying, and a curated general legal knowledge base within a single, securely isolated platform. LexAI addresses this gap by enforcing strict database-level filtering (document ID isolation), ensuring users only receive answers grounded in their private contracts or the admin-curated repository, thereby maximizing privacy and mitigating hallucinations.")

    # --- 3. Aims & Objective ---
    add_heading(doc, "3. Aims & Objective")
    add_paragraph(doc, "The primary aim of the LexAI project is to develop a secure, highly accurate, and accessible web-based platform that utilizes Artificial Intelligence to demystify complex legal documents.")
    add_paragraph(doc, "Specific Objectives:")
    add_bullet(doc, "To securely authenticate users and isolate their uploaded legal documents.")
    add_bullet(doc, "To extract and mathematically embed text from uploaded PDF and DOCX files.")
    add_bullet(doc, "To implement a Retrieval-Augmented Generation (RAG) pipeline utilizing ChromaDB for highly accurate semantic search.")
    add_bullet(doc, "To automatically generate structured executive summaries highlighting key obligations and risks using the Gemini API.")
    add_bullet(doc, "To provide a conversational document chatbot strictly grounded in the user's specific uploaded contract.")
    add_bullet(doc, "To maintain a deterministic fallback mechanism capable of serving general legal knowledge even if external AI APIs become unavailable.")

    # --- 4. Problem Definition ---
    add_heading(doc, "4. Problem Definition")
    add_paragraph(doc, "The sheer volume and archaic terminology of legal text make contracts largely inaccessible to the general public. When presented with standard legal agreements, individuals face several challenges:")
    add_bullet(doc, "Manual Review Effort: Reading and comprehending dense, multi-page documents requires prohibitive amounts of time.")
    add_bullet(doc, "Hidden Risks: Critical obligations, termination conditions, and liability waivers are frequently obfuscated by legalese, making manual identification error-prone.")
    add_bullet(doc, "Retrieval Friction: Locating the exact clause for a specific question (e.g., \"What is the governing law?\") via basic keyword search often fails if exact terminology is not used.")
    add_bullet(doc, "Unreliable Public AI: Pasting confidential contracts into public generative AI chatbots poses severe privacy risks, and generic LLMs frequently hallucinate legal answers rather than citing the provided text.")

    # --- 5. Proposed Model ---
    add_heading(doc, "5. Proposed Model")
    add_paragraph(doc, "LexAI proposes a decoupled client-server architecture to provide a secure environment for document intelligence.")
    add_paragraph(doc, "Architecture Components:")
    add_bullet(doc, "Frontend: Responsive web interface built with HTML5, Bootstrap 5, and JavaScript. Uses DOMPurify to sanitize AI responses and MathJax to render complex logic.")
    add_bullet(doc, "Backend Application: A robust Python Flask server managing session authentication (Flask-Login, Bcrypt), secure routing, and orchestration of the AI pipeline.")
    add_bullet(doc, "Relational Database: MySQL (via SQLAlchemy) stores user credentials, document metadata, and conversation histories.")
    add_bullet(doc, "Vector Database & Embeddings: Extracted document text is processed by a local SentenceTransformers model (all-MiniLM-L6-v2) to generate 384-dimensional embeddings, which are stored in ChromaDB for high-speed semantic retrieval.")
    add_bullet(doc, "Generative LLM: The Google Gemini API processes the retrieved context alongside strict system prompts to generate factual, grounded responses.")

    # --- 6. Methodology ---
    add_heading(doc, "6. Methodology")
    add_paragraph(doc, "The operational methodology of LexAI is structured into a sequential processing pipeline:")
    add_bullet(doc, "Secure Ingestion: Users upload PDF or DOCX files. The backend validates file integrity and extracts raw unicode text using PyMuPDF and python-docx.")
    add_bullet(doc, "Contextual Chunking: To accommodate LLM token limits, the text is sliced into manageable overlapping segments (e.g., 500 words with a 50-word overlap) to preserve contextual boundaries.")
    add_bullet(doc, "Vectorization: Each chunk is converted into a mathematical vector embedding locally and indexed in ChromaDB, tagged strictly with the user's ID to prevent cross-contamination.")
    add_bullet(doc, "Semantic Retrieval (RAG): When a user queries a document, their question is embedded into a vector. ChromaDB calculates mathematical similarities and retrieves the top matching chunks.")
    add_bullet(doc, "Grounded Generation: The retrieved chunks are appended to a strict prompt instructing the Gemini API to answer based solely on the provided text. The generated response is formatted in Markdown and returned to the user interface.")
    add_bullet(doc, "Deterministic Fallback: If the Gemini API experiences an outage, a Python fallback parser directly extracts and formats the retrieved raw database chunks, ensuring uninterrupted access to the Knowledge Base.")

    # --- 7. Plan of Work ---
    add_heading(doc, "7. Plan of Work")
    add_paragraph(doc, "The project execution was organized into distinct phases separating implemented features from future scope:")
    
    add_heading(doc, "Implemented Phases:")
    add_bullet(doc, "Phase 1: Environment Setup & Authentication. Configuration of Flask, MySQL, and implementation of secure Bcrypt user registration and login.")
    add_bullet(doc, "Phase 2: Document Processing. Implementation of secure file uploads, validation, and PyMuPDF/python-docx text extraction pipelines.")
    add_bullet(doc, "Phase 3: AI Legal Analysis. Integration of the Gemini API with structured JSON prompts to generate automated executive summaries.")
    add_bullet(doc, "Phase 4: RAG & Chat Interfaces. Deployment of local SentenceTransformers, ChromaDB vector indexing, and asynchronous Document Chat implementation.")
    add_bullet(doc, "Phase 5: Knowledge Base & Testing. Development of the admin-curated legal Knowledge Base, fallback mechanisms, and comprehensive Pytest validation suites.")
    
    add_heading(doc, "Future Scope (Planned):")
    add_bullet(doc, "Phase 6: Optical Character Recognition (OCR). Integration of Tesseract OCR to process scanned, image-based legal documents.")
    add_bullet(doc, "Phase 7: Multilingual Support. Expanding semantic models to analyze and translate legal concepts into regional languages.")

    # --- 8. Conclusion ---
    add_heading(doc, "8. Conclusion")
    add_paragraph(doc, "The LexAI platform successfully demonstrates the practical application of Retrieval-Augmented Generation (RAG) in solving the accessibility crisis surrounding legal document comprehension. By integrating an intuitive Flask-based web interface with a robust, locally embedded vector pipeline, LexAI provides a secure, isolated environment for intelligent contract analysis.")
    add_paragraph(doc, "Through automated executive summaries, semantic clause identification, and conversational querying, the system significantly reduces the cognitive load required to navigate dense legalese. Enforcing strict database isolation and utilizing deterministic fallback mechanisms ensures that the platform remains reliable, private, and highly resistant to AI hallucinations, representing a substantial technological advancement in making legal information transparent and understandable.")

    # --- 9. References ---
    add_heading(doc, "9. References")
    
    # 1
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_font(p.add_run("[1] Jain, D., Borah, M. D., & Biswas, A. (2021). \"Summarization of legal documents: Where are we now and the way forward.\" "), bold=False)
    set_font(p.add_run("Computer Science Review"), bold=True)
    set_font(p.add_run(", 40, 100388."), bold=False)

    # 2
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_font(p.add_run("[2] Chalkidis, I., Fergadiotis, M., Malakasiotis, P., Aletras, N., & Androutsopoulos, I. (2020). \"LEGAL-BERT: The Muppets straight out of Law School.\" "), bold=False)
    set_font(p.add_run("Findings of the Association for Computational Linguistics: EMNLP 2020"), bold=True)
    set_font(p.add_run("."), bold=False)

    # 3
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_font(p.add_run("[3] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Riedel, S. (2020). \"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.\" "), bold=False)
    set_font(p.add_run("Advances in Neural Information Processing Systems (NeurIPS)"), bold=True)
    set_font(p.add_run("."), bold=False)

    # 4
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_font(p.add_run("[4] Ariai, F., Mackenzie, J., & Demartini, G. (2025). \"Natural Language Processing for the Legal Domain: A Survey of Tasks, Datasets, Models, and Challenges.\" "), bold=False)
    set_font(p.add_run("ACM Computing Surveys"), bold=True)
    set_font(p.add_run(", 58(6)."), bold=False)

    # 5
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_font(p.add_run("[5] Martinez-Gil, J. (2023). \"A survey on legal question–answering systems.\" "), bold=False)
    set_font(p.add_run("Computer Science Review"), bold=True)
    set_font(p.add_run(", 48, 100551."), bold=False)

    doc.add_paragraph("\n\n")

    # --- Signatures ---
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

    doc.save("LexAI_Project_Synopsis_Revised.docx")

if __name__ == "__main__":
    create_revised_docx()
