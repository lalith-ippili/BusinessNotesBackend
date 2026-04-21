from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.db.models import Sum, Q
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from collections import defaultdict
from calendar import monthrange
from datetime import date
from django.db.models.functions import ExtractWeek



from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProfileSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    TaskSerializer,
    NoteSerializer,
    GoalSerializer,
    DayPlanSerializer,
    IncomeSerializer, 
    ExpenseSerializer,
    HabitTrackerSerializer,
    PomodoroTimerSerializer
)
from .tokens import password_reset_token
from .models import Task
from .models import Note
from .models import Goal
from .models import DayPlan
from .models import HabitTracker
from .models import PomodoroTimer
from .models import Income, Expense











User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)

            return Response({
                "success": True,
                "message": "User registered successfully.",
                "user": ProfileSerializer(user, context={'request': request}).data,
                "tokens": tokens
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        tokens = get_tokens_for_user(user)

        return Response({
            "success": True,
            "message": "Login successful.",
            "user": ProfileSerializer(user, context={'request': request}).data,
            "tokens": tokens
        }, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user, context={'request': request})
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = ProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Profile updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = password_reset_token.make_token(user)

            reset_link = f"http://127.0.0.1:8000/api/accounts/reset-password/?uid={uid}&token={token}"

            send_mail(
                subject="Password Reset Request",
                message=f"Use this link to reset your password:\n\n{reset_link}",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response({
                "success": True,
                "message": "Password reset link sent to your email.",
                "reset_link_for_testing": reset_link
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = {
            "uid": request.data.get("uid"),
            "token": request.data.get("token"),
            "new_password": request.data.get("new_password"),
            "confirm_password": request.data.get("confirm_password"),
        }

        serializer = ResetPasswordSerializer(data=data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({
                "success": True,
                "message": "Password reset successful. You can now login with new password."
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({
            "message": "Send uid, token, new_password, confirm_password in POST request."
        }, status=status.HTTP_200_OK)


class TaskListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(user=request.user)
        serializer = TaskSerializer(tasks, many=True)

        total_tasks = tasks.count()
        completed_tasks = tasks.filter(is_completed=True).count()
        remaining_tasks = tasks.filter(is_completed=False).count()

        return Response({
            "success": True,
            "counts": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "remaining_tasks": remaining_tasks
            },
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "success": True,
                "message": "Task created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(Task, pk=pk, user=request.user)

    def get(self, request, pk):
        task = self.get_object(request, pk)
        serializer = TaskSerializer(task)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        task = self.get_object(request, pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Task updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        task = self.get_object(request, pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Task partially updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = self.get_object(request, pk)
        task.delete()
        return Response({
            "success": True,
            "message": "Task deleted successfully."
        }, status=status.HTTP_200_OK)


# Notes-----------

class NoteListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notes = Note.objects.filter(user=request.user)
        serializer = NoteSerializer(notes, many=True, context={'request': request})
        return Response({
            "success": True,
            "count": notes.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = NoteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "success": True,
                "message": "Note created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class NoteDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(Note, pk=pk, user=request.user)

    def get(self, request, pk):
        note = self.get_object(request, pk)
        serializer = NoteSerializer(note, context={'request': request})
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        note = self.get_object(request, pk)
        serializer = NoteSerializer(note, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Note updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        note = self.get_object(request, pk)
        serializer = NoteSerializer(note, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Note partially updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        note = self.get_object(request, pk)
        note.delete()
        return Response({
            "success": True,
            "message": "Note deleted successfully."
        }, status=status.HTTP_200_OK)



# Goals----

class GoalListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        goals = Goal.objects.filter(user=request.user)
        serializer = GoalSerializer(goals, many=True)

        total_goals = goals.count()
        completed_goals = goals.filter(is_completed=True).count()
        remaining_goals = goals.filter(is_completed=False).count()

        return Response({
            "success": True,
            "counts": {
                "total_goals": total_goals,
                "completed_goals": completed_goals,
                "remaining_goals": remaining_goals
            },
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GoalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "success": True,
                "message": "Goal created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class GoalDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(Goal, pk=pk, user=request.user)

    def get(self, request, pk):
        goal = self.get_object(request, pk)
        serializer = GoalSerializer(goal)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        goal = self.get_object(request, pk)
        serializer = GoalSerializer(goal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Goal updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        goal = self.get_object(request, pk)
        serializer = GoalSerializer(goal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Goal partially updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        goal = self.get_object(request, pk)
        goal.delete()
        return Response({
            "success": True,
            "message": "Goal deleted successfully."
        }, status=status.HTTP_200_OK)


# dayplan-----------------------------------------

class DayPlanListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        day_plans = DayPlan.objects.filter(user=request.user).order_by('plan_date', 'time')
        serializer = DayPlanSerializer(day_plans, many=True, context={'request': request})

        total_plans = day_plans.count()
        completed_plans = day_plans.filter(is_done=True).count()
        remaining_plans = day_plans.filter(is_done=False).count()

        return Response({
            "success": True,
            "counts": {
                "total_plans": total_plans,
                "completed_plans": completed_plans,
                "remaining_plans": remaining_plans,
            },
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DayPlanSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "success": True,
                "message": "Day plan created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DayPlanDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(
            DayPlan,
            pk=pk,
            user=request.user
        )

    def get(self, request, pk):
        day_plan = self.get_object(request, pk)
        serializer = DayPlanSerializer(day_plan, context={'request': request})
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        day_plan = self.get_object(request, pk)
        serializer = DayPlanSerializer(
            day_plan,
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Day plan updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        day_plan = self.get_object(request, pk)
        serializer = DayPlanSerializer(
            day_plan,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Day plan partially updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        day_plan = self.get_object(request, pk)
        day_plan.delete()
        return Response({
            "success": True,
            "message": "Day plan deleted successfully."
        }, status=status.HTTP_200_OK)

# Home dashboard overview-----------------------------


class HomeDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        current_month = today.month
        current_year = today.year

        user = request.user

        # Tasks
        tasks = Task.objects.filter(user=user)
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(is_completed=True).count()
        pending_tasks = tasks.filter(is_completed=False).count()
        recent_tasks = tasks.order_by('-id')[:5]

        recent_tasks_data = [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date,
                "category": task.category,
                "is_completed": task.is_completed,
            }
            for task in recent_tasks
        ]

        # Notes
        notes = Note.objects.filter(user=user)
        total_notes = notes.count()
        recent_notes = notes.order_by('-id')[:5]

        recent_notes_data = [
            {
                "id": note.id,
                "title": note.title,
                "category": note.category,
                "image": note.image.url if note.image else None,
                "created_at": note.created_at,
            }
            for note in recent_notes
        ]

        # Goals
        goals = Goal.objects.filter(user=user)
        total_goals = goals.count()
        completed_goals = goals.filter(is_completed=True).count()
        active_goals = goals.filter(is_completed=False).count()
        avg_goal_progress = goals.aggregate(total_progress=Sum('progress'))['total_progress'] or 0

        if total_goals > 0:
            avg_goal_progress = round(avg_goal_progress / total_goals, 2)

        recent_goals = goals.order_by('-id')[:5]
        recent_goals_data = [
            {
                "id": goal.id,
                "title": goal.title,
                "category": goal.category,
                "target_date": goal.target_date,
                "status": goal.status,
                "progress": goal.progress,
                "is_completed": goal.is_completed,
            }
            for goal in recent_goals
        ]

        # Day Plans
        today_plans = DayPlan.objects.filter(
            user=user,
            plan_date=today
        )

        total_today_plans = today_plans.count()
        completed_today_plans = today_plans.filter(is_done=True).count()
        pending_today_plans = today_plans.filter(is_done=False).count()

        today_plans_data = [
            {
                "id": plan.id,
                "time": plan.time,
                "plan_date": plan.plan_date,
                "description": plan.description,
                "category": plan.category,
                "is_done": plan.is_done,
            }
            for plan in today_plans
        ]

        # Income - current month dashboard data
        incomes = Income.objects.filter(
            user=user,
            is_active=True
        )

        total_income_sources = incomes.count()
        total_month_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        recent_incomes = incomes.order_by('-id')[:5]

        recent_incomes_data = [
            {
                "id": income.id,
                "name": income.name,
                "amount": income.amount,
                "category": income.category,
                "income_type": income.income_type,
                "due_day_of_month": income.due_day_of_month,
                "start_date": income.start_date,
                "is_active": income.is_active,
                "notes": income.notes,
            }
            for income in recent_incomes
        ]

        # Expenses - current month only
        month_expenses = Expense.objects.filter(
            user=user,
            expense_date__month=current_month,
            expense_date__year=current_year
        )

        total_month_expense = month_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_expense_items = month_expenses.count()
        paid_expenses_count = month_expenses.filter(is_paid=True).count()
        unpaid_expenses_count = month_expenses.filter(is_paid=False).count()

        recent_expenses = month_expenses.order_by('-expense_date', '-id')[:5]
        recent_expenses_data = [
            {
                "id": expense.id,
                "name": expense.name,
                "amount": expense.amount,
                "category": expense.category,
                "expense_type": expense.expense_type,
                "due_day_of_month": expense.due_day_of_month,
                "expense_date": expense.expense_date,
                "is_paid": expense.is_paid,
                "notes": expense.notes,
            }
            for expense in recent_expenses
        ]

        # Finance summary
        remaining_amount = total_month_income - total_month_expense

        savings_rate = Decimal('0.00')
        if total_month_income > 0:
            savings_rate = round((remaining_amount / total_month_income) * 100, 2)

        savings_label = "Poor"
        if savings_rate >= 50:
            savings_label = "Excellent"
        elif savings_rate >= 30:
            savings_label = "Good"
        elif savings_rate >= 10:
            savings_label = "Fair"

        return Response({
            "success": True,
            "date_context": {
                "today": today,
                "current_month": current_month,
                "current_year": current_year,
            },
            "cards": {
                "tasks": {
                    "title": "Tasks",
                    "total": total_tasks,
                    "completed": completed_tasks,
                    "pending": pending_tasks,
                },
                "notes": {
                    "title": "Notes",
                    "total": total_notes,
                },
                "goals": {
                    "title": "Goals",
                    "total": total_goals,
                    "completed": completed_goals,
                    "active": active_goals,
                    "average_progress": avg_goal_progress,
                },
                "today_plans": {
                    "title": "Today's Plans",
                    "total": total_today_plans,
                    "completed": completed_today_plans,
                    "pending": pending_today_plans,
                },
                "income": {
                    "title": "Income",
                    "total_sources": total_income_sources,
                    "month_income": total_month_income,
                },
                "expenses": {
                    "title": "Expenses",
                    "total_items": total_expense_items,
                    "month_expense": total_month_expense,
                    "paid": paid_expenses_count,
                    "unpaid": unpaid_expenses_count,
                },
                "finance_summary": {
                    "title": "Finance Summary",
                    "month_income": total_month_income,
                    "month_expense": total_month_expense,
                    "remaining_amount": remaining_amount,
                    "savings_rate": savings_rate,
                    "savings_label": savings_label,
                }
            },
            "sections": {
                "recent_tasks": recent_tasks_data,
                "recent_notes": recent_notes_data,
                "recent_goals": recent_goals_data,
                "today_day_plans": today_plans_data,
                "recent_incomes": recent_incomes_data,
                "recent_expenses": recent_expenses_data,
            }
        }, status=status.HTTP_200_OK)


#HabitTrackerListCreateView--------------------------------------------

class HabitTrackerListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        habits = HabitTracker.objects.filter(user=request.user)
        serializer = HabitTrackerSerializer(habits, many=True)
        return Response({
            "success": True,
            "count": habits.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = HabitTrackerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "success": True,
                "message": "Habit created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class HabitTrackerDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(HabitTracker, pk=pk, user=request.user)

    def get(self, request, pk):
        habit = self.get_object(request, pk)
        serializer = HabitTrackerSerializer(habit)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        habit = self.get_object(request, pk)
        serializer = HabitTrackerSerializer(habit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Habit updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        habit = self.get_object(request, pk)
        serializer = HabitTrackerSerializer(habit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Habit partially updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        habit = self.get_object(request, pk)
        habit.delete()
        return Response({
            "success": True,
            "message": "Habit deleted successfully."
        }, status=status.HTTP_200_OK)

#PomodoroTimer--------------------------------

class PomodoroTimerListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        timers = PomodoroTimer.objects.filter(user=request.user)
        serializer = PomodoroTimerSerializer(timers, many=True)
        return Response({
            "success": True,
            "count": timers.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PomodoroTimerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "success": True,
                "message": "Pomodoro timer created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PomodoroTimerDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(PomodoroTimer, pk=pk, user=request.user)

    def get(self, request, pk):
        timer = self.get_object(request, pk)
        serializer = PomodoroTimerSerializer(timer)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        timer = self.get_object(request, pk)
        serializer = PomodoroTimerSerializer(timer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Pomodoro timer updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        timer = self.get_object(request, pk)
        serializer = PomodoroTimerSerializer(timer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Pomodoro timer partially updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        timer = self.get_object(request, pk)
        timer.delete()
        return Response({
            "success": True,
            "message": "Pomodoro timer deleted successfully."
        }, status=status.HTTP_200_OK)

#IncomeListC-------------------------------------------------

def is_monthly_visible(start_date, selected_year, selected_month):
    if not start_date:
        return False

    start_month_date = date(start_date.year, start_date.month, 1)
    selected_month_date = date(selected_year, selected_month, 1)
    return start_month_date <= selected_month_date


def is_yearly_visible(start_date, due_month_of_year, selected_year, selected_month):
    if not start_date or not due_month_of_year:
        return False

    start_month_date = date(start_date.year, start_date.month, 1)
    selected_month_date = date(selected_year, selected_month, 1)

    return start_month_date <= selected_month_date and due_month_of_year == selected_month


def get_visible_income_queryset(user, month, year):
    incomes = Income.objects.filter(user=user, is_active=True)
    visible_ids = []

    for income in incomes:
        if income.income_type == 'daily':
            if income.income_date and income.income_date.month == month and income.income_date.year == year:
                visible_ids.append(income.id)

        elif income.income_type == 'monthly':
            if is_monthly_visible(income.start_date, year, month):
                visible_ids.append(income.id)

        elif income.income_type == 'yearly':
            if is_yearly_visible(income.start_date, income.due_month_of_year, year, month):
                visible_ids.append(income.id)

    return incomes.filter(id__in=visible_ids)


def get_visible_expense_queryset(user, month, year):
    expenses = Expense.objects.filter(user=user, is_active=True)
    visible_ids = []

    for expense in expenses:
        if expense.expense_type == 'daily':
            if expense.expense_date and expense.expense_date.month == month and expense.expense_date.year == year:
                visible_ids.append(expense.id)

        elif expense.expense_type == 'monthly':
            if is_monthly_visible(expense.start_date, year, month):
                visible_ids.append(expense.id)

        elif expense.expense_type == 'yearly':
            if is_yearly_visible(expense.start_date, expense.due_month_of_year, year, month):
                visible_ids.append(expense.id)

    return expenses.filter(id__in=visible_ids)


class IncomeListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        month = int(request.query_params.get('month', today.month))
        year = int(request.query_params.get('year', today.year))

        incomes = get_visible_income_queryset(request.user, month, year)

        income_type = request.query_params.get('income_type')
        category = request.query_params.get('category')

        if income_type:
            incomes = incomes.filter(income_type=income_type)
        if category:
            incomes = incomes.filter(category=category)

        serializer = IncomeSerializer(incomes.order_by('-id'), many=True)

        total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        monthly_income = incomes.filter(income_type='monthly').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        daily_income = incomes.filter(income_type='daily').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        yearly_income = incomes.filter(income_type='yearly').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        return Response({
            "success": True,
            "filters": {
                "month": month,
                "year": year,
                "income_type": income_type,
                "category": category,
            },
            "summary": {
                "total_income": total_income,
                "monthly_income": monthly_income,
                "daily_income": daily_income,
                "yearly_income": yearly_income,
            },
            "count": incomes.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = IncomeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "success": True,
                "message": "Income created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class IncomeDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(Income, pk=pk, user=request.user)

    def get(self, request, pk):
        income = self.get_object(request, pk)
        serializer = IncomeSerializer(income)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        income = self.get_object(request, pk)
        serializer = IncomeSerializer(income, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Income updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        income = self.get_object(request, pk)
        serializer = IncomeSerializer(income, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Income partially updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        income = self.get_object(request, pk)
        income.delete()
        return Response({
            "success": True,
            "message": "Income deleted successfully."
        }, status=status.HTTP_200_OK)


class ExpenseListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        month = int(request.query_params.get('month', today.month))
        year = int(request.query_params.get('year', today.year))

        expenses = get_visible_expense_queryset(request.user, month, year)

        expense_type = request.query_params.get('expense_type')
        category = request.query_params.get('category')
        is_paid = request.query_params.get('is_paid')

        if expense_type:
            expenses = expenses.filter(expense_type=expense_type)
        if category:
            expenses = expenses.filter(category=category)
        if is_paid is not None:
            if is_paid.lower() == 'true':
                expenses = expenses.filter(is_paid=True)
            elif is_paid.lower() == 'false':
                expenses = expenses.filter(is_paid=False)

        serializer = ExpenseSerializer(expenses.order_by('-id'), many=True)

        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        monthly_expense = expenses.filter(expense_type='monthly').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        daily_expense = expenses.filter(expense_type='daily').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        yearly_expense = expenses.filter(expense_type='yearly').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        return Response({
            "success": True,
            "filters": {
                "month": month,
                "year": year,
                "expense_type": expense_type,
                "category": category,
                "is_paid": is_paid,
            },
            "summary": {
                "total_expense": total_expense,
                "monthly_expense": monthly_expense,
                "daily_expense": daily_expense,
                "yearly_expense": yearly_expense,
            },
            "count": expenses.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "success": True,
                "message": "Expense created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(Expense, pk=pk, user=request.user)

    def get(self, request, pk):
        expense = self.get_object(request, pk)
        serializer = ExpenseSerializer(expense)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        expense = self.get_object(request, pk)
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Expense updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        expense = self.get_object(request, pk)
        serializer = ExpenseSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Expense partially updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        expense = self.get_object(request, pk)
        expense.delete()
        return Response({
            "success": True,
            "message": "Expense deleted successfully."
        }, status=status.HTTP_200_OK)


class FinanceDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        month = int(request.query_params.get('month', today.month))
        year = int(request.query_params.get('year', today.year))

        incomes = get_visible_income_queryset(request.user, month, year)
        expenses = get_visible_expense_queryset(request.user, month, year)

        total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        remaining = total_income - total_expense

        savings_rate = Decimal('0.00')
        if total_income > 0:
            savings_rate = round((remaining / total_income) * 100, 2)

        savings_label = "Poor"
        if savings_rate >= 50:
            savings_label = "Excellent"
        elif savings_rate >= 30:
            savings_label = "Good"
        elif savings_rate >= 10:
            savings_label = "Fair"

        return Response({
            "success": True,
            "month": month,
            "year": year,
            "summary_cards": {
                "month_income": {
                    "title": "Month Income",
                    "amount": total_income,
                    "display": f"+₹{total_income}"
                },
                "month_expenses": {
                    "title": "Month Expenses",
                    "amount": total_expense,
                    "display": f"-₹{total_expense}"
                },
                "savings_rate": {
                    "title": "Savings Rate",
                    "percentage": savings_rate,
                    "display": f"{savings_rate}%",
                    "label": savings_label
                },
                "month_net": {
                    "title": "Month Net",
                    "amount": remaining,
                    "display": f"₹{remaining}"
                }
            },
            "income_counts": {
                "total": incomes.count(),
                "monthly": incomes.filter(income_type='monthly').count(),
                "daily": incomes.filter(income_type='daily').count(),
                "yearly": incomes.filter(income_type='yearly').count(),
            },
            "expense_counts": {
                "total": expenses.count(),
                "monthly": expenses.filter(expense_type='monthly').count(),
                "daily": expenses.filter(expense_type='daily').count(),
                "yearly": expenses.filter(expense_type='yearly').count(),
            },
            "recent_incomes": IncomeSerializer(incomes.order_by('-id')[:10], many=True).data,
            "recent_expenses": ExpenseSerializer(expenses.order_by('-id')[:10], many=True).data
        }, status=status.HTTP_200_OK)


class MonthlyBudgetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        month = int(request.query_params.get('month', today.month))
        year = int(request.query_params.get('year', today.year))

        incomes = get_visible_income_queryset(request.user, month, year)
        expenses = get_visible_expense_queryset(request.user, month, year)

        total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_spend = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        remaining = total_income - total_spend

        days_in_month = monthrange(year, month)[1]

        weekly_breakdown = []
        for week_start in [1, 8, 15, 22, 29]:
            week_end = min(week_start + 6, days_in_month)
            week_total = Decimal('0.00')

            for expense in expenses:
                day_value = None

                if expense.expense_type == 'daily' and expense.expense_date:
                    day_value = expense.expense_date.day
                elif expense.expense_type in ['monthly', 'yearly'] and expense.due_day_of_month:
                    day_value = expense.due_day_of_month

                if day_value and week_start <= day_value <= week_end:
                    week_total += expense.amount

            weekly_breakdown.append({
                "week_label": f"{week_start}-{week_end}",
                "spent": week_total
            })

        by_category = list(
            expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
        )

        usage_rate = Decimal('0.00')
        if total_income > 0:
            usage_rate = round((total_spend / total_income) * 100, 2)

        budget_status = "safe"
        if total_spend > total_income:
            budget_status = "over_budget"
        elif usage_rate >= 80:
            budget_status = "warning"

        return Response({
            "success": True,
            "month": month,
            "year": year,
            "summary": {
                "total_budget": total_income,
                "total_spend": total_spend,
                "remaining": remaining,
                "usage_rate": usage_rate,
                "status": budget_status
            },
            "income_count": incomes.count(),
            "expense_count": expenses.count(),
            "by_category": by_category,
            "weekly_breakdown": weekly_breakdown
        }, status=status.HTTP_200_OK)


#Day Calendar overview-----------------------------------------
class CalendarDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()

        month = int(request.query_params.get('month', today.month))
        year = int(request.query_params.get('year', today.year))

        user = request.user

        calendar_data = defaultdict(lambda: {
            "date": None,
            "tasks": [],
            "goals": [],
            "notes": [],
            "day_plans": [],
            "incomes": [],
            "expenses": [],
            "counts": {
                "tasks": 0,
                "goals": 0,
                "notes": 0,
                "day_plans": 0,
                "incomes": 0,
                "expenses": 0,
            }
        })

        # Tasks by due_date
        tasks = Task.objects.filter(
            user=user,
            due_date__month=month,
            due_date__year=year
        )

        for task in tasks:
            date_key = str(task.due_date)
            calendar_data[date_key]["date"] = task.due_date
            calendar_data[date_key]["tasks"].append({
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "category": task.category,
                "is_completed": task.is_completed,
            })
            calendar_data[date_key]["counts"]["tasks"] += 1

        # Goals by target_date
        goals = Goal.objects.filter(
            user=user,
            target_date__month=month,
            target_date__year=year
        )

        for goal in goals:
            date_key = str(goal.target_date)
            calendar_data[date_key]["date"] = goal.target_date
            calendar_data[date_key]["goals"].append({
                "id": goal.id,
                "title": goal.title,
                "category": goal.category,
                "status": goal.status,
                "progress": goal.progress,
                "is_completed": goal.is_completed,
            })
            calendar_data[date_key]["counts"]["goals"] += 1

        # Notes by created_at date
        notes = Note.objects.filter(
            user=user,
            created_at__month=month,
            created_at__year=year
        )

        for note in notes:
            note_date = note.created_at.date()
            date_key = str(note_date)
            calendar_data[date_key]["date"] = note_date
            calendar_data[date_key]["notes"].append({
                "id": note.id,
                "title": note.title,
                "category": note.category,
                "image": note.image.url if note.image else None,
                "created_at": note.created_at,
            })
            calendar_data[date_key]["counts"]["notes"] += 1

        # Day plans by plan_date
        day_plans = DayPlan.objects.filter(
            user=user,
            plan_date__month=month,
            plan_date__year=year
        )

        for plan in day_plans:
            date_key = str(plan.plan_date)
            calendar_data[date_key]["date"] = plan.plan_date
            calendar_data[date_key]["day_plans"].append({
                "id": plan.id,
                "time": plan.time,
                "description": plan.description,
                "category": plan.category,
                "is_done": plan.is_done,
            })
            calendar_data[date_key]["counts"]["day_plans"] += 1

        # Expenses by expense_date
        expenses = Expense.objects.filter(
            user=user,
            expense_date__month=month,
            expense_date__year=year
        )

        for expense in expenses:
            date_key = str(expense.expense_date)
            calendar_data[date_key]["date"] = expense.expense_date
            calendar_data[date_key]["expenses"].append({
                "id": expense.id,
                "name": expense.name,
                "amount": expense.amount,
                "category": expense.category,
                "expense_type": expense.expense_type,
                "is_paid": expense.is_paid,
            })
            calendar_data[date_key]["counts"]["expenses"] += 1

        # Incomes by due_day_of_month or start_date
        incomes = Income.objects.filter(
            user=user,
            is_active=True
        )

        for income in incomes:
            income_date = None

            if income.income_type == 'monthly' and income.due_day_of_month:
                try:
                    income_date = today.replace(year=year, month=month, day=income.due_day_of_month)
                except ValueError:
                    continue
            elif income.start_date and income.start_date.month == month and income.start_date.year == year:
                income_date = income.start_date

            if income_date:
                date_key = str(income_date)
                calendar_data[date_key]["date"] = income_date
                calendar_data[date_key]["incomes"].append({
                    "id": income.id,
                    "name": income.name,
                    "amount": income.amount,
                    "category": income.category,
                    "income_type": income.income_type,
                    "due_day_of_month": income.due_day_of_month,
                    "is_active": income.is_active,
                })
                calendar_data[date_key]["counts"]["incomes"] += 1

        sorted_days = sorted(calendar_data.items(), key=lambda x: x[0])

        month_summary = {
            "tasks": tasks.count(),
            "goals": goals.count(),
            "notes": notes.count(),
            "day_plans": day_plans.count(),
            "incomes": sum(day["counts"]["incomes"] for _, day in sorted_days),
            "expenses": expenses.count(),
        }

        today_key = str(today)
        today_data = calendar_data.get(today_key, {
            "date": today,
            "tasks": [],
            "goals": [],
            "notes": [],
            "day_plans": [],
            "incomes": [],
            "expenses": [],
            "counts": {
                "tasks": 0,
                "goals": 0,
                "notes": 0,
                "day_plans": 0,
                "incomes": 0,
                "expenses": 0,
            }
        })

        return Response({
            "success": True,
            "filters": {
                "month": month,
                "year": year,
                "today": today,
            },
            "month_summary": month_summary,
            "today_data": today_data,
            "calendar_days": [day_data for _, day_data in sorted_days]
        }, status=status.HTTP_200_OK)























