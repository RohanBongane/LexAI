import os
import asyncio
from docx import Document
from docx.shared import Pt, Inches, RGBColor as DocxRGB
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from pptx import Presentation
from pptx.util import Inches as PptxInches, Pt as PptxPt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from playwright.async_api import async_playwright
import pymupdf as fitz

# ---------------------------------------------------------
# CONTENT DEFINITIONS
# ---------------------------------------------------------

SLIDES_DATA = [
    {
        "title": "LexAI – AI-Powered Legal Assistant\n& Contract Intelligence Platform",
        "subtitle": "MCA Project Presentation\nChhatrapati Shivaji Maharaj University\nAcademic Year: 2026–27\n\nSubmitted By:\nRohan Bongane, Harsh Jha, Aishwariya Bhunia, Nitu Sharma\n\nGuide: Dr. Surekha Kohle",
        "type": "title",
        "notes": "Slide Meaning: This is the title slide introducing our project, LexAI, our team, and our guide.\n\nWhat to say: 'Good morning respected faculty members and evaluators. Today, our team will present our MCA final year project, LexAI, which is an AI-Powered Legal Assistant and Contract Intelligence Platform. My name is [Your Name], and I will be walking you through the core concepts and architecture of our system.'\n\nTransition: 'Let's begin by understanding why we chose this problem and the challenges people face with legal documents.'"
    },
    {
        "title": "Introduction",
        "bullets": [
            "The legal domain is filled with dense terminology and lengthy documents.",
            "Contracts are obfuscated by specialized jargon, making it difficult for non-lawyers to understand their rights and hidden risks.",
            "Professional legal counsel is expensive, leading many to sign contracts blindly.",
            "LexAI aims to democratize basic legal comprehension using AI.",
            "It acts as a preliminary informational assistant, not a replacement for human lawyers."
        ],
        "type": "content",
        "notes": "Slide Meaning: Explains the basic motivation behind the project.\n\nWhat to say: 'Legal documents are notoriously difficult for the average person to read. They are long, filled with complex jargon, and often hide critical risks. Because hiring a lawyer for every small contract is too expensive, many people just sign agreements without understanding them. LexAI was built to bridge this gap by acting as a smart, accessible first-pass reviewer.'\n\nTransition: 'Specifically, we identified several major problems that our system needs to solve.'"
    },
    {
        "title": "Problem Statement",
        "bullets": [
            "Time-Consuming Manual Review: Reading 50+ page contracts takes immense cognitive effort and time.",
            "Keyword Search Limitations: Standard 'Ctrl+F' fails if you don't guess the exact legal synonym.",
            "Privacy Risks of Public AI: Uploading confidential corporate contracts to public chatbots poses severe data leak risks.",
            "AI Hallucination: Generic AI models often hallucinate standard industry practices instead of reading your actual contract."
        ],
        "type": "content",
        "notes": "Slide Meaning: Breaks down the exact problems with manual review and existing AI tools.\n\nWhat to say: 'The primary problems are time and accuracy. Manual review takes hours. Keyword searching fails if you search for \"penalty\" but the contract uses the word \"liquidated damages\". While public AI like ChatGPT exists, pasting confidential contracts into them is a massive privacy violation. Furthermore, public AIs often hallucinate—meaning they invent answers based on general internet data rather than your specific document.'\n\nTransition: 'To address these specific problems, we set clear objectives for LexAI.'"
    },
    {
        "title": "Aim and Objectives",
        "bullets": [
            "Aim: Build a secure, web-based platform that uses Retrieval-Augmented Generation (RAG) to demystify complex legal documents.",
            "Objective 1: Securely extract text from PDF and DOCX files locally.",
            "Objective 2: Implement strict data isolation so users only access their own files.",
            "Objective 3: Use local vector embeddings (ChromaDB) for semantic search.",
            "Objective 4: Constrain the Gemini AI to generate answers grounded ONLY in the retrieved document chunks.",
            "Objective 5: Provide a deterministic fallback if external AI APIs fail."
        ],
        "type": "content",
        "notes": "Slide Meaning: Lists what the project actually aims to achieve technically.\n\nWhat to say: 'Our main goal was to build a secure platform using a technique called RAG. Our technical objectives were to parse PDFs and Word docs accurately, ensure strict database isolation so user data is private, and use ChromaDB for semantic search. Most importantly, we wanted to force the Gemini AI to only answer using the document we feed it, completely minimizing hallucination.'\n\nTransition: 'Here is how our proposed system compares to existing methods.'"
    },
    {
        "title": "Existing System vs Proposed System",
        "bullets": [
            "Existing System (Manual / Ctrl+F): Misses semantic meaning. Very slow. Error-prone.",
            "Existing System (Public ChatGPT): High privacy risk. Often hallucinates legal precedent. Data is used for training.",
            "Proposed System (LexAI):",
            " - Semantic Vector Search understands context and meaning.",
            " - Strict RAG architecture grounds answers in verified text.",
            " - Local file and vector storage ensures privacy and data isolation.",
            " - Automated, structured extraction of risks and obligations."
        ],
        "type": "content",
        "notes": "Slide Meaning: Compares LexAI to what people currently do.\n\nWhat to say: 'Compared to Ctrl+F, which only finds exact text matches, LexAI understands context. Compared to public ChatGPT, LexAI is private. Your documents are stored locally on our server, and the AI is restricted by our backend from hallucinating external information.'\n\nTransition: 'Let's look at the key features we implemented to make this possible.'"
    },
    {
        "title": "Proposed System and Key Features",
        "bullets": [
            "Document Processing: Secure upload and raw text extraction from PDF/DOCX.",
            "Automated Summaries: AI generates executive summaries and highlights key clauses.",
            "Document-Specific Chat: A conversational interface restricted to the user's uploaded contract.",
            "General Legal Knowledge Base: A separate, admin-curated repository for general legal queries.",
            "User Isolation: Database-level filtering ensures privacy.",
            "Fallback Mechanism: A Python parser handles queries gracefully if the Gemini API is offline."
        ],
        "type": "content",
        "notes": "Slide Meaning: Summarizes the major functional modules of the application.\n\nWhat to say: 'Our key features include automated extraction of text, generating immediate executive summaries, and a dedicated document chat. We also built a separate General Legal Chat powered by an admin-curated Knowledge Base, ensuring general questions don't mix with private contract data. Finally, we implemented a fallback mechanism to keep the system running if the Gemini API goes down.'\n\nTransition: 'To build this, we carefully selected our technology stack.'"
    },
    {
        "title": "Technology Stack",
        "bullets": [
            "Frontend: HTML5, CSS3, Bootstrap 5, JavaScript (DOMPurify, marked.js).",
            "Backend Framework: Python and Flask.",
            "Relational Database: MySQL with Flask-SQLAlchemy (User Auth, Metadata).",
            "Document Parsing: PyMuPDF (PDFs) and python-docx (Word documents).",
            "Embeddings: SentenceTransformers (all-MiniLM-L6-v2).",
            "Vector Database: ChromaDB (Local semantic storage).",
            "Generative AI: Google Gemini API."
        ],
        "type": "content",
        "notes": "Slide Meaning: Lists the specific languages and libraries used.\n\nWhat to say: 'For the frontend, we used standard web technologies with Bootstrap 5. Our backend is entirely Python and Flask. For relational data like user accounts, we use MySQL. For extracting text, we use PyMuPDF. The core AI pipeline uses a local SentenceTransformers model to create embeddings, ChromaDB to store them, and the Google Gemini API to generate the final text.'\n\nTransition: 'Here is how these technologies fit together in our system architecture.'"
    },
    {
        "title": "System Architecture",
        "bullets": [
            "User Browser ➔ Flask Web Server ➔ (Authentication & Route Protection)",
            "Flask ➔ PyMuPDF / python-docx ➔ (Extract Text)",
            "Flask ➔ SentenceTransformers ➔ (Generate Vectors)",
            "Vectors ➔ ChromaDB ➔ (Store and Retrieve Semantics)",
            "Flask ➔ MySQL ➔ (Store Metadata and Chat History)",
            "Flask ➔ Gemini API ➔ (Generate Final Answer)"
        ],
        "type": "content",
        "notes": "Slide Meaning: Shows the data flow across the tech stack.\n\nWhat to say: 'This is the architecture flow. A user uploads a document through the browser. Flask receives it, authenticates the user, and uses PyMuPDF to extract text. The text is passed to our local SentenceTransformers model to create mathematical vectors. These are saved in ChromaDB. When a user asks a question, we search ChromaDB, pull the relevant text, and send only that text to the Gemini API to formulate a response.'\n\nTransition: 'Let's break down this workflow step-by-step.'"
    },
    {
        "title": "System Workflow",
        "bullets": [
            "1. User Registration/Login: Bcrypt password hashing secures the session.",
            "2. Upload: System validates file extensions and MIME types.",
            "3. Chunking: Text is divided into 500-word chunks with overlapping windows to preserve context.",
            "4. Indexing: Chunks are embedded and stored in ChromaDB with 'user_id' and 'doc_id' tags.",
            "5. Querying: User asks a question in the chat interface.",
            "6. Retrieval: System retrieves top-k chunks mathematically closest to the question.",
            "7. Generation: Chunks are bundled into a strict prompt for Gemini to answer."
        ],
        "type": "content",
        "notes": "Slide Meaning: The chronological steps of how the software operates internally.\n\nWhat to say: 'The workflow starts with secure Bcrypt login. When a file is uploaded, we don't just save it; we extract the text and chunk it into small overlapping pieces so we don't lose context. Each chunk gets embedded and tagged with the user's ID in ChromaDB. When a question is asked, we retrieve only the chunks tagged with that user's ID, ensuring absolute privacy before sending the context to Gemini.'\n\nTransition: 'This specific process of retrieving before generating is called RAG.'"
    },
    {
        "title": "AI and RAG Working",
        "bullets": [
            "RAG = Retrieval-Augmented Generation.",
            "Why RAG? Standard LLMs have token limits and hallucinate. RAG solves this.",
            "Step A (Retrieval): The system searches the local ChromaDB for factual text segments matching the query.",
            "Step B (Augmentation): The retrieved text is injected into a strict system prompt.",
            "Step C (Generation): The LLM is instructed: 'Answer ONLY using the provided text.'",
            "Result: Highly accurate, grounded responses with significantly reduced hallucination risk."
        ],
        "type": "content",
        "notes": "Slide Meaning: Explains the core AI mechanism (Retrieval-Augmented Generation).\n\nWhat to say: 'RAG stands for Retrieval-Augmented Generation. Instead of asking the AI a question directly and hoping it knows the answer, we first Retrieve the exact paragraphs from the user's contract. We then Augment our prompt with these paragraphs, and ask the LLM to Generate an answer based ONLY on that text. This is how we drastically reduce hallucinations.'\n\nTransition: 'To keep all this data safe, we implemented strong database security.'"
    },
    {
        "title": "Database and Security",
        "bullets": [
            "MySQL Authentication: Users are managed via Flask-Login. Passwords are salted and hashed using Bcrypt.",
            "Document Isolation: Uploaded files are stored securely on the local filesystem.",
            "Vector Filtering: Every ChromaDB query strictly filters by `user_id == current_user.id`.",
            "Data Separation: The General Legal Knowledge Base uses a completely separate ChromaDB collection from private documents.",
            "Input Sanitization: The frontend uses DOMPurify to prevent XSS attacks from rendered Markdown."
        ],
        "type": "content",
        "notes": "Slide Meaning: Details how user privacy and system security are maintained.\n\nWhat to say: 'Security is paramount for legal documents. We use Bcrypt for passwords. For vector retrieval, we enforce strict metadata filtering in ChromaDB—if the document ID doesn't belong to the logged-in user, the database simply will not return it. Furthermore, we keep the public Knowledge Base in a totally separate collection so public and private data never mix.'\n\nTransition: 'Here is what the actual implementation looks like.'"
    },
    {
        "title": "Testing and Validation",
        "bullets": [
            "Framework: System reliability is verified using the Pytest framework.",
            "Authentication Tests: Validated user registration, secure login routes, and session protection.",
            "Upload Validation: Verified that the system rejects unsupported file types (e.g., .exe).",
            "Database Isolation Tests: Confirmed that users cannot access documents or vector data belonging to other accounts.",
            "Fallback Testing: Verified that the local Python parser takes over gracefully when the external API is unreachable."
        ],
        "type": "content",
        "notes": "Slide Meaning: Explains how the system was tested for bugs and security flaws.\n\nWhat to say: 'We built a test suite using Pytest. We rigorously tested the authentication system and route protection. Most importantly, we tested database isolation to mathematically prove that one user cannot retrieve another user's contract data. We also successfully tested our fallback parser to ensure the app doesn't completely crash if Google's API goes down.'\n\nTransition: 'While the system works well, we have identified areas for future improvement.'"
    },
    {
        "title": "Limitations and Future Scope",
        "bullets": [
            "Limitation 1: No OCR. The system currently requires documents with embedded text layers. It cannot read scanned images.",
            "Limitation 2: No Multilingual Support. Processing is currently optimized for English legal text.",
            "Limitation 3: AI Inaccuracy. While RAG minimizes hallucination, no AI is 100% flawless.",
            "Future Scope: Integrate Tesseract OCR for scanned PDFs.",
            "Future Scope: Implement translation pipelines for regional language support.",
            "Future Scope: Migrate local ChromaDB and file storage to AWS/GCP for enterprise scalability."
        ],
        "type": "content",
        "notes": "Slide Meaning: Honest assessment of what the project can't do yet and how to improve it.\n\nWhat to say: 'Currently, LexAI cannot read scanned images because we haven't implemented Optical Character Recognition (OCR). It also only supports English. We also acknowledge that while RAG is highly effective, the AI can still occasionally misinterpret complex nuances. In the future, we plan to add Tesseract OCR, regional languages, and migrate our local storage to the cloud.'\n\nTransition: 'To conclude our presentation...'"
    },
    {
        "title": "Conclusion",
        "bullets": [
            "LexAI successfully demonstrates a secure, functional prototype for AI-assisted contract intelligence.",
            "By combining local vector indexing with RAG, we bridged the gap between complex legalese and accessible comprehension.",
            "Strict database-level isolation ensures user privacy is maintained.",
            "The deterministic fallback parser guarantees baseline resilience against API outages.",
            "LexAI serves as a powerful informational assistant, empowering users without replacing the need for professional legal counsel."
        ],
        "type": "content",
        "notes": "Slide Meaning: The final summary of the project's impact.\n\nWhat to say: 'In conclusion, LexAI is a secure and functional prototype that makes legal documents easier to understand. By processing data locally and using RAG, we protect user privacy and drastically reduce AI errors. While it doesn't replace a real lawyer, it empowers individuals and small businesses to read contracts with confidence.'\n\nTransition: 'Thank you for your time and attention.'"
    },
    {
        "title": "Thank You",
        "subtitle": "Questions & Answers\n\nLexAI – AI-Powered Legal Assistant & Contract Intelligence Platform",
        "type": "title",
        "notes": "Slide Meaning: Closing slide.\n\nWhat to say: 'Thank you for listening to our presentation. We would now be happy to answer any questions you might have about our implementation, architecture, or testing.'"
    }
]

