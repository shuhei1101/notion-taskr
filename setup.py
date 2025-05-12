from setuptools import setup, find_packages

setup(
    name="notion-api",  # パッケージ名
    version="0.1",  # バージョン番号（公開しない場合は削除可能）
    packages=find_packages(),  # src ディレクトリ内のパッケージをインクルード
    test_suite="tests",  # テストスイートの指定
)
