import os
import requests


class Tag:
    def __init__(self):
        self.url = os.getenv('TAGS_URL')
        data = requests.get(self.url).json()
        self.tag: str = data[0]['name'].replace('v', '') if len(data) != 0 else '1.0.0'
        self.label: str = os.getenv('LABEL')

    def cal_new_tag(self) -> str:
        [major, minor, patch] = self.tag.split('.')[:3]
        if self.label == 'enhancement':
            minor = str(int(minor) + 1)
            patch = '0'
        elif self.label == 'bug':
            patch = str(int(patch) + 1)
        else:
            pass
        return f'v{major}.{minor}.{patch}'


if __name__ == '__main__':
    print(f'::set-output name=tag::{Tag().cal_new_tag()}')
