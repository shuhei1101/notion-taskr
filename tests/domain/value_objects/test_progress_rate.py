from notiontaskr.domain.value_objects.progress_rate import ProgressRate


class Test_ProgressRateのテスト:
    class Test_初期化メソッド:
        def test_空の値を渡すと0で初期化されること(self):
            progress_rate = ProgressRate(None)  # type: ignore
            assert progress_rate.value == 0.0

        def test_負の値を渡すと0で初期化されること(self):
            progress_rate = ProgressRate(-0.5)
            assert progress_rate.value == 0.0

        def test_1より大きい値を渡すと1で初期化されること(self):
            progress_rate = ProgressRate(1.5)
            assert progress_rate.value == 1.0

        def test_0から1の範囲の値を渡すとその値で初期化されること(self):
            progress_rate = ProgressRate(0.5)
            assert progress_rate.value == 0.5

    class Test_floatメソッド:
        def test_インスタンスをfloatに変換できること(self):
            progress_rate = ProgressRate(0.5)
            assert float(progress_rate) == 0.5

    class Test_eqメソッド:
        def test_異なる型のオブジェクトと比較するとFalseを返すこと(self):
            progress_rate = ProgressRate(0.5)
            assert progress_rate != "0.5"

        def test_同じ値のインスタンスは等しいこと(self):
            progress_rate1 = ProgressRate(0.5)
            progress_rate2 = ProgressRate(0.5)
            assert progress_rate1 == progress_rate2

        def test_異なる値のインスタンスは等しくないこと(self):
            progress_rate1 = ProgressRate(0.5)
            progress_rate2 = ProgressRate(0.75)
            assert progress_rate1 != progress_rate2
