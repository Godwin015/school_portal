import sys
import json
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .models import Payment
from .utils import generate_receipt_pdf
import requests
import uuid

# ===========================================
# PAY FORM VIEW
# ===========================================
def pay_fees(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        session = request.POST.get('session')
        student_class = request.POST.get('student_class')
        term = request.POST.get('term')
        parent_email = request.POST.get('parent_email')
        amount = request.POST.get('amount')

        context = {
            'student_name': student_name,
            'session': session,
            'student_class': student_class,
            'term': term,
            'parent_email': parent_email,
            'amount': amount,
        }
        return render(request, 'payments/payment_confirm.html', context)

    # Show the payment form
    return render(request, 'payments/payment_form.html')


# ===========================================
# INITIALIZE PAYMENT
# ===========================================

@csrf_exempt
def initialize_payment(request):
    print("📢 initialize_payment() triggered", file=sys.stderr)

    if request.method == "POST":
        email = request.POST.get("email")
        amount = request.POST.get("amount")
        print(f"🧾 Received form data -> email: {email}, amount: {amount}", file=sys.stderr)

        if not email or not amount:
            print("⚠️ Missing email or amount", file=sys.stderr)
            return render(request, "error.html", {"message": "Email and amount are required"})

        try:
            amount = float(amount)
        except ValueError:
            print("❌ Invalid amount format", file=sys.stderr)
            return render(request, "error.html", {"message": "Invalid amount format"})

        # ✅ Flutterwave API setup
        headers = {
            "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "tx_ref": f"TX-{uuid.uuid4().hex[:10]}",
            "amount": str(amount),
            "currency": "NGN",
            "redirect_url": "https://school-payment-portal.onrender.com/payments/verify/",
            "customer": {
                "email": email,
            },
            "meta": {
                "reason": "School Fee Payment",
            },
            "customizations": {
                "title": "Sunshine Academy Fee Payment",
                "description": "Pay your school fees securely via Flutterwave",
            },
        }

        try:
            print("🚀 Sending request to Flutterwave...", file=sys.stderr)
            response = requests.post(
                f"{settings.FLW_BASE_URL}/payments",
                headers=headers,
                json=data,
                timeout=10
            )

            print("✅ Status Code:", response.status_code, file=sys.stderr)
            print("🔍 Flutterwave init response:", response.text, file=sys.stderr)

            result = response.json()

        except Exception as e:
            print("⚠️ Flutterwave request failed:", str(e), file=sys.stderr)
            return render(request, "error.html", {"message": f"Connection to Flutterwave failed: {e}"})

        # ✅ Redirect user to payment page if successful
        if result.get("status") == "success":
            payment_link = result["data"]["link"]
            print("✅ Redirecting user to Flutterwave payment page", file=sys.stderr)
            return redirect(payment_link)
        else:
            error_message = result.get("message", "Error initializing payment")
            print("🚫 Flutterwave Error Message:", error_message, file=sys.stderr)
            return render(request, "error.html", {"message": f"Flutterwave Error: {error_message}"})

    print("ℹ️ GET request received for initialize_payment", file=sys.stderr)
    return render(request, "payments/payment_form.html")

# ===========================================
# VERIFY PAYMENT
# ===========================================
def verify_payment(request):
    tx_ref = request.GET.get("tx_ref")
    transaction_id = request.GET.get("transaction_id")

    print(f"🔎 Verifying payment -> tx_ref: {tx_ref}, transaction_id: {transaction_id}", file=sys.stderr)

    if not transaction_id:
        return render(request, "error.html", {"message": "Transaction ID is missing."})

    headers = {
        "Authorization": f"Bearer {settings.FLW_SECRET_KEY}"
    }

    url = f"{settings.FLW_BASE_URL}/transactions/{transaction_id}/verify"

    try:
        response = requests.get(url, headers=headers)
        result = response.json()
        print("🔍 Flutterwave verify response:", result, file=sys.stderr)

        if result.get("status") == "success" and result["data"]["status"] == "successful":
            payment = Payment.objects.filter(payment_reference=tx_ref).first()
            if payment:
                payment.status = "Successful"
                payment.save()

                # Send confirmation email
                subject = "Payment Confirmation - Sunshine Academy"
                message = (
                    f"Dear Parent,\n\n"
                    f"Your payment for {payment.student_name} "
                    f"({payment.term}, {payment.session}) was successful.\n\n"
                    f"Amount: ₦{payment.amount:,.2f}\n"
                    f"Reference: {payment.payment_reference}\n\n"
                    f"Thank you for choosing Sunshine Academy.\n\n"
                    f"Best regards,\nSunshine Academy Accounts Office"
                )

                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [payment.parent_email, 'accounts@schoolname.com'],
                    fail_silently=True,
                )

                context = {
                    'student_name': payment.student_name,
                    'session': payment.session,
                    'student_class': payment.student_class,
                    'term': payment.term,
                    'parent_email': payment.parent_email,
                    'amount': payment.amount,
                    'reference': payment.payment_reference,
                }
                return render(request, 'payments/payment_success.html', context)
            else:
                print("⚠️ Payment record not found for tx_ref:", tx_ref, file=sys.stderr)
        else:
            print("❌ Flutterwave verification failed:", result, file=sys.stderr)

    except Exception as e:
        print("⚠️ Verification request failed:", str(e), file=sys.stderr)
        return render(request, "error.html", {"message": f"Verification failed: {e}"})

    return render(request, "payments/payment_failed.html")


# ===========================================
# DOWNLOAD RECEIPT
# ===========================================
def download_receipt(request, reference):
    pdf_buffer = generate_receipt_pdf(reference)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receipt_{reference}.pdf"'
    return response


# ===========================================
# ABOUT PAGE
# ===========================================
def about(request):
    return render(request, 'about.html')
