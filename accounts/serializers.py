from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from google.oauth2 import id_token
from django.conf import settings
from google.auth.transport import requests as google_requests


from .models import User
from .models import Task
from .models import Note
from .models import Goal
from .models import DayPlan
from .tokens import password_reset_token
from .models import Income, Expense
from .models import HabitTracker
from .models import PomodoroTimer
from .models import CalculatorHistory
from .models import Notification












class GoogleLoginSerializer(serializers.Serializer):
    credential = serializers.CharField(write_only=True)

    def validate(self, attrs):
        credential = attrs.get('credential')

        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                credential, 
                google_requests.Request(), 
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )

            # Extract user info from Google's payload
            email = idinfo['email']
            name = idinfo.get('name', 'Google User')
            
            # Check if user exists. If not, create a new one.
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'name': name}
            )

            # If created via Google, they don't have a password. 
            # set_unusable_password() ensures they can't login via normal email/password 
            # unless they specifically set one later.
            if created:
                user.set_unusable_password()
                # If your model requires image handling, you can also extract idinfo.get('picture') here
                user.save()

            if not user.is_active:
                raise serializers.ValidationError("User account is inactive.")

            attrs['user'] = user
            return attrs

        except ValueError:
            raise serializers.ValidationError("Invalid or expired Google token.")



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'image', 'password', 'confirm_password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is inactive.")

        attrs['user'] = user
        return attrs
from rest_framework import serializers
from .models import User


class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'email',
            'image',
            'image_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class Meta:
    model = User
    fields = ['id', 'name', 'email', 'image', 'image_url', 'created_at', 'updated_at']
    read_only_fields = ['id', 'email', 'created_at', 'updated_at']

def get_image_url(self, obj):
    request = self.context.get('request')
    if obj.image and request:
        return request.build_absolute_uri(obj.image.url)
        return None

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

def validate_email(self, value):
    if not User.objects.filter(email=value).exists():
        raise serializers.ValidationError("No account found with this email.")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

def validate(self, attrs):
    if attrs['new_password'] != attrs['confirm_password']:
        raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except Exception:
            raise serializers.ValidationError({"uid": "Invalid user id."})

            if not password_reset_token.check_token(user, attrs['token']):
                raise serializers.ValidationError({"token": "Invalid or expired token."})

                validate_password(attrs['new_password'])
                attrs['user'] = user
                return attrs


                # task--

# Task---------------

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
        'id',
        'title',
        'description',
        'status',
        'priority',
        'due_date',
        'category',
        'is_completed',
        'created_at',
        'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

def validate(self, attrs):
    is_completed = attrs.get('is_completed')
    status_value = attrs.get('status')

    if is_completed is True and not status_value:
        attrs['status'] = 'completed'

        if status_value == 'completed' and 'is_completed' not in attrs:
            attrs['is_completed'] = True

            return attrs

# Notes--------------------


class NoteSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category = serializers.CharField(required=False, allow_blank=True, max_length=200)

    class Meta:
        model = Note
        fields = [
            'id',
            'title',
            'content',
            'category',
            'image',
            'image_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'image_url', 'created_at', 'updated_at']

    def validate_category(self, value):
        value = (value or "").strip()
        return value if value else "other"

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

# Goals-------------

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = [
            'id',
            'title',
            'description',
            'category',
            'target_date',
            'status',
            'progress',
            'is_completed',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

# dayplan-------------------------------------------


class DayPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayPlan
        fields = [
            'id',
            'user',
            'plan_date',
            'time',
            'description',
            'category',
            'is_done',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

# HabitTrackerSerializer-----------------------------------

class HabitTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTracker
        fields = [
            'id',
            'name',
            'icon',
            'days',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_days(self, value):
        allowed_days = {
            'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday'
        }

        if not isinstance(value, list):
            raise serializers.ValidationError("Days must be a list.")

        for day in value:
            if str(day).lower() not in allowed_days:
                raise serializers.ValidationError(
                    f"Invalid day: {day}. Use valid weekday names."
                )

        return [str(day).lower() for day in value]

#PomodoroTimerSerializer-------------------------------

class PomodoroTimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PomodoroTimer
        fields = [
            'id',
            'title',
            'work_duration',
            'break_duration',
            'long_break_duration',
            'cycles',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_work_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Work duration must be greater than 0.")
        return value

    def validate_break_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Break duration must be greater than 0.")
        return value

    def validate_long_break_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Long break duration must be greater than 0.")
        return value

    def validate_cycles(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cycles must be greater than 0.")
        return value


#IncomeSerializer------------------------
class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = [
            'id',
            'name',
            'amount',
            'category',
            'income_type',
            'income_date',
            'start_date',
            'due_day_of_month',
            'due_month_of_year',
            'is_active',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_due_day_of_month(self, value):
        if value is not None and not (1 <= value <= 31):
            raise serializers.ValidationError("Due day of month must be between 1 and 31.")
        return value

    def validate_due_month_of_year(self, value):
        if value is not None and not (1 <= value <= 12):
            raise serializers.ValidationError("Due month of year must be between 1 and 12.")
        return value

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        income_type = attrs.get('income_type', getattr(instance, 'income_type', None))
        income_date = attrs.get('income_date', getattr(instance, 'income_date', None))
        start_date = attrs.get('start_date', getattr(instance, 'start_date', None))
        due_day = attrs.get('due_day_of_month', getattr(instance, 'due_day_of_month', None))
        due_month = attrs.get('due_month_of_year', getattr(instance, 'due_month_of_year', None))

        if income_type == 'daily':
            if not income_date:
                raise serializers.ValidationError({
                    "income_date": "This field is required for daily income."
                })

            attrs['start_date'] = None
            attrs['due_day_of_month'] = None
            attrs['due_month_of_year'] = None

        elif income_type == 'monthly':
            if not start_date:
                raise serializers.ValidationError({
                    "start_date": "This field is required for monthly income."
                })
            if due_day is None:
                raise serializers.ValidationError({
                    "due_day_of_month": "This field is required for monthly income."
                })

            attrs['income_date'] = None
            attrs['due_month_of_year'] = None

        elif income_type == 'yearly':
            if not start_date:
                raise serializers.ValidationError({
                    "start_date": "This field is required for yearly income."
                })
            if due_day is None:
                raise serializers.ValidationError({
                    "due_day_of_month": "This field is required for yearly income."
                })
            if due_month is None:
                raise serializers.ValidationError({
                    "due_month_of_year": "This field is required for yearly income."
                })

            attrs['income_date'] = None

        else:
            raise serializers.ValidationError({
                "income_type": "Invalid income type."
            })

        return attrs

#EXPENSESerializer---------------------------

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'id',
            'name',
            'amount',
            'category',
            'expense_type',
            'expense_date',
            'start_date',
            'due_day_of_month',
            'due_month_of_year',
            'is_active',
            'is_paid',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_due_day_of_month(self, value):
        if value is not None and not (1 <= value <= 31):
            raise serializers.ValidationError("Due day of month must be between 1 and 31.")
        return value

    def validate_due_month_of_year(self, value):
        if value is not None and not (1 <= value <= 12):
            raise serializers.ValidationError("Due month of year must be between 1 and 12.")
        return value

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        expense_type = attrs.get('expense_type', getattr(instance, 'expense_type', None))
        expense_date = attrs.get('expense_date', getattr(instance, 'expense_date', None))
        start_date = attrs.get('start_date', getattr(instance, 'start_date', None))
        due_day = attrs.get('due_day_of_month', getattr(instance, 'due_day_of_month', None))
        due_month = attrs.get('due_month_of_year', getattr(instance, 'due_month_of_year', None))

        if expense_type == 'daily':
            if not expense_date:
                raise serializers.ValidationError({
                    "expense_date": "This field is required for daily expense."
                })

            attrs['start_date'] = None
            attrs['due_day_of_month'] = None
            attrs['due_month_of_year'] = None

        elif expense_type == 'monthly':
            if not start_date:
                raise serializers.ValidationError({
                    "start_date": "This field is required for monthly expense."
                })
            if due_day is None:
                raise serializers.ValidationError({
                    "due_day_of_month": "This field is required for monthly expense."
                })

            attrs['expense_date'] = None
            attrs['due_month_of_year'] = None

        elif expense_type == 'yearly':
            if not start_date:
                raise serializers.ValidationError({
                    "start_date": "This field is required for yearly expense."
                })
            if due_day is None:
                raise serializers.ValidationError({
                    "due_day_of_month": "This field is required for yearly expense."
                })
            if due_month is None:
                raise serializers.ValidationError({
                    "due_month_of_year": "This field is required for yearly expense."
                })

            attrs['expense_date'] = None

        else:
            raise serializers.ValidationError({
                "expense_type": "Invalid expense type."
            })

        return attrs



# CalculatorHistorySerializer---------------------------

class CalculatorHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculatorHistory
        fields = [
            'id',
            'expression',
            'result',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']





# NotificationSerializer---------------------------

class NotificationSerializer(serializers.ModelSerializer):
    # Format the date nicely for the frontend (e.g., "10 mins ago" logic can be done on frontend, 
    # but we send a clean ISO timestamp from backend)
    time = serializers.DateTimeField(source='created_at', read_only=True, format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'type', 'is_read', 'time']
        read_only_fields = ['id', 'time']

    def create(self, validated_data):
        # Automatically set the user to the currently logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



























