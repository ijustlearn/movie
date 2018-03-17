import uuid
import time
class CommoneUtils():
    @staticmethod
    def getTableId():
        return str(uuid.uuid1())
    @staticmethod
    def current_milli_time() -> int:
        return int(time.time())

    @staticmethod
    def singleton(cls, *args, **kw):
        instances = {}

        def _singleton():
            if cls not in instances:
                instances[cls] = cls(*args, **kw)
            return instances[cls]

        return _singleton