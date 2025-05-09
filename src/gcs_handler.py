# gcs_manager.py
import os
from typing import Callable
from google.cloud import storage

class GCSHandler():
    def __init__(self, bucket_name: str,
                 on_error: Callable[[Exception], None] = None,
                 ):
        try:
            self.bucket = storage.Client().bucket(bucket_name)
        except Exception as e:
            on_error(e)

    def upload(self, from_: str, to: str,
               on_upload_error: Callable[[Exception], None] = None,
               ):
        """GCSにファイルをアップロード
        
        :param from_: アップロードするファイルのパス
        :param to: アップロード先のGCSのパス
        :param on_upload_error: アップロード失敗時のコールバック関数。引数で例外情報とファイルパスを受け取る
        """

        # ファイルの存在確認
        if not os.path.exists(from_):
            raise ValueError(f"File {from_} does not exist.")
    
        try:
            blob = self.bucket.blob(to)
            blob.upload_from_filename(from_)
        except Exception as e:
            on_upload_error(e,)
        
    def download(self, from_: str, to: str,
                 on_download_error: Callable[[Exception], None] = None,
                 ):
        """GCSからファイルをダウンロード
        
        :param from_: ダウンロードするGCSのパス
        :param to: ダウンロード先のファイルのパス
        :param on_download_error: ダウンロード失敗時のコールバック関数。引数で例外情報とファイルパスを受け取る
        """
        # ディレクトリの作成
        os.makedirs(os.path.dirname(to), exist_ok=True)
        try:
            blob = self.bucket.blob(from_)
            blob.download_to_filename(to)
        except Exception as e:
            on_download_error(e)
        