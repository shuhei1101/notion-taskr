from dataclasses import dataclass
import re
from typing import List

from domain.name_tag import NameTag

@dataclass
class TaskName():
    task_name: str  # タスク名
    tags: List[NameTag]  # タグのリスト

    def __init__(self, task_name: str, tags: List[NameTag]):
        self.task_name = task_name
        self.tags = tags
        self._sort_tags()

    @classmethod
    def from_raw_task_name(cls, raw_task_name: str):
        '''生のタスク名からタイトルオブジェクトを生成する

        :param str raw_task_name: タスク名
        :return: TaskNameオブジェクト
        '''
        # タグを取得
        # 正規表現で[title-value]形式のタグを探す
        pattern = r"\[(?P<title>\w+)-(?P<value>\d+)\]"
        matches = re.findall(pattern, raw_task_name)
        
        # マッチしたタグをTagオブジェクトに変換してリストに追加
        tags = [NameTag(match[0], int(match[1])) for match in matches]
        
        # タイトルからタグを削除
        for match in matches:
            raw_task_name = raw_task_name.replace(f'[{match[0]}-{match[1]}]', '')

        return cls(
            task_name=raw_task_name, 
            tags=tags
        )
    
    def register_tag(self, tag: NameTag):
        '''タグを登録する

        タグが既に存在する場合は上書きする
        
        :param Tag tag: 登録するタグ
        '''
        # 既に登録されているタグを削除
        self.tags = [t for t in self.tags if t.key != tag.key]
        self.tags.append(tag)
        self._sort_tags()

    def get_tag(self, key: str) -> NameTag:
        '''指定したタイトルのタグを取得する

        指定タグが存在しない場合はNoneを返す
        
        :param str key: タイトル
        :return: タグ
        '''
        for tag in self.tags:
            if tag.key == key:
                return tag
        return None
    
    def _sort_tags(self):
        '''タグをソートする

        タグのvalueで昇順にソートする
        '''
        self.tags = sorted(self.tags, key=lambda x: x.value)