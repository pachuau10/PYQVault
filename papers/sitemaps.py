from datetime import date
from django.urls import reverse
from papers.models import Exam, Paper


def get_sitemap_urls(request):
    protocol = request.scheme
    host = request.get_host()
    base = f"{protocol}://{host}"
    urls = []

    # Static pages
    static_pages = [
        ("home", 1.0, "daily"),
        ("exams", 0.9, "daily"),
        ("search", 0.5, "weekly"),
        ("latest", 0.8, "daily"),
        ("about", 0.7, "monthly"),
        ("contact", 0.5, "monthly"),
        ("privacy", 0.4, "monthly"),
        ("terms", 0.4, "monthly"),
    ]
    for name, priority, freq in static_pages:
        urls.append({
            "loc": f"{base}{reverse(name)}",
            "priority": priority,
            "changefreq": freq,
            "lastmod": None,
        })

    # Exams
    for exam in Exam.objects.all():
        urls.append({
            "loc": f"{base}{reverse('exam_detail', args=[exam.slug])}",
            "priority": 0.9,
            "changefreq": "daily",
            "lastmod": None,
        })

    # Papers
    for paper in Paper.objects.all():
        urls.append({
            "loc": f"{base}{paper.get_absolute_url()}",
            "priority": 0.7,
            "changefreq": "weekly",
            "lastmod": paper.created_at.isoformat() if paper.created_at else None,
        })

    return urls
