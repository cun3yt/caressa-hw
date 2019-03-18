import json
from injectable_content.models import InjectableContent
from typing import Optional


class List:
    def __init__(self, lst=None, download_fn=None, upload_fn=None):
        self._lst = lst if lst else []
        assert (download_fn is None and upload_fn is None) or \
               (download_fn is not None and upload_fn is not None), (
            "Either both of `pull_fn` and `push_fn` must be provided or neither must be provided."
        )
        self._download_fn = download_fn
        self._upload_fn = upload_fn

    def __len__(self):
        return len(self._lst)

    def add(self, content: InjectableContent):
        self._lst.append(content)

    def set(self):
        return set(self._lst)

    def collect_garbage(self):
        self._lst = [content for content in self._lst if content.is_alive]

    def deliverables(self):
        return [content for content in self._lst if content.is_deliverable]

    def fetch_one(self) -> Optional[InjectableContent]:
        """
        The fetched content is a reference to the item in the list.
        This means that any update on the content is marked on the list.

        Common case is as follows:
            1. fetch a content
            2. use the content
            3. marking the content as used

        :return: Optional[InjectableContent]
        """

        deliverables = self.deliverables()
        return deliverables[0] if len(deliverables) > 0 else None

    def clear(self):
        self._lst.clear()

    def download(self):
        if self._download_fn is None:
            return
        list_str = self._download_fn()
        self.import_(list_str)

    def upload(self):
        if self._upload_fn is None:
            return
        export_str = self.export()
        self._upload_fn(export_str)

    def export(self) -> str:
        lst = [content.export() for content in self._lst]
        return json.dumps(lst)

    def import_(self, list_str):
        lst_list = json.loads(list_str)
        self._lst = [InjectableContent.import_(content_str) for content_str in lst_list]
