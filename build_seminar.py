import os
import asyncio
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from pptx import Presentation
from pptx.util import Inches as PptxInches, Pt as PptxPt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from playwright.async_api import async_playwright
import pymupdf as fitz

# ---------------------------------------------------------
# CONTENT DEFINITIONS
# ---------------------------------------------------------

SLIDES_DATA = [
    {
        "title": "Enhancing Legal Efficiency\nThrough AI",
        "subtitle": "Academic Seminar Presentation\n\nPresenter: [Your Name]\nDepartment: [Your Department]\nCollege/University: [Your College]\nGuide: [Guide Name]\nDate: [Date]",
        "type": "title",
        "notes": "Slide Meaning: This is your introductory slide.\n\nSpeaking Script (60s): 'Good morning respected faculty and peers. My name is [Your Name]. Today, I am presenting my seminar on \"Enhancing Legal Efficiency Through AI\". We will explore how Artificial Intelligence is transforming the legal sector from a slow, manual process into a highly optimized digital workflow.'\n\nTransition: 'Let's start by defining what we mean by legal efficiency.'\n\nQuestions: \nQ: What is the core theme of your seminar? \nA: How AI technologies optimize legal research and document processing to save time and reduce errors."
    },
    {
        "title": "Introduction: What is Legal Efficiency?",
        "bullets": [
            "Legal Efficiency: Maximizing the speed and accuracy of legal workflows while minimizing administrative overhead.",
            "The legal sector relies heavily on processing massive volumes of text (case laws, contracts, evidence).",
            "Efficiency is critical to reducing case backlogs and making legal services accessible.",
            "AI serves as a catalyst to automate repetitive tasks, allowing professionals to focus on complex legal reasoning."
        ],
        "type": "content",
        "notes": "Slide Meaning: Defines the concept of efficiency in a legal context.\n\nSpeaking Script: 'Legal efficiency is about doing more with less—maximizing accuracy and speed without increasing administrative burden. The legal system runs on text: thousands of pages of case laws and contracts. By using AI to automate the repetitive reading and sorting of this text, we allow legal professionals to focus on what they do best: applying legal reasoning.'\n\nExample: Think of AI as a very fast paralegal that can read 10,000 pages in a minute to find a single relevant clause.\n\nTransition: 'But why is this necessary? Let's look at the current challenges.'"
    },
    {
        "title": "Challenges in Traditional Legal Work",
        "bullets": [
            "Information Overload: Contracts and case files often span hundreds of pages.",
            "Time-Consuming Research: Finding relevant legal precedents manually takes hours or days.",
            "Repetitive Paperwork: Drafting standard contracts and notices involves high administrative workload.",
            "Keyword Limitations: Traditional search engines miss context if exact synonyms aren't used.",
            "Case Backlogs: Manual processing contributes to severe delays in judicial systems."
        ],
        "type": "content",
        "notes": "Slide Meaning: Highlights the bottlenecks in traditional law.\n\nSpeaking Script: 'Traditionally, lawyers face severe information overload. Finding a specific precedent among decades of case law using basic keyword searches takes days. If a lawyer searches for \"penalty\" but the document says \"liquidated damages\", a standard search fails. This manual processing directly contributes to the massive case backlogs we see globally and in India.'\n\nTransition: 'To understand how we solve this, we first need to define Artificial Intelligence.'"
    },
    {
        "title": "What Is Artificial Intelligence?",
        "bullets": [
            "Artificial Intelligence (AI): Machines simulating human intelligence to solve problems.",
            "Machine Learning (ML): Algorithms that learn patterns from data without explicit programming.",
            "Natural Language Processing (NLP): AI focusing on understanding and generating human language.",
            "Large Language Models (LLM): Massive neural networks trained on vast text data to understand context (e.g., GPT-4, Gemini)."
        ],
        "type": "content",
        "notes": "Slide Meaning: A quick, simple primer on AI terminology.\n\nSpeaking Script: 'AI is a broad term for machines solving problems. Under that umbrella is Machine Learning, where systems learn from data. For the legal sector, the most important branch is NLP—Natural Language Processing. This is what allows computers to actually understand sentences. Finally, Large Language Models, or LLMs like ChatGPT and Gemini, are advanced NLP models that can generate human-like text and summarize complex documents.'\n\nTransition: 'So, how do these technologies actually apply to a legal workflow?'"
    },
    {
        "title": "How AI Works in the Legal Sector",
        "bullets": [
            "1. Data Ingestion: Raw documents (PDFs, Scans) are uploaded.",
            "2. Text Extraction: OCR and parsing tools extract raw text.",
            "3. NLP Processing: The text is analyzed for meaning, entities, and context.",
            "4. Semantic Search / AI Review: Relevant sections are retrieved and summarized by an LLM.",
            "5. Human Verification: Lawyers review the AI's output for final legal judgment."
        ],
        "type": "content",
        "notes": "Slide Meaning: The step-by-step pipeline of legal AI.\n\nSpeaking Script: 'The workflow is straightforward. First, physical or digital documents are ingested. Tools extract the raw text. Then, NLP algorithms process this text to understand its meaning. The AI retrieves relevant sections and summarizes them. However, step 5 is the most critical: Human Verification. AI does not replace the lawyer; it prepares the data for the lawyer's final judgment.'\n\nTransition: 'Let's explore the major applications built on this pipeline.'"
    },
    {
        "title": "Major Applications of AI in Law",
        "bullets": [
            "Legal Research: Quickly finding relevant case laws and statutes.",
            "Document Summarization: Condensing 50-page judgments into 1-page executive summaries.",
            "Contract Analysis: Automating the review of NDAs and commercial agreements.",
            "E-Discovery: Filtering millions of emails and files for litigation evidence.",
            "Translation Services: Converting legal documents into regional languages automatically."
        ],
        "type": "content",
        "notes": "Slide Meaning: The main use cases of AI in the real world.\n\nSpeaking Script: 'AI is used in several areas. It powers Legal Research to find case laws instantly. It is heavily used in Document Summarization to condense long judgments. Contract Analysis tools automatically review NDAs. E-Discovery uses AI to scan millions of corporate emails during lawsuits to find evidence. Lastly, AI translation is crucial for multilingual countries.'\n\nTransition: 'Let's look deeper into Contract Analysis.'"
    },
    {
        "title": "AI-Powered Contract Analysis",
        "bullets": [
            "Clause Extraction: Automatically identifying termination, liability, and renewal clauses.",
            "Risk Flagging: Highlighting unusual or highly unfavorable terms.",
            "Obligation Tracking: Creating checklists of what each party must do and by when.",
            "Due Diligence: Rapidly reviewing thousands of contracts during corporate mergers.",
            "Crucial Caveat: AI outputs serve as preliminary reviews and require human verification."
        ],
        "type": "content",
        "notes": "Slide Meaning: How AI reviews contracts specifically.\n\nSpeaking Script: 'In contract analysis, AI acts as a high-speed scanner. It extracts specific clauses like liability or termination rules. It can flag risks—for example, if a penalty clause is unusually high compared to standard contracts. During corporate mergers, this allows companies to review thousands of contracts in days instead of months. But again, outputs must be verified by humans.'\n\nTransition: 'Another massive application is Legal Research.'"
    },
    {
        "title": "AI for Legal Research & Case Management",
        "bullets": [
            "Semantic Search: Searching by meaning rather than exact keywords (e.g., finding \"vehicle\" when searching for \"car\").",
            "Precedent Retrieval: Matching a current case's facts against millions of past judgments.",
            "Case Organization: Automatically sorting case files, evidence, and chronological timelines.",
            "Impact: Reduces research time from days to minutes, ensuring critical precedents are not missed."
        ],
        "type": "content",
        "notes": "Slide Meaning: How AI helps lawyers find past cases and organize current ones.\n\nSpeaking Script: 'Legal research relies on finding past precedents. Traditional searches require exact keywords. AI uses Semantic Search, meaning it understands concepts. If you search for \"car accident\", it will also find cases mentioning \"motor vehicle collision\". This reduces research time drastically and helps organize case timelines automatically.'\n\nTransition: 'This advanced search is often powered by Generative AI and RAG.'"
    },
    {
        "title": "Generative AI & Retrieval-Augmented Generation (RAG)",
        "bullets": [
            "Generative AI: Models (like LLMs) that generate natural text answers.",
            "The Problem: Unconstrained LLMs can \"hallucinate\" or make up fake laws.",
            "The Solution (RAG):",
            " - Retrieval: The system searches a verified legal database first.",
            " - Augmentation: It provides the retrieved documents to the LLM.",
            " - Generation: The LLM answers based strictly on the retrieved facts.",
            "Note: RAG greatly minimizes, but does not entirely eliminate, inaccuracies."
        ],
        "type": "content",
        "notes": "Slide Meaning: Explains how to stop AI from lying (hallucinating) using RAG.\n\nSpeaking Script: 'Generative AI is powerful but dangerous in law because it can \"hallucinate\" or invent fake laws. To fix this, the industry uses RAG: Retrieval-Augmented Generation. First, we Retrieve verified documents from a secure database. Then, we Augment the AI's prompt with these documents, telling it to Generate an answer strictly based on them. This grounds the AI in reality.'\n\nTransition: 'What does this look like in practice?'"
    },
    {
        "title": "Practical Examples and Use Cases",
        "bullets": [
            "Illustrative Example 1 (Corporate Law): A legal department uses AI to scan 500 vendor contracts to ensure compliance with new data privacy laws.",
            "Illustrative Example 2 (Public Defenders): Overworked lawyers use AI to summarize massive police reports to quickly identify inconsistencies in evidence.",
            "Illustrative Example 3 (Access to Justice): A small business owner uses a legal chatbot to understand the basic terms of a commercial lease before hiring a lawyer."
        ],
        "type": "content",
        "notes": "Slide Meaning: Real-world, practical scenarios of AI usage.\n\nSpeaking Script: 'Let's look at practical examples. A corporate legal department can use AI to scan 500 contracts overnight to check for data privacy compliance. An overworked public defender can use it to summarize hundreds of pages of police reports. And for ordinary citizens, simple AI chatbots can help explain a commercial lease in plain English, improving access to justice.'\n\nTransition: 'These examples highlight several core benefits.'"
    },
    {
        "title": "Benefits of AI in Legal Work",
        "bullets": [
            "Unprecedented Speed: Processing thousands of pages in seconds.",
            "Enhanced Consistency: AI does not suffer from fatigue during repetitive document review.",
            "Democratized Access: Helps ordinary citizens understand complex legal jargon.",
            "Administrative Efficiency: Automates filing, scheduling, and metadata tagging.",
            "Cost Reduction: Lowers the billable hours required for preliminary research."
        ],
        "type": "content",
        "notes": "Slide Meaning: Summary of the positive impacts.\n\nSpeaking Script: 'The benefits are clear. Speed is the most obvious, but consistency is equally important—an AI doesn't get tired reading the 500th contract at 2 AM. It also lowers the cost of preliminary research and democratizes access, making basic legal understanding affordable for the general public.'\n\nTransition: 'However, this technology is not without significant risks.'"
    },
    {
        "title": "Risks, Limitations, and Ethical Issues",
        "bullets": [
            "Hallucinations: AI inventing fake cases (e.g., The 2023 US case where lawyers were sanctioned for submitting fake ChatGPT citations).",
            "Confidentiality & Privacy: Inputting sensitive client data into public AI models risks data breaches.",
            "Algorithmic Bias: AI trained on historical data may perpetuate systemic biases in predictive policing or sentencing.",
            "Explainability: The \"Black Box\" problem—it's difficult to prove exactly how an AI reached a conclusion.",
            "Accountability: The human lawyer is always legally responsible for the final output."
        ],
        "type": "content",
        "notes": "Slide Meaning: The dangers and ethical hurdles of legal AI.\n\nSpeaking Script: 'There are severe risks. In 2023, lawyers in the US were sanctioned for submitting court briefs with fake cases completely invented by ChatGPT. This is why human verification is critical. Furthermore, putting confidential client data into public AI violates privacy. There are also concerns about bias in AI models. Ultimately, a machine cannot be sued or disbarred—the human lawyer remains 100% accountable.'\n\nTransition: 'How is this technology being adopted in India specifically?'"
    },
    {
        "title": "AI in the Indian Legal Context",
        "bullets": [
            "SUVAS (Supreme Court Vidhik Anuvaad Software): An AI tool translating Supreme Court judgments into regional Indian languages to improve accessibility.",
            "SUPACE (Supreme Court Portal for Assistance in Court's Efficiency): An AI research assistant designed to help judges process case facts and research efficiently.",
            "e-Courts Project: Primarily focused on digitalization, creating the essential foundation of digital records required for future AI deployment.",
            "Context: The Indian Judiciary is carefully adopting AI for administrative and research efficiency, not for decision-making."
        ],
        "type": "content",
        "notes": "Slide Meaning: Verifiable facts about AI adoption in the Indian Supreme Court.\n\nSpeaking Script: 'In India, the Supreme Court has officially launched two major AI initiatives. SUVAS is an AI translation tool that translates judgments into regional languages, aiding access to justice. SUPACE is an AI research assistant designed specifically for judges. It's important to note that the judiciary uses AI strictly for research and administrative efficiency, never for making judicial decisions.'\n\nTransition: 'Looking globally and locally, what does the future hold?'"
    },
    {
        "title": "Future Scope",
        "bullets": [
            "Advanced Multilingual Processing: Seamless legal assistance across diverse regional dialects.",
            "Hyper-Accurate Retrieval: Next-generation RAG models approaching zero-hallucination rates for factual queries.",
            "Open-Source Legal Models: Development of specialized, secure, offline LLMs trained exclusively on verified legal data.",
            "Human-AI Synergy: Transitioning from AI as a \"tool\" to AI as a collaborative \"co-counsel\".",
            "Regulatory Frameworks: Establishing strict ethical guidelines for AI use in law."
        ],
        "type": "content",
        "notes": "Slide Meaning: Where the technology is heading in the next 5-10 years.\n\nSpeaking Script: 'The future scope includes advanced multilingual support and hyper-accurate retrieval systems. We will see the rise of open-source legal models that run entirely offline to guarantee data privacy. We will also see governments establishing strict regulatory frameworks to govern how AI can be ethically used in legal practice.'\n\nTransition: 'To summarize our presentation...'"
    },
    {
        "title": "Conclusion",
        "bullets": [
            "AI is transforming the legal sector by automating repetitive tasks, enhancing research, and improving access to justice.",
            "Technologies like Semantic Search and RAG make legal information retrieval faster and more accurate than ever before.",
            "However, AI is an assistive technology, not a replacement for human expertise.",
            "Issues regarding privacy, bias, and hallucination require strict professional oversight.",
            "Human judgment, ethical accountability, and legal verification remain absolutely essential."
        ],
        "type": "content",
        "notes": "Slide Meaning: The final takeaway message.\n\nSpeaking Script: 'To conclude, AI is fundamentally transforming legal efficiency. It speeds up research and breaks down barriers. However, it is an assistive tool. Because of risks like hallucinations and data privacy, it cannot replace the ethical accountability and nuanced judgment of a qualified human lawyer. The future of law is human-AI collaboration.'\n\nTransition: 'Thank you for your attention.'"
    },
    {
        "title": "References & Questions",
        "bullets": [
            "References:",
            "1. Artificial Intelligence and the Legal Profession (Various Industry Reports).",
            "2. Overview of SUPACE and SUVAS (Supreme Court of India tech initiatives).",
            "3. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al., 2020).",
            "\nThank You!",
            "Any Questions?"
        ],
        "type": "content",
        "notes": "Slide Meaning: Closing slide with academic references.\n\nSpeaking Script: 'Here are some of the foundational concepts and initiatives referenced today, including the Supreme Court's AI portals and the foundational research on RAG. Thank you very much for listening. I am now open to any questions you might have.'"
    }
]

