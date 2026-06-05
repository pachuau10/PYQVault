import re
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from mega import Mega


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
            if not folder:
                folder = m.create_folder(folder_name)
        except Exception:
            folder = m.create_folder(folder_name)
        return folder

    def _save(self, name, content):
        m = self._connect()
        folder = self._get_or_create_folder(m)
        content_bytes = content.read()
        file_node = m.upload((name, content_bytes), dest=folder[0])
        link = m.get_link(file_node)
        return link

    def url(self, name):
        return name

    def open(self, name, mode="rb"):
        m = self._connect()
        match = MEGA_LINK_RE.match(name)
        if not match:
            raise FileNotFoundError(f"Invalid MEGA link: {name}")
        file_id, key = match.group(1), match.group(2)
        node = m.find(file_id)
        if node:
            data = m.download(node)
            return ContentFile(data)
        raise FileNotFoundError(f"File not found on MEGA: {name}")

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
