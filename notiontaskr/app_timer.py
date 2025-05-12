import time

class AppTimer:
    def __init__(self):
        self.start_time = None

    @classmethod
    def init_and_start(cls):
        instance = cls()
        instance.start_time = time.time()
        return instance

    def get_elapsed_time(self):
        """経過時間を取得するメソッド
        
        少数点以下2桁までの精度で経過時間を取得する。
        """
        if self.start_time is None:
            raise ValueError("Timer has not been started.")
        
        current_time = time.time()
        return round(current_time - self.start_time, 2)
    
