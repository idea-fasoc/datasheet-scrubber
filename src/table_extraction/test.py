# from paddleocr import PPStructure, save_structure_res
# import os

# # 设置图片路径
# img_path = r"C:\Users\11217\datasheet3\src\table_extraction\Table_extract_robust\debug_cells\concatenated_cells.jpg"
# output_dir = r"C:\Users\11217\datasheet3\output_csv"  # 你希望保存的位置

# # 创建结构化识别器（只使用 table 模式）
# ocr_engine = PPStructure(layout=False, show_log=True, lang='en', structure_version='PP-StructureV2', type='table')

# # 执行结构化识别
# result = ocr_engine(img_path)

# # 保存结果（会保存为 Excel 表格）
# save_structure_res(result, output_dir, os.path.basename(img_path))

# print(f"✅ 表格识别完成，结果保存在：{output_dir}")
