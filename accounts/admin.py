from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .models import Task
from .models import Note
from .models import Goal
from .models import DayPlan
from .models import Income, Expense
from .models import HabitTracker
from .models import PomodoroTimer


@admin.register(User)

class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
    'id',
    'name',
    'email',
    'is_staff',
    'is_active',
    'is_superuser',
    'created_at',
    )
    list_filter = (
    'is_staff',
    'is_active',
    'is_superuser',
    )
    search_fields = (
    'name',
    'email',
    )
    ordering = ('-id',)

    fieldsets = (
    ('Login Info', {
    'fields': ('email', 'password')
    }),
    ('Personal Info', {
    'fields': ('name', 'image')
    }),
    ('Permissions', {
    'fields': (
    'is_active',
    'is_staff',
    'is_superuser',
    'groups',
    'user_permissions',
    )
    }),
    ('Important Dates', {
    'fields': ('last_login', 'created_at', 'updated_at')
    }),
    )

    readonly_fields = ('created_at', 'updated_at', 'last_login')

    add_fieldsets = (
    ('Create User', {
    'classes': ('wide',),
    'fields': (
    'name',
    'email',
    'image',
    'password1',
    'password2',
    'is_active',
    'is_staff',
    'is_superuser',
    ),
    }),
    )

# task----
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'status', 'priority', 'due_date', 'category', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description', 'user__email', 'user__name')
    ordering = ('-id',)

# Notes----

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'content', 'user__email', 'user__name')
    ordering = ('-id',)

# Goals-----------------------

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = (
    'id',
    'title',
    'user',
    'category',
    'target_date',
    'status',
    'progress',
    'is_completed',
    'created_at',
    )
    list_filter = ('status', 'is_completed', 'category', 'target_date')
    search_fields = ('title', 'description', 'category', 'user__email', 'user__name')
    ordering = ('-id',)
# dayplan------------------------------

@admin.register(DayPlan)
class DayPlanAdmin(admin.ModelAdmin):
    list_display = (
    'id',
    'user',
    'plan_date',
    'time',
    'category',
    'is_done',
    'created_at',
    )
    list_filter = (
    'plan_date',
    'is_done',
    'category',
    )
    search_fields = (
    'user__email',
    'description',
    'category',
    )
    ordering = ('plan_date', 'time')
    list_editable = ('is_done',)
    list_per_page = 20
#HabitTracker---------------------------------------

@admin.register(HabitTracker)
class HabitTrackerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'icon', 'created_at')
    search_fields = ('name', 'user__email', 'user__name')
    ordering = ('-id',)

#PomodoroTimer---------------------------------------
@admin.register(PomodoroTimer)
class PomodoroTimerAdmin(admin.ModelAdmin):
    list_display = (
    'id',
    'title',
    'user',
    'work_duration',
    'break_duration',
    'long_break_duration',
    'cycles',
    'is_active',
    'created_at',
    )
    list_filter = ('is_active',)
    search_fields = ('title', 'user__email', 'user__name')
    ordering = ('-id',)

#IncomeAdmin----------------------

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'user',
        'amount',
        'category',
        'income_type',
        'income_date',
        'start_date',
        'due_day_of_month',
        'due_month_of_year',
        'is_active',
        'created_at',
    )
    list_filter = ('category', 'income_type', 'is_active')
    search_fields = ('name', 'notes', 'user__email', 'user__name')
    ordering = ('-id',)
#ExpenseAdmin---------------------------

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
    'id',
    'name',
    'user',
    'amount',
    'category',
    'expense_type',
    'expense_date',
    'is_paid',
    'created_at',
    )
    list_filter = ('category', 'expense_type', 'is_paid', 'expense_date')
    search_fields = ('name', 'notes', 'user__email', 'user__name')
    ordering = ('-expense_date', '-id')
