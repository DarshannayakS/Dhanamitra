from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from .models import (
    Profile, Income, Expense, AccountIntegration, Investment,
    FinancialGoal, InvestmentSuggestion
)
from .forms import (
    ProfileForm, IncomeForm, ExpenseForm, AccountIntegrationForm,
    InvestmentForm, FinancialGoalForm, InvestmentSuggestionForm
)
from datetime import date, datetime

def get_translations(text):
    return text
def splash(request):
    return render(request, 'authentication/splash.html')


def generate_goal_suggestion(goal_name, current, target, due_date, user, lang='en'):
    today = date.today()
    if isinstance(due_date, str):
        due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
    months = (due_date.year - today.year) * 12 + (due_date.month - today.month)
    left = target - current

    if months < 1:
        return get_translations("It is not possible to achieve this goal in less than a month. Try to extend your due date or use current savings.")
    if left <= 0:
        return get_translations(f"You already have enough to achieve '{goal_name}'!")

    # Get user's monthly income
    try:
        monthly_income = float(sum(i.amount for i in Income.objects.filter(user=user)) or user.profile.salary or 0)
    except:
        monthly_income = 0.0

    if monthly_income == 0:
        return get_translations("Unable to calculate suggestions without income data. Please add your income details.")

    # Available for investment: 70% of income, leave 30% for personal use
    max_monthly_investment = monthly_income * 0.7

    # Conservative option: FD/Debt MF, rates 6.5% for <=12 months, 8% for >12 months
    if months <= 12:
        r_cons = 0.065 / 12  # 6.5% p.a.
    else:
        r_cons = 0.08 / 12   # 8% p.a.
    s_monthly_cons = left / (((1 + r_cons) ** months - 1) / r_cons)
    principal_cons = current + s_monthly_cons * months
    fv_cons = current + s_monthly_cons * (((1 + r_cons) ** months - 1) / r_cons)
    profit_cons = fv_cons - principal_cons

    # Moderate option: Hybrid MF/Equity SIP, rates 10% for <=12 months, 12% for >12 months
    if months <= 12:
        r_mod = 0.10 / 12  # 10% p.a.
    else:
        r_mod = 0.12 / 12   # 12% p.a.
    s_monthly_mod = left / (((1 + r_mod) ** months - 1) / r_mod)
    principal_mod = current + s_monthly_mod * months
    fv_mod = current + s_monthly_mod * (((1 + r_mod) ** months - 1) / r_mod)
    profit_mod = fv_mod - principal_mod

    # Check feasibility
    if s_monthly_cons > max_monthly_investment and s_monthly_mod > max_monthly_investment:
        # Not possible in given period, calculate extended period
        extended_months_cons = 0
        extended_months_mod = 0
        temp = left
        while temp > 0 and extended_months_cons < 120:  # Max 10 years
            extended_months_cons += 1
            temp -= max_monthly_investment
            temp *= (1 + r_cons)
        extended_months_cons = max(extended_months_cons, months)

        temp = left
        while temp > 0 and extended_months_mod < 120:
            extended_months_mod += 1
            temp -= max_monthly_investment
            temp *= (1 + r_mod)
        extended_months_mod = max(extended_months_mod, months)

        suggestion = f"Goal: {goal_name} (₹{int(target)}) in {months} months.\n\n"
        suggestion += f"Your monthly income: ₹{int(monthly_income)}\n"
        suggestion += f"Available for investment (70% of income): ₹{int(max_monthly_investment)}\n\n"
        suggestion += "Unfortunately, it's not possible to achieve this goal within the given due date with your current income.\n\n"
        profit_cons = target - max_monthly_investment * extended_months_cons
        profit_mod = target - max_monthly_investment * extended_months_mod
        suggestion += f"Alternative: Extend to {extended_months_cons} months (Conservative, FD/Debt MF, {r_cons*12*100:.1f}% p.a.):\n"
        suggestion += f"- Monthly Investment: ₹{int(max_monthly_investment)}\n"
        suggestion += f"- Total Principal: ₹{int(max_monthly_investment * extended_months_cons)}\n"
        suggestion += f"- Maturity Value: ₹{int(target)}\n"
        suggestion += f"- Profit: ₹{'+' if profit_cons >= 0 else ''}{int(profit_cons)} ({'Gain' if profit_cons >= 0 else 'Loss'})\n\n"
        suggestion += f"Alternative: Extend to {extended_months_mod} months (Moderate, Hybrid MF/Equity SIP, {r_mod*12*100:.1f}% p.a., higher risk):\n"
        suggestion += f"- Monthly Investment: ₹{int(max_monthly_investment)}\n"
        suggestion += f"- Total Principal: ₹{int(max_monthly_investment * extended_months_mod)}\n"
        suggestion += f"- Maturity Value: ₹{int(target)}\n"
        suggestion += f"- Profit: ₹{'+' if profit_mod >= 0 else ''}{int(profit_mod)} ({'Gain' if profit_mod >= 0 else 'Loss'})\n\n"
        suggestion += "Consider increasing your income or extending the due date."
    else:
        suggestion = f"Goal: {goal_name} (₹{int(target)}) in {months} months.\n\n"
        suggestion += f"Your monthly income: ₹{int(monthly_income)}\n"
        suggestion += f"Available for investment (70% of income): ₹{int(max_monthly_investment)}\n\n"
        suggestion += f"Conservative Option (FD/Debt MF, {r_cons*12*100:.1f}% p.a.):\n"
        suggestion += f"- Monthly Savings: ₹{int(s_monthly_cons)}\n"
        suggestion += f"- Total Principal: ₹{int(principal_cons)}\n"
        suggestion += f"- Maturity Value: ₹{int(fv_cons)}\n"
        suggestion += f"- Profit: ₹{'+' if profit_cons >= 0 else ''}{int(profit_cons)} ({'Gain' if profit_cons >= 0 else 'Loss'})\n\n"
        suggestion += f"Moderate Option (Hybrid MF/Equity SIP, {r_mod*12*100:.1f}% p.a., higher risk):\n"
        suggestion += f"- Monthly Savings: ₹{int(s_monthly_mod)}\n"
        suggestion += f"- Total Principal: ₹{int(principal_mod)}\n"
        suggestion += f"- Maturity Value: ₹{int(fv_mod)}\n"
        suggestion += f"- Profit: ₹{'+' if profit_mod >= 0 else ''}{int(profit_mod)} ({'Gain' if profit_mod >= 0 else 'Loss'})\n\n"
        suggestion += "Choose based on your risk tolerance. Conservative is safer, moderate offers higher returns but with risk."

    return get_translations(suggestion)

