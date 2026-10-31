import os
import asyncio
import markdown
from playwright.async_api import async_playwright

async def convert_setup_md_to_pdf():
    md_file = "TEAM_MEMBER_LOCAL_SETUP.md"
    pdf_file = "TEAM_MEMBER_LOCAL_SETUP.pdf"
    
    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()
        
    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                margin: 0.8in;
            }}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10.5pt;
                line-height: 1.5;
                color: #222;
                margin: 0;
                padding: 10px;
            }}
            h1 {{
                color: #0A192F;
                border-bottom: 3px solid #00A3A3;
                padding-bottom: 8px;
                font-size: 20pt;
                margin-top: 10px;
                margin-bottom: 12px;
            }}
            h2 {{
                color: #007788;
                border-bottom: 1px solid #ddd;
                padding-bottom: 4px;
                font-size: 13pt;
                margin-top: 24px;
                margin-bottom: 10px;
                page-break-after: avoid;
            }}
            h3 {{
                color: #333;
                font-size: 11pt;
                margin-top: 16px;
                margin-bottom: 6px;
                page-break-after: avoid;
            }}
            p {{
                margin-top: 4px;
                margin-bottom: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 12px 0;
                font-size: 9.5pt;
                page-break-inside: avoid;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 6px 8px;
                text-align: left;
                vertical-align: top;
            }}
            th {{
                background-color: #0A192F;
                color: #fff;
                font-weight: 600;
            }}
            tr:nth-child(even) {{
                background-color: #f7f9fa;
            }}
            code {{
                background-color: #eef2f5;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 9.5pt;
                color: #c7254e;
            }}
            pre {{
                background-color: #1E293B;
                color: #F8FAFC;
                padding: 10px 14px;
                border-radius: 6px;
                overflow-x: auto;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 9pt;
                line-height: 1.4;
                margin: 8px 0;
                page-break-inside: avoid;
            }}
            pre code {{
                background-color: transparent;
                color: #F8FAFC;
                padding: 0;
            }}
            ul, ol {{
                margin-top: 4px;
                margin-bottom: 8px;
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 4px;
            }}
            blockquote {{
                background-color: #eff6ff;
                border-left: 4px solid #3b82f6;
                margin: 10px 0;
                padding: 8px 12px;
                font-size: 9.5pt;
            }}
            hr {{
                border: 0;
                border-top: 1px solid #e2e8f0;
                margin: 18px 0;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    temp_html = "temp_setup_guide.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file:///{os.path.abspath(temp_html).replace(chr(92), '/')}")
        await page.pdf(
            path=pdf_file,
            format="A4",
            margin={"top": "0.6in", "bottom": "0.6in", "left": "0.6in", "right": "0.6in"},
            print_background=True
        )
        await browser.close()
        
    print(f"Successfully generated {pdf_file}")

if __name__ == "__main__":
    asyncio.run(convert_setup_md_to_pdf())
