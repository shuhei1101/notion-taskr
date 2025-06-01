from notiontaskr.domain.update_content import UpdateContent
from notiontaskr.domain.update_contents import UpdateContents


class TestUpdateContents:
    def test_空の状態で初期化できること(self):
        update_contents = UpdateContents()
        assert update_contents is not None
        assert len(update_contents) == 0
        assert not update_contents.is_updated()

    class Test_更新内容を追加_変更する:
        def test_更新内容を追加できること(self):
            update_contents = UpdateContents()
            content = UpdateContent(
                key="ステータス",
                original_value="未着手",
                update_value="進行中",
            )
            update_contents.upsert(content)

        def test_同じキーの更新内容を変更できること(self):
            """ただし、変更されるのはupdate_valueのみ"""
            update_contents = UpdateContents()
            content1 = UpdateContent(
                key="ステータス",
                original_value="未着手",
                update_value="進行中",
            )
            update_contents.upsert(content1)

            content2 = UpdateContent(
                key="ステータス",
                original_value="進行中",
                update_value="完了",
            )
            update_contents.upsert(content2)

            assert len(update_contents._contents) == 1
            assert update_contents[0].update_value == "完了"

    class Test_更新されているかどうかを判定する:
        def test_更新された際にoriginal_valueとupdate_valueが同じになった場合Falseを返すこと(
            self,
        ):
            update_contents = UpdateContents()
            content1 = UpdateContent(
                key="ステータス",
                original_value="未着手",
                update_value="進行中",
            )
            update_contents.upsert(content1)
            content2 = UpdateContent(
                key="ステータス",
                original_value="進行中",
                update_value="未着手",
            )
            update_contents.upsert(content2)
            assert not update_contents.is_updated()

        def test_一つでも更新されている場合はTrueを返すこと(self):
            update_contents = UpdateContents()
            content1 = UpdateContent(
                key="ステータス",
                original_value="未着手",
                update_value="進行中",
            )
            update_contents.upsert(content1)
            assert update_contents.is_updated()
            content2 = UpdateContent(
                key="ステータス",
                original_value="進行中",
                update_value="未着手",
            )
            update_contents.upsert(content2)
            assert not update_contents.is_updated()
            content3 = UpdateContent(
                key="優先度",
                original_value="低",
                update_value="高",
            )
            update_contents.upsert(content3)
            assert update_contents.is_updated()

    class Test_配列関連のメソッド:
        def test_要素にアクセスできること(self):
            update_contents = UpdateContents()
            content = UpdateContent(
                key="ステータス",
                original_value="未着手",
                update_value="進行中",
            )
            update_contents.upsert(content)
            assert update_contents[0] == content

        def test_lenメソッドが正しく動作すること(self):
            update_contents = UpdateContents()
            content1 = UpdateContent(
                key="ステータス",
                original_value="未着手",
                update_value="進行中",
            )
            content2 = UpdateContent(
                key="優先度",
                original_value="低",
                update_value="高",
            )
            update_contents.upsert(content1)
            update_contents.upsert(content2)
            assert len(update_contents) == 2

        def test_strメソッドで更新内容を表示できること(self):
            update_contents = UpdateContents()
            content1 = UpdateContent(
                key="ステータス",
                original_value="未着手",
                update_value="進行中",
            )
            content2 = UpdateContent(
                key="優先度",
                original_value="低",
                update_value="高",
            )
            update_contents.upsert(content1)
            update_contents.upsert(content2)
            assert (
                str(update_contents)
                == "[ステータス]: 未着手 -> 進行中, [優先度]: 低 -> 高"
            )
