import threading

import win32com.client
import pythoncom
from Pyfemap import model

class FemapSession:
    """Управление COM-соединением с Femap (Singleton)."""
    _instance = None
    app = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FemapSession, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Инициализация подключения в контексте текущего потока."""
        if self.app is not None:
            return self.app
            
        try:
            # Инициализируем COM для текущего потока
            pythoncom.CoInitialize()
            
            # Подключение к активному экземпляру Femap
            from pythoncom import connect
            self.app = model(connect("femap.model"))
            print(f"Поток {threading.get_native_id() if 'threading' in globals() else ''}: Успешное подключение к Femap.")
            return self.app
        except Exception as e:
            print(f"Ошибка подключения к Femap: {e}")
            self.app = None
            return None

    def is_connected(self):
        return self.app is not None
