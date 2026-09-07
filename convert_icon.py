from PIL import Image
import os

# Проверяем, есть ли файл
input_path = "images/icon.png"
if not os.path.exists(input_path):
    print(f"❌ Файл {input_path} не найден!")
    print("Убедитесь, что вы сохранили icon.png в папке images/")
    exit(1)

# Открываем PNG
img = Image.open(input_path)
print(f"✅ Загружен: {input_path} ({img.size[0]}x{img.size[1]})")

# Конвертируем в ICO с размерами для Windows
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
output_path = "images/icon.ico"

# Сохраняем как ICO
img.save(output_path, format="ICO", sizes=sizes)

print(f"✅ Иконка создана: {output_path}")
print(f"   Размеры: {', '.join([f'{w}x{h}' for w, h in sizes])}")
