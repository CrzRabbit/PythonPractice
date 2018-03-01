# # -*-coding:UTF-8-*-
# from PIL import Image
# import colorsys
# from pylab import  *
# import os, math, random
#
# xstep = 2               #x轴搜索步长
# ystep = 30              #y轴搜索步长
# width = 0               #截屏宽度
# height = 0              #截屏高度
# ymin = 500              #搜索范围高度最小值
# ymax = 1700             #搜索范围高度最大值
# samplename = '0.png'    #小人样本图片
# picturename = '1.png'   #截屏图片
#
# #获取手机截屏并放到当前文件夹
# def get_screencap():
#     os.system("adb shell wm size")
#     os.system("adb shell screencap -p /sdcard/1.png")
#     os.system("adb pull /sdcard/1.png .")
# #通知手机起跳
# def jump(time):
#     x1 = int(random.uniform(100, 1000))
#     x2 = int(random.uniform(100, 1000))
#     y1 = int(random.uniform(100, 1900))
#     y2 = int(random.uniform(100, 1900))
#     os.system("adb shell input swipe {0:d} {1:d} {2:d} {3:d} {4:d}".format(x1, y1, x2, y2, int(time)))
# #通过next_pos和now_pos确定时间
# def get_time(nowx, nowy, nextx, nexty):
#     xd = 0.
#     xd = fabs(nowx - nextx)
#     time = xd / sqrt(3) * 2 * 2560 / 1920 * 1.04
#     return time
# #根据HSV和LEVEL判断两个像素相近
# def color_judge(h0, s0, v0, h1, s1, v1, level):
#     R = 100
#     ANGLE = 30
#     H = R * cos(ANGLE / 180 * pi)
#
#     x0 = R * v0 * s0 * cos(h0 / 180 * pi)
#     y0 = R * v0 * s0 * sin(h0 / 180 * pi)
#     z0 = H * (1 - v0)
#
#     x1 = R * v1 * s1 * cos(h1 / 180 * pi)
#     y1 = R * v1 * s1 * sin(h1 / 180 * pi)
#     z1 = H * (1 - v1)
#
#     dx = x1 - x0
#     dy = y1 - y0
#     dz = z1 - z0
#
#     ret = sqrt(dx * dx + dy * dy + dz * dz)
#
#     if level == 1:
#         if ret < 10:
#             return True
#         else:
#             return False
#     elif level == 0:
#         if ret < 2:
#             return True
#         else:
#             return False
#     elif level == 2:
#         if ret == 0:
#             return True
#         else:
#             return False
#     elif level == 4:
#         if fabs(h0 - h1) < 0.1 and s0 < s1:
#             return True
#         else:
#             return False
# #RGB值转换到HSV值
# def rgb_to_hsv(r, g, b):
#     if not (r >= 0 and r <= 255 and g >= 0 and g <=255 and b >=0 and b <=255):
#         print 'wrong rgb data'
#         return 0, 0, 0
#
#     rgb = [r, g, b]
#     sort(rgb)
#     min = rgb[2]
#     max = rgb[0]
#     v = max / 255.
#     if max == 0:
#         s = 0
#     else:
#         s = (max - min) / max
#     if max == min:
#         h = 0
#     elif max == r and g >= b:
#         h = ((g - b) * 60) / (max - min)
#     elif max == r and g < b:
#         h = ((g - b) * 60) / (max - min) + 360
#     elif max == g:
#         h = ((b - r) * 60) / (max - min) + 120
#     elif max == b:
#         h = ((r - g) * 60) / (max - min) + 240
#     return h, s, v
# #下一个点的辅助点
# def find_next_aux(im, i, h0, s0, v0):
#     im0 = Image.open(samplename)
#     pix0 = im0.load()
#     r, g, b, a = pix0[0, 0]
#     h, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
#     pix = im.load()
#     j = width - 1
#     while j > 0:
#         r1, g1, b1, a1= pix[j, i]
#         h1, s1, v1 = colorsys.rgb_to_hsv(r1 / 255., g1 / 255., b1 / 255.)
#         if not (color_judge(h1, s1, v1, h0, s0, v0, 1)) and not (color_judge(h1, s1, v1, h, s, v, 4)):
#             return j, i
#         j = j - xstep
#     return 0, 0
# #寻找下一个点
# def find_next_pos(im0):
#     #获取小人样本图片
#     im = Image.open(samplename)
#     pix = im.load()
#     r, g, b, a = pix[0, 0]
#     h, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
#
#     pix0 = im0.load()
#     r0, g0, b0, a0= pix0[0, ymin]
#     h0, s0, v0 = colorsys.rgb_to_hsv(r0 / 255., g0 / 255., b0 / 255.)
#     for i in range(ymin, height, ystep):
#         for j in range(0, width, xstep):
#             r1, g1, b1, a1= pix0[j, i]
#             h1, s1, v1 = colorsys.rgb_to_hsv(r1 / 255., g1 / 255., b1 / 255.)
#             #和背景不同，和小人样本不同（小人头部可能高于下一个位置）
#             if (not color_judge(h1, s1, v1, h0, s0, v0, 1)) and not (color_judge(h1, s1, v1, h, s, v, 4)):
#                 m, n = find_next_aux(im0, i, h0, s0, v0)
#                 if abs(j - m) < 40:
#                     break
#                 p1 = [j, m]
#                 p2 = [i, n]
#                 plot(p1, p2, 'r-')
#                 cx = (j + m) / 2
#                 cy = i
#                 plot(cx, cy, 'r.')
#                 return cx, cy
#     return  0, 0
# #寻找当前小人的辅助点
# def find_now_aux(im, i0, h0, s0, v0):
#     pix = im.load()
#     j = 0
#     while j < width:
#         r1, g1, b1, a1= pix[j, i0]
#         h1, s1, v1 = colorsys.rgb_to_hsv(r1 / 255.0, g1 / 255.0, b1 / 255.0)
#         if color_judge(h1, s1, v1, h0, s0, v0, 0):
#             return j, i0
#         j = j + xstep
#     return 0, 0
# #寻找当前小人的位置
# def find_now_pos(im):
#     #获取小人样本图片的HSV
#     im0 = Image.open(samplename)
#     pix0 = im0.load()
#     r0, g0, b0, a0 = pix0[0, 0]
#     h0, s0, v0 = colorsys.rgb_to_hsv(r0 / 255.0, g0 / 255.0, b0 / 255.0)
#
#     pix1 = im.load()
#     i = ymax
#     while i >= ymin:
#         j = width - 1
#         while j >= 0:
#             r1, g1, b1, a1= pix1[j, i]
#             h1, s1, v1 = colorsys.rgb_to_hsv(r1 / 255.0, g1 / 255.0, b1 / 255.0)
#             #找到小人样本相同的像素
#             if color_judge(h1, s1, v1, h0, s0, v0, 0):
#                 m, n = find_now_aux(im, i, h0, s0, v0)
#                 if m == 0 and n == 0:
#                     break
#                 if abs(j - m) < 40:
#                     break
#                 p1 = [j , m]
#                 p2 = [i , n]
#                 plot(p1, p2, 'g-')
#                 cx = (j + m) / 2
#                 cy = i
#                 plot(cx, cy, 'g.')
#                 return cx, cy
#             j = j - xstep
#         i = i - 10
#     return 0, 0
#
# loop = True
# while loop:
#     get_screencap()
#     pil_im = Image.open(picturename)
#     width = pil_im.size[0]
#     height = pil_im.size[1]
#     im = array(Image.open(picturename))
#     nowx, nowy = find_now_pos(pil_im)
#     nextx, nexty = find_next_pos(pil_im)
#     jump(get_time(nowx, nowy, nextx, nexty))
#     #打印当前搜索结果
#     # imshow(im)
#     # show()
#     time.sleep(1)
#     loop = True
