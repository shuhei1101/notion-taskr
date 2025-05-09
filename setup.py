from setuptools import setup, find_packages

setup(
    name="src",  # パッケージ名
    version="0.1",  # バージョン番号（公開しない場合は削除可能）
    packages=find_packages(where="src", include=["src", "src.*"]),  # src ディレクトリ内のパッケージをインクルード
    package_dir={'': 'src'},  # ソースコードは src ディレクトリ内にある
    test_suite="tests",  # テストスイートの指定
)
