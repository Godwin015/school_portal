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
    import sys
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
            return render(request, "error.html", {"message": "Invalid amount"})

        # ✅ Prepare headers and payload for Flutterwave
        headers = {
            "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "tx_ref": f"TX-{email.replace('@', '_')}",
            "amount": amount,
            "currency": "NGN",
            "redirect_url": "https://school-payment-portal.onrender.com/payments/verify/",
            "customer": {
                "email": email,
                "phonenumber": "",
                "name": email.split('@')[0],
            },
            "customizations": {
                "title": "Sunshine Academy Payment",
                "description": "School fee payment for student",
                "logo": "https://school-payment-portal.onrender.com/static/img/logo.png",
            },
        }

        try:
            print("🚀 Sending request to Flutterwave...", file=sys.stderr)
            response = requests.post(
                "https://api.flutterwave.com/v3/payments",
                headers=headers,
                json=data,
                timeout=10,
            )

            print("✅ Status Code:", response.status_code, file=sys.stderr)
            print("🔍 Flutterwave init response:", response.text, file=sys.stderr)

            result = response.json()

        except Exception as e:
            print("⚠️ Flutterwave request failed:", str(e), file=sys.stderr)
            return render(
                request,
                "error.html",
                {"message": f"Connection to Flutterwave failed: {e}"},
            )

        # ✅ Check if initialization succeeded
        if result.get("status") == "success":
            payment_link = result["data"]["link"]
            print("✅ Redirecting to Flutterwave payment page...", file=sys.stderr)
            return redirect(payment_link)
        else:
            error_message = result.get("message", "Error initializing payment")
            print("🚫 Flutterwave Error Message:", error_message, file=sys.stderr)
            return render(
                request,
                "error.html",
                {"message": f"Flutterwave Error: {error_message}"},
            )

    print("ℹ️ GET request received for initialize_payment", file=sys.stderr)
    return render(request, "payments/payment_form.html")


# ===========================================
# VERIFY PAYMENT
# ===========================================
def verify_payment(request):
    import sys
    print("📢 verify_payment() triggered", file=sys.stderr)

    transaction_id = request.GET.get("transaction_id")
    if not transaction_id:
        print("⚠️ Missing transaction_id", file=sys.stderr)
        return render(request, "error.html", {"message": "Transaction ID missing"})

    headers = {
        "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"

    try:
        print("🔎 Verifying payment with Flutterwave...", file=sys.stderr)
        res = requests.get(url, headers=headers, timeout=10)
        response_data = res.json()
        print("✅ Flutterwave verify response:", response_data, file=sys.stderr)
    except Exception as e:
        print("⚠️ Flutterwave verification failed:", str(e), file=sys.stderr)
        return render(request, "error.html", {"message": f"Verification failed: {e}"})

    data = response_data.get("data", {})
    if data.get("status") == "successful":
        reference = data.get("tx_ref")
        amount = data.get("amount")
        email = data.get("customer", {}).get("email")

        # ✅ Save payment to DB
        payment, created = Payment.objects.get_or_create(payment_reference=reference)
        payment.status = "Successful"
        payment.amount = amount
        payment.parent_email = email
        payment.save()

        # ✅ Send confirmation email
        subject = "Payment Confirmation - Sunshine Academy"
        message = (
            f"Dear Parent,\n\n"
            f"Your payment of ₦{amount:,.2f} was successful.\n\n"
            f"Reference: {reference}\n\n"
            f"Thank you for choosing Sunshine Academy.\n\n"
            f"Best regards,\nSunshine Academy Accounts Office"
        )
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=True,
        )

        # ✅ Render success page
        context = {
            "reference": reference,
            "amount": amount,
            "email": email,
        }
        return render(request, "payments/payment_success.html", context)
    else:
        print("❌ Payment verification failed:", response_data, file=sys.stderr)
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

