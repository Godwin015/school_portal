from django.db import models

class Payment(models.Model):
    student_name = models.CharField(max_length=255)
    student_class = models.CharField(max_length=100)  # ✅ Newly added field
    session = models.CharField(max_length=20)
    term = models.CharField(max_length=20)
    parent_email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=100, unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.payment_reference}"
