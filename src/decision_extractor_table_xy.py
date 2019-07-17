#MIT License

#Copyright (c) 2018 The University of Michigan

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

#removed broken comments
import sublist_equal_element
import clean_array_single
import copy
def decision_extractor_table_xy(all_row,x_row_counter,x_column_counter,x_type,y_row_counter,y_column_counter,y_kind, test_row, test_col):
#    print(x_type)
#    print("(attribute) y: ", x_row_counter, " (attribute) x: ", x_column_counter)
 #   print(test_row, " ", test_col)
    result={}
    No_title_count=0
    title_count=0
    clean_titles = []   #needed for some edge case... not sure why... AD7183
    if len(y_row_counter)!=0:#CSV page includes spec?Yes
        sorted_row=sublist_equal_element.sublist_equal_element(x_row_counter)
        for s in range(0,len(sorted_row)):
            clean_tiltes = []
            if(sorted_row[s][0]-1 >= 0):
                clean_titles=clean_array_single.clean_array_single(all_row[sorted_row[s][0]-1])##why we need this? add to pretify  ///gives row above min, typ, max
            if((len(clean_tiltes) == 0) and sorted_row[s][0]-2 >= 0 ):
                clean_titles=clean_array_single.clean_array_single(all_row[sorted_row[s][0]-2])##why we need this? add to pretify  ///gives row 2 above min, typ, max

            nothing = True
            for x in all_row[y_row_counter[0]][1:]:
                if(x.replace("-","").replace("+","").replace(".","").replace("?","").replace("±","").isdigit()):
                    nothing = False

            too_long = False #here in case the element is at the bottom of all_row to make sure the index wont go out of bounds
            try:
                 garbage = all_row[y_row_counter[0]+1][y_column_counter[0]]
            except:
                too_long = True
                pass

            if (len(clean_titles)!=0): #added incase min/typ/max are in row 0 
            #    print("Path: a")
                for j in range(0,len(sorted_row[s])):
                    for k in range(0,len(y_row_counter)):
                       # if s==len(sorted_row)-1:    #last element
                            if sorted_row[s][j]<y_row_counter[k]:  #Keyword under Max/Min/Typ                  
                                dic_title_accessory=[clean_titles[j],str(title_count)]
                                dic_title="_".join(dic_title_accessory)
                                try: #needed in case the csv is not rectangular
                                    result[dic_title]=all_row[y_row_counter[k]][x_column_counter[j]]
                                    title_count+=1
                                except:
                                    pass
            elif (not too_long and all_row[y_row_counter[0]+1][y_column_counter[0]] == "" and test_col and all_row[y_row_counter[0]][test_col[0]] != "" and all_row[y_row_counter[0]+1][test_col[0]] != ""): #LDO ADP7185
            #    print("Path: b")
                iter = 0 
                try:
                    while((all_row[y_row_counter[0]+iter][y_column_counter[0]] == "" or iter == 0) and all_row[y_row_counter[0]+iter][test_col[0]] != ""):
                        useful = False 
                        temp = copy.deepcopy(all_row[y_row_counter[0]+iter])
                        temp.pop(test_col[0]) 
             #           print(temp) 
                        for r in temp:
                            if(r != ''):
                                useful = True
                        if(useful):
                            dic_title_accessory=[all_row[y_row_counter[0]+iter][test_col[0]],str(title_count)]
                            dic_title="_".join(dic_title_accessory)
                            result[dic_title]=all_row[y_row_counter[0]+iter][x_column_counter[0]]
                            title_count+=1
                        iter+=1
                except:
                    pass
                break
            elif (not too_long and (all_row[y_row_counter[0]+1][y_column_counter[0]] == "") and nothing): #wierd case //might need to make broader //perfect split
              #     print("Path: c")
                   if (all_row[y_row_counter[0] - 1][y_column_counter[0]] == ""): #look above
                       temp = all_row[y_row_counter[0] - 1][y_column_counter[0] + 1]
                       if(temp != ""):
                            for j in range(0,len(sorted_row[s])):
                                for k in range(0,len(y_row_counter)):
                                   dic_title_accessory=[temp,str(title_count)]
                                   dic_title="_".join(dic_title_accessory)
                                   result[dic_title]=all_row[y_row_counter[k]-1][x_column_counter[j]]
                                   title_count+=1
                   if (all_row[y_row_counter[0] + 1][y_column_counter[0]] == ""): #look below
                        temp = all_row[y_row_counter[0] + 1][y_column_counter[0] + 1]
                        if(temp != ""):
                            for j in range(0,len(sorted_row[s])):
                                for k in range(0,len(y_row_counter)):
                                    dic_title_accessory=[temp,str(title_count)]
                                    dic_title="_".join(dic_title_accessory)
                                    result[dic_title]=all_row[y_row_counter[k]+1][x_column_counter[j]]
                                    title_count+=1
                   break
            else:   #basic no title
               # print("Path: d")
                for j in range(0,len(sorted_row[s])):
                    for k in range(0,len(y_row_counter)):
                     #   if s==len(sorted_row)-1:
                            if sorted_row[s][j]<y_row_counter[k]:                                                 
                                result[No_title_count]=all_row[y_row_counter[k]][x_column_counter[j]]
                                No_title_count+=1        
    else:
        result["nothing"]="nothing"
    return   result  
