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
def decision_extractor_table_xx(all_row,x_main_row_counter,x_main_column_counter,x_subsidiary1_row_counter,x_subsidiary1_column_counter,x_subsidiary2_row_counter,x_subsidiary2_column_counter,x_type_gen,x_type_spe,y_row_counter,y_column_counter,y_kind):
    ##make more efficientm, less lines code
    result={}
    No_title_count=0
    y_extracted=[]
    sorted_main_row=sublist_equal_element.sublist_equal_element(x_main_row_counter)
    sorted_subsidiary_row1=sublist_equal_element.sublist_equal_element(x_subsidiary1_row_counter)
    sorted_subsidiary_row2=sublist_equal_element.sublist_equal_element(x_subsidiary2_row_counter)
    sorted_main_column=sublist_equal_element.sublist_equal_element(x_main_column_counter)
    sorted_subsidiary_column1=sublist_equal_element.sublist_equal_element(x_subsidiary1_column_counter)
    sorted_subsidiary_column2=sublist_equal_element.sublist_equal_element(x_subsidiary2_column_counter)
    if len(y_row_counter)!=0:#CSV page includes spec?
        if len(x_main_row_counter)!=0:
            #Path A
          #  print("Path A")
            for s in range(0,len(sorted_main_row)):
                for j in range(0,len(sorted_main_row[s])):
                    for k in range(0,len(y_row_counter)):
                        if s==len(sorted_main_row)-1:
                            if sorted_main_row[s][j]<y_row_counter[k]:## add this: The subtable in this CSV page includes spec? Yes
                                m=sorted_main_column[s][j]##what if both version and specification were mentioned
                                tag_exist_xtype_in_y_row=False
                                kthrow="".join(all_row[y_row_counter[k]])
                                if x_type_gen in kthrow.lower() and x_type_spe in kthrow.lower():
                                    tag_exist_xtype_in_y_row=True
                                if tag_exist_xtype_in_y_row:
                                    if len(sorted_subsidiary_column1)!=0:##change to check sorted_subsidiary_column1 be in this subtable not just in the page
                                        title=all_row[y_row_counter[k]][sorted_subsidiary_column1[s][j]]
                                      #  print ("{first} {second} {third} {forth} {fifth} {sixth} {seventh}".format(first=x_type_gen, second=y_kind, third="for", forth=title, fifth="is", sixth=all_row[y_row_counter[k]][m], seventh="LSB"))                       
                                        result[title]=all_row[y_row_counter[k]][m]
                                       # print ("baba")
                                    else:
                                        No_title_count+=1
                             #           print ("There is no title")
                              #          print ("{first} {second} {third} {forth} {fifth}".format(first=x_type_gen, second=y_kind, third="is", forth=all_row[y_row_counter[k]][m], fifth="LSB"))                       
                                        result[No_title_count]=all_row[y_row_counter[k]][m]
                               #         print ("mama")
                                    f=1
                                    while y_row_counter[k]+f<len(all_row):
                                        if len(all_row[y_row_counter[k]+f][y_column_counter[k]])==0:
                                            tag_exist_xtype_in_y_row=False
                                            kthrow="".join(all_row[y_row_counter[k]+f])
                                            if x_type_gen in kthrow.lower() and x_type_spe in kthrow.lower():
                                                tag_exist_xtype_in_y_row=True
                                            if tag_exist_xtype_in_y_row:
                                                if len(sorted_subsidiary_column1)!=0:
                                                    title=all_row[y_row_counter[k]+f][sorted_subsidiary_column1[s][j]]
                                          #          print ("{first} {second} {third} {forth} {fifth} {sixth} {seventh}".format(first=x_type_gen, second=y_kind, third="for", forth=title, fifth="is", sixth=all_row[y_row_counter[k]+f][m], seventh="LSB"))                       
                                                    result[title]=all_row[y_row_counter[k]+f][m]
                                                    f+=1
                                           #         print ("fafa")
                                                else:
                                                    No_title_count+=1
                                            #        print ("There is no title")
                                             #       print ("{first} {second} {third} {forth} {fifth}".format(first=x_type_gen, second=y_kind, third="is", forth=all_row[y_row_counter[k]+f][m], fifth="LSB"))                       
                                                    result[No_title_count]=all_row[y_row_counter[k]+f][m]
                                                    f+=1
                                              #      print ("leyla")
                                            else:
                                                f+=1
                                        else:
                                            break                            
                                else:
                                    f=1
                                    while y_row_counter[k]+f<len(all_row):
                                        if len(all_row[y_row_counter[k]+f][y_column_counter[k]])==0:
                                            tag_exist_xtype_in_y_row=False
                                            kthrow="".join(all_row[y_row_counter[k]+f])
                                            if x_type_gen in kthrow.lower() and x_type_spe in kthrow.lower():
                                                tag_exist_xtype_in_y_row=True 
                                            if tag_exist_xtype_in_y_row:
                                                if len(sorted_subsidiary_column1)!=0:
                                          #          print (all_row[y_row_counter[k]+f][m])
                                                    title=all_row[y_row_counter[k]+f][sorted_subsidiary_column1[s][j]]
                                           #         print ("{first} {second} {third} {forth} {fifth} {sixth} {seventh}".format(first=x_type_gen, second=y_kind, third="for", forth=title, fifth="is", sixth=all_row[y_row_counter[k]+f][m], seventh="LSB"))                       
                                                    result[title]=all_row[y_row_counter[k]+f][m]
                                                    f+=1
                                            #        print ("dada")
                                                else:
                                                    No_title_count+=1
                                             #       print ("There is no title")
                                              #      print ("{first} {second} {third} {forth} {fifth}".format(first=x_type_gen, second=y_kind, third="is", forth=all_row[y_row_counter[k]+f][m], fifth="LSB"))                       
                                                    result[No_title_count]=all_row[y_row_counter[k]+f][m]
                                                    f+=1
                                               #     print ("nana")
                                            else:
                                                f+=1
                                        else:
                                            break
                        elif s<len(sorted_main_row)-1:
                            if sorted_main_row[s][j]<y_row_counter[k]<sorted_main_row[s+1][j]:
                                m=x_main_column_counter[j]
                                tag_exist_xtype_in_y_row=False
                                kthrow="".join(all_row[y_row_counter[k]])
                                if x_type_gen in kthrow.lower() and x_type_spe in kthrow.lower():
                                    tag_exist_xtype_in_y_row=True
                                if tag_exist_xtype_in_y_row:
                                    if len(sorted_subsidiary_column1)!=0:
                                        title=all_row[y_row_counter[k]][sorted_subsidiary_column1[s][j]]
                                 #       print ("{first} {second} {third} {forth} {fifth} {sixth} {seventh}".format(first=x_type_gen, second=y_kind, third="for", forth=title, fifth="is", sixth=all_row[y_row_counter[k]][m], seventh="LSB"))                       
                                        result[title]=all_row[y_row_counter[k]][m]
                                  #      print ("kaka")
                                    else:
                                        No_title_count+=1
                                   #     print ("There is no title")
                                    #    print ("{first} {second} {third} {forth} {fifth}".format(first=x_type_gen, second=y_kind, third="is", forth=all_row[y_row_counter[k]][m], fifth="LSB"))                       
                                        result[No_title_count]=all_row[y_row_counter[k]][m]
                                     #   print ("gaga")
                                else:
                                    f=1
                                    while y_row_counter[k]+f<len(all_row):
                                        if len(all_row[y_row_counter[k]+f][y_column_counter[k]])==0:
                                            tag_exist_xtype_in_y_row=False
                                            kthrow="".join(all_row[y_row_counter[k]+f])
                                            if x_type_gen in kthrow.lower() and x_type_spe in kthrow.lower():
                                                tag_exist_xtype_in_y_row=True 
                                            if tag_exist_xtype_in_y_row:
                                                if len(sorted_subsidiary_column1)!=0:
                                                    title=all_row[y_row_counter[k]+f][sorted_subsidiary_column1[s][j]]
                                  #                  print ("{first} {second} {third} {forth} {fifth} {sixth} {seventh}".format(first=x_type_gen, second=y_kind, third="for", forth=title, fifth="is", sixth=all_row[y_row_counter[k]+f][m], seventh="LSB"))                       
                                                    result[title]=all_row[y_row_counter[k]+f][m]
                                                    f+=1
                                   #                 print ("ghagha")
                                                else:
                                                    No_title_count+=1
                                    #                print ("There is no title")
                                     #               print ("{first} {second} {third} {forth} {fifth}".format(first=x_type_gen, second=y_kind, third="is", forth=all_row[y_row_counter[k]+f][m], fifth="LSB"))                       
                                                    result[No_title_count]=all_row[y_row_counter[k]+f][m]
                                                    f+=1
                                      #              print ("parvin")
                                            else:
                                                f+=1
                                        else:
                                            break
        else:
            #path B
            for s in range(0,len(sorted_subsidiary_row2)):##check whether its length ==0 or not
                for j in range(0,len(sorted_subsidiary_row2[s])):
                    for k in range(0,len(y_row_counter)):
                        if s==len(sorted_subsidiary_row2)-1:
                            if sorted_subsidiary_row2[s][j]<y_row_counter[k]:
                                m=y_column_counter[k]+1##pretify
                                while m<len(all_row[y_row_counter[k]]):
                                    if m==sorted_subsidiary_column2[s][j]:
                                        m+=1
                                    elif m==sorted_subsidiary_column1[s][j]:
                                        m+=1
                                    elif len(all_row[sorted_subsidiary_row2[s][j]][m])==0:##you can remove this line after prettifiction
                                        m+=1
                                    else:
                                        break
                                if m==len(all_row[y_row_counter[k]]):
                                    m-=1
                                tag_exist_xtype_in_y_row=False
                                kthrow="".join(all_row[y_row_counter[k]])
                                if x_type_gen in kthrow.lower() and x_type_spe in kthrow.lower():
                                    tag_exist_xtype_in_y_row=True
                                if tag_exist_xtype_in_y_row:
                                    if len(sorted_subsidiary_column1)!=0:
                                        title=all_row[y_row_counter[k]][sorted_subsidiary_column1[s][j]]
                                     #   print ("{first} {second} {third} {forth} {fifth} {sixth} {seventh}".format(first=x_type_gen, second=y_kind, third="for", forth=title, fifth="is", sixth=all_row[y_row_counter[k]][m], seventh="LSB"))                       
                                        result[title]=all_row[y_row_counter[k]][m]
                                      #  print ("pardis")
                                    else:
                                        No_title_count+=1
                                #        print ("There is no title")
                                 #       print ("{first} {second} {third} {forth} {fifth}".format(first=x_type_gen, second=y_kind, third="is", forth=all_row[y_row_counter[k]][m], fifth="LSB"))                      
                                        result[No_title_count]=all_row[y_row_counter[k]][m]
                                  #      print ("behnam")
                                else:
                                    f=1
                                    while y_row_counter[k]+f<len(all_row):#Is row=(spec row +f) empty?
                                        if len(all_row[y_row_counter[k]+f][y_column_counter[k]])==0:
                                            tag_exist_xtype_in_y_row=False
                                            kthrow="".join(all_row[y_row_counter[k]+f])
                                            if x_type_gen in kthrow.lower() and x_type_spe in kthrow.lower():
                                                tag_exist_xtype_in_y_row=True 
                                            if tag_exist_xtype_in_y_row:
                                                if len(sorted_subsidiary_column1)!=0:
                                                    title=all_row[y_row_counter[k]+f][sorted_subsidiary_column1[s][j]]
                                           #         print ("{first} {second} {third} {forth} {fifth} {sixth} {seventh}".format(first=x_type_gen, second=y_kind, third="for", forth=title, fifth="is", sixth=all_row[y_row_counter[k]+f][m], seventh="LSB"))                       
                                                    result[title]=all_row[y_row_counter[k]+f][m]
                                                    f+=1
                                            #        print ("rezaak")
                                                else:
                                                    No_title_count+=1
                                             #       print ("There is no title")
                                              #      print ("{first} {second} {third} {forth} {fifth}".format(first=x_type_gen, second=y_kind, third="is", forth=all_row[y_row_counter[k]+f][m], fifth="LSB"))                       
                                                    result[No_title_count]=all_row[y_row_counter[k]+f][m]
                                                    f+=1
                                               #     print ("zakhar")
                                            else:
                                                f+=1
                                        else:
                                            break   
                        elif s<len(sorted_subsidiary_row2)-1:
                            if sorted_subsidiary_row2[s][j]<y_row_counter[k]<sorted_subsidiary_row2[s+1][j]:#The subtable in this CSV page includes spec? Yes
                                m=y_column_counter[k]+1##pretify
                                while m<len(all_row[y_row_counter[k]]):
                                    if m==sorted_subsidiary_column1[s][j]:
                                         m+=1
                                    elif m==sorted_subsidiary_column2[s][j]:
                                        m+=1
                                    elif len(all_row[sorted_subsidiary_row1[s][j]][m])==0:
                                        m+=1
                                    else:
                                        break
                                if m==len(all_row[y_row_counter[k]]):
                                    m-=1
                                tag_exist_xtype_in_y_row=False
                                kthrow="".join(all_row[y_row_counter[k]])
                                if x_type_gen in kthrow.lower() and x_type_spe in kthrow.lower():
                                    tag_exist_xtype_in_y_row=True
                                if tag_exist_xtype_in_y_row:
                                    if len(sorted_subsidiary_column1)!=0:
                                        title=all_row[y_row_counter[k]][sorted_subsidiary_column1[s][j]]
                                #        print ("{first} {second} {third} {forth} {fifth} {sixth} {seventh}".format(first=x_type_gen, second=y_kind, third="for", forth=title, fifth="is", sixth=all_row[y_row_counter[k]][m], seventh="LSB"))                       
                                        result[title]=all_row[y_row_counter[k]][m]
                                 #       print ("mehraad")
                                    else:
                                        No_title_count+=1
                                  #      print ("There is no title")
                                   #     print ("{first} {second} {third} {forth} {fifth}".format(first=x_type_gen, second=y_kind, third="is", forth=all_row[y_row_counter[k]][m], fifth="LSB"))                       
                                        result[No_title_count]=all_row[y_row_counter[k]][m]
                                    #    print ("erfan")
                                else:
                                    f=1
                                    while y_row_counter[k]+f<len(all_row):#Is row=(spec row +f) empty?
                                        if len(all_row[y_row_counter[k]+f][y_column_counter[k]])==0:
                                            tag_exist_xtype_in_y_row=False
                                            kthrow="".join(all_row[y_row_counter[k]+f])
                                            if x_type_gen in kthrow.lower() and x_type_spe in kthrow.lower():
                                                tag_exist_xtype_in_y_row=True 
                                            if tag_exist_xtype_in_y_row:
                                                if len(sorted_subsidiary_column1)!=0:
                                                    title=all_row[y_row_counter[k]+f][sorted_subsidiary_column1[s][j]]
                                          #          print ("{first} {second} {third} {forth} {fifth} {sixth} {seventh}".format(first=x_type_gen, second=y_kind, third="for", forth=title, fifth="is", sixth=all_row[y_row_counter[k]+f][m], seventh="LSB"))                       
                                                    result[title]=all_row[y_row_counter[k]+f][m]
                                           #         print ("ho3eyn")
                                                    f+=1
                                                else:
                                                    No_title_count+=1
                                            #        print ("There is no title")
                                             #       print ("{first} {second} {third} {forth} {fifth}".format(first=x_type_gen, second=y_kind, third="is", forth=all_row[y_row_counter[k]+f][m], fifth="LSB"))                       
                                                    result[No_title_count]=all_row[y_row_counter[k]+f][m]
                                                    f+=1
                                              #      print ("omid")
                                            else:
                                                f+=1
                                        else:
                                            break 
    else:
        result["nothing"]="nothing" 
    return   result  
