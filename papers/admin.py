from django import forms
from django.contrib import admin
from django.db.models import Sum, Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Exam, Paper, AISummary, Topic, Subscription, ContactMessage, PageView, Revenue


class PdfUploadWidget(forms.Widget):
    template_name = "admin/widgets/pdf_upload.html"

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx["upload_url"] = reverse("generate_presigned_upload")
        ctx["current_name"] = value.name if value else ""
        return ctx

    class Media:
        js = ("admin/js/pdf_upload.js",)


class DescriptionWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        html += mark_safe(
            '<button type="button" onclick="'
            "var d=this.parentElement.querySelector('textarea');"
            "if(!d.value){""
            "var e=document.getElementById('id_exam');"
            "var s=document.getElementById('id_subject');"
            "var y=document.getElementById('id_year');"
            "var ex=e?e.options[e.selectedIndex].text:'';"
            "var sj=s?s.value:'';"
            "var yr=y?y.value:'';"
            "var tmpl=["
            "'Looking for '+ex+' '+yr+' '+sj+' question paper? Download the official PYQ PDF for free. Ideal for practicing and understanding the exam pattern before the actual test.',"
            "'Download '+ex+' '+yr+' '+sj+' previous year question paper PDF. Practice with real exam questions to boost your preparation and score higher.',"
            "'Free '+ex+' '+yr+' '+sj+' question paper PDF download. Practice '+sj+' questions from the actual '+ex+' exam to improve your performance.',"
            "'Prepare for '+ex+' with the official '+yr+' '+sj+' question paper. Download the PDF and practice from the real exam. Completely free.',"
            "'Get the '+ex+' '+yr+' '+sj+' PYQ PDF for free. Solve actual exam questions and build confidence for your upcoming '+ex+' test.',"
            "];"
            "var idx=Math.abs((ex+sj+yr).split('').reduce(function(a,c){return a+c.charCodeAt(0)},0))%tmpl.length;"
            "d.value=tmpl[idx];"
            "}this.textContent='Done!';"
            '" style="margin-top:4px;padding:4px 12px;cursor:pointer;border:1px solid #ccc;border-radius:4px;background:#fff">Generate</button>'
        )
        return html


class PaperForm(forms.ModelForm):
    pdf_key = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Paper
        fields = "__all__"
        widgets = {"pdf_file": PdfUploadWidget, "description": DescriptionWidget}

    def save(self, commit=True):
        instance = super().save(commit=False)
        key = self.cleaned_data.get("pdf_key")
        if key:
            instance.pdf_file = key
        if commit:
            instance.save()
        return instance


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "paper_count_display", "order")
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_paper_cnt=Count("papers"))

    @admin.display(description="Papers")
    def paper_count_display(self, obj):
        return getattr(obj, "_paper_cnt", obj.paper_set.count())


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    form = PaperForm
    list_display = ("title", "exam", "subject", "year", "created_at")
    list_filter = ("exam", "year", "subject")
    search_fields = ("title", "subject", "description")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    actions = ("regenerate_descriptions",)

    def regenerate_descriptions(self, request, queryset):
        count = 0
        for paper in queryset:
            paper.description = paper._generate_description()
            paper.save(update_fields=("description",))
            count += 1
        self.message_user(request, f"Regenerated descriptions for {count} paper(s).")
    regenerate_descriptions.short_description = "Regenerate descriptions for selected papers"


@admin.register(AISummary)
class AISummaryAdmin(admin.ModelAdmin):
    list_display = ("paper", "difficulty", "created_at")
    list_filter = ("difficulty",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "started_at", "expires_at")
    list_filter = ("is_active",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("path", "ip_address", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("path", "ip_address")
    date_hierarchy = "timestamp"


@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ("date", "amount_display", "source", "note")
    list_filter = ("source", "date")
    date_hierarchy = "date"
    search_fields = ("note", "source")

    def changelist_view(self, request, extra_context=None):
        total = Revenue.objects.aggregate(total=Sum("amount"))["total"] or 0
        adsense = Revenue.objects.filter(source="adsense").aggregate(total=Sum("amount"))["total"] or 0
        count = Revenue.objects.count()
        extra_context = extra_context or {}
        extra_context["total_revenue"] = total
        extra_context["adsense_revenue"] = adsense
        extra_context["entry_count"] = count
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description="Amount")
    def amount_display(self, obj):
        color = "#22C55E" if obj.amount > 0 else "#EF4444"
        return format_html('<span style="color:{};font-weight:600">${}</span>', color, obj.amount)
