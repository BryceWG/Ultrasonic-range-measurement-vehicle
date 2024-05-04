###################################################
#Name: 雷达扫描神器
#Copyright: 不莣初芯
#Author: 不莣初芯
#Date: 12/07/20 23:38
#Description: 串口接收到Arduino发送的超声波测距数据，
#             使用Pygame绘制雷达扫描界面，当超声波检
#             测到障碍物时在雷达中显示出来
#             注意：程序运行时需要在终端输入串口，例
#             如：COM4
###################################################
import pygame,sys
import pygame.freetype
import settings
from pygame.locals import *  #导入绘图库
import math   #导入数学库
import serial  #导入串口库

#变量的初始化
arc = 0
distance = 0.00
listarc = []
listDistance = []

#初始化列表，可保存200个数据
for i in range(200):
    listarc.append(0)
    listDistance.append(200)

#打开串口
serialPort = input("输入COM口:")
serialBaud = 9600   #波特率
ser = serial.Serial(serialPort,serialBaud,timeout=0.5) #打开串口，超时时间为0.5秒
#pygame的初始化
pygame.init()
size = settings.width,settings.height
screen = pygame.display.set_mode(size)
pygame.display.set_caption("超声波雷达监测")
#设置各类文字字体
#角度字体
font = pygame.font.SysFont("arial",20)
ft30_surf = font.render("30°",True,settings.white_color)
ft60_surf = font.render("60°",True,settings.white_color)
ft90_surf = font.render("90°",True,settings.white_color)
ft120_surf = font.render("120°",True,settings.white_color)
ft150_surf = font.render("150°",True,settings.white_color)
#距离字体
fontcm = pygame.font.SysFont("arial",12)
ft20cm_surf = fontcm.render("20cm",True,settings.white_color)
ft40cm_surf = fontcm.render("40cm",True,settings.white_color)
ft60cm_surf = fontcm.render("60cm",True,settings.white_color)
ft80cm_surf = fontcm.render("80cm",True,settings.white_color)
#文字字体
ftob_surf = font.render("超出检测范围",True,settings.white_color)
ftan_surf = font.render("当前角度: ",True,settings.white_color)
ftdi_surf = font.render("当前距离: ",True,settings.white_color)
#设置刷新帧率
fps = 60
fclock = pygame.time.Clock()
#主循环程序
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit() #退出程序

    screen.fill(settings.bg_color)
    ch =str(ser.readline()) #接收串口发送来的数据
    chlist=ch.split('#') #将接收的数据以 # 为间隔进行切片
    if len(chlist) >=4:  #当切片后的列表长度大于4时才是接收到的完整数据
        distance=float(chlist[2]) #获取超声波测距数据，转为浮点数
        arc = int(chlist[1])  #获取舵机的角度，转为整数
    #for i in range(39,0,-1): #列表中保存40条数据，用于绘制扫描线
        #listarc[i] = listarc[i-1]
        #listDistance[listarc[i]] = listDistance[listarc[i-1]]
    #listarc[0] = arc
    #listDistance[arc] = distance
    #for i in range(40):
        #if listDistance[listarc[i]]<80: #当超声波检测的距离小于80时，绘制红色扫描线
    point_x = settings.centre_point_x + distance * math.cos(arc/180*math.pi) * 10
    point_y = settings.centre_point_y + distance * math.sin(arc/180*math.pi) * 10
    #pygame.draw.line(screen,settings.red_color,(400,430),(400+listDistance[listarc[i]]*360/45*math.cos(listarc[i]/180*math.pi),430-listDistance[listarc[i]]*360/45*math.sin(listarc[i]/180*math.pi)),5) #angle
    pygame.draw.rect(screen,settings.obj_color,[point_x,point_y,3,3],1)
        #else:
            #pygame.draw.line(screen,settings.white_color,(400,430),(400+450*math.cos(listarc[i]/180*math.pi),430-450*math.sin(listarc[i]/180*math.pi)),5) 
    #修改文字
    if distance < 80:
        ftob_surf = font.render("检测范围内",True,settings.white_color)
        ftdi_surf = font.render("当前距离: "+str(distance)+"cm",True,settings.white_color)
    else:
        ftob_surf = font.render("超出检测范围",True,settings.white_color)
        ftdi_surf = font.render("当前距离:   cm",True,settings.white_color)
    ftan_surf = font.render("当前角度: "+str(arc)+"°",True,settings.white_color)
    #绘制同心半圆：参数1：surface;参数2：颜色;参数3：((x,y),(w,h)),表示所绘制圆弧的外切矩形左上角坐标和矩形的宽度和高度
    #参数4：该圆弧的起始角度，参数5：该圆弧的终止角度(有点偏差所以加0.05/0.01);参数6：弧线的宽度0——10
    pygame.draw.arc(screen,settings.white_color,((280,310),(240,240)),0,math.pi+0.05,2)
    pygame.draw.arc(screen,settings.white_color,((200,230),(400,400)),0,math.pi+0.05,2)
    pygame.draw.arc(screen,settings.white_color,((120,150),(560,560)),0,math.pi+0.01,2)
    pygame.draw.arc(screen,settings.white_color,((40,70),(720,720)),0,math.pi+0.01,2)
    #绘制射线
    #参数3：起点坐标，参数4：终点坐标(需要计算)
    pygame.draw.line(screen,settings.white_color,(400,430),(400+380*math.cos(0),430-380*math.sin(0)),2) #0°
    pygame.draw.line(screen,settings.white_color,(400,430),(400+380*math.cos(math.pi/6),430-380*math.sin(math.pi/6)),2) #30°
    pygame.draw.line(screen,settings.white_color,(400,430),(400+380*math.cos(math.pi/3),430-380*math.sin(math.pi/3)),2) #60°
    pygame.draw.line(screen,settings.white_color,(400,430),(400+380*math.cos(math.pi/2),430-380*math.sin(math.pi/2)),2) #90°
    pygame.draw.line(screen,settings.white_color,(400,430),(400+380*math.cos(2*math.pi/3),430-380*math.sin(2*math.pi/3)),2) #120°
    pygame.draw.line(screen,settings.white_color,(400,430),(400+380*math.cos(5*math.pi/6),430-380*math.sin(5*math.pi/6)),2) #150°
    pygame.draw.line(screen,settings.white_color,(400,430),(400+380*math.cos(math.pi),430-380*math.sin(math.pi)),2) #180°
    #绘制度数 参数3：y坐标，计算时有偏差
    screen.blit(ft30_surf,(400+380*math.cos(math.pi/6)+5,430-380*math.sin(math.pi/6)-15))
    screen.blit(ft60_surf,(400+380*math.cos(math.pi/3)+5,430-380*math.sin(math.pi/3)-20))
    screen.blit(ft90_surf,(400+380*math.cos(math.pi/2)-10,430-380*math.sin(math.pi/2)-23))
    screen.blit(ft120_surf,(400+380*math.cos(2*math.pi/3)-25,430-380*math.sin(2*math.pi/3)-23))
    screen.blit(ft150_surf,(400+380*math.cos(5*math.pi/6)-25,430-380*math.sin(5*math.pi/6)-23))
    #绘制距离
    screen.blit(ft20cm_surf,(495,417))
    screen.blit(ft40cm_surf,(575,417))
    screen.blit(ft60cm_surf,(655,417))
    screen.blit(ft80cm_surf,(735,417))
    #绘制文字
    screen.blit(ftob_surf,(120,430))
    screen.blit(ftan_surf,(450,430))
    screen.blit(ftdi_surf,(620,430))
    #刷新窗口
    pygame.display.update()
    fclock.tick(fps)