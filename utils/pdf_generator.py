"""PDF generation for sanction letters"""
from datetime import datetime, timedelta
from pathlib import Path
import uuid

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from models.agent_io import SanctionInput


def generate_sanction_letter(data: SanctionInput, output_dir: str = "outputs/sanction_letters") -> tuple[str, str]:
    """
    Generate a professional sanction letter PDF
    
    Args:
        data: Sanction input data
        output_dir: Directory to save the PDF
    
    Returns:
        Tuple of (file_path, sanction_id)
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate unique sanction ID
    sanction_id = f"SL{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
    
    # File path
    file_path = output_path / f"{data.session_id}.pdf"
    
    # Create PDF
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    # Bank Header
    bank_name = Paragraph("<b>BFSI BANK LIMITED</b>", title_style)
    elements.append(bank_name)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Sanction Letter Title
    title = Paragraph("<b>LOAN SANCTION LETTER</b>", header_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Sanction details
    sanction_date = datetime.now().strftime("%d %B %Y")
    validity_date = (datetime.now() + timedelta(days=30)).strftime("%d %B %Y")
    
    details_text = f"""
    <b>Sanction ID:</b> {sanction_id}<br/>
    <b>Date:</b> {sanction_date}<br/>
    <b>Valid Until:</b> {validity_date}
    """
    elements.append(Paragraph(details_text, body_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Customer details
    customer_text = f"""
    <b>Dear {data.customer_name},</b><br/><br/>
    We are pleased to inform you that your personal loan application has been <b>approved</b>. 
    Please find the loan details below:
    """
    elements.append(Paragraph(customer_text, body_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Loan details table
    loan_data = [
        ['Loan Amount', f'₹ {data.approved_amount:,}'],
        ['Interest Rate', f'{data.final_interest_rate}% per annum'],
        ['Tenure', f'{data.tenure_months} months ({data.tenure_months // 12} years)'],
        ['Monthly EMI', f'₹ {data.estimated_emi:,.2f}'],
        ['Risk Grade', data.risk_grade],
        ['Customer ID', data.customer_id]
    ]
    
    loan_table = Table(loan_data, colWidths=[2.5 * inch, 3.5 * inch])
    loan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    
    elements.append(loan_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Terms and Conditions
    terms_header = Paragraph("<b>Terms and Conditions:</b>", header_style)
    elements.append(terms_header)
    
    terms = """
    1. This sanction is valid for 30 days from the date of issue.<br/>
    2. The loan is subject to submission of required documents and verification.<br/>
    3. Processing fee of 1% of the loan amount (minimum ₹1,000) is applicable.<br/>
    4. Prepayment charges: 2% of outstanding principal if prepaid within 12 months.<br/>
    5. Late payment charges: ₹500 per instance plus 2% per month on overdue amount.<br/>
    6. The bank reserves the right to modify or withdraw this sanction at any time.<br/>
    7. Please read the detailed loan agreement before acceptance.<br/>
    """
    elements.append(Paragraph(terms, body_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Closing
    closing_text = """
    Please contact our loan officer to proceed with the documentation process.<br/><br/>
    <b>Congratulations on your loan approval!</b><br/><br/>
    Sincerely,<br/>
    <b>BFSI Bank Limited</b><br/>
    Loan Origination Department
    """
    elements.append(Paragraph(closing_text, body_style))
    
    # Build PDF
    doc.build(elements)
    
    return str(file_path), sanction_id
