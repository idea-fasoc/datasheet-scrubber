import cv2
import numpy as np

def split_by_wide_white_gap(image, debug=False):
    height, width = image.shape[:2]

    # Step 1: 转灰度图
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Step 2: 二值化（255是白色）
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Step 3: 判断每一列是否“全白”
    white_cols = np.all(binary == 255, axis=0)  # shape: (width,)

    # Step 4: 找连续白色列区域（长度 > 1% 图像宽度）
    min_blank_width = int(width * 0.01)

    start = None
    for i in range(width):
        if white_cols[i]:
            if start is None:
                start = i
        else:
            if start is not None:
                gap_width = i - start
                if gap_width >= min_blank_width:
                    cut_col = start + gap_width // 2
                    break
                start = None
    else:
        # 如果循环结束还没有 break，检查最后一段白色
        if start is not None and width - start >= min_blank_width:
            cut_col = start + (width - start) // 2
        else:
            cut_col = width // 2  # 没找到符合条件的空白区域，强制从中间裁剪

    # Step 5: 只裁剪一次
    left_img = binary[:, :cut_col]
    right_img = binary[:, cut_col:]

    # Step 6: 展示图像
    if debug:
        cv2.imshow('Binary Image', binary)
        cv2.imshow('Left Part', left_img)
        cv2.imshow('Right Part', right_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return left_img, right_img



# 使用示例
image = cv2.imread('C:/Users/11217/datasheet3/src/table_extraction/Table_extract_robust/debug_table_1.jpg')
processed_image = split_by_wide_white_gap(image, debug=True)

# def table_identifier(pixel_data, root, identify_model, identify_model2):
#     """
#     Identify tables in an image using two CNN models.
#     This function uses two CNN models to identify tables in an image. The first model detects potential table regions,
#     and the second model refines the detection. The final output is a list of detected table regions and their coordinates.
#     Args:
#         pixel_data (numpy.ndarray): Grayscale image data as a 2D NumPy array.
#         root (str): Path to the working directory.
#         identify_model (keras.Model): First model for detecting table regions.
#         identify_model2 (keras.Model): Second model for refining table regions.
#     Returns:
#         tuple: Tuple containing two lists of detected table regions.
#     """
#     start_time = time.time()
#     pTwo_size = 600
#     X_size = 800
#     Y_size = 64
#     cuts_labels = 60
#     label_precision = 8
#     y_fail_num = 3
#     #normalize the pixel data
#     original_pixel_data_255 = pixel_data.copy()
#     pixel_data = cv2.normalize(pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
#     original_pixel_data = pixel_data.copy()

#     height, width = pixel_data.shape
#     scale = X_size/width
#     #resize the pixel data
#     pixel_data = cv2.resize(pixel_data, (X_size, int(height*scale))) #X, then Y
#     #add a border to the pixel data
#     bordered_pixel_data = cv2.copyMakeBorder(pixel_data,top=int(Y_size/4),bottom=int(Y_size/4),left=0,right=0,borderType=cv2.BORDER_CONSTANT,value=1)



#     dynamic_factor = 1.9

#     slice_skip_size = int(Y_size / dynamic_factor)




#     #slice the image into smaller pieces
   
#     iter = 0
#     slices = []
#     while((iter*slice_skip_size + Y_size) < int(height*scale+Y_size/2)):
#         s_iter = iter*slice_skip_size
#         slices.append(bordered_pixel_data[int(s_iter):int(s_iter+Y_size)])
#         iter += 1

#     #convert the slices to a numpy array
#     slices = np.array(np.expand_dims(slices,  axis = -1))
#     #predict the data
#     data = identify_model.predict(slices)

#     #concatenate the data
#     conc_data = []
#     for single_array in data:
#         for single_data in single_array:
#             conc_data.append(single_data)
#     #add 0s to the end of the data
#     conc_data += [0 for i in range(y_fail_num+1)] #Still needed
#     #find the groups
#     groups = []
#     column_threshold = 0.25
#     fail = y_fail_num
#     group_start = 1 #start at 1 to prevent numbers below zero in groups
#     for iter in range(len(conc_data)-1):
#         if(conc_data[iter] < column_threshold):
#             fail += 1
#         else:
#             fail = 0
#         #if the fail is greater than the y_fail_num, then add the group to the list
#         if(fail >= y_fail_num):
#             if(iter - group_start >= 4):
#                 groups.append((int((group_start-1)*label_precision/scale), int((iter+1-y_fail_num)*label_precision/scale)))
#             group_start = iter

#     #refine detection
#     groups2 = []
#     for group in groups:
#         #resize the image
#         temp_final_original = cv2.resize(original_pixel_data[group[0]:group[1]], (pTwo_size, pTwo_size))

#         #convert the image to a numpy array
#         temp_final = np.expand_dims(np.expand_dims(temp_final_original,  axis = 0), axis = -1)
#         #predict the data
#         data_final = identify_model2.predict(temp_final)

#         #find the start and end of the horizontal lines
#         hor_start = -1
#         hor_finish = 10000
#         #get the original width
#         pointless, original_width = original_pixel_data.shape

#         for iter in range(len(data_final[0])):
#             if(data_final[0][iter] > column_threshold and hor_start == -1):
#                 if(iter > 0):
#                     hor_start = int((iter-0.5)*original_width/cuts_labels)
#                 else:
#                     hor_start = int(iter*original_width/cuts_labels)

#             if(data_final[0][iter] > column_threshold):
#                 hor_finish = int((iter+0.5)*original_width/cuts_labels)

#         if(0 and hor_finish - hor_start > (0.7 * original_width)): #Fix for tables that cover the entire image
#             groups2.append((0, original_width))
#         else:
#             groups2.append((hor_start, hor_finish))

#     final_splits = []
#     coords = []
#     #get the final splits
#     for iter in range(len(groups)):
#         #get the final split
#         final_split = original_pixel_data_255[groups[iter][0]:groups[iter][1], groups2[iter][0]:groups2[iter][1]]
#         #get the coordinates
#         coords.append([groups[iter][0],groups2[iter][0],groups[iter][1],groups2[iter][1]])
#         #add the final split to the list
#         final_splits.append(final_split)
#         if(0):
#             cv2.imshow('image', final_split)
#             cv2.waitKey(0)
#             cv2.destroyAllWindows()
#     print("--- %s seconds identify tables ---" % (time.time() - start_time))
#     #time.sleep(1)
#     return final_splits,coords


# def table_identifier(pixel_data, root, identify_model, identify_model2):
#     start_time = time.time()
#     pTwo_size = 600
#     X_size = 800
#     Y_size = 64
#     cuts_labels = 60
#     label_precision = 8
#     y_fail_num = 4  # original is 3

#     original_pixel_data_255 = pixel_data.copy()
#     pixel_data = cv2.normalize(pixel_data, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
#     original_pixel_data = pixel_data.copy()

#     height, width = pixel_data.shape
#     scale = X_size / width

#     # improve 1: anti-aliasing scaling + sharpening preprocess
#     pixel_data = cv2.resize(pixel_data, (X_size, int(height * scale)), interpolation=cv2.INTER_LANCZOS4)
#     kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
#     pixel_data = cv2.filter2D(pixel_data, -1, kernel)

#     bordered_pixel_data = cv2.copyMakeBorder(
#         pixel_data, top=int(Y_size / 4), bottom=int(Y_size / 4),
#         left=0, right=0, borderType=cv2.BORDER_CONSTANT, value=1
#     )

#     # improve 2: enhance text line detection robustness
#     def count_text_lines(image):
#         try:
#             binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)[1]
#             horizontal_projection = np.sum(binary, axis=1)
#             line_count = np.count_nonzero(horizontal_projection > np.mean(horizontal_projection) * 0.5)
#             return max(1, line_count)  # ensure at least 1 line
#         except Exception as e:
#             print(f"text line detection exception: {str(e)}")
#             return 1  # default return 1 line

#     num_of_detected_lines = count_text_lines(pixel_data)


#     # improve 3: limit dynamic factor range
#     if num_of_detected_lines > 20:
#         dynamic_factor = max(1.2, min(1.8, num_of_detected_lines / 150))  # very dense
#     elif num_of_detected_lines > 10:
#         dynamic_factor = max(1.5, min(2.2, num_of_detected_lines / 120))  # medium dense
#     elif num_of_detected_lines > 5:
#         dynamic_factor = max(2.2, min(2.8, num_of_detected_lines / 100))  # slightly dense
#     else:
#         dynamic_factor = max(2.8, min(3.5, num_of_detected_lines / 80))  # sparse
   


#     # improve 3: force dynamic factor in safe range   
#     dynamic_factor = max(1.0, min(dynamic_factor, 3.0))

#     # improve 4: double slice step length constraint
#     slice_skip_size = min(int(Y_size / 2), max(int(Y_size / 3), int(Y_size / dynamic_factor)))
#     slice_skip_size = max(slice_skip_size, int(Y_size / 4))  # new minimum step length constraint

#     print(f"parameter status: Y_size={Y_size}, dynamic_factor={dynamic_factor:.2f}, slice_skip_size={slice_skip_size}")

#     # generate slices
#     iter = 0
#     slices = []
#     while (iter * slice_skip_size + Y_size) < int(height * scale + Y_size / 2):
#         s_iter = iter * slice_skip_size
#         slices.append(bordered_pixel_data[int(s_iter):int(s_iter + Y_size)])
#         iter += 1

#     # model prediction
#     slices = np.array(np.expand_dims(slices, axis=-1))
#     data = identify_model.predict(slices)

#     # concatenate confidence data
#     conc_data = []
#     for single_array in data:
#         for single_data in single_array:
#             conc_data.append(single_data)
#     conc_data += [0 for _ in range(y_fail_num + 1)]

#     # detect vertical area grouping
#     groups = []
#     column_threshold = np.percentile(np.array(conc_data), 30)  # dynamic threshold
#     column_threshold = max(0.05, min(0.15, column_threshold))  # limit in reasonable range
#     print(f"dynamic column threshold: {column_threshold:.2f}")

#     fail = y_fail_num
#     group_start = 1
#     for iter in range(len(conc_data) - 1):
#         if conc_data[iter] < column_threshold:
#             fail += 1
#         else:
#             fail = 0

#         if fail >= y_fail_num:
#             if iter - group_start >= 4:
#                 groups.append((
#                     int((group_start - 1) * label_precision / scale),
#                     int((iter + 1 - y_fail_num) * label_precision / scale)
#                 ))
#             group_start = iter

#     print(f"detected {len(groups)} candidate table regions")

#     # improve 5: strictly verify the validity of groups
#     valid_groups = []
#     for group in groups:
#         y_start, y_end = group
#         # verify coordinate range
#         if (
#             y_start >= y_end 
#             or y_start < 0 
#             or y_end > original_pixel_data.shape[0]
#             or (y_end - y_start) < 10  # minimum height constraint
#         ):
#             print(f"skip invalid area: ({y_start}, {y_end})")
#             continue
#         valid_groups.append(group)
#     groups = valid_groups

#     # horizontal boundary detection
#     groups2 = []
#     for group in groups:
#         y_start, y_end = group
#         try:
#             # improve 6: exception capture + edge padding
#             region = original_pixel_data[y_start:y_end, :]
#             if region.size == 0:
#                 print(f"empty area: {group}")
#                 continue
                
#             temp_final_original = cv2.resize(region, (pTwo_size, pTwo_size))
#         except Exception as e:
#             print(f"area scaling failed: {str(e)}")
#             continue

#         temp_final = np.expand_dims(np.expand_dims(temp_final_original, axis=0), axis=-1)
#         data_final = identify_model2.predict(temp_final)

#         # detect horizontal boundaries
#         hor_start = -1
#         hor_finish = 0
#         _, original_width = original_pixel_data.shape
#         for iter in range(len(data_final[0])):
#             if data_final[0][iter] > column_threshold:
#                 if hor_start == -1:
#                     hor_start = int(max(0, (iter - 0.5) * original_width / cuts_labels))
#                 hor_finish = int(min(original_width, (iter + 0.5) * original_width / cuts_labels))

#         # improve 7: force full width logic
#         if hor_finish - hor_start < 0.7 * original_width:
#             groups2.append((hor_start, hor_finish))
#         else:
#             groups2.append((0, original_width))

#     # post-processing verification
#     final_splits = []
#     coords = []
#     for i in range(len(groups)):
#         y_start, y_end = groups[i]
#         x_start, x_end = groups2[i]
        
#         # final verification
#         if (
#             y_end <= y_start 
#             or x_end <= x_start 
#             or (y_end - y_start) < 10 
#             or (x_end - x_start) < 20
#         ):
#             print(f"skip final invalid area: Y({y_start}-{y_end}), X({x_start}-{x_end})")
#             continue

#         try:
#             final_split = original_pixel_data_255[y_start:y_end, x_start:x_end]
#             final_splits.append(final_split)
#             coords.append([y_start, x_start, y_end, x_end])
#         except Exception as e:
#             print(f"final cropping failed: {str(e)}")

#     print(f"valid table number: {len(final_splits)}")
#     print("--- time %.2f seconds ---" % (time.time() - start_time))
    
#     # 在这里添加显示代码，仍在函数内部
#     # 保存所有裁剪的表格
#     for i, img in enumerate(final_splits):
#         save_path = os.path.join(root, f"cropped_table_{i+1}.jpg")
#         print(f"Saving table image to: {save_path}")
#         cv2.imwrite(save_path, img)
    
#     return final_splits, coords

# def count_text_lines(image):
#     binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)[1]  # invert binary
#     horizontal_projection = np.sum(binary, axis=1)  # calculate horizontal projection
#     return np.count_nonzero(horizontal_projection > np.mean(horizontal_projection) * 0.5)  # count non-zero peaks

# def split_by_wide_white_gap(image, debug_save=False):
#     """
#     Automatically trims wide white margin areas from the right or left of the image.
#     Works best when tables are adjacent to other large non-table areas (e.g., circuit diagrams).
#     """
#     if len(image.shape) == 3:
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     else:
#         gray = image.copy()

#     # Invert and binarize
#     _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

#     height, width = binary.shape
#     white_threshold = int(height * 0.95)  # if > 95% white in a column, treat as blank

#     blank_columns = []
#     for col in range(width):
#         if np.count_nonzero(binary[:, col]) < (height - white_threshold):
#             blank_columns.append(col)

#     # Group into wide blank areas
#     min_gap_width = int(width * 0.05)  # Only consider white gaps wider than 5% of image
#     start = None
#     for i in range(1, len(blank_columns)):
#         if blank_columns[i] != blank_columns[i - 1] + 1:
#             if start is not None and (blank_columns[i - 1] - start) > min_gap_width:
#                 cut_col = (start + blank_columns[i - 1]) // 2
#                 if debug_save:
#                     cv2.line(image, (cut_col, 0), (cut_col, height), (0, 0, 255), 2)
#                 return image[:, :cut_col]
#             start = None
#         else:
#             if start is None:
#                 start = blank_columns[i - 1]

#     # fallback
#     return image
