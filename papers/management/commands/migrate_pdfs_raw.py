import os
import cloudinary
import cloudinary.uploader
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from papers.models import Paper


class Command(BaseCommand):
    help = "Re-upload existing PDFs as Cloudinary raw resources"

    def handle(self, *args, **options):
        cloudinary.config(
            cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
            api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
            api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""),
        )

        papers = Paper.objects.exclude(pdf_file="")
        total = papers.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("No PDFs to migrate."))
            return

        self.stdout.write(f"Found {total} papers with PDFs to migrate...")

        for i, paper in enumerate(papers, 1):
            name = paper.pdf_file.name
            public_id = name
            old_url = f"https://res.cloudinary.com/{os.environ.get('CLOUDINARY_CLOUD_NAME', '')}/image/upload/{public_id}"

            self.stdout.write(f"  [{i}/{total}] {paper.title}...", ending=" ")

            try:
                resp = requests.get(old_url, timeout=30)
                resp.raise_for_status()

                result = cloudinary.uploader.upload(
                    resp.content,
                    resource_type="raw",
                    public_id=public_id,
                    overwrite=True,
                )

                self.stdout.write(self.style.SUCCESS("OK"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"FAILED: {e}"))

        self.stdout.write(self.style.SUCCESS("Migration complete."))
