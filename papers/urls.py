from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("exams/", views.exams, name="exams"),
    path("search/", views.search, name="search"),
    path("search/suggest/", views.search_suggest, name="search_suggest"),
    path("latest/", views.latest, name="latest"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("unlock/<int:paper_id>/", views.unlock_summary, name="unlock_summary"),
    path("<slug:exam_slug>/<int:year>/", views.exam_detail, name="exam_detail_year"),
    re_path(r"^(?P<slug>.+)-question-paper-pdf/$", views.paper_detail, name="paper_detail"),
    path("articles/", views.article_list, name="article_list"),
    path("articles/<slug:slug>/", views.article_detail, name="article_detail"),
    path("setup-b2-cors/", views.setup_b2_cors, name="setup_b2_cors"),
    path("generate-presigned-upload/", views.generate_presigned_upload, name="generate_presigned_upload"),
    path("<slug:slug>/download/", views.paper_download, name="paper_download"),
    path("<slug:slug>/", views.dispatcher, name="exam_detail"),
]
