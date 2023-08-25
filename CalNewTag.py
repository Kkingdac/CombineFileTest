import os
import requests


class Tag:
    def __init__(self):
        self.url = os.getenv('TAGS_URL')
        self.tag: str = requests.get(self.url).json()[0]['name'].replace('v', '')
        self.label: str = os.getenv('LABEL')

    def cal_new_tag(self) -> str:
        [major, minor, patch] = self.tag.split('.')
        if self.label == 'enhancement':
            minor = str(int(minor) + 1)
            patch = '0'
        elif self.label == 'bug':
            patch = str(int(patch) + 1)
        else:
            pass
        return f'v{major}.{minor}.{patch}'


if __name__ == '__main__':
    print(Tag().cal_new_tag())
