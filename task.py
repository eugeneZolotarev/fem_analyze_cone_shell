import time


class Task:
    def __init__(self, file_path, session=None):
        """
        Инициализирует задачу: создает новую модель в Femap.
        :param file_path: Полный путь к будущему файлу .modfem
        """
        self.session = session
        if session is None:
            from main import FemapSession

            self.session = FemapSession()

        if not self.session.is_connected():
            raise Exception("Femap не подключен. Невозможно создать задачу.")

        self.app = self.session.app
        self.file_path = file_path
        self.model_id = None

        self._create_new_model()

    def _create_new_model(self):
        try:
            # Получаем ID текущей активной вкладки
            rc, current_model_id = self.app.feAppGetModel(0)

            # Спрашиваем физический путь к файлу текущей вкладки
            rc_file, file_name = self.app.feFileGetName()

            # Если пути нет (пустая строка), значит это дефолтная несохраненная вкладка
            if file_name == "":
                print(f"--> Захватили стартовую вкладку (ID {current_model_id}).")
                self.model_id = current_model_id
                return  # Жестко выходим, feFileNew() не вызывается

            # Только если файл уже был куда-то сохранен (вкладка занята), создаем новую
            print("--> Текущая вкладка уже сохранена на диск. Создаем новую.")
            self.app.feFileNew()
            rc, self.model_id = self.app.feAppGetModel(0)

        except Exception as e:
            print(f"Критическая ошибка при проверке: {e}")
            # Резерв на случай полного сбоя API
            self.app.feFileNew()
            rc, self.model_id = self.app.feAppGetModel(0)

    def activate(self):
        """Делает модель этой задачи активной в Femap."""
        if self.model_id is not None:
            self.app.feAppSetModel(self.model_id)

    def save(self):
        """Сохраняет модель по указанному пути."""
        self.activate()  # Гарантируем, что сохраняем нужную модель

        # feFileSaveAs(useDlg, fName)
        # useDlg = False (0), fName = путь к файлу
        rc = self.app.feFileSaveAs(False, self.file_path)
        if rc == -1:
            print(f"Модель успешно сохранена: {self.file_path}")
        else:
            print(f"Ошибка при сохранении модели (код {rc}): {self.file_path}")
