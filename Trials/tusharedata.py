# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 23:17:47 2018

@author: Administrator
"""

import tushare as ts
from wordcloud import WordCloud

font_path = 'E:\workfile\PyQuant\pyQuant\Trials\simkai.ttf' # 为matplotlib设置中文字体路径没

wc = WordCloud(font_path=font_path,  # 设置字体
               background_color="white",  # 背景颜色
               max_words=2000,  # 词云显示的最大词数
               #mask=back_coloring,  # 设置背景图片
               max_font_size=100,  # 字体最大值
               #random_state=42,
               width=1000, height=860, margin=2,# 设置图片默认的大小,但是如果使用背景图片的话,那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
               )

stk_area = ts.get_area_classified()
area_data = list(stk_area['area'])
area = (',').join(area_data)

# Generate a word cloud image
#wordcloud = WordCloud().generate(area)
wordcloud = wc.generate(area)
# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")