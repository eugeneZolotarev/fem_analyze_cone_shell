import win32com.client
from pythoncom import connect
from Pyfemap import model

class FemapSession:
    """Управление COM-соединением с Femap (Singleton)."""
    _instance = None
    app = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FemapSession, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            # Подключение к активному экземпляру Femap
            self.app = model(connect("femap.model"))
            print("Успешное подключение к активному Femap.")
        except Exception as e:
            print(f"Ошибка подключения к Femap: {e}")
            self.app = None

    def is_connected(self):
        return self.app is not None
