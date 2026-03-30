from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from authentication import views

urlpatterns = [
    

    path('admin/', admin.site.urls),
    path('', views.splash, name='splash'),

    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('income/', views.income_list, name='income_list'),
    path('income/add/', views.income_add, name='income_add'),
    path('income/<int:pk>/edit/', views.edit_income, name='edit_income'),
    path('income/<int:pk>/delete/', views.delete_income, name='delete_income'),
    path('expense/', views.expense_list, name='expense_list'),
    path('expense/add/', views.expense_add, name='expense_add'),
    path('expense/<int:pk>/edit/', views.edit_expense, name='edit_expense'),
    path('expense/<int:pk>/delete/', views.delete_expense, name='delete_expense'),

    path('account-integration/', views.account_integration, name='account_integration'),
    path('accounts/<int:pk>/edit/', views.account_edit, name='edit_account'),
    path('accounts/<int:pk>/delete/', views.account_delete, name='delete_account'),

    path('investments/', views.investment_list, name='investment_list'),
    path('investments/add/', views.investment_add, name='investment_add'),
    path('investments/<int:pk>/edit/', views.investment_edit, name='edit_investment'),
    path('investments/<int:pk>/delete/', views.investment_delete, name='delete_investment'),

    # Financial Goals CRUD (no 'financial_goals' view)
    path('goals/', views.goals_list, name='goals_list'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('goals/<int:pk>/edit/', views.edit_goal, name='edit_goal'),
    path('goals/<int:pk>/delete/', views.delete_goal, name='delete_goal'),

    path('suggestions/', views.suggestion_list, name='suggestion_list'),
    path('suggestion/add/', views.add_suggestion, name='add_suggestion'),
    path('suggestion/<int:pk>/edit/', views.edit_suggestion, name='edit_suggestion'),
    path('suggestion/<int:pk>/delete/', views.delete_suggestion, name='delete_suggestion'),
]



