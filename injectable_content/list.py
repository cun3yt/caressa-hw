import json
from injectable_content.models import InjectableContent
from typing import Optional
from logger import get_logger
from datetime import datetime
from settings import DATETIME_TZ_FORMAT


logger = get_logger()


class List:
    def __init__(self, lst=None, download_fn=None, upload_fn=None, api_fetch_fn=None):
        self._lst = lst if lst else []
        assert (download_fn is None and upload_fn is None) or \
               (download_fn is not None and upload_fn is not None), (
            "Either both of `pull_fn` and `push_fn` must be provided or neither must be provided."
        )
        self._download_fn = download_fn
        self._upload_fn = upload_fn
        self._api_fetch_fn = api_fetch_fn

    def __len__(self):
        return len(self._lst)

    def is_addable(self, content: InjectableContent) -> bool:
        """
        If content.hash_ is not the same as one of the hashes
        in the list the content is addable to the list

        :param content: InjectableContent
        :return: bool
        """

        return content.hash_ not in [c.hash_ for c in self._lst]

    def add(self, content: InjectableContent):
        if not self.is_addable(content):
            logger.info('Content is not add-able, passing')
            return

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

    def fetch_from_api(self):
        if self._api_fetch_fn is None:
            return

        content_lst = self._api_fetch_fn()

        from injectable_content.models import DeliveryRule

        for content in content_lst:
            audio_url = content.get('audio_url')
            hash_ = content.get('hash')
            delivery_rule = content.get('delivery_rule', {})

            start = delivery_rule.get('start', None)
            start = datetime.strptime(start, DATETIME_TZ_FORMAT) if isinstance(start, str) else start

            end = delivery_rule.get('end', None)
            end = datetime.strptime(end, DATETIME_TZ_FORMAT) if isinstance(end, str) else end

            frequency = delivery_rule.get('frequency', None)
            frequency = DeliveryRule.FREQUENCY_ONE_TIME if frequency == 0 else frequency

            self.add(InjectableContent(audio_url=audio_url,
                                       hash_=hash_,
                                       start=start,
                                       end=end,
                                       frequency=frequency))

    def export(self) -> str:
        lst = [content.export() for content in self._lst]
        return json.dumps(lst)

    def import_(self, list_str):
        lst_list = json.loads(list_str)

        self._lst = [InjectableContent.import_(content_str) for content_str in lst_list]
