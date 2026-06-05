from django.contrib import admin
from .models import Exam, Paper, AISummary, Topic, Subscription, ContactMessage, PageView, Revenue

admin.site.register(Exam)
admin.site.register(Paper)
admin.site.register(AISummary)
admin.site.register(Topic)
admin.site.register(Subscription)
admin.site.register(ContactMessage)
admin.site.register(PageView)
admin.site.register(Revenue)
