import pandas as pd
import os

base_dir = r"Прил_ОЗ_КОД 09.02.07-2-2026 (2)\╨Я╤А╨╕╨╗_╨Ю╨Ч_╨Ъ╨Ю╨Ф 09.02.07-2-2026\╨С╨г\╨Ь╨╛╨┤╤Г╨╗╤М 1\import"

files = [
    "Tovar.xlsx",
    "user_import.xlsx",
    "╨Ч╨░╨║╨░╨╖_import.xlsx",
    "╨Я╤Г╨╜╨║╤В╤Л ╨▓╤Л╨┤╨░╤З╨╕_import.xlsx"
]

with open("excel_info.txt", "w", encoding="utf-8") as out:
    for f in files:
        path = os.path.join(base_dir, f)
        out.write(f"=== {f} ===\n")
        try:
            df = pd.read_excel(path)
            out.write("Columns: " + ", ".join([str(c) for c in df.columns]) + "\n")
            for _, row in df.head(2).iterrows():
                out.write("Row: " + " | ".join([f"{c}={val}" for c, val in row.items()]) + "\n")
        except Exception as e:
            out.write("Error: " + str(e) + "\n")
        out.write("\n")
