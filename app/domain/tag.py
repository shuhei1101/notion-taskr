from dataclasses import dataclass

@dataclass
class Tag():
    key: str
    value: str
    
    def get_display_str(self):
        '''表示用の文字列を返す'''
        return f'[{self.key}-{self.value}]'
    
        