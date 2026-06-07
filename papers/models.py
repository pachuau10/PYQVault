import os

from django.db import models
from django.utils import timezone
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

    def _generate_description(self):
        exam_name = self.exam.name
        subj = self.subject
        yr = self.year
        templates = [
            f"Looking for {exam_name} {yr} {subj} question paper? Download the official PYQ PDF for free. Ideal for practicing and understanding the exam pattern before the actual exam.",
            f"Download {exam_name} {yr} {subj} previous year question paper PDF. Practice with real exam questions to boost your preparation and score higher marks.",
            f"Free {exam_name} {yr} {subj} question paper PDF download. Practice {subj} questions from the actual {exam_name} exam to improve your performance.",
            f"Prepare for {exam_name} with the official {yr} {subj} question paper. Download the PDF and practice {subj} questions from the real exam. Completely free.",
            f"Get the {exam_name} {yr} {subj} PYQ PDF for free. Solve actual exam questions and build confidence for your upcoming {exam_name} test.",
            f"{exam_name} {yr} {subj} question paper — download free PDF. Practice with previous year questions to understand the exam difficulty and key topics.",
            f"Download {exam_name} {subj} question paper from {yr}. This PYQ PDF helps you practice real exam questions and improve your problem-solving speed.",
            f"Need {exam_name} {yr} {subj} PYQ? Download the official question paper PDF and start practicing today. Best resource for {exam_name} exam preparation.",
            f"Prepare smarter with {exam_name} {yr} {subj} question paper PDF. Solve actual past exam questions and get familiar with the paper pattern and marking scheme.",
            f"Free download: {exam_name} {yr} {subj} previous year question paper. Use this PDF to practice {subj} questions and boost your {exam_name} exam score.",
            f"Practice with {exam_name} {yr} {subj} question paper. This PDF contains real exam questions to help you prepare effectively for {exam_name}.",
            f"{exam_name} {yr} {subj} PYQ available for free download. Practice past questions to master {subj} and ace your {exam_name} examination.",
            f"Download {exam_name} {subj} previous year question paper ({yr}) PDF. Real exam questions for focused practice. Ideal for {exam_name} aspirants.",
            f"Get free access to {exam_name} {yr} {subj} question paper. Solve previous year questions to identify important topics and improve your preparation strategy.",
            f"Boost your {exam_name} preparation with {yr} {subj} question paper PDF. Practice with actual exam questions and track your progress before the final exam.",
        ]
        idx = hash(self.slug or self.title) % len(templates)
        return templates[idx]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.exam.name} {self.year} {self.subject} {self.shift}")
        if not self.description:
            self.description = self._generate_description()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/{self.slug}-question-paper-pdf/"

    @property
    def pdf_download_url(self):
        if self.pdf_url:
            parsed = urlparse(self.pdf_url)
            if parsed.netloc and parsed.netloc not in ("example.com", "www.example.com"):
                return self.pdf_url
        if self.pdf_file:
            name = self.pdf_file.name
            if name and '://' in name:
                return name
            try:
                return self.pdf_file.url
            except Exception:
                pass
        return None

    @property
    def pdf_view_url(self):
        return self.pdf_download_url

    @property
    def pdf_download_attachment_url(self):
        return self.pdf_download_url

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


class Article(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=300)
    excerpt = models.TextField(help_text="Short summary shown in listings")
    content = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/articles/{self.slug}/"


class Revenue(models.Model):
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    source = models.CharField(max_length=100, default="adsense")
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.source} - ${self.amount} on {self.date}"