# ---------------------------------------------------------
# 1. PPTX GENERATION
# ---------------------------------------------------------
def create_pptx():
    prs = Presentation()
    
    # 16:9 Aspect Ratio
    prs.slide_width = PptxInches(13.333)
    prs.slide_height = PptxInches(7.5)
    
    BG_COLOR = RGBColor(10, 25, 47)    # Dark Navy
    ACCENT_COLOR = RGBColor(0, 200, 200) # Teal
    TEXT_COLOR = RGBColor(255, 255, 255) # White
    
    # We will use blank layouts and draw our own master elements to ensure total control
    blank_layout = prs.slide_layouts[6]
    
    for slide_data in SLIDES_DATA:
        slide = prs.slides.add_slide(blank_layout)
        
        # Set Background
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = BG_COLOR
        
        # Draw Top Accent Line
        top_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, PptxInches(0.15))
        top_line.fill.solid()
        top_line.fill.fore_color.rgb = ACCENT_COLOR
        top_line.line.color.rgb = ACCENT_COLOR
        
        if slide_data["type"] == "title":
            # Title Slide Layout
            title_box = slide.shapes.add_textbox(PptxInches(1), PptxInches(2), prs.slide_width - PptxInches(2), PptxInches(1.5))
            tf = title_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = slide_data["title"]
            p.font.bold = True
            p.font.size = PptxPt(44)
            p.font.color.rgb = ACCENT_COLOR
            p.alignment = PP_ALIGN.CENTER
            
            sub_box = slide.shapes.add_textbox(PptxInches(1), PptxInches(4), prs.slide_width - PptxInches(2), PptxInches(2.5))
            stf = sub_box.text_frame
            stf.word_wrap = True
            for i, line in enumerate(slide_data.get("subtitle", "").split('\n')):
                sp = stf.add_paragraph() if i > 0 else stf.paragraphs[0]
                sp.text = line
                sp.font.size = PptxPt(20)
                sp.font.color.rgb = TEXT_COLOR
                sp.alignment = PP_ALIGN.CENTER
                
        elif slide_data["type"] == "content":
            # Header
            header_box = slide.shapes.add_textbox(PptxInches(0.5), PptxInches(0.4), prs.slide_width - PptxInches(1), PptxInches(1))
            htf = header_box.text_frame
            hp = htf.paragraphs[0]
            hp.text = slide_data["title"]
            hp.font.bold = True
            hp.font.size = PptxPt(36)
            hp.font.color.rgb = ACCENT_COLOR
            
            # Content / Bullets
            content_box = slide.shapes.add_textbox(PptxInches(0.8), PptxInches(1.5), prs.slide_width - PptxInches(1.6), PptxInches(5))
            ctf = content_box.text_frame
            ctf.word_wrap = True
            
            for i, bullet in enumerate(slide_data.get("bullets", [])):
                bp = ctf.add_paragraph() if i > 0 else ctf.paragraphs[0]
                bp.text = "• " + bullet if not bullet.startswith("- ") else "  " + bullet
                bp.font.size = PptxPt(24)
                bp.font.color.rgb = TEXT_COLOR
                bp.space_after = PptxPt(14)
                
        # Footer
        footer_box = slide.shapes.add_textbox(PptxInches(0.5), PptxInches(7.1), PptxInches(4), PptxInches(0.3))
        ftf = footer_box.text_frame
        fp = ftf.paragraphs[0]
        fp.text = "LexAI Project Presentation"
        fp.font.size = PptxPt(12)
        fp.font.color.rgb = RGBColor(150, 150, 150)
        
        # Add Speaker Notes
        if slide.has_notes_slide:
            notes_slide = slide.notes_slide
        else:
            notes_slide = slide.notes_slide # Accessing it creates it
        
        notes_tf = notes_slide.notes_text_frame
        notes_tf.text = slide_data.get("notes", "")

    prs.save("LexAI_Project_Presentation.pptx")
    print("Created LexAI_Project_Presentation.pptx")

