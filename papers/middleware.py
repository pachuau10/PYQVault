from datetime import timedelta

from django.utils import timezone

from .models import PageView


class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    def __call__(self, request):
        response = self.get_response(request)
        if request.method != "GET":
            return response
        if response.status_code // 100 == 3:
            return response
        path = request.path
        if path.startswith(("/static/", "/media/", "/admin/", "/dashboard/")):
            return response
        ip = self._get_client_ip(request)
        cutoff = timezone.now() - timedelta(hours=1)
        if not PageView.objects.filter(path=path, ip_address=ip, timestamp__gte=cutoff).exists():
            PageView.objects.create(
                path=path,
                ip_address=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:200],
            )
        return response
