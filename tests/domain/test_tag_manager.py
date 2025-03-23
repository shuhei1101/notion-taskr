from domain.tag_manager import TagManager

def test_get_tags():
    title = 'Notion APIでできること[実績-1] [予定-2]'
    
    # タグを取得
    tag_manager = TagManager()
    tags = tag_manager.get_tags(title)
    
    assert len(tags) == 2
    assert tags[0].key == '実績'
    assert tags[0].value == 1
    assert tags[1].key == '予定'
    assert tags[1].value == 2
