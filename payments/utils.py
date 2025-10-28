from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from io import BytesIO
from .models import Payment
import qrcode
from reportlab.lib.utils import ImageReader

def generate_receipt_pdf(reference):
    payment = Payment.objects.get(payment_reference=reference)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 80, "Sunshine Academy")

    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, height - 100, "Official Payment Receipt")

    # Payment details
    y = height - 160
    details = [
        ("Student Name:", payment.student_name),
        ("Academic Session:", payment.session),
        ("Class:", payment.student_class),
        ("Term:", payment.term),
        ("Parent Email:", payment.parent_email),
        ("Amount Paid:", f"₦{payment.amount:,.2f}"),
        ("Payment Reference:", payment.payment_reference),
        ("Status:", payment.status),
        ("Date:", payment.date.strftime("%Y-%m-%d %H:%M")),
    ]

    for label, value in details:
        p.drawString(80, y, f"{label}")
        p.drawString(220, y, str(value))
        y -= 25

    # QR Code (optional)
    qr = qrcode.make(f"Reference: {payment.payment_reference}")
    qr_image = ImageReader(qr)
    p.drawImage(qr_image, width - 200, height - 250, 100, 100)

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width / 2, 80, "This is a system-generated receipt. No signature required.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
