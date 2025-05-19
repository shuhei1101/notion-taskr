# gcs_manager.py
import os
from typing import Callable
from google.cloud import storage


class GCSHandler:
    def __init__(
        self,
        bucket_name: str,
        on_error: Callable[[Exception], None],
    ):
        try:
            self.bucket = storage.Client().bucket(bucket_name)
        except Exception as e:
            on_error(e)

    def upload(
        self,
        from_: str,
        to: str,
    ):
        """GCSにファイルをアップロード

        :param from_: アップロードするファイルのパス
        :param to: アップロード先のGCSのパス
        """

        # ファイルの存在確認
        if not os.path.exists(from_):
            raise ValueError(f"File {from_} does not exist.")

        try:
            blob = self.bucket.blob(to)
            blob.upload_from_filename(from_)
        except Exception as e:
            raise e

    def download(
        self,
        from_: str,
        to: str,
    ):
        """GCSからファイルをダウンロード

        :param from_: ダウンロードするGCSのパス
        :param to: ダウンロード先のファイルのパス
        """
        # ディレクトリの作成
        os.makedirs(os.path.dirname(to), exist_ok=True)
        try:
            blob = self.bucket.blob(from_)
            blob.download_to_filename(to)
        except Exception as e:
            raise e
