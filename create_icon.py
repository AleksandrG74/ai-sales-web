from PIL import Image, ImageDraw, ImageFont
import os

# Создаем папку images, если её нет
os.makedirs("images", exist_ok=True)

# Создаем изображение 256x256
img = Image.new('RGBA', (256, 256), color=(26, 26, 46, 255))
draw = ImageDraw.Draw(img)

# Рисуем круг
draw.ellipse([20, 20, 236, 236], fill=(74, 222, 128, 255))

# Рисуем текст
try:
    font = ImageFont.truetype("arial.ttf", 100)
except:
    font = ImageFont.load_default()

draw.text((70, 70), "AI", fill=(26, 26, 46, 255), font=font)

# Сохраняем
img.save("images/icon.png")
print("✅ Создана иконка: images/icon.png")
