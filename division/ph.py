from copy import deepcopy
from collections import namedtuple
import sys
import logging

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_logger = logging.StreamHandler()
console_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
console_logger.setFormatter(formatter)
logger.addHandler(console_logger)



Rectangle = namedtuple('Rectangle', ['x', 'y', 'w', 'h', 'id', 'No', 'material' , 'batch'])
#第一个原片序号 = 1 
no =1

def splitprg(width, height ,rectangles,  no ,batch ,sorting="width" ):
    """
    该函数决定了原片中每一个 stripe 的第一个切割位置
    result[idx] = Rectangle(x, y, r[0], r[1])的结构是    产品x坐标 产品y坐标 产品x方向长度 产品y方向长度 产品id,原片序号
    """
    

    # 数据的预处理，排序，编号
    if sorting not in ["width", "height" ]:
        raise ValueError("The algorithm only supports sorting by width or height but {} was given.".format(sorting))
    if sorting == "width":#如果按宽度分类，记录 wh = 0
        wh = 0
    else:
        wh = 1
    logger.debug('The original array: {}'.format(rectangles))
    #result 的顺序和放入顺序无关，和sorted_indices是一致的
    result = [None] * len(rectangles)
    remaining = deepcopy(rectangles)#rectangles 的一个深拷贝,存储数据列表
    #enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标，一般用在 for 循环当中。
    #保证 item 中 r[1] 高总是大于宽 r[0] 的,既默认的 item 是站着的
    for idx, r in enumerate(remaining):
        if r[0] > r[1]:
            remaining[idx][0], remaining[idx][1] = remaining[idx][1], remaining[idx][0]
    logger.debug('Swapped some widths and height with the following result: {}'.format(remaining))#tiaos 调试用的输出日志，不管它
    
    #按照宽度对所有 item进行排序，得到排序后的 item 顺序号
    sorted_indices = sorted(range(len(remaining)), key=lambda x: -remaining[x][wh])
    logger.debug('The sorted indices: {}'.format(sorted_indices))
    #按照排序的顺序把 item 的参数给sorted_rect，但是sorted_rect好像后面没用到？phsppog 中用到了
    sorted_rect = [remaining[idx] for idx in sorted_indices]
    logger.debug('The sorted array is: {}'.format(sorted_rect))




    #第 i 个 item 放在上一个 x，y 的位置。
    #每一行的第一个 item，规定了第一阶段切的位置
    x, y, w, h, H = 0, 0, 0, 0, 0
    while sorted_indices:
        #pop(0)弹出第一个元素
        idx = sorted_indices.pop(0)
        r = remaining[idx]
        #如果当前 item 的高大于原片宽,那么不改变 item 的方向，直接放进去(这里假设 item 的宽总是比原片宽小。)
        #处理长宽超限的情况，例如。和【for idx, r in enumerate(remaining):】这一行的宽高排序有关。
        if r[1] > width:
            if H + r[1] >  height:       #终止条件：以高度测度的原片容量[每次更新 H 前判断]
                return H, result
            #该序号的 item 放在 result 的第0个（1，2...）位置。此时 x，y 坐标为（0，0）
            result[idx] = Rectangle(x, y, r[0], r[1], r[2], no, r[3], batch)
            #更新参数：x坐标 为 item 的宽度；y 是更新前的 H（第一期为0）；w 是宽度-item的高；h 为item 的高；H 是更新前 H+高
            x, y, w, h, H = r[0], H, width - r[0], r[1], H + r[1]
            
        #如果当前 item 的高不大于原片宽，那么改变 item 的方向，将item 躺着放在原片上
        else:
            if H + r[0] >  height:       #终止条件：以高度测度的原片容量[每次更新 H 前判断]
                return H, result            
            result[idx] = Rectangle(x, y, r[1], r[0], r[2], no, r[3], batch)
            #更新参数：x 坐标为 item 的高（躺着放），y 为 H 上一期，w 为原片宽 - 高（躺），h 为 item 的宽（躺），H 是上一期 + item宽（躺）
            x, y, w, h, H = r[1], H, width - r[1], r[0], H + r[0]
        #????,这里传递的参数1是啥意思？ w 是原片剩余宽的意思
        recursive_packing(x, y, w, h, 1, remaining, sorted_indices, result , no, batch)
        x, y = 0, H
    logger.debug('The resulting rectangles are: {}'.format(result))

    return H, result



