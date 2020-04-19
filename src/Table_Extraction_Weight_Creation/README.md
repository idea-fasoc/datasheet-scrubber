table_extracter_training_data_checker:			
  Shows the bounding box from the raw xml data on the image

Table_Extracter_robust:					
  Processes the training data into a usable format

Table_Extracter_robust_row 	(NOT USED CURRENTLY):
  Identifies the locations of all rows within a table, needs more training data to be accurate

Table_extracter_robust_concatenate:			
  Creates the model that can concatenate two cells over a vertical line also creates the model that identifies data within the cells

table_identification_final_2.py				
  Creates 2 models that together identify the location of a table on a page
