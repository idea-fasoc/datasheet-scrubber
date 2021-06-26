cnn:
	../../src/table_extraction/table_extraction_cnn.py --weight_dir ../../src/table_extraction/Table_extract_robust --pdf_dir ./test.pdf --work_dir ./ --first_table_page 2 --last_table_page 5
cnn_yolo:
	../../src/table_extraction/table_extraction.py --weight_dir ../../src/table_extraction/Table_extract_robust --pdf_dir ./test.pdf --work_dir ./ --first_table_page 2 --last_table_page 5	
yolo:
	../../src/table_extraction/table_extraction.py --weight_dir path/to/cnn_models --pdf_dir ./test.pdf --work_dir ./ --first_table_page 4 --last_table_page 4 --use_yolo --yolo_model path/to/yolo_model

clean:
	../../src/table_extraction/clean_table_extraction.py --work_dir ./