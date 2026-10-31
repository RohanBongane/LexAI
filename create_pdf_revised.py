import asyncio
from playwright.async_api import async_playwright
import os

async def generate_pdf():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        filepath = os.path.abspath('synopsis_revised.html')
        await page.goto(f"file://{filepath}")
        
        await page.pdf(
            path="LexAI_Project_Synopsis_Revised.pdf",
            format="A4",
            margin={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
            display_header_footer=True,
            header_template="<span></span>",
            footer_template="""
            <div style="width: 100%; font-size: 12px; text-align: center; font-family: 'Bookman Old Style', serif;">
                <span class="pageNumber"></span>
            </div>
            """
        )
        await browser.close()

asyncio.run(generate_pdf())
