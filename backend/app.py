from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from analyzer.python_analyzer import PythonAnalyzer
from pymongo import MongoClient
from datetime import datetime
import copy
import json
import base64
import os
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO

app = FastAPI()

# Allow CORS for frontend (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["code_quality"]
collection = db["reports"]

@app.post("/analyze")
async def analyze_code(file: UploadFile = File(...)):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are supported")

    content = (await file.read()).decode()
    
    # Analyze Python code
    analyzer = PythonAnalyzer(content)
    result = analyzer.analyze()
    result["filename"] = file.filename
    result["timestamp"] = datetime.utcnow().isoformat()
    
    # Prepare a copy for MongoDB
    try:
        db_result = copy.deepcopy(result)
        db_result["smell_details"] = [
            {k: str(v) for k, v in smell.items()} if isinstance(smell, dict) else str(smell)
            for smell in db_result["smell_details"]
        ]
        collection.insert_one(db_result)
    except Exception as e:
        print(f"MongoDB error: {e}")

    # Ensure response is JSON-serializable
    result["smell_details"] = [
        {k: str(v) for k, v in smell.items()} if isinstance(smell, dict) else str(smell)
        for smell in result["smell_details"]
    ]
    
    print(f"Returning response: {json.dumps(result, indent=2)}")
    return result

@app.post("/generate_pdf")
async def generate_pdf(data: dict):
    temp_pdf = None
    temp_img = None
    pdf_file = None
    img_path = None
    try:
        # Extract data
        filename = data.get("filename", "report")
        complexity = data.get("complexity", 0)
        smells = data.get("smells", 0)
        maintainability = data.get("maintainability", 0.0)
        smell_details = data.get("smell_details", [])
        chart_image = data.get("chart_image", "")

        # Create a temporary file for the PDF
        temp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        pdf_file = temp_pdf.name
        temp_pdf.close()  # Close to allow ReportLab to write

        print(f"Creating PDF at: {pdf_file}")

        # Initialize ReportLab document
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(name='Title', fontSize=16, spaceAfter=12, alignment=1)
        elements.append(Paragraph("Code Quality Analysis Report", title_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Summary
        elements.append(Paragraph("Summary", styles['Heading2']))
        summary_data = [
            ["Filename", filename],
            ["Cyclomatic Complexity", str(complexity)],
            ["Code Smells", f"{smells} issues"],
            ["Maintainability Index", f"{maintainability:.1f}"]
        ]
        summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Code Smells
        elements.append(Paragraph("Code Smells", styles['Heading2']))
        if smell_details:
            smells_data = [["Type", "Message", "Line"]] + [
                [smell.get('type', 'unknown'), smell.get('message', ''), str(smell.get('line', 0))]
                for smell in smell_details
            ]
            smells_table = Table(smells_data, colWidths=[1.5 * inch, 3.5 * inch, 1 * inch])
            smells_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
            ]))
            elements.append(smells_table)
        else:
            elements.append(Paragraph("No code smells detected.", styles['Italic']))
        elements.append(Spacer(1, 0.2 * inch))

        # Metrics Chart
        elements.append(Paragraph("Metrics Chart", styles['Heading2']))
        if chart_image:
            # Create temporary file for image
            temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            img_path = temp_img.name
            print(f"Creating image at: {img_path}")

            # Write base64 image
            if chart_image.startswith("data:image/png;base64,"):
                chart_image = chart_image[len("data:image/png;base64,"):]
            img_data = base64.b64decode(chart_image)
            temp_img.write(img_data)
            temp_img.flush()  # Ensure data is written
            temp_img.close()  # Close file

            # Verify file exists
            if not os.path.exists(img_path):
                raise Exception(f"Image file not created: {img_path}")

            print(f"Image file size: {os.path.getsize(img_path)} bytes")

            # Add image to PDF
            img = Image(img_path, width=6 * inch, height=3 * inch)
            elements.append(img)
        else:
            elements.append(Paragraph("Chart image not available.", styles['Italic']))

        # Build PDF
        doc.build(elements)
        print(f"PDF generated successfully: {pdf_file}")

        # Verify PDF exists
        if not os.path.exists(pdf_file):
            raise Exception(f"PDF file not created: {pdf_file}")

        # Return PDF file
        return FileResponse(
            pdf_file,
            media_type="application/pdf",
            filename=f"{filename}_analysis.pdf",
            background=None  # Disable background cleanup
        )
    except Exception as e:
        print(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
    finally:
        # Clean up image file only
        if temp_img and img_path and os.path.exists(img_path):
            try:
                os.unlink(img_path)
                print(f"Cleaned up image file: {img_path}")
            except Exception as e:
                print(f"Error cleaning up image file: {e}")
        # Do not delete pdf_file here; let FileResponse handle it