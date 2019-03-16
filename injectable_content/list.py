from injectable_content.models import InjectableContent


class List:
    def __init__(self):
        self.lst = []

    def __len__(self):
        return len(self.lst)

    def add(self, content: InjectableContent):
        self.lst.append(content)

    def set(self):
        return set(self.lst)

    def collect_garbage(self):
        self.lst = [content for content in self.lst if content.is_alive]
