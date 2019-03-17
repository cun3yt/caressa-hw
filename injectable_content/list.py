import json
from injectable_content.models import InjectableContent


class List:
    def __init__(self, lst=None):
        self.lst = lst if lst else []

    def __len__(self):
        return len(self.lst)

    def add(self, content: InjectableContent):
        self.lst.append(content)

    def set(self):
        return set(self.lst)

    def collect_garbage(self):
        self.lst = [content for content in self.lst if content.is_alive]

    def deliverables(self):
        return [content for content in self.lst if content.is_deliverable]

    def export(self) -> str:
        lst = [content.export() for content in self.lst]
        return json.dumps(lst)

    @staticmethod
    def import_(list_str) -> 'List':
        lst_list = json.loads(list_str)
        return List([InjectableContent.import_(content_str) for content_str in lst_list])
