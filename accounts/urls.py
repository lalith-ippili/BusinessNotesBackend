from django.urls import path
from .views import RegisterView,CalculatorHistoryListCreateView, CalculatorHistoryDetailView, LoginView,HabitTrackerListCreateView, HabitTrackerDetailView, ForgotPasswordView,GoalListCreateView,DayPlanListCreateView, DayPlanDetailView, GoalDetailView, ResetPasswordView,NoteListCreateView, NoteDetailView, ProfileView,TaskListCreateView, TaskDetailView, HomeDashboardView,PomodoroTimerListCreateView, PomodoroTimerDetailView, IncomeListCreateView,IncomeDetailView,ExpenseListCreateView,ExpenseDetailView,FinanceDashboardView,MonthlyBudgetView,CalendarDashboardView

urlpatterns = [
path('register/', RegisterView.as_view(), name='register'),
path('login/', LoginView.as_view(), name='login'),
path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
path('profile/', ProfileView.as_view(), name='profile'),

# task----

path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

# notes----

path('notes/', NoteListCreateView.as_view(), name='note-list-create'),
path('notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail'),

# Goals-----------------------

path('goals/', GoalListCreateView.as_view(), name='goal-list-create'),
path('goals/<int:pk>/', GoalDetailView.as_view(), name='goal-detail'),

# dayplan------------------------------

path('day-plans/', DayPlanListCreateView.as_view(), name='day-plan-list-create'),
path('day-plans/<int:pk>/', DayPlanDetailView.as_view(), name='day-plan-detail'),

# home dashboard------------------------------
path('home-dashboard/', HomeDashboardView.as_view(), name='home-dashboard'),

#abitTracker--------------------------------------------

path('habits/', HabitTrackerListCreateView.as_view(), name='habit-list-create'),
path('habits/<int:pk>/', HabitTrackerDetailView.as_view(), name='habit-detail'),

#PomodoroTimer------------------------------------

path('pomodoro-timers/', PomodoroTimerListCreateView.as_view(), name='pomodoro-timer-list-create'),
path('pomodoro-timers/<int:pk>/', PomodoroTimerDetailView.as_view(), name='pomodoro-timer-detail'),

#Income----------------------------

path('incomes/', IncomeListCreateView.as_view(), name='income-list-create'),
path('incomes/<int:pk>/', IncomeDetailView.as_view(), name='income-detail'),

#expenses--------------------------

path('expenses/', ExpenseListCreateView.as_view(), name='expense-list-create'),
path('expenses/<int:pk>/', ExpenseDetailView.as_view(), name='expense-detail'),

#finance-dashboard--------------------------

path('finance-dashboard/', FinanceDashboardView.as_view(), name='finance-dashboard'),
path('monthly-budget/', MonthlyBudgetView.as_view(), name='monthly-budget'),


#CalendarDashboard------------------------------------------
path('calendar-dashboard/', CalendarDashboardView.as_view(), name='calendar-dashboard'),

# CalculatorHistoryList------------------------------------------

path('calculator-history/', CalculatorHistoryListCreateView.as_view(), name='calculator-history-list-create'),
path('calculator-history/<int:pk>/', CalculatorHistoryDetailView.as_view(), name='calculator-history-detail'),











































]
