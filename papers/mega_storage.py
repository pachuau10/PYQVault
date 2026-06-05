import re
import os
import tempfile
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from papers.vendor_mega import Mega


MEGA_LINK_RE = re.compile(r"https://mega\.nz/file/([^#]+)#(.+)")


class MEGAPDFStorage(Storage):
    def __init__(self):
        self._mega = None

    def _connect(self):
        if self._mega is None:
            if not settings.MEGA_EMAIL or not settings.MEGA_PASSWORD:
                raise ValueError(
                    "MEGA_EMAIL and MEGA_PASSWORD must be set in environment variables"
                )
            mega = Mega()
            self._mega = mega.login(
                settings.MEGA_EMAIL, settings.MEGA_PASSWORD
            )
        return self._mega

    def _get_or_create_folder(self, m):
        folder_name = getattr(settings, "MEGA_FOLDER", "PYQNest_PDFs")
        try:
            folder = m.find(folder_name)
            if folder:
                return folder[0]
        except Exception:
            pass
        result = m.create_folder(folder_name)
        return result.get(folder_name)

    def _save(self, name, content):
        m = self._connect()
        dest_node_id = self._get_or_create_folder(m)
        data = content.read()
        file_node = m.upload(None, dest=dest_node_id,
                             dest_filename=name, data=data)
        link = m.get_upload_link(file_node)
        return link

    def url(self, name):
        return name

    def open(self, name, mode="rb"):
        m = self._connect()
        match = MEGA_LINK_RE.match(name)
        if not match:
            raise FileNotFoundError(f"Invalid MEGA link: {name}")
        with tempfile.TemporaryDirectory() as td:
            tmp_path = os.path.join(td, "download.pdf")
            out = m.download_url(name, dest_path=td, dest_filename="download.pdf")
            with open(out, "rb") as f:
                data = f.read()
        return ContentFile(data)

    def delete(self, name):
        pass

    def exists(self, name):
        return bool(name)

    def size(self, name):
        return 0

    def get_accessed_time(self, name):
        return None

    def get_created_time(self, name):
        return None

    def get_modified_time(self, name):
        return None

    def path(self, name):
        raise NotImplementedError("MEGA storage does not support local paths")
