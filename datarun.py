from operator import itemgetter
import time
import pandas as pd
import numpy as np
import os





def indata(file_path):
    '''
    最终得到一张总表 datapd ，里面有所有的 item 信息；一个列表 material_list 里面有 总表中不同材料的名称
    '''
    t = time.time()
    datapd = pd.concat(
        (pd.read_csv(os.path.join(file_path, file0)) for file0 in os.listdir(file_path) if file0[-3:] == 'csv'), ignore_index=True)  # 只读取csv文件,避免隐藏文件等其他干扰
    print(f'载入文件耗时:{time.time() - t:.4f}s')

    
    for i in range(len(datapd)):
        str0 = datapd.item_order[i]
        #如果不删除生成的 csv 结果，读入数据会出错：'float' object has no attribute 'strip'
        datapd.item_order[i] = int(str0.strip('order'))

    print(datapd)


    #数据筛选，选取一张表中不同的material：，将material列录入集合。然后对集合进行迭代，录入 list。得到 list 形式的material列表
    material_set = set(datapd.item_material)
    material_list = list(material_set)
    print('数据集中有{}个item_material?',len(material_list))

    #数据筛选，选取一张表中不同的order：，将order列录入集合。然后对集合进行迭代，录入 list。得到 list 形式的order列表
    order_set =   set(datapd.item_order)
    order_list = list(order_set)
    print('数据集中有{}个item_order?',len(order_list))


    return order_list, material_list, datapd



def grouping(order_list, material_list, datapd):
    #根据 item 所要求的 material，对所有 item 进行分组
    for i in range(len(material_list)):
        data0 = datapd[datapd.item_material==material_list[i]]
        data1 = np.array(data0)
        material_indexnp = [data1[:,0],data1[:,1]]
        #因为大部分数据集都是 item_length > item_width .数据集顺序（item_length，item_width），单板计算顺序（w,h）.最后输出的时候注意即可
        data1 = np.delete(data1, [1, 2, 5], 1) #data[1, 2, 5] 分别代表 item_material、item_num、item_order
        #讲 data1 的顺序改变为   item_length ， item_width  ，item——id
        data1[:, [0, 1, 2]] = data1[:, [1, 2, 0]]
    del data1

    #没有实现预期目标。既所有相同 order 排在一起
    data0 = datapd[datapd.item_order == order_list[0]]
    data_list = np.array(data0)
    for i in range(1, len(order_list)):
        data0 = datapd[datapd.item_order == order_list[i]]
        #每次循环的 data_list 都更新在后面
        data_list = np.append(data_list, data0, axis=0)
        
    #讲 data_list 的顺序改变为   item_length ， item_width  ，item——id。。。
    data_list[:, [0, 1, 2, 3, 4, 5]] = data_list[:, [3, 4, 0, 1, 2, 5]]





    return(data_list, material_indexnp)

def removeNone(rectangles):
        #数据预处理，删去 rectangles 中的 None ,数据结构处理函数
    list0 = []
    #存储 None 索引号
    for i in range(len(rectangles)):
        if rectangles[i] == None:
            list0.append(i)
    #删除 NONe 索引号
    list0 = sorted(list0,reverse=True)
    for i in enumerate(list0):
        del rectangles[i[1]]
    return rectangles


def outdata(file_path, data, material_indexnp):

    list0 = list(data[0][0])
    for i in range(1, len(data[0])):
        dataXXX = data[0][i]
        list0 = np.append(list0, dataXXX, axis=0)
    for j in range(1, len(data)):
        for i in range(1, len(data[j])):
            dataXXX = data[j][i]
            list0 = np.append(list0, dataXXX, axis=0)
        list0 = np.append(list0, dataXXX, axis=0)
    list0 = list0.reshape(-1,8)
    


    #计算优化结果
    #item 面积
    itemmianji = 0
    for i in range(len(list0)):
        itemmianji += float(list0[i,2])*float(list0[i,3])


    #板材面积
    bancaimianji = len(data) * 2440 * 1220

    #计算优化结果
    minbili = itemmianji / bancaimianji
    print('优化结果',minbili)

    dicdata={
        "批次序号"      :list0[:,7],
        "原片材质"      :list0[:,6],
        "原片序号"      :list0[:,5],
        "产品id"        :list0[:,4],
        "产品x坐标"     :list0[:,0],
        "产品y坐标"     :list0[:,1],
        "产品x方向长度"  :list0[:,2],
        "产品y方向长度"  :list0[:,3],
            }
    csv_out =  pd.DataFrame(dicdata)
    csv_out.to_csv(
        os.path.join(file_path, 'cut_program.csv'))  # 导出csv
    print("# cut_program.csv result has sevaed")



def calculate(rectangles):
        #数据预处理，删去 rectangles 中的 None 
    list0 = []
    #存储 None 索引号
    for i in range(len(rectangles)):
        if rectangles[i] == None:
            list0.append(i)
    #删除 NONe 索引号
    list0 = sorted(list0,reverse=True)
    for i in enumerate(list0):
        del rectangles[i[1]]
    return rectangles



"""
DataFrame.copy(deep=True)[来源]
复制此对象的索引和数据。

当deep=True（默认）时，将创建一个带有调用对象数据和索引的副本的新对象。对副本数据或索引的修改将不会反映在原始对象中（见下面的注释）。

deep=False时，将在不复制调用对象的数据或索引的情况下创建新对象（仅复制对数据和索引的引用）。对原始数据的任何更改都将反映在浅拷贝中（反之亦然）。
"""

"""
 主要区别在于 np.array （默认情况下）将会copy该对象，而 np.asarray 除非必要，否则不会copy该对象。
"""