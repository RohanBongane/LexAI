import os
import asyncio
import markdown
from playwright.async_api import async_playwright

async def convert_md_to_pdf():
    md_file = "LexAI_Complete_Technical_Master_Guide.md"
    pdf_file = "LexAI_Complete_Technical_Master_Guide.pdf"
    
    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()
        
    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 40px;
            }}
            h1, h2, h3 {{
                color: #0A192F;
            }}
            h1 {{
                border-bottom: 2px solid #00C8C8;
                padding-bottom: 10px;
                text-align: center;
                font-size: 2.5em;
            }}
            h2 {{
                color: #00C8C8;
                margin-top: 40px;
                border-bottom: 1px solid #eee;
                padding-bottom: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                page-break-inside: avoid;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #0A192F;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 4px;
                border-radius: 4px;
                font-family: Consolas, monospace;
            }}
            pre {{
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                page-break-inside: avoid;
            }}
            ul, ol {{
                margin-bottom: 20px;
            }}
            li {{
                margin-bottom: 5px;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    temp_html = "temp_technical_guide.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{os.path.abspath(temp_html)}")
        await page.pdf(
            path=pdf_file,
            format="A4",
            margin={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
            print_background=True
        )
        await browser.close()
        
    print(f"Successfully generated {pdf_file}")

if __name__ == "__main__":
    asyncio.run(convert_md_to_pdf())
