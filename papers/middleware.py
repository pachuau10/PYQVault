from django.utils.timezone import now
from .models import PageView


class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path
        if not path.startswith(("/static/", "/media/", "/admin/", "/dashboard/")):
            if request.method == "GET":
                PageView.objects.create(
                    path=path,
                    ip_address=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:200],
                )
        return response
