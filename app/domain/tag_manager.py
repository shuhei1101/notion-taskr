import re
from typing import List

from domain.tag import Tag

class TagManager():
    '''[<title>-<value>]形式のタグを管理するクラス
    
    タグ例: [タグ-1] -> title: タグ, value: 1
    '''

    def __init__(self):
        pass

    def get_tags(self, title: str) -> List[Tag]:
        '''タグを含む文字列からTagのリストを取得する
        
        :param str title: タグを含む文字列
        :return: タグのリスト
        '''
        
        # 正規表現で[title-value]形式のタグを探す
        pattern = r"\[(?P<title>\w+)-(?P<value>\d+)\]"
        matches = re.findall(pattern, title)
        
        # マッチしたタグをTagオブジェクトに変換してリストに追加
        tags = [Tag(match[0], int(match[1])) for match in matches]
        
        return tags
    
# 動作確認用
if __name__ == '__main__':
    # タグを含む文字列
    title = 'Notion APIでできること[実績-1] [予定-2]'
    
    # タグを取得
    tag_manager = TagManager()
    tags = tag_manager.get_tags(title)
    
    # タグの表示用文字列を出力
    for tag in tags:
        print(tag.get_display_str())


