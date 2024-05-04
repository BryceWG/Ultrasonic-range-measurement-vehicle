###################################################
#Name: 雷达扫描神器
#Copyright: 不莣初芯
#Author: 不莣初芯
#Date: 12/07/20 23:38
#Description: 串口接收到Arduino发送的超声波测距数据，
#             使用Pygame绘制雷达扫描界面，当超声波检
#             测到障碍物时在雷达中显示出来。
#             注意：程序运行时需要在终端输入串口，例
#             如：COM4
###################################################
import pygame,sys
import pygame.freetype
from pygame.locals import *  #导入绘图库
import math   #导入数学库
import serial  #导入串口库

#变量的初始化
listColor =[]
listColor2 =[]
index = 0
distance = 0.0
listIndex = []
listDistance = []
#设置两个颜色列表中的颜色
######
for i in range(40):
    ab = 255-i*8
    if ab <0:
        ab = 0
    listColor.append((31,ab,31))
    listColor2.append((ab,0,0))
    
#初始化列表，可保存200个数据
for i in range(200):
    listIndex.append(0)
    listDistance.append(200)

#打开串口
serialPort = input("输入COM口：")
serialBaud = 9600   #波特率
ser = serial.Serial(serialPort,serialBaud,timeout=0.5) #打开串口，超时时间为0.5秒
#pygame的初始化
pygame.init()
size = width,height = 800,500
screen = pygame.display.set_mode(size)
pygame.display.set_caption("雷达监测")
#设置各类文字字体
#角度字体
font = pygame.font.SysFont("arial",20)
ft30_surf = font.render("30°",True,listColor[0])
ft60_surf = font.render("60°",True,listColor[0])
ft90_surf = font.render("90°",True,listColor[0])
ft120_surf = font.render("120°",True,listColor[0])
ft150_surf = font.render("150°",True,listColor[0])
#距离字体
fontcm = pygame.font.SysFont("arial",12)
ft15cm_surf = fontcm.render("15cm",True,listColor[0])
ft25cm_surf = fontcm.render("25cm",True,listColor[0])
ft35cm_surf = fontcm.render("35cm",True,listColor[0])
ft45cm_surf = fontcm.render("45cm",True,listColor[0])
#文字字体
ftob_surf = font.render("Object: Out of Range",True,listColor[0])
ftan_surf = font.render("Angle: ",True,listColor[0])
ftdi_surf = font.render("Distance: ",True,listColor[0])
#设置刷新帧率
fps = 30
fclock = pygame.time.Clock()
#主循环程序
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    screen.fill([0,0,0])
    ch =str(ser.readline()) #接收串口发送来的数据
    chlist=ch.split('#') #将接收的数据以 # 为间隔进行切片
    if len(chlist) >=4:  #当切片后的列表长度大于4时才是接收到的完整数据
        distance=float(chlist[2]) #获取超声波测距数据，转为浮点数
        index = int(chlist[1])  #获取舵机的角度，转为整数
    for i in range(39,0,-1): #列表中保存40条数据，用于绘制扫描线
        listIndex[i] = listIndex[i-1]
        listDistance[listIndex[i]] = listDistance[listIndex[i-1]]
    listIndex[0] = index
    listDistance[index] = distance
    for i in range(40):
        if listDistance[listIndex[i]]<45: #当超声波检测的距离小于45时，绘制红色扫描线
            point_x = 400+listDistance[listIndex[i]]*360/45*math.cos(listIndex[i]/180*math.pi)
            point_y = 430-listDistance[listIndex[i]]*360/45*math.sin(listIndex[i]/180*math.pi)
            point_x2 = 400+listDistance[listIndex[i-1]]*360/45*math.cos(listIndex[i-1]/180*math.pi)
            point_y2 = 430-listDistance[listIndex[i-1]]*360/45*math.sin(listIndex[i-1]/180*math.pi)
            #pygame.draw.line(screen,listColor2[i],(400,430),(point_x,point_y),5) #angle
            #pygame.draw.line(screen,listColor2[i],(400+listDistance[listIndex[i]]*360/45*math.cos(listIndex[i]/180*math.pi),430-listDistance[listIndex[i]]*360/45*math.sin(listIndex[i]/180*math.pi)),(400+380*math.cos(listIndex[i]/180*math.pi),430-380*math.sin(listIndex[i]/180*math.pi)),5)
            #pygame.draw.line(screen,listColor[i],(400+380*math.cos(listIndex[i]/180*math.pi),430-380*math.sin(listIndex[i]/180*math.pi)),(400+450*math.cos(listIndex[i]/180*math.pi),430-450*math.sin(listIndex[i]/180*math.pi)),5)
            #pygame.draw.rect(screen,listColor2[i],[point_x,point_y,5,5],3)
            pygame.draw.line(screen,[255,0,0],(point_x2,point_y2),(point_x,point_y),3)
        else:
            pygame.draw.line(screen,listColor[i],(400,430),(400+450*math.cos(listIndex[i]/180*math.pi),430-450*math.sin(listIndex[i]/180*math.pi)),5) 
    #修改文字
    if distance < 45:
        ftob_surf = font.render("Object: In Range",True,listColor[0])
        ftdi_surf = font.render("Distance: "+str(distance)+"cm",True,listColor[0])
    else:
        ftob_surf = font.render("Object: Out of Range",True,listColor[0])
        ftdi_surf = font.render("Distance:   cm",True,listColor[0])
    ftan_surf = font.render("Angle: "+str(index)+"°",True,listColor[0])
    #绘制同心半圆：参数1：surface;参数2：颜色;参数3：((x,y),(w,h)),表示所绘制圆弧的外切矩形左上角坐标和矩形的宽度和高度
    #参数4：该圆弧的起始角度，参数5：该圆弧的终止角度(有点偏差所以加0.05/0.01);参数6：弧线的宽度0——10
    pygame.draw.arc(screen,listColor[0],((280,310),(240,240)),0,math.pi+0.05,2)
    pygame.draw.arc(screen,listColor[0],((200,230),(400,400)),0,math.pi+0.05,2)
    pygame.draw.arc(screen,listColor[0],((120,150),(560,560)),0,math.pi+0.01,2)
    pygame.draw.arc(screen,listColor[0],((40,70),(720,720)),0,math.pi+0.01,2)
    #绘制射线
    #参数3：起点坐标，参数4：终点坐标(需要计算)
    pygame.draw.line(screen,listColor[0],(400,430),(400+380*math.cos(0),430-380*math.sin(0)),2) #0°
    pygame.draw.line(screen,listColor[0],(400,430),(400+380*math.cos(math.pi/6),430-380*math.sin(math.pi/6)),2) #30°
    pygame.draw.line(screen,listColor[0],(400,430),(400+380*math.cos(math.pi/3),430-380*math.sin(math.pi/3)),2) #60°
    pygame.draw.line(screen,listColor[0],(400,430),(400+380*math.cos(math.pi/2),430-380*math.sin(math.pi/2)),2) #90°
    pygame.draw.line(screen,listColor[0],(400,430),(400+380*math.cos(2*math.pi/3),430-380*math.sin(2*math.pi/3)),2) #120°
    pygame.draw.line(screen,listColor[0],(400,430),(400+380*math.cos(5*math.pi/6),430-380*math.sin(5*math.pi/6)),2) #150°
    pygame.draw.line(screen,listColor[0],(400,430),(400+380*math.cos(math.pi),430-380*math.sin(math.pi)),2) #180°
    #绘制度数 参数3：y坐标，计算时有偏差
    screen.blit(ft30_surf,(400+380*math.cos(math.pi/6)+5,430-380*math.sin(math.pi/6)-15))
    screen.blit(ft60_surf,(400+380*math.cos(math.pi/3)+5,430-380*math.sin(math.pi/3)-20))
    screen.blit(ft90_surf,(400+380*math.cos(math.pi/2)-10,430-380*math.sin(math.pi/2)-23))
    screen.blit(ft120_surf,(400+380*math.cos(2*math.pi/3)-25,430-380*math.sin(2*math.pi/3)-23))
    screen.blit(ft150_surf,(400+380*math.cos(5*math.pi/6)-25,430-380*math.sin(5*math.pi/6)-23))
    #绘制距离
    screen.blit(ft15cm_surf,(495,417))
    screen.blit(ft25cm_surf,(575,417))
    screen.blit(ft35cm_surf,(655,417))
    screen.blit(ft45cm_surf,(735,417))
    #绘制文字
    screen.blit(ftob_surf,(120,430))
    screen.blit(ftan_surf,(450,430))
    screen.blit(ftdi_surf,(620,430))
    #刷新窗口
    pygame.display.update()
    fclock.tick(fps)