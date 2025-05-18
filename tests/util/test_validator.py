from notiontaskr.util.validator import has_emoji, is_emoji_matches


class Test_has_emoji:
    def test_文字列に絵文字が含まれている場合にTrueを返すこと(self):
        s = "Hello 🌍"
        result = has_emoji(s)
        assert result is True

    def test_文字列に絵文字が含まれていない場合にFalseを返すこと(self):
        s = "Hello World"
        result = has_emoji(s)
        assert result is False


class Test_is_emoji_matches:
    def test_絵文字が一致する場合にTrueを返すこと(self):
        emoji1 = "🌍"
        emoji2 = "🌍"
        result = is_emoji_matches(emoji1, emoji2)
        assert result is True

    def test_絵文字が一致しない場合にFalseを返すこと(self):
        emoji1 = "🌍"
        emoji2 = "🌎"
        result = is_emoji_matches(emoji1, emoji2)
        assert result is False
