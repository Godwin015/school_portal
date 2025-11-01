import sys
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .models import Payment
from .utils import generate_receipt_pdf


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

        # Validate all fields
        if not all([student_name, session, student_class, term, parent_email, amount]):
            return render(request, 'error.html', {'message': 'All fields are required.'})

        # Save form data to session
        context = {
            'student_name': student_name,
            'session': session,
            'student_class': student_class,
            'term': term,
            'parent_email': parent_email,
            'amount': amount,
        }
        request.session['payment_data'] = context

        return render(request, 'payments/payment_confirm.html', context)

    return render(request, 'payments/payment_form.html')


# ===========================================
# INITIALIZE PAYMENT
# ===========================================
@csrf_exempt
def initialize_payment(request):
    print("📢 initialize_payment() triggered", file=sys.stderr)

    data = request.session.get('payment_data', {})
    email = request.POST.get('parent_email') or data.get('parent_email')
    amount = request.POST.get('amount') or data.get('amount')

    print(f"🧾 Received data -> email: {email}, amount: {amount}", file=sys.stderr)

    if not email or not amount:
        return render(request, "error.html", {"message": "Email and amount are required"})

    try:
        amount = float(amount)
    except ValueError:
        return render(request, "error.html", {"message": "Invalid amount format"})

    # ✅ Create transaction reference
    tx_ref = f"TX-{email.replace('@', '_')}"

    # ✅ Save payment record before redirecting
    Payment.objects.create(
        student_name=data.get("student_name"),
        student_class=data.get("student_class"),
        session=data.get("session"),
        term=data.get("term"),
        parent_email=email,
        amount=amount,
        payment_reference=tx_ref,
        status="pending"
    )

    # ✅ Prepare Flutterwave request
    headers = {
        "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "tx_ref": tx_ref,
        "amount": amount,
        "currency": "NGN",
        "redirect_url": "https://school-payment-portal.onrender.com/payments/verify/",
        "customer": {"email": email, "phonenumber": "", "name": data.get("student_name")},
        "customizations": {
            "title": "Sunshine Academy Payment",
            "description": "School fee payment for student",
            "logo": "https://school-payment-portal.onrender.com/static/img/logo.png",
        },
    }

    try:
        print("🚀 Sending request to Flutterwave...", file=sys.stderr)
        res = requests.post(
            "https://api.flutterwave.com/v3/payments",
            headers=headers,
            json=payload,
            timeout=10,
        )
        result = res.json()
        print("✅ Flutterwave response:", result, file=sys.stderr)
    except Exception as e:
        return render(request, "error.html", {"message": f"Flutterwave request failed: {e}"})

    if result.get("status") == "success":
        return redirect(result["data"]["link"])
    else:
        return render(request, "error.html", {"message": f"Flutterwave Error: {result.get('message')}"})


# ===========================================
# VERIFY PAYMENT
# ===========================================
def verify_payment(request):
    print("📢 verify_payment() triggered", file=sys.stderr)

    transaction_id = request.GET.get("transaction_id")
    if not transaction_id:
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
        return render(request, "error.html", {"message": f"Verification failed: {e}"})

    data = response_data.get("data", {})
    if data.get("status") == "successful":
        reference = data.get("tx_ref")
        amount = data.get("amount")

        # ✅ Retrieve saved payment (already created earlier)
        payment = Payment.objects.filter(payment_reference=reference).first()
        if payment:
            payment.status = "successful"
            payment.amount = amount
            payment.save()
        else:
            # fallback (should not normally happen)
            payment = Payment.objects.create(
                payment_reference=reference,
                amount=amount,
                status="successful",
                student_name="Unknown",
            )

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
            [payment.parent_email],
            fail_silently=True,
        )

        context = {
            "reference": reference,
            "amount": amount,
            "email": payment.parent_email,
            "student_name": payment.student_name,
            "session": payment.session,
            "student_class": payment.student_class,
            "term": payment.term,
        }
        return render(request, "payments/payment_success.html", context)

    else:
        return render(request, "payments/payment_failed.html")


# ===========================================
# DOWNLOAD RECEIPT
# ===========================================
def download_receipt(request, reference):
    pdf_buffer = generate_receipt_pdf(reference)
    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Receipt_{reference}.pdf"'
    return response


# ===========================================
# ABOUT PAGE
# ===========================================
def about(request):
    return render(request, "about.html")