# ---------------------------------------------------------
# 2. PDF GENERATION VIA PLAYWRIGHT (Guarantees fidelity without COM)
# ---------------------------------------------------------
async def create_pdf():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page { size: 13.33in 7.5in; margin: 0; }
            body { 
                margin: 0; padding: 0; background-color: #0A192F; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                color: #FFFFFF;
            }
            .slide { 
                width: 13.33in; height: 7.5in; 
                position: relative;
                page-break-after: always;
                box-sizing: border-box;
                overflow: hidden;
            }
            .top-bar {
                width: 100%; height: 0.15in; background-color: #00C8C8;
                position: absolute; top: 0; left: 0;
            }
            .footer {
                position: absolute; bottom: 0.2in; left: 0.5in;
                font-size: 14pt; color: #969696;
            }
            .title-slide {
                display: flex; flex-direction: column; 
                justify-content: center; align-items: center;
                height: 100%; text-align: center; padding: 1in;
            }
            .title-slide h1 { color: #00C8C8; font-size: 48pt; margin-bottom: 30px; }
            .title-slide h2 { font-size: 24pt; font-weight: normal; line-height: 1.5; white-space: pre-wrap; }
            
            .content-slide { padding: 0.8in 1in; }
            .content-slide h1 { color: #00C8C8; font-size: 40pt; margin-top: 0; margin-bottom: 40px; }
            .content-slide ul { list-style-type: disc; padding-left: 40px; }
            .content-slide li { font-size: 28pt; margin-bottom: 20px; line-height: 1.3; }
            .nested { list-style-type: circle; margin-left: 20px; color: #00C8C8; }
        </style>
    </head>
    <body>
    """
    
    for slide in SLIDES_DATA:
        html_content += '<div class="slide"><div class="top-bar"></div>'
        if slide["type"] == "title":
            html_content += f'<div class="title-slide"><h1>{slide["title"].replace(chr(10), "<br>")}</h1>'
            html_content += f'<h2>{slide.get("subtitle", "").replace(chr(10), "<br>")}</h2></div>'
        else:
            html_content += f'<div class="content-slide"><h1>{slide["title"]}</h1><ul>'
            for bullet in slide.get("bullets", []):
                if bullet.startswith("- "):
                    html_content += f'<li class="nested" style="list-style-type: circle;">{bullet[2:]}</li>'
                else:
                    html_content += f'<li>{bullet}</li>'
            html_content += '</ul></div>'
            
        html_content += '<div class="footer">LexAI Project Presentation</div></div>'
        
    html_content += "</body></html>"
    
    with open("presentation_temp.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{os.path.abspath('presentation_temp.html')}")
        await page.pdf(
            path="LexAI_Project_Presentation.pdf",
            width="13.33in",
            height="7.5in",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )
        await browser.close()
    
    if os.path.exists("presentation_temp.html"):
        os.remove("presentation_temp.html")
    print("Created LexAI_Project_Presentation.pdf")


# ---------------------------------------------------------
# 3. VIVA DOCX GENERATION
# ---------------------------------------------------------
def create_viva_doc():
    doc = Document()
    
    # Styling
    def add_h1(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(16)
        p.space_after = Pt(12)
        
    def add_h2(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(14)
        p.space_after = Pt(6)
        
    def add_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        if bold_prefix:
            run1 = p.add_run(bold_prefix)
            run1.bold = True
            p.add_run(text)
        else:
            p.add_run(text)
        p.space_after = Pt(10)
        
    add_h1("LexAI – Viva Preparation Guide")
    
    add_h2("1. 60-Second Project Introduction")
    add_p("Good morning. Our project is LexAI, an AI-powered legal assistant and contract intelligence platform. We built this to solve the problem of complex, lengthy legal documents that are difficult for average people to understand. Using Python, Flask, and a technique called Retrieval-Augmented Generation (RAG), our platform allows users to securely upload PDF and Word contracts, extracts the text locally, and uses a vector database to search for specific clauses. We then feed only those relevant clauses to the Gemini AI to generate accurate executive summaries and answer questions. Unlike public AI tools, LexAI keeps user documents completely isolated to ensure privacy and significantly reduces AI hallucinations.")

    add_h2("2. 2-Minute Project Workflow")
    add_p("The workflow begins when a user logs in securely using Bcrypt authentication. They upload a PDF or DOCX file, which is validated and saved locally. Our backend uses PyMuPDF to extract the raw text. Because LLMs have token limits, we slice this text into overlapping chunks. Each chunk is passed through a local SentenceTransformers model to generate mathematical embeddings—vectors that represent the meaning of the text. These are saved in our ChromaDB vector database and tagged with the user's ID.")
    add_p("When the user asks a question in the chat, we convert their question into a vector and perform a cosine similarity search in ChromaDB. The database returns the 3 or 4 chunks of the contract that best match the question. We bundle these chunks together with a strict system prompt and send them to the Gemini API. Gemini reads our chunks and formulates a final, human-readable answer. This ensures the AI is answering based strictly on the user's document, not making things up.")

    add_h2("3. Core Technologies Explained (Simple Terms)")
    add_p(" Flask:", " A lightweight Python web framework used to handle our routing, file uploads, and API connections.")
    add_p(" MySQL & SQLAlchemy:", " Our relational database. It stores user accounts, hashed passwords, and basic document metadata (like upload time).")
    add_p(" Embeddings:", " Mathematical representations of text. Sentences with similar meanings have vectors that are closer together in space.")
    add_p(" SentenceTransformers (all-MiniLM-L6-v2):", " The open-source local AI model we use to convert our document text into embeddings. It runs entirely on our server.")
    add_p(" ChromaDB:", " A specialized Vector Database designed to store embeddings and perform ultra-fast similarity searches.")
    add_p(" RAG (Retrieval-Augmented Generation):", " A hybrid AI architecture. Instead of relying on an LLM's memory, you 'Retrieve' facts from a local database and 'Augment' the LLM's prompt with those facts before 'Generating' the answer.")

    add_h2("4. Document Isolation & Security")
    add_p("When a chunk is embedded and saved in ChromaDB, we attach 'Metadata' to it—specifically `user_id` and `doc_id`. When a user runs a search, our backend code explicitly tells ChromaDB: `where={'user_id': current_user.id}`. If the chunk belongs to someone else, ChromaDB acts like it doesn't exist. This mathematically guarantees data isolation.")

    add_h2("5. Document Chat vs. General Legal Chat")
    add_p("Document-Specific Chat filters queries strictly against the user's uploaded file ID in ChromaDB. General Legal Chat uses a completely separate ChromaDB collection that is populated exclusively by the administrator with general legal knowledge. They do not cross over.")

    add_h2("6. 20 Likely Viva Questions & Answers")
    
    qas = [
        ("Q1. What is the main objective of your project?", "To democratize legal understanding by automating contract analysis using secure, private RAG architecture."),
        ("Q2. Why did you use Flask instead of Django?", "Flask is lightweight, highly customizable, and perfectly suited for creating specialized microservices and AI integrations without the overhead of Django."),
        ("Q3. What is RAG and why not just send the whole PDF to Gemini?", "RAG is Retrieval-Augmented Generation. We can't send huge PDFs directly because of token limits, high API costs, and the tendency of LLMs to lose context in the middle of massive prompts. RAG isolates just the relevant clauses."),
        ("Q4. Does your system eliminate AI hallucinations?", "No AI is 100% immune to hallucination. However, RAG drastically reduces the risk because we strictly instruct the AI to answer ONLY using the retrieved text provided in the prompt."),
        ("Q5. How do you handle user passwords?", "Passwords are salted and mathematically hashed using the Bcrypt algorithm before being saved to MySQL. They are never stored in plain text."),
        ("Q6. What happens if the Gemini API goes offline?", "We built a deterministic fallback parser. If the API fails, our system catches the error, retrieves the raw text chunks directly from ChromaDB, formats them nicely, and presents them to the user."),
        ("Q7. Can your system read scanned physical documents?", "Currently, no. We use PyMuPDF which requires documents to have embedded text layers. Adding Tesseract OCR for scanned images is part of our future scope."),
        ("Q8. Why use ChromaDB?", "It is an open-source, highly efficient vector database that integrates perfectly with Python and runs locally, which is crucial for data privacy in legal tech."),
        ("Q9. What embedding model did you use and why?", "We used 'all-MiniLM-L6-v2' via SentenceTransformers. It provides a great balance of semantic accuracy and very fast execution speed without requiring heavy GPU resources."),
        ("Q10. How do you prevent User A from seeing User B's documents?", "In ChromaDB, every text chunk is stored with metadata containing the user_id. Every search query forces a strict metadata filter matching the logged-in user's ID."),
        ("Q11. What is the difference between Extractive and Abstractive summarization?", "Extractive copies exact sentences from the text. Abstractive generates new sentences that capture the meaning. LexAI uses an abstractive approach via the Gemini LLM based on extracted chunks."),
        ("Q12. What frontend technologies were used?", "HTML5, CSS3, JavaScript, and Bootstrap 5 for responsiveness. We also use DOMPurify to prevent XSS attacks when rendering markdown."),
        ("Q13. How did you test the system?", "We used the Pytest framework. We tested the authentication routes, file validation logic, and specifically ran database isolation tests to ensure users can't access unauthorized data."),
        ("Q14. Why separate Document Chat and General Legal Chat?", "To prevent data contamination. A user asking a general question shouldn't accidentally pull answers from their private, highly specific business contract."),
        ("Q15. What format does ChromaDB store vectors in?", "It stores them as dense high-dimensional floating-point arrays. Our model generates 384-dimensional vectors."),
        ("Q16. How does Semantic Search differ from Keyword Search?", "Keyword search looks for exact string matches (e.g., 'car'). Semantic search converts meaning into math, so searching for 'automobile' will mathematically match 'car'."),
        ("Q17. What happens if I upload an invalid file like an .exe?", "The Flask backend uses `werkzeug` utilities to securely check the MIME type and file extension. It will reject the file before processing begins."),
        ("Q18. Why chunk the text? Why use overlapping windows?", "We chunk text to respect LLM token limits. We use overlapping windows (e.g., 50 words from the previous chunk) so that a legal sentence isn't accidentally cut in half and stripped of its context."),
        ("Q19. What is the biggest limitation of your project right now?", "The lack of OCR for scanned PDFs and the lack of multilingual support, which restricts accessibility for non-English speakers."),
        ("Q20. What is your future scope?", "Migrating local ChromaDB storage to a scalable cloud environment (AWS/GCP), adding OCR capabilities, and building regional language translation pipelines.")
    ]
    
    for q, a in qas:
        add_p(a, bold_prefix=q + " ")

    doc.save("LexAI_Viva_Preparation.docx")
    print("Created LexAI_Viva_Preparation.docx")

if __name__ == "__main__":
    create_pptx()
    create_viva_doc()
    asyncio.run(create_pdf())
