import pygame,sys
import pygame.freetype
from pygame.locals import *  #导入绘图库
import math   #导入数学库
import serial  #导入串口库
import settings
#变量的初始化
listColor =[]
listColor2 =[]
angle = 0
distance = 0.0
point_x2 = 0
point_y2 = 0
lines = []
points = []

#打开串口
serialPort = input("输入COM口:")
serialBaud = 9600   #波特率
ser = serial.Serial(serialPort,serialBaud,timeout=0.5) #打开串口，超时时间为0.5秒
#pygame的初始化
pygame.init()
size = settings.width,settings.height
screen = pygame.display.set_mode(size)
pygame.display.set_caption("超声波雷达监测")

#设置刷新帧率
fps = 60
fclock = pygame.time.Clock()
#主循环程序
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    screen.fill(settings.bg_color)
    ch =str(ser.readline()) #接收串口发送来的数据
    chlist=ch.split('#') #将接收的数据以 # 为间隔进行切片
    if len(chlist) >=4:  #当切片后的列表长度大于4时才是接收到的完整数据
        distance=float(chlist[2]) #获取超声波测距数据，转为浮点数
        angle = int(chlist[1])  #获取舵机的角度，转为整数
    
    if distance<45: 
        point_x = 400+distance*360/45*math.cos(angle/180*math.pi)
        point_y = 430-distance*360/45*math.sin(angle/180*math.pi)
        points.append((point_x,point_y))
        if len(points) > 1:
            lines = [(points[1],points[i + 1]) for i in range(len(points) - 1)]
    else:
        pygame.draw.line(screen,settings.green_color,(400,430),(400+450*math.cos(angle/180*math.pi),430-450*math.sin(angle/180*math.pi)),5) 
    for line in lines:
            pygame.draw.line(screen,(255,0,0),line[0],line[1],3)

    pygame.display.update()
    fclock.tick(fps)