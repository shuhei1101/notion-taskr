import os
import pickle


class PickleHandler:
    def __init__(self, save_path: str):
        self.save_path = save_path

    def save(
        self,
        tasks: object,
    ) -> None:
        """objectをファイルに保存する"""
        try:
            with open(self.save_path, "wb") as f:
                pickle.dump(tasks, f)
        except Exception as e:
            raise e

    def load(
        self,
    ) -> object:
        """ファイルからobjectを読み込む"""
        try:
            if not os.path.exists(self.save_path):
                raise FileNotFoundError(f"{self.save_path}は存在しません。")
            with open(self.save_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            raise e
