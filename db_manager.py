from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from PySide6.QtCore import QObject
import numpy as np

class DatabaseManager(QObject):
    """Менеджер для работы с PostgreSQL с гарантированной записью."""
    
    def __init__(self):
        super().__init__()
        self.db = None

    def connect_db(self, config):
        connection_name = "OptimizationConnection"
        if QSqlDatabase.contains(connection_name):
            self.db = QSqlDatabase.database(connection_name)
        else:
            self.db = QSqlDatabase.addDatabase("QPSQL", connection_name)
        
        self.db.setHostName(str(config.get("host", "localhost")))
        self.db.setPort(int(config.get("port", 5432)))
        self.db.setDatabaseName(str(config.get("name", "")))
        self.db.setUserName(str(config.get("user", "")))
        self.db.setPassword(str(config.get("password", "")))

        if not self.db.open():
            return False, f"Ошибка: {self.db.lastError().text()}"
        
        self._sync_schema()
        return True, "Подключено."

    def _sync_schema(self):
        """Создает таблицу и добавляет недостающие колонки без ошибок."""
        query = QSqlQuery(self.db)
        # 1. Создаем базовую таблицу
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
        
        # 2. Проверяем и добавляем новые колонки (eigenvalue, total_mass)
        # Используем PostgreSQL-специфичный запрос для проверки колонок
        for col in [("eigenvalue", "DOUBLE PRECISION"), ("total_mass", "DOUBLE PRECISION")]:
            check_query = f"""
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='optimization_results' AND column_name='{col[0]}'
            """
            query.exec(check_query)
            if not query.next():
                query.exec(f"ALTER TABLE optimization_results ADD COLUMN {col[0]} {col[1]}")

    def save_iteration_result(self, data):
        """Сохраняет результат с проверкой ошибок выполнения."""
        if not self.db or not self.db.isOpen():
            print("БД: Попытка записи в закрытую базу!")
            return False
        
        def safe_f(val):
            try:
                f = float(val)
                return f if np.isfinite(f) else 0.0
            except: return 0.0

        query = QSqlQuery(self.db)
        query.prepare("""
            INSERT INTO optimization_results 
            (skin_thickness, stringer_count, profile_number, max_stress, eigenvalue, total_mass, status)
            VALUES (:t, :n, :p, :s, :e, :m, :st)
        """)
        query.bindValue(":t", safe_f(data.get("t")))
        query.bindValue(":n", int(data.get("n", 0)))
        query.bindValue(":p", str(data.get("profile", "Unknown")))
        query.bindValue(":s", safe_f(data.get("max_stress")))
        query.bindValue(":e", safe_f(data.get("eigenvalue")))
        query.bindValue(":m", safe_f(data.get("mass")))
        query.bindValue(":st", str(data.get("status", "Success")))
        
        success = query.exec()
        if not success:
            print(f"КРИТИЧЕСКАЯ ОШИБКА ЗАПИСИ В БД: {query.lastError().text()}")
        return success

    def close(self):
        if self.db and self.db.isOpen(): self.db.close()
