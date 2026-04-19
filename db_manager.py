import numpy as np
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from PySide6.QtCore import QObject

class DatabaseManager(QObject):
    """Менеджер для работы с PostgreSQL с расширенной диагностикой."""
    
    def __init__(self):
        super().__init__()
        if "QPSQL" not in QSqlDatabase.drivers():
            print("КРИТИЧЕСКАЯ ОШИБКА: Драйвер QPSQL не найден.")

    def connect_db(self, config):
        """Устанавливает соединение с БД."""
        if "QPSQL" not in QSqlDatabase.drivers():
            return False, "Драйвер QPSQL не найден."

        # Используем уникальное имя соединения для потокобезопасности
        connection_name = "OptimizationConnection"
        if QSqlDatabase.contains(connection_name):
            self.db = QSqlDatabase.database(connection_name)
        else:
            self.db = QSqlDatabase.addDatabase("QPSQL", connection_name)
        
        host = str(config.get("host", "localhost"))
        port = int(config.get("port", 5432))
        dbname = str(config.get("name", ""))
        user = str(config.get("user", ""))
        pwd = str(config.get("password", ""))

        self.db.setHostName(host)
        self.db.setPort(port)
        self.db.setDatabaseName(dbname)
        self.db.setUserName(user)
        self.db.setPassword(pwd)

        if not self.db.open():
            err = self.db.lastError()
            msg = f"БД: {err.text()} (Host: {host}, Port: {port})"
            return False, msg
        
        self._create_table_if_not_exists()
        return True, "Успешное подключение."

    def _create_table_if_not_exists(self):
        query = QSqlQuery(self.db)
        query.exec("""
            CREATE TABLE IF NOT EXISTS optimization_results (
                id SERIAL PRIMARY KEY,
                calc_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                skin_thickness DOUBLE PRECISION,
                stringer_count INTEGER,
                profile_number TEXT,
                max_stress DOUBLE PRECISION,
                status TEXT
            )
        """)

    def save_iteration_result(self, data):
        """Сохраняет результат, предотвращая вставку некорректных чисел."""
        if not self.db.isOpen(): return False
        
        # Защита от NaN или бесконечных значений
        try:
            stress = float(data.get("max_stress", 0.0))
            if np.isnan(stress) or np.isinf(stress):
                stress = -1.0
        except:
            stress = -1.0

        query = QSqlQuery(self.db)
        query.prepare("""
            INSERT INTO optimization_results (skin_thickness, stringer_count, profile_number, max_stress, status)
            VALUES (:t, :n, :p, :s, :st)
        """)
        query.bindValue(":t", float(data.get("t", 0.0)))
        query.bindValue(":n", int(data.get("n", 0)))
        query.bindValue(":p", str(data.get("profile", "Unknown")))
        query.bindValue(":s", stress)
        query.bindValue(":st", str(data.get("status", "Success")))
        
        if not query.exec():
            print(f"Ошибка вставки: {query.lastError().text()}")
            return False
        return True

    def close(self):
        if hasattr(self, 'db') and self.db.isOpen():
            self.db.close()
