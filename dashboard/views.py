from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count, Sum
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from papers.models import Exam, Paper, ContactMessage, PageView, Revenue


def admin_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseForbidden("Admin access required")
        return view_func(request, *args, **kwargs)
    return wrapper


def _visitor_stats():
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    return {
        "visitors_today": PageView.objects.filter(timestamp__date=today).count(),
        "visitors_week": PageView.objects.filter(timestamp__date__gte=week_ago).count(),
        "visitors_month": PageView.objects.filter(timestamp__date__gte=month_ago).count(),
        "total_visitors": PageView.objects.count(),
        "top_pages": PageView.objects.values("path").annotate(c=Count("id")).order_by("-c")[:10],
    }


def _revenue_stats():
    return {
        "total_revenue": Revenue.objects.aggregate(s=Sum("amount"))["s"] or 0,
        "revenue_this_month": Revenue.objects.filter(
            date__gte=timezone.now().date().replace(day=1)
        ).aggregate(s=Sum("amount"))["s"] or 0,
        "revenue_entries": Revenue.objects.all().order_by("-date")[:20],
    }


@admin_login_required
def dashboard_home(request):
    total_pdfs = Paper.objects.count()
    total_downloads = Paper.objects.aggregate(s=Sum("summary_unlocks"))["s"] or 0
    total_categories = Exam.objects.count()
    total_messages = ContactMessage.objects.count()
    recent_papers = Paper.objects.all().order_by("-created_at")[:10]
    visitors = _visitor_stats()
    revenue = _revenue_stats()

    return render(request, "dashboard/home.html", {
        "total_pdfs": total_pdfs,
        "total_downloads": total_downloads,
        "total_categories": total_categories,
        "total_messages": total_messages,
        "recent_papers": recent_papers,
        "section": "dashboard",
        **visitors, **revenue,
    })


@admin_login_required
def dashboard_pdfs(request):
    papers = Paper.objects.all().order_by("-created_at")
    exams = Exam.objects.all()
    return render(request, "dashboard/pdfs.html", {
        "papers": papers, "exams": exams, "section": "pdfs",
    })


@admin_login_required
def dashboard_messages(request):
    messages = ContactMessage.objects.all().order_by("-created_at")
    return render(request, "dashboard/messages.html", {
        "messages": messages, "section": "messages",
    })


@admin_login_required
def dashboard_analytics(request):
    visitors = _visitor_stats()
    revenue = _revenue_stats()
    return render(request, "dashboard/analytics.html", {
        "section": "analytics", **visitors, **revenue,
    })


@admin_login_required
def dashboard_settings(request):
    return render(request, "dashboard/settings.html", {"section": "settings"})


@admin_login_required
def dashboard_logout(request):
    logout(request)
    return redirect("/admin/login/")


@require_POST
@csrf_exempt
def dashboard_delete_message(request, msg_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)
    msg = get_object_or_404(ContactMessage, id=msg_id)
    msg.delete()
    return JsonResponse({"success": True})
