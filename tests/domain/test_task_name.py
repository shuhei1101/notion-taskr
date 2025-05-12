from notiontaskr.domain.name_label import NameLabel
from notiontaskr.domain.task_name import TaskName

class TestTaskName:
    def test_task_name(self):
        '''正常値テスト'''
        task_name = TaskName.from_raw_task_name(
            raw_task_name="Hello, world![key1-1][key2-2]"
        )
        assert task_name.task_name == "Hello, world!"
        assert task_name.labels[0].key == "key1"
        assert task_name.labels[0].value == 1
        assert task_name.labels[1].key == "key2"
        assert task_name.labels[1].value == 2

    def test_task_name_when_no_tag(self):
        '''タグがない場合のテスト'''
        task_name = TaskName.from_raw_task_name(
            raw_task_name="Hello, world!"
        )
        assert task_name.task_name == "Hello, world!"
        assert task_name.labels == []

    def test_register_tag(self):
        '''タグ登録テスト'''
        task_name = TaskName.from_raw_task_name(
            raw_task_name="Hello, world![key1-1]"
        )
        task_name.register_label(NameLabel("key2", 2))
        assert task_name.labels[1].key == "key2"
        assert task_name.labels[1].value == 2
        
    def test_register_tag_when_tag_exists(self):
        '''既存タグ上書きテスト'''
        task_name = TaskName.from_raw_task_name(
            raw_task_name="Hello, world![key1-1]"
        )
        task_name.register_label(NameLabel("key1", 2))
        assert task_name.labels[0].key == "key1"
        assert task_name.labels[0].value == 2

    def test_get_tag(self):
        '''タグ取得テスト'''
        task_name = TaskName.from_raw_task_name(
            raw_task_name="Hello, world![key1-1]"
        )
        tag = task_name.get_label("key1")
        assert tag.key == "key1"
        assert tag.value == 1

    def test_get_tag_when_no_tag(self):
        '''タグが存在しない場合のテスト'''
        task_name = TaskName.from_raw_task_name(
            raw_task_name="Hello, world!"
        )
        tag = task_name.get_label("key1")
        assert tag == None
        
