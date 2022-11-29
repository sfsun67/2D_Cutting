from division.ph import splitprg
from division.visualize import visualizerec
from collections import namedtuple
import datarun
import time
import numpy as np






def main(boxes, width, height, file_path, material_indexnp, order_list):
    t = time.time()
    #第一个原片,用 result_list 记录结果  ， No = 1 , batch = 1
    No = 1 
    batch = 1 
    itemmianji = 0
    itemshuliang = 0



    #记录第一个 item 的材质，并只选取该材质的item 形成一个新数组 
    cur_material = boxes[0,3]
    j = 0 
    sammat_boxes = boxes[0].reshape(-1,6)      #使用 reshape 函数使数组保持原来的形状  #sammat_boxes = same material boxes
    for i in range(1, len(boxes)):
        if boxes[i,3] == cur_material:
            sammat_boxes0 = boxes[i].reshape(-1,6)      #使用 reshape 函数使数组保持原来的形状
            sammat_boxes = np.append(sammat_boxes, sammat_boxes0, axis=0)
            j += 1

    #并只选取该材质的item 进入组板 
    ture_height, rectangles = splitprg(width, height ,sammat_boxes ,No, batch)   #ture_height == ture 指板子放下了所有 item ；faulse 指 item 超出了该原片的容量。
    rectangles = datarun.removeNone(rectangles)      #数据预处理，删去 rectangles 中的 None
    result_list = [0] * len(boxes)         #列表长度是NO板子的数量。
    

    #以当前原片为第一批次，计算面积和数量是否符合条件。
    for i in range(len(rectangles)):
        itemmianji += rectangles[0][2] * rectangles[0][3]
    itemshuliang += len(rectangles)

    if itemmianji < (250*1000000+1) and itemshuliang < 1001: #符合条件：是当前批次的，弹出 boxes 中的数据
        result_list[0] = rectangles         #记录到新结果列表中
        # 根据返回的 rectangles 找出需要的新表boxes
        pop_index = [0]*len(rectangles)                 #list()
        for i in range(len(rectangles)):
            pop_index[i] = rectangles[i][4]           #pop_index 记录上一期 item 的 id
        pop_index = sorted(pop_index, reverse = False)
        for j in range(len(pop_index)):
            pop = pop_index.pop()
            #根据 id 找出需要弹出的 list 中的序号       
            for k in range(len(boxes)-1,-1,-1):   #从大到小循环
                if boxes[k,2] == pop:
                    index0 = k
                    boxes = np.delete(boxes, index0 , 0)                   #弹出上一期 item 
                    break
    else:               #不符合条件：不是当前批次的，不要弹出 boxes，retangle 中也不要记录这块板子的信息 , 进入下一批次更新面积和数量的累计
        batch += 1
        itemmianji = 0
        itemshuliang = 0





            


    #计算新原片 No++
    while boxes.size != 0 :
        No += 1                                           #用 No 来记录第几个板子
        #记录第一个 item 的材质，并只选取该材质的item 形成一个新数组 
        cur_material = boxes[0,3]
        j = 0 
        sammat_boxes = boxes[0].reshape(-1,6)      #使用 reshape 函数使数组保持原来的形状  #sammat_boxes = same material boxes
        for i in range(1, len(boxes)):
            if boxes[i,3] == cur_material:
                sammat_boxes0 = boxes[i].reshape(-1,6)      #使用 reshape 函数使数组保持原来的形状
                sammat_boxes = np.append(sammat_boxes, sammat_boxes0, axis=0)
                j += 1

        #并只选取该材质的item 进入组板 
        ture_height, rectangles = splitprg(width, height ,sammat_boxes ,No , batch)   #ture_height == ture 指板子放下了所有 item ；faulse 指 item 超出了该原片的容量。
        rectangles = datarun.removeNone(rectangles)      #数据预处理，删去 rectangles 中的 None
        
        
        #以当前原片为第一批次，计算面积和数量是否符合条件。
        for i in range(len(rectangles)):
            itemmianji += rectangles[0][2] * rectangles[0][3]
        itemshuliang += len(rectangles)

        if itemmianji < (250*1000000+1) and itemshuliang < 1001: #符合条件：是当前批次的，弹出 boxes 中的数据
            result_list[No-1] = rectangles                     #记录到新结果列表中#虽然是第 No 个板子，但结果其实是-1 的，数组从0 开始
            # 根据返回的 rectangles 找出需要的新表boxes
            pop_index = [0]*len(rectangles)                 #list()
            for i in range(len(rectangles)):
                pop_index[i] = rectangles[i][4]           #pop_index 记录上一期 item 的 id
            pop_index = sorted(pop_index, reverse = False)
            for j in range(len(pop_index)):
                pop = pop_index.pop()        
                #根据 id 找出需要弹出的 list 中的序号       
                for k in range(len(boxes)-1,-1,-1):   #从大到小循环
                    if boxes[k,2] == pop:
                        index0 = k
                        boxes = np.delete(boxes, index0 , 0)                   #弹出上一期 item 
                        break

        else:               #不符合条件：不是当前批次的，不要弹出 boxes，retangle 中也不要记录这块板子的信息 , 进入下一批次更新面积和数量的累计
            batch += 1
            itemmianji = 0
            itemshuliang = 0


        

    print(f'排样优化耗时:{time.time() - t:.4f}s')

    #result_list  ,删除多余的数据
    for i in range(len(result_list)-1,-1,-1):
        if result_list[i] == 0 :
            del result_list[i]

    #输出
    t = time.time()
    datarun.outdata(file_path , result_list ,material_indexnp)
    print(f'输出耗时:{time.time() - t:.4f}s')

    #画图
    t = time.time()
    visualizerec(width, height, result_list ,file_path)
    print(f'绘图耗时:{time.time() - t:.4f}s')
    



  



if __name__ == "__main__":
    Rectangle = namedtuple('Rectangle', ['x', 'y', 'w', 'h', 'id', 'No', 'material' , 'batch'])
    '''
    输入参数：
    单个批次产品项（item）总数上限 max_item_num = 1000
    单个批次产品项（item）的面积总和上限max_item_area = 250（m2）
    原片长度plate_length = 2440（mm）
    原片宽度plate_width = 1220 (mm)
    file_path = 数据集文件夹的绝对位置
    '''
    #数据集文件夹地址,pandas,还是number是不允许读 r 的
    file_path = r'/Users/sf/Library/Mobile Documents/com~apple~CloudDocs/repositories/mathematical_modeling/2022_MATH/code/strip-packing-master/problem1_dataA'
    max_item_num = 1000
    max_item_area = 250
    plate_length = 2440
    plate_width = 1220
    #数据读入，预处理
    #读入数据
    # 测试代码
    t = time.time()
    order_list, material_list, datapd = datarun.indata(file_path)  #最终得到一张总表 datapd ，里面有所有的 item 信息；一个列表 material_list 里面有 总表中不同材料的名称
    #数据分组, 得到的数据是可以直接用在单个原片的
    data ,material_indexnp= datarun.grouping(order_list, material_list, datapd)  # numpy格式
    print(f'数据载入耗时:{time.time() - t:.4f}s') 




    #反转90度板子,因为我的板材是90℃计算的
    #单板算法，传入一组数据。#因为大部分数据集都是 item_length > item_width .数据集顺序（item_length，item_width），单板计算顺序（w,h）.最后输出的时候注意即可
    main( data,  plate_length, plate_width, file_path ,material_indexnp ,order_list ) 
