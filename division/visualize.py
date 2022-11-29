import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from random import random


def visualizerec(width, height, rectangles, file_path):
    """
        如果文件名和函数名重复，就会出现TypeError: 'module' object is not callable（“模块”对象不可调用）
    """
    

    fig = plt.figure()
    axes = fig.add_subplot(1, 1, 1)


    #循环所有列表画图
    for i in range(len(rectangles)):  
        axes.add_patch(
        patches.Rectangle(
            (0, 0),  # (x,y)
            width,  # width
            height,  # height
            hatch='x',
            fill=False,
        )
    )
        for idx, r in enumerate(rectangles[i]):
            axes.add_patch(
                patches.Rectangle(
                    (r.x, r.y),  # (x,y)
                    r.w,  # width
                    r.h,  # height
                    color=(random(), random(), random()),
                )
            )
            axes.text(r.x + 0.5 * r.w, r.y + 0.5 * r.h, 'id:' + str(r.id))
        axes.set_xlim(0, width)
        axes.set_ylim(0, height)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.savefig(os.path.join(file_path, str(i) + '_problem1_cut.png' ))
        #plt.show()
        plt.cla()
        
