import os
import asyncio
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from playwright.async_api import async_playwright

OUTPUT_DIR = "Seminar_Synopsis_Output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------- DOCX GENERATION -----------------

def set_font(run, name='Bookman Old Style', size=12, bold=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold

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
    
    # Section 1: Cover Page
    s1 = doc.sections[0]
    setup_margins_and_borders(s1)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add spacing at the top
    p.add_run("\n\n")
    
    set_font(p.add_run("SEMINAR SYNOPSIS\n"), bold=True)
    set_font(p.add_run("ON\n\n"), bold=True)
    set_font(p.add_run("Enhancing Legal Efficiency Through AI\n\n\n"), bold=True)
    
    set_font(p.add_run("Submitted to\n"), bold=True)
    set_font(p.add_run("Chhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai\n\n"), bold=True)
    
    if os.path.exists("csmu_logo.png"):
        p.add_run().add_picture("csmu_logo.png", width=Inches(1.5))
        p.add_run("\n\n")
    else:
        p.add_run("\n\n[University Logo]\n\n")
        
    set_font(p.add_run("For the partial fulfillment of requirement for the Degree of\n"), bold=False)
    set_font(p.add_run("MASTER OF COMPUTER APPLICATION\n\n\n"), bold=True)
    
    set_font(p.add_run("Submitted By\n\n"), bold=True)
    set_font(p.add_run("Rohan Bongane\n\n\n"), bold=True)
    
    set_font(p.add_run("Guide\n\n"), bold=True)
    set_font(p.add_run("Dr. Surekha Kohle\n"), bold=True)
    set_font(p.add_run("Department of Computer Science & Information Technology\n"), bold=True)
    set_font(p.add_run("Chhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai\n\n"), bold=True)
    
    set_font(p.add_run("Academic Year:\n"), bold=True)
    set_font(p.add_run("2026–27\n"), bold=True)
    
    # Section 2: Main Content
    s2 = doc.add_section()
    setup_margins_and_borders(s2)
    
    def add_heading(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        set_font(run, bold=True)
        return p
        
    def add_paragraph(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(text)
        set_font(run)
        return p
        
    add_heading("1. Introduction")
    add_paragraph("The legal sector relies heavily on processing massive volumes of text, including case laws, commercial contracts, and litigation evidence. Handling this information overload manually leads to significant administrative overhead, time-consuming research, and severe case backlogs. Maximizing the speed and accuracy of these workflows is the core principle of legal efficiency. Artificial Intelligence (AI) serves as a critical catalyst in this domain by automating repetitive and standardized tasks. By leveraging Natural Language Processing (NLP) and Large Language Models (LLMs), AI empowers legal professionals to quickly extract meaning and context from extensive documents, allowing them to focus their expertise on complex legal reasoning rather than manual reading and sorting.")
    
    add_heading("2. Aim and Objectives")
    add_paragraph("The primary aim of this seminar is to explore how Artificial Intelligence enhances operational efficiency within the legal sector. The key objectives are to analyze the application of AI in automated legal research and contract analysis, and to examine how document summarization condenses lengthy judgments into accessible formats. Furthermore, the seminar studies the implementation of Semantic Search to retrieve precedents based on context rather than exact keywords, and evaluates Retrieval-Augmented Generation (RAG) as a mechanism to minimize factual inaccuracies in AI-generated legal responses.")
    
    add_heading("3. Main Topics Covered")
    add_paragraph("Artificial Intelligence offers diverse applications in modern legal practice. Contract analysis tools automatically extract crucial clauses, such as termination and liability terms, while flagging unusual or unfavorable risks during corporate due diligence. E-discovery systems filter millions of emails to locate litigation evidence in seconds, and AI-driven translation services convert complex legal documents into regional languages automatically.")
    add_paragraph("In the Indian legal context, specialized initiatives are demonstrating the practical benefits of AI. SUVAS (Supreme Court Vidhik Anuvaad Software) is actively translating Supreme Court judgments into regional Indian languages to democratize access to justice. SUPACE (Supreme Court Portal for Assistance in Court's Efficiency) operates as an AI research assistant designed to help judges process case facts rapidly. These tools build upon the foundational digitalization achieved by the e-Courts Project.")
    add_paragraph("To ensure accuracy, the legal sector is increasingly adopting Retrieval-Augmented Generation (RAG), which grounds AI models by forcing them to retrieve verified legal precedents before generating an answer. Despite these advancements, significant risks remain. AI models are prone to 'hallucinations,' occasionally inventing fake legal cases or citations. Additionally, uploading sensitive client data to public AI models poses severe confidentiality and privacy risks, while algorithmic bias can perpetuate systemic inequalities in predictive legal systems.")
    
    add_heading("4. Conclusion")
    add_paragraph("Artificial Intelligence is fundamentally transforming the legal sector by processing thousands of pages in seconds, reducing administrative burdens, and improving overall access to justice. Technologies like Semantic Search and RAG make the retrieval of legal information faster and significantly more accurate than traditional keyword-based methods. However, AI remains an assistive technology designed to support rather than replace human expertise. Given the ethical risks surrounding privacy, bias, and hallucination, rigorous human verification, professional oversight, and ethical accountability remain absolutely essential in all legal AI applications.")
    
    add_heading("5. References")
    add_paragraph("1. Artificial Intelligence and the Legal Profession (Various Industry Reports).")
    add_paragraph("2. Overview of SUPACE and SUVAS (Supreme Court of India tech initiatives).")
    add_paragraph("3. Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.")
    
    docx_path = os.path.join(OUTPUT_DIR, "Enhancing_Legal_Efficiency_AI_Seminar_Synopsis.docx")
    doc.save(docx_path)
    return docx_path

# ----------------- PDF GENERATION -----------------

async def create_pdf():
    logo_path = os.path.abspath("csmu_logo.png").replace("\\", "/")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                margin: 1in;
            }}
            body {{
                font-family: "Bookman Old Style", "Times New Roman", serif;
                font-size: 12pt;
                line-height: 1.5;
                color: black;
                text-align: justify;
                margin: 0;
                padding: 0;
            }}
            .page-border {{
                position: fixed;
                top: -0.5in; left: -0.5in; right: -0.5in; bottom: -0.5in;
                border: 1px solid black;
                z-index: -100;
                pointer-events: none;
            }}
            .cover-page {{
                text-align: center;
                page-break-after: always;
            }}
            .cover-page p {{
                margin: 8px 0;
            }}
            .cover-page .title-space {{
                margin-top: 30px;
            }}
            .bold {{
                font-weight: bold;
            }}
            .logo-img {{
                width: 1.5in;
                height: auto;
                margin: 20px 0;
            }}
            h2 {{
                font-size: 12pt;
                font-weight: bold;
                margin-top: 24px;
                margin-bottom: 12px;
                text-align: left;
            }}
            p.content-para {{
                margin-bottom: 12px;
                margin-top: 0;
            }}
            p.ref-para {{
                margin-bottom: 6px;
                margin-top: 0;
            }}
        </style>
    </head>
    <body>
        <div class="page-border"></div>
        
        <!-- Cover Page -->
        <div class="cover-page">
            <div class="title-space"></div>
            <p class="bold">SEMINAR SYNOPSIS</p>
            <p class="bold">ON</p>
            <p class="bold">Enhancing Legal Efficiency Through AI</p>
            <br>
            <p class="bold">Submitted to</p>
            <p class="bold">Chhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai</p>
            
            <img src="file:///{logo_path}" class="logo-img" alt="University Logo">
            
            <p>For the partial fulfillment of requirement for the Degree of</p>
            <p class="bold">MASTER OF COMPUTER APPLICATION</p>
            <br>
            <p class="bold">Submitted By</p>
            <p class="bold">Rohan Bongane</p>
            <br>
            <p class="bold">Guide</p>
            <p class="bold">Dr. Surekha Kohle</p>
            <p class="bold">Department of Computer Science & Information Technology</p>
            <p class="bold">Chhatrapati Shivaji Maharaj University, Panvel, Navi Mumbai</p>
            <br>
            <p class="bold">Academic Year:</p>
            <p class="bold">2026–27</p>
        </div>
        
        <!-- Main Content -->
        <div>
            <h2>1. Introduction</h2>
            <p class="content-para">The legal sector relies heavily on processing massive volumes of text, including case laws, commercial contracts, and litigation evidence. Handling this information overload manually leads to significant administrative overhead, time-consuming research, and severe case backlogs. Maximizing the speed and accuracy of these workflows is the core principle of legal efficiency. Artificial Intelligence (AI) serves as a critical catalyst in this domain by automating repetitive and standardized tasks. By leveraging Natural Language Processing (NLP) and Large Language Models (LLMs), AI empowers legal professionals to quickly extract meaning and context from extensive documents, allowing them to focus their expertise on complex legal reasoning rather than manual reading and sorting.</p>
            
            <h2>2. Aim and Objectives</h2>
            <p class="content-para">The primary aim of this seminar is to explore how Artificial Intelligence enhances operational efficiency within the legal sector. The key objectives are to analyze the application of AI in automated legal research and contract analysis, and to examine how document summarization condenses lengthy judgments into accessible formats. Furthermore, the seminar studies the implementation of Semantic Search to retrieve precedents based on context rather than exact keywords, and evaluates Retrieval-Augmented Generation (RAG) as a mechanism to minimize factual inaccuracies in AI-generated legal responses.</p>
            
            <h2>3. Main Topics Covered</h2>
            <p class="content-para">Artificial Intelligence offers diverse applications in modern legal practice. Contract analysis tools automatically extract crucial clauses, such as termination and liability terms, while flagging unusual or unfavorable risks during corporate due diligence. E-discovery systems filter millions of emails to locate litigation evidence in seconds, and AI-driven translation services convert complex legal documents into regional languages automatically.</p>
            <p class="content-para">In the Indian legal context, specialized initiatives are demonstrating the practical benefits of AI. SUVAS (Supreme Court Vidhik Anuvaad Software) is actively translating Supreme Court judgments into regional Indian languages to democratize access to justice. SUPACE (Supreme Court Portal for Assistance in Court's Efficiency) operates as an AI research assistant designed to help judges process case facts rapidly. These tools build upon the foundational digitalization achieved by the e-Courts Project.</p>
            <p class="content-para">To ensure accuracy, the legal sector is increasingly adopting Retrieval-Augmented Generation (RAG), which grounds AI models by forcing them to retrieve verified legal precedents before generating an answer. Despite these advancements, significant risks remain. AI models are prone to 'hallucinations,' occasionally inventing fake legal cases or citations. Additionally, uploading sensitive client data to public AI models poses severe confidentiality and privacy risks, while algorithmic bias can perpetuate systemic inequalities in predictive legal systems.</p>
            
            <h2>4. Conclusion</h2>
            <p class="content-para">Artificial Intelligence is fundamentally transforming the legal sector by processing thousands of pages in seconds, reducing administrative burdens, and improving overall access to justice. Technologies like Semantic Search and RAG make the retrieval of legal information faster and significantly more accurate than traditional keyword-based methods. However, AI remains an assistive technology designed to support rather than replace human expertise. Given the ethical risks surrounding privacy, bias, and hallucination, rigorous human verification, professional oversight, and ethical accountability remain absolutely essential in all legal AI applications.</p>
            
            <h2>5. References</h2>
            <p class="ref-para">1. Artificial Intelligence and the Legal Profession (Various Industry Reports).</p>
            <p class="ref-para">2. Overview of SUPACE and SUVAS (Supreme Court of India tech initiatives).</p>
            <p class="ref-para">3. Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.</p>
        </div>
    </body>
    </html>
    """
    
    html_path = os.path.join(OUTPUT_DIR, "temp_synopsis.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    pdf_path = os.path.join(OUTPUT_DIR, "Enhancing_Legal_Efficiency_AI_Seminar_Synopsis.pdf")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file:///{os.path.abspath(html_path).replace(chr(92), '/')}")
        
        await page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True
        )
        await browser.close()
        
    return pdf_path

if __name__ == "__main__":
    print("Generating DOCX...")
    docx_out = create_docx()
    print(f"DOCX created at: {docx_out}")
    
    print("Generating PDF...")
    pdf_out = asyncio.run(create_pdf())
    print(f"PDF created at: {pdf_out}")