#递归包？是什么
def recursive_packing(x, y, w, h, D, remaining, indices, result, no ,batch,w_last=0):
    '''
    x (x,y)
    y (x,y)
    w 此 stirp 右边剩余空间
    h 此strip 高度
    D 维数。默认1，用的时候+1，代表2维
    '''
    # 核心变量 余item 数组remaining[idx]  ；  优先级priority
    """Helper function to recursively fit a certain area.帮助程序函数以递归方式拟合某个区域。"""
    #这是啥？优先级？
    #在余下的 item 中进行遍历，对组内 item 赋予优先级。由于 item 是按照宽或者高的顺序由大到小排列好的，因此符合贪心思想。
    '''
    优先级1：
    优先级2：
    3：
    4： 
    5： 如果该 stack 中没有空余宽度w，既没有位置放所有剩下的 item，那么 priority = 5 ,跳出recursive_packing，进入下一个 strip
    '''
    priority = 6
    for idx in indices:
        #D是维度的意思吗？D+1 = 1+1 = 2 = 2维？
        for j in range(0, D + 1):
            '''
            根据 item 和 rusult 的前一期结果的宽高做优先级排序。。ps：(0 + j) % 2取余数，7%2=1;   
            一共有两步（循环 j=0;j=1）:   0:item的宽
            remaining[idx][(0 + j) % 2] == w 指当前 item 的宽 j=0/高 j=1 是否和原片剩余宽 w 相同或小于
            remaining[idx][(1 + j) % 2] == h 指当前 item 的宽 j=0/高 j=1 是否和该stack高相同或小于
            一共有4种组合，  ”=“”=“组合优先级最高为1；”<“”<“组合优先级最低 为4 。
            如果该 stack 中没有空余宽度w，既没有位置放所有剩下的 item，那么跳过循环
            '''
            #优先级 =1 当前 item 和剩余空间相同
            if priority > 1 and remaining[idx][(0 + j) % 2] == w and remaining[idx][(1 + j) % 2] == h:
                priority, orientation, best = 1, j, idx
                break
            # 当前 item 的宽和剩余宽一样，高小于该 strip 的高，
            elif priority > 2 and remaining[idx][(0 + j) % 2] == w and remaining[idx][(1 + j) % 2] < h:
                priority, orientation, best = 2, j, idx
            # 当前 item 的宽小于剩余宽，高等于该 stack 的高
            # 增加条件：要大于等于上一期 item 的宽
            elif priority > 3 and remaining[idx][(0 + j) % 2] < w and remaining[idx][(1 + j) % 2] == h and (remaining[idx][(0 + j) % 2] > w_last or remaining[idx][(0 + j) % 2] == w_last):
                priority, orientation, best = 3, j, idx
            # 当前item 的宽小于剩余宽，高小于剩余高
            # 增加条件：要大于等于上一期 item 的宽
            elif priority > 4 and remaining[idx][(0 + j) % 2] < w and remaining[idx][(1 + j) % 2] < h and (remaining[idx][(0 + j) % 2] > w_last or remaining[idx][(0 + j) % 2] == w_last):
                priority, orientation, best = 4, j, idx
            #如果该 stack 中没有空余宽度w，既没有位置放所有剩下的 item，那么 priority = 5 ,跳出recursive_packing，进入下一个 strip
            elif priority > 5:
                priority, orientation, best = 5, j, idx


    #优先级小于5 ，代表该 strip 里要放后续 item。有三种情况：优先级4；优先级2；优先级3
    #result ：该 strip 里要放后续 item ,索引为 remaining[best]
    if priority < 5:
        # orientation确定什么方向更合适，并将宽高赋给  w_best ， h_best 。w_best = 宽  h_best = 高。反人类的写法....
        if orientation == 0:
            w_best, h_best ,id_best, material_best= remaining[best][0], remaining[best][1], remaining[best][2], remaining[best][3]
        else:
            w_best, h_best ,id_best, material_best= remaining[best][1], remaining[best][0], remaining[best][2], remaining[best][3]
        #result ：该 strip 里要放后续 item 的坐标信息
        result[best] = Rectangle(x, y, w_best, h_best, id_best, no, material_best , batch)
        #弹出现在这个 item 的引用序号
        indices.remove(best)

        # 优先级 = 2 ，代表宽和给定的剩余宽相同，剩下的直接叠放上面（放不了就退出该剩余空间的搜索）
        # 增加条件，下次搜索的 item宽 要大于等于现在的 w_best
        if priority == 2:
            recursive_packing(x, y + h_best, w, h - h_best, D, remaining, indices, result, no, batch,w_best)
        # ？？？这里应该有三阶段算法？？？优先级 = 3 ， 代表宽小于给定空间宽，高度等于给定空间高度，直接 放右边。
        elif priority == 3:
            recursive_packing(x + w_best, y, w - w_best, h, D, remaining, indices, result, no, batch)
        
        #优先级是4这种情况的 result 之后的空间搜索方案：
        elif priority == 4:
            min_w = sys.maxsize                      #Py_ssize_t的最大值取决于架构
            min_h = sys.maxsize
            # 在余下的 item 中选出最小的宽和高，如果剩余空间小于最小的，那么跳出该 strip
            for idx in indices:
                min_w = min(min_w, remaining[idx][0])
                min_h = min(min_h, remaining[idx][1])
            # Because we can rotate: 
            min_w = min(min_h, min_w)
            min_h = min_w


            '''
            #这里的 w 还是传递过来的 w ，还没有更新。既放入本次 result 之前的 w
            #这里的 w_best 是本次 result 的宽度
            #这里的 h 是本次 strip 高度
            #这里的 h_best 是是本次 result 的宽度/高度
            '''

            #空间搜索的顺序：本次 result 的右，上，下左
            #  搜索空间.w - w_best 是本次 result 的之后的宽度余量，满足不等式（说明右边空间小的连最小的 item 都放不下），下一项放 result 上面；不满足不等式进行下一项判断，搜索右边空间。
            if w - w_best < min_w:       #右边没空间吗？放上面，进入迭代。否则，右边有空间，判断上面elif h - h_best < min_h:
                #！！！本次搜索放置可能不符合三阶段
                # 增加条件，下次搜索的 item宽 要大于等于现在的 w_best
                recursive_packing(x, y + h_best, w, h - h_best, D, remaining, indices, result, no, batch,w_best)
            #  h - h_best 是本次 result 之上的，和 strip 之间的余量，满足不等式（说明result上面的空间小的连最小的 ltem 都放不下），下一项放右边
            elif h - h_best < min_h:         #上面没空间嘛？放右边，进入迭代。否则右边，上面都有空间，判断elif w_best < min_w:
                recursive_packing(x + w_best, y, w - w_best, h, D, remaining, indices, result, no,batch)
            #  w_best 是本次 result 的宽度
            #！！！！！这里可以修改是否为三阶段切法。只要result 上面的 item 宽度一致，第三阶段将他们分开即可
            elif w_best < min_w:         #右边上面都有空间， result 上能放 item 嘛？...，否则进入最后
                # ？？？放右边，进入迭代
                recursive_packing(x + w_best, y, w - w_best, h_best, D, remaining, indices, result, no, batch)
                #？？？放上面，进入迭代，但是 w 给的是否超出 result 了？
                #这里不用增加条件，因为最小的 item 的长或者宽，都大于w_best，不存在三阶段无法切割情况。
                recursive_packing(x, y + h_best, w, h - h_best, D, remaining, indices, result, no,batch)
            #  result 的宽度够，高度够，可以叠放
            else:
                #先放result 上面
                # 增加条件，下次搜索的 item宽 要大于等于现在的 w_best
                recursive_packing(x, y + h_best, w_best, h - h_best, D, remaining, indices, result, no, batch,w_best)
                #再放 result 右边
                recursive_packing(x + w_best, y, w - w_best, h, D, remaining, indices, result, no ,batch)


