#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 10:15:47 2018

@author: liuhuanshuo
"""

import matplotlib.pyplot as plt

from random_walk import RandomWalk
#创建一个randomwalk实例，并将其包含的点都绘制出来
rw = RandomWalk()
rw.fill_walk()
plt.scatter(rw.x_values,rw.y_values,s=15)
plt.show()