# ---------------------------------------------------------
# 1. PPTX GENERATION
# ---------------------------------------------------------
def create_pptx():
    prs = Presentation()
    prs.slide_width = PptxInches(13.333)
    prs.slide_height = PptxInches(7.5)
    
    BG_COLOR = RGBColor(10, 25, 47)    # Navy Blue
    ACCENT_COLOR = RGBColor(0, 200, 200) # Teal
    TEXT_COLOR = RGBColor(255, 255, 255) # White
    
    blank_layout = prs.slide_layouts[6]
    
    for slide_data in SLIDES_DATA:
        slide = prs.slides.add_slide(blank_layout)
        
        # Background
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = BG_COLOR
        
        # Top Accent Line
        top_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, PptxInches(0.15))
        top_line.fill.solid()
        top_line.fill.fore_color.rgb = ACCENT_COLOR
        top_line.line.color.rgb = ACCENT_COLOR
        
        if slide_data["type"] == "title":
            # Title Slide
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
            # Content Slide Header
            header_box = slide.shapes.add_textbox(PptxInches(0.5), PptxInches(0.4), prs.slide_width - PptxInches(1), PptxInches(1))
            htf = header_box.text_frame
            hp = htf.paragraphs[0]
            hp.text = slide_data["title"]
            hp.font.bold = True
            hp.font.size = PptxPt(36)
            hp.font.color.rgb = ACCENT_COLOR
            
            # Content Bullets
            content_box = slide.shapes.add_textbox(PptxInches(0.8), PptxInches(1.5), prs.slide_width - PptxInches(1.6), PptxInches(5))
            ctf = content_box.text_frame
            ctf.word_wrap = True
            
            for i, bullet in enumerate(slide_data.get("bullets", [])):
                bp = ctf.add_paragraph() if i > 0 else ctf.paragraphs[0]
                if bullet.startswith(" - "):
                    bp.text = "  " + bullet
                elif bullet == "\nThank You!" or bullet == "Any Questions?" or bullet == "References:":
                    bp.text = bullet
                else:
                    bp.text = "• " + bullet
                
                bp.font.size = PptxPt(24)
                bp.font.color.rgb = TEXT_COLOR
                bp.space_after = PptxPt(14)
                
        # Footer text
        footer_box = slide.shapes.add_textbox(PptxInches(0.5), PptxInches(7.1), PptxInches(4), PptxInches(0.3))
        ftf = footer_box.text_frame
        fp = ftf.paragraphs[0]
        fp.text = "Enhancing Legal Efficiency Through AI"
        fp.font.size = PptxPt(12)
        fp.font.color.rgb = RGBColor(150, 150, 150)
        
        # Add Speaker Notes
        notes_slide = slide.notes_slide if slide.has_notes_slide else slide.notes_slide
        notes_tf = notes_slide.notes_text_frame
        notes_tf.text = slide_data.get("notes", "")

    prs.save("Enhancing_Legal_Efficiency_Through_AI.pptx")
    print("Created Enhancing_Legal_Efficiency_Through_AI.pptx")

