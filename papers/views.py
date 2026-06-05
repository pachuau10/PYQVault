import json
from datetime import date
from urllib.parse import urlparse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, F
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from .models import Exam, Paper, AISummary, ContactMessage

DAILY_LIMIT = 3


def home(request):
    exams = Exam.objects.all()[:6]
    latest_papers = Paper.objects.all()[:6]
    total_papers = Paper.objects.count()
    total_exams = Exam.objects.count()
    return render(request, "home.html", {
        "exams": exams,
        "latest_papers": latest_papers,
        "total_papers": total_papers,
        "total_exams": total_exams,
    })


def exams(request):
    return render(request, "exams.html", {"exams": Exam.objects.all()})


def dispatcher(request, slug):
    exam = Exam.objects.filter(slug=slug).first()
    if exam:
        return exam_detail(request, slug)
    return paper_detail(request, slug)


def exam_detail(request, exam_slug, year=None):
    exam = get_object_or_404(Exam, slug=exam_slug)
    papers = Paper.objects.filter(exam=exam)
    if year:
        papers = papers.filter(year=year)
    years = Paper.objects.filter(exam=exam).values_list("year", flat=True).distinct().order_by("-year")
    return render(request, "exam_detail.html", {
        "exam": exam, "papers": papers, "years": years, "selected_year": year,
    })


def paper_detail(request, slug):
    paper = get_object_or_404(Paper, slug=slug)
    related = Paper.objects.filter(exam=paper.exam).exclude(id=paper.id)[:4]
    try:
        summary = paper.ai_summary
    except AISummary.DoesNotExist:
        summary = None

    unlocked_papers = request.session.get("unlocked_summaries", [])
    unlocked = paper.id in unlocked_papers

    if unlocked and summary:
        Paper.objects.filter(id=paper.id).update(summary_views=F("summary_views") + 1)
        paper.refresh_from_db()

    return render(request, "paper_detail.html", {
        "paper": paper,
        "summary": summary,
        "related_papers": related,
        "unlocked": unlocked,
    })


@require_POST
def unlock_summary(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    unlocked = request.session.get("unlocked_summaries", [])
    if paper.id not in unlocked:
        unlocked.append(paper.id)
        request.session["unlocked_summaries"] = unlocked
        Paper.objects.filter(id=paper.id).update(summary_unlocks=F("summary_unlocks") + 1)
    return JsonResponse({"unlocked": True})


def search(request):
    query = request.GET.get("q", "")
    exam_filter = request.GET.get("exam", "")
    subject_filter = request.GET.get("subject", "")
    year_filter = request.GET.get("year", "")

    papers = Paper.objects.all()
    if query:
        papers = papers.filter(
            Q(title__icontains=query) | Q(subject__icontains=query) |
            Q(exam__name__icontains=query) | Q(description__icontains=query)
        )
    if exam_filter:
        papers = papers.filter(exam__slug=exam_filter)
    if subject_filter:
        papers = papers.filter(subject__icontains=subject_filter)
    if year_filter:
        papers = papers.filter(year=int(year_filter))

    return render(request, "search.html", {
        "papers": papers, "query": query, "exams": Exam.objects.all(),
        "years": Paper.objects.values_list("year", flat=True).distinct().order_by("-year"),
        "selected_exam": exam_filter, "selected_subject": subject_filter, "selected_year": year_filter,
    })


def search_suggest(request):
    q = request.GET.get("q", "")
    if len(q) < 2:
        return JsonResponse([], safe=False)
    papers = Paper.objects.filter(
        Q(title__icontains=q) | Q(subject__icontains=q) | Q(exam__name__icontains=q)
    )[:6]
    results = []
    seen = set()
    for p in papers:
        label = f"{p.title[:60]}"
        if label not in seen:
            seen.add(label)
            results.append({"label": label, "url": p.get_absolute_url()})
    if not results:
        exams = Exam.objects.filter(name__icontains=q)[:3]
        for e in exams:
            results.append({"label": f"{e.name} papers", "url": f"/{e.slug}/"})
    return JsonResponse(results, safe=False)


def latest(request):
    return render(request, "latest.html", {"papers": Paper.objects.all().order_by("-created_at")[:20]})


def robots_txt(request):
    return render(request, "robots.txt", content_type="text/plain")


def sitemap_xml(request):
    from .sitemaps import get_sitemap_urls
    urls = get_sitemap_urls(request)
    return render(request, "sitemap.xml", {"urls": urls}, content_type="application/xml")


def about(request):
    total_papers = Paper.objects.count()
    total_exams = Exam.objects.count()
    return render(request, "about.html", {
        "total_papers": total_papers,
        "total_exams": total_exams,
    })


def privacy(request):
    return render(request, "privacy.html")

def terms(request):
    return render(request, "terms.html")


@csrf_exempt
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name, email=email, subject=subject, message=message
            )
            try:
                send_mail(
                    subject=f"[PYQNest] {subject}",
                    message=f"From: {name} ({email})\n\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
            except Exception:
                pass
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "All fields are required."}, status=400)
    return render(request, "contact.html")


def paper_download(request, slug):
    paper = get_object_or_404(Paper, slug=slug)

    if paper.pdf_url:
        parsed = urlparse(paper.pdf_url)
        if parsed.netloc and parsed.netloc not in ("example.com", "www.example.com"):
            return redirect(paper.pdf_url)

    if paper.pdf_file and paper.pdf_file.name:
        name = paper.pdf_file.name
        if '://' in name:
            return redirect(name)
        try:
            storage = paper.pdf_file.field.storage
            url = storage.url(name, parameters={
                'ResponseContentDisposition': f'attachment; filename="{paper.title}.pdf"'
            })
            return redirect(url)
        except Exception:
            pass

    return redirect('paper_detail', slug=slug)


def setup_b2_cors(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'unauthorized'}, status=403)

    try:
        from django.core.files.storage import default_storage
        s3 = default_storage.connection.meta.client

        s3.put_bucket_cors(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            CORSConfiguration={
                "CORSRules": [
                    {
                        "AllowedOrigins": [
                            "https://www.pyqnest.in",
                            "http://localhost:8000",
                        ],
                        "AllowedMethods": ["GET", "PUT"],
                        "AllowedHeaders": ["Content-Type"],
                        "MaxAgeSeconds": 3600,
                    },
                ]
            },
        )
        return JsonResponse({'success': True, 'message': 'CORS rules applied'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def generate_presigned_upload(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'unauthorized'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    filename = request.POST.get('filename', '')
    if not filename:
        return JsonResponse({'error': 'filename required'}, status=400)

    import uuid
    ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'pdf'
    key = f"pdfs/{uuid.uuid4()}.{ext}"

    try:
        from django.core.files.storage import default_storage
        s3 = default_storage.connection.meta.client
        url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': key,
                'ContentType': 'application/pdf',
            },
            ExpiresIn=3600,
        )
        return JsonResponse({'url': url, 'key': key})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)