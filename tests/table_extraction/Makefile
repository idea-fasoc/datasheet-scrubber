cnn_basic:
	python ../../src/table_extraction/table_extraction_cnn.py --pdf_dir ./test.pdf --work_dir ./ --first_table_page 9 --last_table_page 9
2:
	python ../../src/table_extraction/table_extraction.py --pdf_dir ./test.pdf --work_dir ./ --first_table_page 2 --last_table_page 4
3:
	python ../../src/table_extraction/table_extraction.py --pdf_dir ./test.pdf --work_dir ./ --first_table_page 5 --last_table_page 5
cnn_yolo:
	python ../../src/table_extraction/table_extraction.py --pdf_dir ./test.pdf --work_dir ./ --first_table_page 4 --last_table_page 4 --use_yolo
clean:
	python ../../src/table_extraction/clean_table_extraction.py --work_dir ./
original:
	python ../../src/table_extraction/original.py --pdf_dir ./test.pdf --work_dir ./ --first_table_page 2 --last_table_page 3

4:
	python ../../src/table_extraction/table_extraction.py --pdf_dir ./test.pdf --work_dir ./ --first_table_page 9 --last_table_page 9 --use_double_column_split