# ---------------------------------------------------------
# 2. PDF GENERATION VIA PLAYWRIGHT
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
            .content-slide ul { list-style-type: none; padding-left: 0; }
            .content-slide li { font-size: 28pt; margin-bottom: 20px; line-height: 1.3; }
            .content-slide li::before { content: "• "; color: #00C8C8; font-weight: bold; }
            .content-slide li.no-bullet::before { content: ""; }
            .nested { margin-left: 40px; font-size: 24pt !important; }
            .nested::before { content: "○ " !important; }
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
                if bullet.startswith(" - "):
                    html_content += f'<li class="nested">{bullet[3:]}</li>'
                elif bullet.startswith("References:") or bullet.startswith("\n") or bullet.startswith("Any "):
                    html_content += f'<li class="no-bullet">{bullet.strip()}</li>'
                else:
                    html_content += f'<li>{bullet}</li>'
            html_content += '</ul></div>'
            
        html_content += '<div class="footer">Enhancing Legal Efficiency Through AI</div></div>'
        
    html_content += "</body></html>"
    
    with open("seminar_temp.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{os.path.abspath('seminar_temp.html')}")
        await page.pdf(
            path="Enhancing_Legal_Efficiency_Through_AI.pdf",
            width="13.33in",
            height="7.5in",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )
        await browser.close()
    
    if os.path.exists("seminar_temp.html"):
        os.remove("seminar_temp.html")
    print("Created Enhancing_Legal_Efficiency_Through_AI.pdf")


# ---------------------------------------------------------
# 3. SEMINAR GUIDE DOCX
# ---------------------------------------------------------
def create_seminar_guide():
    doc = Document()
    
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
        
    add_h1("Seminar Preparation Guide: Enhancing Legal Efficiency Through AI")
    
    add_h2("1. One-Minute Introduction")
    add_p("Good morning everyone. Today, I am presenting my seminar on 'Enhancing Legal Efficiency Through AI'. The legal profession is famously buried in paperwork. Lawyers spend hours reading massive contracts and hunting for past judgments using outdated keyword searches. This leads to high costs and massive court backlogs. My seminar explores how Artificial Intelligence—specifically Natural Language Processing and Semantic Search—can automate document review, extract key clauses, and instantly retrieve relevant case laws. Ultimately, we will look at how AI acts as an incredibly fast assistant that helps legal professionals work smarter, not harder, while maintaining strict human oversight.")

    add_h2("2. Three-Minute Topic Summary")
    add_p("To summarize the entire topic: The problem is information overload. Legal documents are lengthy, and manual review is slow and error-prone. We solve this using AI technologies like NLP and Large Language Models. The workflow involves converting raw documents into text, having the AI analyze that text for meaning, and using it to summarize judgments or flag risks in commercial contracts.")
    add_p("A major breakthrough in this field is RAG (Retrieval-Augmented Generation). Standard AI models like ChatGPT can 'hallucinate' or invent fake legal cases, which is highly dangerous. RAG fixes this by connecting the AI to a secure, verified legal database. The AI is only allowed to generate answers based on the documents it retrieves from that database.")
    add_p("In India, we are already seeing this. The Supreme Court uses SUVAS to translate judgments and SUPACE to help judges research cases efficiently. While the benefits of speed and consistency are massive, the risks are real—data privacy breaches, algorithmic bias, and hallucinations. Therefore, AI will never replace lawyers; it will only replace lawyers who refuse to use AI. Human verification remains the final, indispensable step.")

    add_h2("3. Simple Definitions")
    add_p(" AI (Artificial Intelligence):", " Machines simulating human logic to solve problems.")
    add_p(" ML (Machine Learning):", " A branch of AI where systems learn from historical data instead of being explicitly programmed.")
    add_p(" NLP (Natural Language Processing):", " The technology that helps computers read, understand, and generate human language.")
    add_p(" LLM (Large Language Model):", " Massive NLP models trained on billions of words to understand context (like ChatGPT or Gemini).")
    add_p(" Semantic Search:", " Searching by meaning and context rather than looking for exact string matches.")
    add_p(" Hallucination:", " When an AI confidently invents false information (e.g., making up a fake court case).")
    add_p(" RAG (Retrieval-Augmented Generation):", " A system that retrieves facts from a verified database before asking the LLM to generate an answer.")
    add_p(" Contract Analysis:", " Using AI to automatically read a contract and extract obligations, dates, and risks.")

    add_h2("4. 20 Likely Seminar Questions & Answers")
    qas = [
        ("Q1. What is the difference between digitization and AI in law?", "Digitization is just scanning paper into PDFs (like the e-Courts project). AI is the system actually reading and understanding the text inside that PDF."),
        ("Q2. Will AI replace lawyers or judges?", "No. AI lacks ethical accountability, empathy, and human judgment. It is an assistive tool to speed up research, not a decision-maker."),
        ("Q3. What is SUVAS?", "Supreme Court Vidhik Anuvaad Software. It is an AI tool used by the Indian judiciary to translate judgments into regional languages."),
        ("Q4. What is SUPACE?", "Supreme Court Portal for Assistance in Court's Efficiency. It is an AI research assistant designed to help judges process case facts quickly."),
        ("Q5. How does AI help with contract analysis?", "It can read a 100-page contract in seconds, extract the termination clauses, and flag any unusual penalties for the lawyer to review."),
        ("Q6. What do you mean by 'Semantic Search'?", "Traditional search requires exact words. If you search 'dog', it won't find 'puppy'. Semantic search understands the meaning, so it finds related concepts automatically."),
        ("Q7. Why is 'Hallucination' dangerous in law?", "If a lawyer uses an AI that hallucinates a fake past judgment, and the lawyer submits it to a judge, they can lose the case and face professional sanctions (as happened in the US in 2023)."),
        ("Q8. How does RAG solve hallucination?", "RAG forces the AI to look up the answer in a verified database first, and restricts the AI to only generate answers based on those retrieved facts."),
        ("Q9. Is client confidentiality at risk?", "Yes, if lawyers paste confidential contracts into public tools like OpenAI's website. Law firms must use private, offline, or enterprise-secured AI models to protect client data."),
        ("Q10. What is E-Discovery?", "During a corporate lawsuit, millions of emails are exchanged. AI is used in E-Discovery to filter out the junk and find the 10 or 20 emails relevant to the crime."),
        ("Q11. Can AI draft contracts?", "Yes, Generative AI can draft standard boilerplate contracts (like NDAs or lease agreements) very quickly, though a human must review the final draft."),
        ("Q12. What is algorithmic bias in law?", "If an AI is trained on historical arrest records that were racially biased, the AI might unfairly predict that certain minorities are at higher risk of re-offending."),
        ("Q13. How does AI improve Access to Justice?", "It allows small businesses or individuals who cannot afford $300/hour lawyers to use simple AI chatbots to understand basic legal documents."),
        ("Q14. What is the 'Black Box' problem?", "It means we often don't know exactly *how* an advanced neural network reached its conclusion, making it hard to explain the AI's logic in court."),
        ("Q15. How do lawyers verify AI output?", "By checking the citations. Good legal AI systems provide hyperlinks to the exact paragraph in the original document where it found the answer."),
        ("Q16. Can AI process scanned physical documents?", "Only if combined with OCR (Optical Character Recognition), which turns images of text into readable digital text first."),
        ("Q17. What is predictive justice?", "Using AI to analyze past rulings of a specific judge to predict how they might rule on a future case. (Ethically controversial)."),
        ("Q18. Are AI decisions legally binding?", "No. Currently, a human must sign off on any legal document or judgment. The machine holds no legal accountability."),
        ("Q19. What is the role of an MCA student in this field?", "MCA students build the infrastructure: the secure databases, the RAG pipelines, the API integrations, and the user interfaces that make these models usable for lawyers."),
        ("Q20. What is the future of legal AI?", "More specialized, open-source models trained purely on verified legal data, running locally to guarantee 100% data privacy.")
    ]
    for q, a in qas:
        add_p(a, bold_prefix=q + " ")

    add_h2("5. Five Practical Examples to Explain")
    add_p("1. The Corporate Merger:", " A company is buying another company and needs to review 5,000 employment contracts in a week. AI scans them and highlights only the contracts with unusual severance packages.")
    add_p("2. The Overworked Public Defender:", " A lawyer is handed a 500-page police report an hour before trial. They use AI to instantly summarize the timeline of events and flag contradictions in witness testimonies.")
    add_p("3. The Language Barrier:", " A farmer in Maharashtra receives a legal notice in English. An AI translation tool (like SUVAS) accurately translates the legal jargon into Marathi.")
    add_p("4. The Small Business Owner:", " An entrepreneur uses a legal AI chatbot to explain a confusing commercial lease agreement before signing it.")
    add_p("5. The Fake Cases (Mata v. Avianca):", " In 2023, lawyers used standard ChatGPT for research. ChatGPT invented fake cases. The lawyers didn't check them and submitted them to the judge, resulting in severe sanctions. This highlights why RAG and verification are needed.")

    add_h2("6. Short Conclusion (To speak at the end)")
    add_p("In conclusion, AI is not here to replace the legal profession; it is here to modernize it. By automating tedious research and document analysis, AI allows legal systems to operate with unprecedented speed and consistency. While we must carefully manage risks like data privacy and hallucinations, technologies like Semantic Search and RAG are already proving their worth. The future of law belongs to human-AI collaboration. Thank you.")

    doc.save("AI_Legal_Efficiency_Seminar_Guide.docx")
    print("Created AI_Legal_Efficiency_Seminar_Guide.docx")

if __name__ == "__main__":
    create_pptx()
    create_seminar_guide()
    asyncio.run(create_pdf())
