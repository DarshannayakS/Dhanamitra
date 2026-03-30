from django.contrib import admin
from .models import Investment, Profile  # add your models

admin.site.register(Investment)
admin.site.register(Profile)
from django.contrib import admin
from .models import FinancialGoal, InvestmentSuggestion

admin.site.register(FinancialGoal)
admin.site.register(InvestmentSuggestion)

# ...register others as needed
