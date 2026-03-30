from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.CharField(max_length=100, blank=True, null=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    aadhaar_number = models.CharField("Aadhaar Number", max_length=12, blank=True, null=True)
    pan_number = models.CharField("PAN Number", max_length=10, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, null=True)
    marital_status = models.CharField(max_length=15, choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed')], blank=True, null=True)
    nominee = models.CharField("Nominee Name", max_length=150, blank=True, null=True)
    emergency_contact = models.CharField("Emergency Contact", max_length=15, blank=True, null=True)
    occupation_type = models.CharField("Occupation Type", max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)  # <-- add
    date_of_birth = models.DateField(blank=True, null=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"



class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - {self.user.username}"


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category} - {self.user.username}"
from django.db import models
from django.contrib.auth.models import User


class AccountIntegration(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('Bank', 'Bank Account'),
        ('Credit Card', 'Credit Card'),
        ('Wallet', 'Digital Wallet'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    institution_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES)
    account_number = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    date_linked = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.institution_name} ({self.account_type})"

from django.db import models
from django.contrib.auth.models import User

class Investment(models.Model):
    INVESTMENT_TYPES = [
        ('MF', 'Mutual Fund'),
        ('STOCK', 'Stock'),
        ('FD', 'Fixed Deposit'),
        ('RD', 'Recurring Deposit'),
        ('GOLD', 'Gold'),
        ('CRYPTO', 'Crypto'),
        ('BOND', 'Bond'),
        ('OTHERS', 'Others'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPES)
    instrument_name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Number of shares/units (for stocks/MF)")
    amount_invested = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    remarks = models.CharField(max_length=255, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.instrument_name} ({self.investment_type})"

class FinancialGoal(models.Model):
    GOAL_TYPE_CHOICES = [
        ('Short-Term', 'Short-Term'),
        ('Long-Term', 'Long-Term'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    goal_type = models.CharField(choices=GOAL_TYPE_CHOICES, max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    due_date = models.DateField(null=True, blank=True)
    duration_months = models.PositiveIntegerField()
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)
    suggestion = models.TextField(blank=True, null=True)

from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class InvestmentSuggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=100)
    current_amount = models.IntegerField()
    target_amount = models.IntegerField()
    due_date = models.DateField()
    suggestion_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.goal_name} ({self.user.username})"

