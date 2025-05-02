from dataclasses import dataclass
import re
from typing import TYPE_CHECKING

from domain.name_labels.man_hours_label import ManHoursLabel

if TYPE_CHECKING:
    from domain.name_labels.id_label import IdLabel
from domain.name_labels.label_registable import LabelRegistable
from domain.name_labels.name_label import NameLabel


@dataclass
class TaskName(LabelRegistable):
    task_name: str  # タスク名
    id_label: 'IdLabel' = None  # IDラベル
    man_hours_label: 'ManHoursLabel' = None  # 人時ラベル
    register_parent_id_label: 'IdLabel' = None  # 親IDラベル

    @classmethod
    def from_raw_task_name(cls, raw_task_name: str):
        '''生のタスク名からタイトルオブジェクトを生成する

        :param str raw_task_name: タスク名
        :return: TaskNameオブジェクト
        '''
        # 角括弧で囲まれた文字列全体を取得
        pattern = r"\[(.*?)\]"
        matches = re.findall(pattern, raw_task_name)  

        # タイトルからラベルを削除
        for match in matches:
            raw_task_name = raw_task_name.replace(f'[{match}]', '').strip()

        instance = cls(
            task_name=raw_task_name,
        )
    
        # マッチしたラベルをラベルオブジェクトに変換してリストに追加
        for match in matches:
            NameLabel.parse_labels(match, instance) 
        
        return instance

    def __str__(self):
        '''表示用の文字列を返す

        :return: 表示用の文字列
        '''
        display_strs = []

        # 表示順に文字列を追加
        if self.id_label: display_strs.append(self.id_label.get_display_str())
        display_strs.append(self.task_name)
        if self.man_hours_label: display_strs.append(self.man_hours_label.get_display_str())

        # 文字列を結合
        return ' '.join(display_strs)

    def __eq__(self, other: 'TaskName'):
        if not isinstance(other, TaskName):
            return False
        return self.task_name == other.task_name \
            and self.id_label == other.id_label \
        
    def register_id_label(self, label: 'IdLabel'):
        '''IDラベルを登録するメソッド'''
        self.id_label = label
        
    def register_man_hours_label(self, label: 'ManHoursLabel'):
        '''工数ラベルを登録するメソッド'''
        self.man_hours_label = label