import uuid
import time
class CommoneUtils():
    @staticmethod
    def getTableId():
        return str(uuid.uuid1())
    @staticmethod
    def current_milli_time() -> int:
        return int(round(time.time() * 1000))