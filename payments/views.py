from django.shortcuts import render, redirect
from django.conf import settings
from .utils import generate_receipt_pdf
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
import requests
import uuid

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

    return render(request, 'payments/payment_form.html')

def initialize_payment(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        session = request.POST.get('session')
        student_class = request.POST.get('student_class')
        term = request.POST.get('term')
        parent_email = request.POST.get('parent_email')
        amount = request.POST.get('amount')

        reference = str(uuid.uuid4())
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        data = {
            "email": parent_email,
            "amount": int(float(amount) * 100),  # convert Naira to Kobo
            "reference": reference,
            "callback_url": "http://127.0.0.1:8000/payments/verify/"  # update in production
        }

        res = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, data=data)
        response_data = res.json()

        if response_data.get('status'):
            # Save payment to database
            Payment.objects.create(
                student_name=student_name,
                session=session,
                student_class=student_class,
                term=term,
                parent_email=parent_email,
                amount=amount,
                payment_reference=reference,
                status='Pending'
            )
            # Redirect to Paystack checkout
            return redirect(response_data['data']['authorization_url'])
        else:
            return render(request, 'payments/payment_failed.html', {'error': 'Payment initialization failed'})

    return redirect('pay_fees')

def verify_payment(request):
    reference = request.GET.get('reference')
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    res = requests.get(url, headers=headers)
    response_data = res.json()

    if response_data['data']['status'] == 'success':
        payment = Payment.objects.get(payment_reference=reference)
        payment.status = 'Successful'
        payment.save()

        # ===============================
        # 📧 SEND EMAIL TO PARENT & SCHOOL
        # ===============================
        from django.core.mail import send_mail

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
            settings.EMAIL_HOST_USER,  # from email (your school email)
            [payment.parent_email, 'accounts@schoolname.com'],
            fail_silently=True,
        )

        # ===============================
        # RENDER SUCCESS PAGE
        # ===============================
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

def download_receipt(request, reference):
    pdf_buffer = generate_receipt_pdf(reference)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receipt_{reference}.pdf"'
    return response
