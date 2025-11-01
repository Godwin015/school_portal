from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Payment
import qrcode
from reportlab.lib.utils import ImageReader


def generate_receipt_pdf(reference):
    payment = Payment.objects.get(payment_reference=reference)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # === HEADER ===
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 80, "Sunshine Academy")

    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, height - 100, "Official Payment Receipt")

    # === PAYMENT DETAILS ===
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
        p.setFont("Helvetica-Bold", 11)
        p.drawString(80, y, f"{label}")
        p.setFont("Helvetica", 11)
        p.drawString(220, y, str(value))
        y -= 25

    # === QR CODE (with verification URL) ===
    verification_url = f"https://school-payment-portal.onrender.com/payments/receipt/{payment.payment_reference}/"
    qr_data = f"Verify Payment Online:\n{verification_url}\n\nStudent: {payment.student_name}\nAmount: ₦{payment.amount:,.2f}\nStatus: {payment.status}"

    qr_image = qrcode.make(qr_data)

    # ✅ Convert QR code image to bytes
    qr_bytes = BytesIO()
    qr_image.save(qr_bytes, format="PNG")
    qr_bytes.seek(0)
    qr_reader = ImageReader(qr_bytes)

    # Draw QR code on the PDF
    p.drawImage(qr_reader, width - 200, height - 250, 100, 100)

    # === FOOTER ===
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width / 2, 80, "Scan the QR code to verify this payment online.")
    p.drawCentredString(width / 2, 65, "This is a system-generated receipt. No signature required.")

    # Finalize PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
