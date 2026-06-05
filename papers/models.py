import os

from django.db import models
from django.utils.text import slugify
from urllib.parse import urlparse


class Exam(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    icon = models.CharField(max_length=50, default="book")
    description = models.TextField(blank=True)
    paper_count = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Paper(models.Model):
    LANGUAGES = [("en", "English"), ("hi", "Hindi"), ("both", "English & Hindi")]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="papers")
    subject = models.CharField(max_length=200)
    year = models.IntegerField()
    shift = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGES, default="en")
    pdf_file = models.FileField(upload_to="pdfs/", blank=True, null=True)
    pdf_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    summary_views = models.IntegerField(default=0)
    summary_unlocks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "subject"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.exam.name} {self.year} {self.subject} {self.shift}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/{self.slug}-question-paper-pdf/"

    @property
    def pdf_download_url(self):
        if self.pdf_file:
            try:
                return self.pdf_file.url
            except Exception:
                pass
        if self.pdf_url:
            parsed = urlparse(self.pdf_url)
            if parsed.netloc and parsed.netloc not in ("example.com", "www.example.com"):
                return self.pdf_url
        return None

    def __str__(self):
        return self.title


class Topic(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AISummary(models.Model):
    DIFFICULTY = [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]

    paper = models.OneToOneField(Paper, on_delete=models.CASCADE, related_name="ai_summary")
    overview = models.TextField()
    topics = models.ManyToManyField(Topic, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY, default="medium")
    best_for = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary: {self.paper.title}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject[:50]}"


class Subscription(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="subscriptions")
    is_active = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {'Active' if self.is_active else 'Inactive'}"


class PageView(models.Model):
    path = models.CharField(max_length=500)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.path} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class Revenue(models.Model):
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    source = models.CharField(max_length=100, default="adsense")
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.source} - ${self.amount} on {self.date}"