@login_required(login_url='login')
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    accounts = AccountIntegration.objects.filter(user=request.user)
    investments = Investment.objects.filter(user=request.user)
    goals = FinancialGoal.objects.filter(user=request.user).order_by('-created_at')

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    balance = total_income - total_expense

    for inv in investments:
        inv.gain = inv.current_value - inv.amount_invested
    total_investment_value = sum(inv.current_value for inv in investments)

    expense_by_category = (
        Expense.objects.filter(user=request.user)
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('category')
    )
    categories = [e['category'] for e in expense_by_category]
    totals = [float(e['total']) for e in expense_by_category]

    profile_form = ProfileForm(instance=profile)
    income_form = IncomeForm()
    expense_form = ExpenseForm()
    edit_profile = False

    # Preserve user input for goal planner form
    goal_suggestion_result = None
    goal_name = request.POST.get("goal_name", "") if request.method == "POST" else ""
    current_amount = request.POST.get("current_amount", "") if request.method == "POST" else ""
    target_amount = request.POST.get("target_amount", "") if request.method == "POST" else ""
    due_date = request.POST.get("due_date", "") if request.method == "POST" else ""
    lang = request.POST.get("lang", "en") if request.method == 'POST' else "en"
    if request.method == 'POST' and 'goal_planner_submit' in request.POST:
        # Only call suggestion if all fields are provided and numbers are valid
        try:
            goal_suggestion_result = generate_goal_suggestion(
                goal_name,
                int(current_amount),
                int(target_amount),
                due_date,
                request.user,
                lang
            )
        except:
            goal_suggestion_result = ["Please enter valid numbers for amounts and select a valid date."]
    elif request.method == 'POST':
        tab = request.POST.get('tab', '')
        if 'edit_profile' in request.POST:
            edit_profile = True
        elif tab == 'profile' and 'profile_submit' in request.POST:
            profile_form = ProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully!")
                profile = Profile.objects.get(user=request.user)
                profile_form = ProfileForm(instance=profile)
                edit_profile = False
        elif tab == 'income' and 'income_submit' in request.POST:
            income_form = IncomeForm(request.POST)
            if income_form.is_valid():
                income = income_form.save(commit=False)
                income.user = request.user
                income.save()
                messages.success(request, "Income added successfully.")
        elif tab == 'expense' and 'expense_submit' in request.POST:
            expense_form = ExpenseForm(request.POST)
            if expense_form.is_valid():
                expense = expense_form.save(commit=False)
                expense.user = request.user
                expense.save()
                messages.success(request, "Expense added successfully.")

    suggestions = InvestmentSuggestion.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'user': request.user,
        'profile': profile,
        'profile_form': profile_form,
        'income_form': income_form,
        'expense_form': expense_form,
        'incomes': incomes,
        'expenses': expenses,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'edit_profile': edit_profile,
        'accounts': accounts,
        'investments': investments,
        'total_investment_value': total_investment_value,
        'expense_categories': categories,
        'expense_totals': totals,
        'goals': goals,
        'goal_suggestion_result': goal_suggestion_result,
        'suggestions': suggestions,
    }
    return render(request, 'authentication/dashboard.html', context)


