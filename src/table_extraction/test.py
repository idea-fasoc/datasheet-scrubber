from paddleocr import PPStructure,draw_structure_result,save_structure_res
import cv2

img_path =  r"C:\Users\11217\datasheet3\tests\table_extraction\images\page_2.jpg"
table_engine = PPStructure(show_log=True,use_gpu = False)
#table_engine = PPStructure(show_log=True,use_gpu = False,rec_model_dir=r'E:\Python\Python38\Lib\site-packages\paddleocr\2.1\rec\ch',
#cls_model_dir=r'E:\Python\Python38\Lib\site-packages\paddleocr\2.1\cls',
#det_model_dir=r'E:\Python\Python38\Lib\site-packages\paddleocr\2.1\det\ch')
img = cv2.imread(img_path)
result = table_engine(img)
print(result)
save_structure_res(result, 'aa','a')