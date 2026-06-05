from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Configure CORS rules on the Backblaze B2 bucket for direct browser uploads"

    def handle(self, *args, **options):
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        self.stdout.write(f"Setting CORS rules on bucket '{bucket}' ...")

        try:
            from django.core.files.storage import default_storage
            s3 = default_storage.connection.meta.client

            s3.put_bucket_cors(
                Bucket=bucket,
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
            self.stdout.write(self.style.SUCCESS("CORS rules applied successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed: {e}"))