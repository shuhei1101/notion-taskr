from dataclasses import dataclass

from domain.name_labels.name_label import NameLabel

@dataclass
class IdLabel(NameLabel):
    @classmethod
    def from_id(cls, id_prefix: str, id_number: str):
        '''IDラベルを生成する'''
        return cls(
            key="",
            value=id_number,
        )

    @classmethod
    def parse_and_register(cls, key: str, value: str, delegate):
        '''ラベルを解析して登録する'''
        if key == "":
            instance = cls(
                key=key,
                value=value,
            )
            delegate.id_label = instance
        else:
            raise ValueError(f'Unknown key: {key}')