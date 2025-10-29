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
    if request.method == "POST":
        email = request.POST.get("email")
        amount = request.POST.get("amount")

        if not email or not amount:
            return render(request, "error.html", {"message": "Email and amount are required"})

        try:
            amount_in_kobo = int(float(amount) * 100)
        except ValueError:
            return render(request, "error.html", {"message": "Invalid amount"})

        # ✅ Prepare headers and payload for Paystack
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        data = {
            "email": email,
            "amount": amount_in_kobo,
            "callback_url": "https://school-payment-portal.onrender.com/payments/verify/",
        }

                # 🚀 Send request to Paystack
        try:
            response = requests.post(
                f"{settings.PAYSTACK_BASE_URL}/transaction/initialize",
                headers=headers,
                data=data,
                timeout=10  # helps catch slow network issues
            )

            # 🪵 Log raw Paystack response
            print("🔍 Paystack init response:", response.text)

            result = response.json()

        except Exception as e:
            # 🔥 Catch network or decoding issues
            print("⚠️ Paystack request failed:", str(e))
            return render(
                request,
                "error.html",
                {"message": f"Connection to Paystack failed: {e}"}
            )

        # 🧠 Debugging: print the response in Render logs
        print("🔍 Paystack init response:", result)

        # ✅ Check for success and redirect user to Paystack checkout
        if result.get("status") and result.get("data"):
            return redirect(result["data"]["authorization_url"])
        else:
            # ❌ Show detailed error message
            error_message = result.get("message", "Error initializing payment")
            return render(request, "error.html", {"message": f"Paystack Error: {error_message}"})

    # ✅ If user visits the page directly
    return render(request, "payments/payment_form.html")

# ===========================================
# VERIFY PAYMENT
# ===========================================
def verify_payment(request):
    reference = request.GET.get('reference')
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    res = requests.get(url, headers=headers)
    response_data = res.json()

    if response_data.get('data', {}).get('status') == 'success':
        payment = Payment.objects.get(payment_reference=reference)
        payment.status = 'Successful'
        payment.save()

        # Send email confirmation
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
        return render(request, 'payments/payment_failed.html')


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




