from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email=email, name=name, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


# task------


class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    CATEGORY_CHOICES = (
        ('work', 'Work'),
        ('personal', 'Personal'),
        ('business', 'Business'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(blank=True, null=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title

# Notes---------------------

class Note(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notes'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=200, default='other', blank=True)
    image = models.ImageField(upload_to='notes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title


# Goals-------------------


class Goal(models.Model):
    CATEGORY_CHOICES = (
        ('personal', 'Personal'),
        ('career', 'Career'),
        ('business', 'Business'),
        ('health', 'Health'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='goals'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    target_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.progress >= 100:
            self.progress = 100
            self.is_completed = True
            self.status = 'completed'
        elif self.progress > 0 and self.progress < 100 and self.status == 'not_started':
            self.status = 'in_progress'
        elif self.is_completed:
            self.status = 'completed'
            if self.progress < 100:
                self.progress = 100

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



# dayplan-------------

class DayPlan(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='day_plans'
    )
    plan_date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True, null=True)
    is_done = models.BooleanField(default=False)
    category = models.CharField(max_length=100, blank=True, null=True)  # user input string
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['plan_date', 'time']

    def __str__(self):
        return f"{self.plan_date} - {self.time}"



# HabitTracker------------------------------------

class HabitTracker(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='habits'
    )
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, blank=True, null=True)
    days = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name



#PomodoroTimer-----------------------------------

class PomodoroTimer(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='pomodoro_timers'
    )
    title = models.CharField(max_length=255)
    work_duration = models.PositiveIntegerField(default=25)
    break_duration = models.PositiveIntegerField(default=5)
    long_break_duration = models.PositiveIntegerField(default=15)
    cycles = models.PositiveIntegerField(default=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title

#Income------------------------------------------------

class Income(models.Model):
    CATEGORY_CHOICES = (
        ('salary', 'Salary'),
        ('business', 'Business'),
        ('rent', 'Rent'),
        ('freelance', 'Freelance'),
        ('interest', 'Interest'),
        ('other', 'Other'),
    )

    TYPE_CHOICES = (
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='incomes'
    )
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    income_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='monthly')
    due_day_of_month = models.PositiveSmallIntegerField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name

#Expense---------------
class Expense(models.Model):
    CATEGORY_CHOICES = (
        ('food', 'Food'),
        ('travel', 'Travel'),
        ('shopping', 'Shopping'),
        ('bills', 'Bills'),
        ('health', 'Health'),
        ('entertainment', 'Entertainment'),
        ('rent', 'Rent'),
        ('education', 'Education'),
        ('emi', 'EMI'),
        ('other', 'Other'),
    )

    TYPE_CHOICES = (
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    expense_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='monthly')
    due_day_of_month = models.PositiveSmallIntegerField(null=True, blank=True)
    expense_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expense_date', '-id']

    def __str__(self):
        return self.name





























