# ---------------- REGISTER ----------------
def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')
    return render(request, 'authentication/register.html')

# ---------------- LOGIN ----------------
from datetime import date

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials!')
            return redirect('login')
    else:
        # List of daily motivation quotes
        quotes = [
            "The best way to predict the future is to create it. – Peter Drucker",
            "Your most unhappy customers are your greatest source of learning. – Bill Gates",
            "The only way to do great work is to love what you do. – Steve Jobs",
            "Believe you can and you're halfway there. – Theodore Roosevelt",
            "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
            "You miss 100% of the shots you don't take. – Wayne Gretzky",
            "The only limit to our realization of tomorrow will be our doubts of today. – Franklin D. Roosevelt",
            "The best revenge is massive success. – Frank Sinatra",
            "Don't watch the clock; do what it does. Keep going. – Sam Levenson",
            "The way to get started is to quit talking and begin doing. – Walt Disney",
            "Your time is limited, so don't waste it living someone else's life. – Steve Jobs",
            "The only person you are destined to become is the person you decide to be. – Ralph Waldo Emerson",
            "Go confidently in the direction of your dreams. Live the life you have imagined. – Henry David Thoreau",
            "The future starts today, not tomorrow. – Pope John Paul II",
            "Don't be afraid to give up the good to go for the great. – John D. Rockefeller",
            "The secret of getting ahead is getting started. – Mark Twain",
            "What lies behind us and what lies before us are tiny matters compared to what lies within us. – Ralph Waldo Emerson",
            "The mind is everything. What you think you become. – Buddha",
            "The best time to plant a tree was 20 years ago. The second best time is now. – Chinese Proverb",
            "You can't build a reputation on what you are going to do. – Henry Ford",
            "The two most important days in your life are the day you are born and the day you find out why. – Mark Twain",
            "The only way to achieve the impossible is to believe it is possible. – Charles Kingsleigh",
            "Dream big and dare to fail. – Norman Vaughan",
            "The harder you work for something, the greater you'll feel when you achieve it. – Unknown",
            "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill",
            "The only place where success comes before work is in the dictionary. – Vidal Sassoon",
            "Don't stop when you're tired. Stop when you're done. – Unknown",
            "The road to success is dotted with many tempting parking spaces. – Will Rogers",
            "Success is walking from failure to failure with no loss of enthusiasm. – Winston Churchill",
            "The difference between ordinary and extraordinary is that little extra. – Jimmy Johnson"
        ]
        # Select quote based on current date for daily rotation
        today = date.today()
        quote_index = today.toordinal() % len(quotes)
        quote = quotes[quote_index]
        context = {'quote': quote}
        return render(request, 'authentication/login.html', context)

# ---------------- LOGOUT ----------------
def logout_user(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')

# ---------------- PROFILE ----------------
@login_required(login_url='login')
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'authentication/profile_view.html', {'profile': profile})

@login_required(login_url='login')
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'authentication/profile_edit.html', {'form': form})

