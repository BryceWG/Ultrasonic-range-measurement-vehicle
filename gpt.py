import pygame
import math
import random

# 初始化Pygame
pygame.init()

# 设置窗口大小
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Radar Scan Simulation")

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# 定义雷达位置和方向
radar_x, radar_y = width // 2, height // 2
radar_angle = 0

# 存储扫描得到的点云数据
point_cloud = []

# 游戏循环
running = True
while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 清空屏幕
    screen.fill(BLACK)

    # 模拟雷达扫描
    scan_angle = radar_angle
    for _ in range(360):
        # 检测当前方向是否有障碍物
        distance = 100  # 假设最大扫描距离为 100 像素
        obstacle_detected = False
        for d in range(distance):
            x = radar_x + math.cos(math.radians(scan_angle)) * d
            y = radar_y + math.sin(math.radians(scan_angle)) * d
            if random.random() < 0.05:  # 5% 的概率检测到障碍物
                obstacle_detected = True
                intersection_point = (int(x), int(y))
                point_cloud.append(intersection_point)
                break

        scan_angle += 1

    # 绘制扫描得到的点云
    for point in point_cloud:
        pygame.draw.circle(screen, GREEN, point, 2)

    # 更新雷达位置和方向
    # 在这里可以添加代码更新雷达位置和方向

    # 更新显示
    pygame.display.flip()

# 退出Pygame
pygame.quit()