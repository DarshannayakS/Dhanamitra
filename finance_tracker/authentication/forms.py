from django import forms
from .models import Profile, Income, Expense

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profession', 'salary', 'phone', 'age', 'address',
            'aadhaar_number', 'pan_number',
            'gender', 'marital_status', 'nominee', 'emergency_contact', 'occupation_type', 'city', 'date_of_birth'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
from django import forms
from .models import Income, Expense

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['source', 'amount']
        widgets = {
            'source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter source of income'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'note']
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter expense category'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Optional description', 'rows': 3}),
        }
from django import forms
from .models import AccountIntegration


class AccountIntegrationForm(forms.ModelForm):
    class Meta:
        model = AccountIntegration
        fields = ['institution_name', 'account_type', 'account_number', 'balance']
        widgets = {
            'institution_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., HDFC Bank, Paytm Wallet'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter account or card number'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter current balance'}),
        }

from .models import Investment
from django import forms

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['investment_type', 'instrument_name', 'quantity', 'amount_invested', 'current_value', 'start_date', 'remarks']
        widgets = {
            'investment_type': forms.Select(attrs={'class': 'form-control'}),
            'instrument_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of Fund/Stock/...'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of shares/units (optional)'}),
            'amount_invested': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount Invested'}),
            'current_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Current Value'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional notes'}),
        }

from django import forms
from .models import FinancialGoal

class FinancialGoalForm(forms.ModelForm):
    class Meta:
        model = FinancialGoal
        fields = ['name', 'goal_type', 'amount', 'current_amount', 'due_date', 'duration_months', 'is_recurring', 'note', 'suggestion']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Optional notes', 'rows': 3}),
            'suggestion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Investment suggestion', 'rows': 5, 'readonly': True}),
        }

from django import forms
from .models import InvestmentSuggestion

class InvestmentSuggestionForm(forms.ModelForm):
    class Meta:
        model = InvestmentSuggestion
        fields = ['goal_name', 'current_amount', 'target_amount', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }

