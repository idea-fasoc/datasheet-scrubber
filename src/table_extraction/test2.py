# from paddleocr import PaddleOCR
# from PIL import Image, ImageDraw
# import cv2
# import numpy as np

# # === 1. 初始化 PaddleOCR ===
# ocr = PaddleOCR(
#     use_angle_cls=False,
#     lang='en',
#     det_db_box_thresh=0.3,
#     det_db_thresh=0.2,
#     det_db_unclip_ratio=2.0,
#     drop_score=0.1,
#     show_log=False,
#     use_gpu=False
# )

# # === 2. 读取图像并转换为 RGB ===
# image_path = r"C:\Users\11217\datasheet3\tests\table_extraction\TempImages\binary_i_5_0.jpg"
# image = Image.open(image_path).convert("RGB")
# image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

# # === 3. 运行 OCR 检测 ===
# result = ocr.ocr(image_cv, cls=False)  # 不使用角度分类器，提高速度

# # === 4. 创建可视化图像对象 ===
# draw = ImageDraw.Draw(image)

# print("识别结果：")
# for line in result[0]:  # 每行为：[box, (text, confidence)]
#     box, (text, conf) = line
#     if conf > 0.3:
#         draw.line([tuple(pt) for pt in box + [box[0]]], fill='red', width=2)
#         print(f"  - '{text}' (conf: {conf:.2f})")

# # === 5. 显示图像 ===
# image.show()
