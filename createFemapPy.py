import sys
from win32com.client import makepy

# Укажите актуальный путь к папке вашей версии Femap
femap_tlb_path = r"D:\Program Files\Siemens\femap.tlb"

sys.argv = ["makepy", "-o", "Pyfemap.py", femap_tlb_path]
makepy.main()
print("Генерация завершена. Проверьте появление файла Pyfemap.py")