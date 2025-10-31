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
        # ✅ Match field names exactly as in your HTML form
        student_name = request.POST.get('student_name')
        session = request.POST.get('session')
        student_class = request.POST.get('student_class')
        term = request.POST.get('term')
        parent_email = request.POST.get('parent_email')
        amount = request.POST.get('amount')

        # ✅ Verify all required fields exist
        if not all([student_name, session, student_class, term, parent_email, amount]):
            return render(request, 'error.html', {'message': 'All fields are required.'})

        context = {
            'student_name': student_name,
            'session': session,
            'student_class': student_class,
            'term': term,
            'parent_email': parent_email,
            'amount': amount,
        }

        # ✅ Save to session (optional continuity)
        request.session['payment_data'] = context

        return render(request, 'payments/payment_confirm.html', context)

    # Show the payment form
    return render(request, 'payments/payment_form.html')


# ===========================================
# INITIALIZE PAYMENT
# ===========================================
@csrf_exempt
def initialize_payment(request):
    print("📢 initialize_payment() triggered", file=sys.stderr)

    # Retrieve from POST or session
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

    # ✅ Prepare Flutterwave request
    headers = {
        "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "tx_ref": f"TX-{email.replace('@', '_')}",
        "amount": amount,
        "currency": "NGN",
        "redirect_url": "https://school-payment-portal.onrender.com/payments/verify/",
        "customer": {"email": email, "phonenumber": "", "name": email.split('@')[0]},
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
        res = requests.get(url, headers=headers, timeout=10)
        response_data = res.json()
        print("✅ Flutterwave verify response:", response_data, file=sys.stderr)
    except Exception as e:
        return render(request, "error.html", {"message": f"Verification failed: {e}"})

    data = response_data.get("data", {})
    if data.get("status") == "successful":
        reference = data.get("tx_ref")
        amount = data.get("amount")
        email = data.get("customer", {}).get("email")

        payment, _ = Payment.objects.get_or_create(payment_reference=reference)
        payment.amount = amount
        payment.parent_email = email
        payment.save()

        # ✅ Email confirmation
        send_mail(
            "Payment Confirmation - Sunshine Academy",
            f"Dear Parent,\n\nYour payment of ₦{amount:,.2f} was successful.\nReference: {reference}\n\nThank you for choosing Sunshine Academy.",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=True,
        )

        context = {"reference": reference, "amount": amount, "email": email}
        return render(request, "payments/payment_success.html", context)

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