# ---------------- INCOME ----------------
@login_required(login_url='login')
def income_list(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    total_income = sum(i.amount for i in incomes)
    return render(request, 'authentication/income_list.html', {'incomes': incomes, 'total_income': total_income})

@login_required(login_url='login')
def income_add(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, "Income added successfully.")
            return redirect('dashboard')
    else:
        form = IncomeForm()
    return render(request, 'authentication/add_income.html', {'form': form})

# ---------------- EXPENSE ----------------
@login_required(login_url='login')
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    total_expense = sum(e.amount for e in expenses)
    return render(request, 'authentication/expense_list.html', {'expenses': expenses, 'total_expense': total_expense})

@login_required(login_url='login')
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense added successfully.")
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'authentication/add_expense.html', {'form': form})

# ---------------- INCOME EDIT/DELETE ----------------
@login_required
def edit_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, "Income updated successfully.")
            return redirect('dashboard')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'authentication/edit_income.html', {'form': form})

@login_required
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        income.delete()
        messages.success(request, "Income deleted successfully.")
        return redirect('dashboard')
    return render(request, 'authentication/delete_confirm.html', {'object': income, 'type': 'Income'})

# ---------------- EXPENSE EDIT/DELETE ----------------
@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully.")
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'authentication/edit_expense.html', {'form': form})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Expense deleted successfully.")
        return redirect('dashboard')
    return render(request, 'authentication/delete_confirm.html', {'object': expense, 'type': 'Expense'})

# ---------------- ACCOUNT INTEGRATION ----------------
@login_required(login_url='login')
def account_integration(request):
    if request.method == 'POST':
        form = AccountIntegrationForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            messages.success(request, "Account integrated successfully and will appear in your Dashboard.")
            return redirect('dashboard')
    else:
        form = AccountIntegrationForm()
    accounts = AccountIntegration.objects.filter(user=request.user)
    return render(request, 'authentication/account_integration.html', {
        'form': form,
        'accounts': accounts,
    })

@login_required
def account_edit(request, pk):
    account = get_object_or_404(AccountIntegration, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AccountIntegrationForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, "Account updated successfully.")
            return redirect('dashboard')
    else:
        form = AccountIntegrationForm(instance=account)
    return render(request, 'authentication/edit_account.html', {'form': form})

@login_required
def account_delete(request, pk):
    account = get_object_or_404(AccountIntegration, pk=pk, user=request.user)
    if request.method == 'POST':
        account.delete()
        messages.success(request, "Account deleted successfully.")
        return redirect('dashboard')
    return render(request, 'authentication/delete_confirm.html', {'object': account, 'type': 'Account'})

# ---------------- INVESTMENT ----------------
@login_required(login_url='login')
def investment_list(request):
    investments = Investment.objects.filter(user=request.user).order_by('-last_updated')
    for inv in investments:
        inv.gain = inv.current_value - inv.amount_invested
    total_current = sum(inv.current_value for inv in investments)
    total_invested = sum(inv.amount_invested for inv in investments)
    profit_loss = total_current - total_invested
    return render(request, 'authentication/investment_list.html', {
        'investments': investments,
        'total_current': total_current,
        'total_invested': total_invested,
        'profit_loss': profit_loss,
    })

@login_required(login_url='login')
def investment_add(request):
    if request.method == "POST":
        form = InvestmentForm(request.POST)
        if form.is_valid():
            invest = form.save(commit=False)
            invest.user = request.user
            invest.save()
            messages.success(request, "Investment added successfully!")
            return redirect('investment_list')
    else:
        form = InvestmentForm()
    return render(request, 'authentication/investment_add.html', {'form': form})

@login_required
def investment_edit(request, pk):
    invest = get_object_or_404(Investment, pk=pk, user=request.user)
    if request.method == "POST":
        form = InvestmentForm(request.POST, instance=invest)
        if form.is_valid():
            form.save()
            messages.success(request, "Investment updated successfully.")
            return redirect('dashboard')
    else:
        form = InvestmentForm(instance=invest)
    return render(request, 'authentication/edit_investment.html', {'form': form})

@login_required
def investment_delete(request, pk):
    invest = get_object_or_404(Investment, pk=pk, user=request.user)
    if request.method == "POST":
        invest.delete()
        messages.success(request, "Investment deleted successfully.")
        return redirect('dashboard')
    return render(request, 'authentication/delete_confirm.html', {'object': invest, 'type': 'Investment'})

