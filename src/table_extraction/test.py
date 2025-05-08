# import cv2
# import pytesseract
# from PIL import Image, ImageDraw

# # 设置 tesseract 路径（根据你的实际安装位置修改）
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # === 1. 加载图像 ===
# img_path = r"C:\Users\11217\datasheet3\tests\table_extraction\TempImages\debug_i_6_0.jpg"
# image = Image.open(img_path).convert("RGB")
# draw = ImageDraw.Draw(image)

# # === 2. 将图像转换为 OpenCV 格式（Tesseract 用这个处理）===
# img_cv = cv2.imread(img_path)

# a = pytesseract.image_to_string(img_cv, lang='eng', config='--psm 6')

# print(a)

# # === 5. 显示结果图像 ===
# image.show()

# # === 可选：保存结果图像 ===
# # image.save("tesseract_output.jpg")
