from docx import Document
from docx.shared import Pt
import re

def convert_md_to_docx():
    md_file = "LexAI_Complete_Technical_Master_Guide.md"
    docx_file = "LexAI_Complete_Technical_Master_Guide.docx"
    
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    doc.add_heading('LexAI Complete Technical Master Guide', 0)
    
    with open(md_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('## '):
            doc.add_heading(line.replace('## ', ''), level=1)
        elif line.startswith('### '):
            doc.add_heading(line.replace('### ', ''), level=2)
        elif line.startswith('# '):
            doc.add_heading(line.replace('# ', ''), level=1)
        elif line.startswith('- '):
            doc.add_paragraph(line.replace('- ', ''), style='List Bullet')
        elif line.startswith('* '):
            doc.add_paragraph(line.replace('* ', ''), style='List Bullet')
        elif line.startswith('|'):
            # It's a table row, just add as normal text for now for simplicity
            doc.add_paragraph(line)
        else:
            # Basic bolding replacement
            clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            doc.add_paragraph(clean_line)
            
    doc.save(docx_file)
    print(f"Successfully generated {docx_file}")

if __name__ == "__main__":
    convert_md_to_docx()