# ---------------- FINANCIAL GOALS ----------------
@login_required
def goals_list(request):
    goals = FinancialGoal.objects.filter(user=request.user)
    return render(request, 'authentication/goals_list.html', {'goals': goals})

@login_required
def add_goal(request):
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            # Generate suggestion based on goal details
            if goal.due_date and goal.amount and goal.current_amount is not None:
                goal.suggestion = generate_goal_suggestion(
                    goal.name,
                    float(goal.current_amount),
                    float(goal.amount),
                    goal.due_date.strftime('%Y-%m-%d'),
                    request.user
                )
            goal.save()
            return redirect('dashboard')
    else:
        form = FinancialGoalForm()
    return render(request, 'authentication/goal_form.html', {'form': form})

@login_required
def edit_goal(request, pk):
    goal = get_object_or_404(FinancialGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('goals_list')
    else:
        form = FinancialGoalForm(instance=goal)
    return render(request, 'authentication/goal_form.html', {'form': form, 'edit': True})

@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(FinancialGoal, pk=pk, user=request.user)
    goal.delete()
    return redirect('goals_list')

@login_required
def suggestion_list(request):
    suggestions = InvestmentSuggestion.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'authentication/suggestion_list.html', {'suggestions': suggestions})

@login_required
def add_suggestion(request):
    if request.method == "POST":
        form = InvestmentSuggestionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.suggestion_text = generate_goal_suggestion(obj.goal_name, obj.current_amount, obj.target_amount, obj.due_date, request.user)
            obj.save()
            return redirect('suggestion_list')
    else:
        form = InvestmentSuggestionForm()
    return render(request, 'authentication/suggestion_form.html', {'form': form})

@login_required
def edit_suggestion(request, pk):
    suggestion = get_object_or_404(InvestmentSuggestion, pk=pk, user=request.user)
    if request.method == "POST":
        form = InvestmentSuggestionForm(request.POST, instance=suggestion)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.suggestion_text = generate_goal_suggestion(obj.goal_name, obj.current_amount, obj.target_amount, obj.due_date, request.user)
            obj.save()
            return redirect('suggestion_list')
    else:
        form = InvestmentSuggestionForm(instance=suggestion)
    return render(request, 'authentication/suggestion_form.html', {'form': form, 'edit': True})

@login_required
def delete_suggestion(request, pk):
    suggestion = get_object_or_404(InvestmentSuggestion, pk=pk, user=request.user)
    if request.method == "POST":
        suggestion.delete()
        return redirect('suggestion_list')
    return render(request, 'authentication/delete_confirm.html', {'object': suggestion, 'type': 'Investment Suggestion'})

def analyze_user_expense_behavior(request, month=None):
    import pandas as pd
    df = pd.read_excel(DATASET_PATH)
    user_id = request.user.username
    prof = ""
    income = 0
    try:
        prof = request.user.profile.profession
        income = float(request.user.profile.salary)
    except:
        pass
    current_row = df[(df.UserID == user_id)].iloc[-1]
    similar = df[(df.JobRole == prof) & (abs(df.Income.astype(float) - income) < 0.2*income)]
    avg_expense_ratio = similar['Expense_Ratio'].mean()
    user_expense_ratio = current_row['Expense_Ratio']
    msg = ""
    if user_expense_ratio > avg_expense_ratio * 1.15:
        msg += f"Your expenses ({user_expense_ratio:.1%}) are higher than similar {prof}s (avg: {avg_expense_ratio:.1%}). "
    elif user_expense_ratio < avg_expense_ratio * 0.8:
        msg += f"Excellent! Your expense rate is much better than the average {prof}. "
    saver = current_row['Saver_Type']
    group_mode_type = similar['Saver_Type'].mode().iloc[0] if not similar.empty else "-"
    if saver != group_mode_type:
        msg += f"Your saver type is '{saver}', while most peers are '{group_mode_type}'. "
    one_time = current_row['One_time_Expenses']
    if one_time > 0.3 * income:
        group_mean = similar['One_time_Expenses'].mean() if not similar.empty else 0
        msg += f"Large one-time expense detected (₹{one_time:.0f}); peer average is ₹{group_mean:.0f}. "
    flag = int(current_row['Overspending_Flag'])
    if flag == 2:
        msg += "You are overspending for your profile group."
    elif flag == 0:
        msg += "Stable and good overall spending habits."
    return msg.strip()


