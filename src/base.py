"""
Base module - Handles base (eagle) protection
基地模块 - 处理基地（鹰）保护
"""
import pygame
from config import *


class Base:
    """基地类 - 玩家需要保护的目标"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.alive = True
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw(self, screen):
        """绘制基地"""
        if self.alive:
            # 绘制鹰的形状
            # 外框
            pygame.draw.rect(screen, COLOR_STEEL, self.rect, 2)
            # 内部填充
            pygame.draw.rect(screen, COLOR_DARK_STEEL, self.rect)

            # 绘制鹰的图案（简化的像素风格）
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2

            # 鹰的身体
            pygame.draw.circle(screen, COLOR_YELLOW, (center_x, center_y), 12)
            # 鹰的翅膀
            pygame.draw.polygon(screen, COLOR_YELLOW, [
                (center_x - 10, center_y - 5),
                (center_x - 20, center_y - 10),
                (center_x - 15, center_y),
                (center_x - 5, center_y - 3)
            ])
            pygame.draw.polygon(screen, COLOR_YELLOW, [
                (center_x + 10, center_y - 5),
                (center_x + 20, center_y - 10),
                (center_x + 15, center_y),
                (center_x + 5, center_y - 3)
            ])
            # 鹰的头部
            pygame.draw.circle(screen, COLOR_YELLOW, (center_x, center_y - 15), 6)
            # 眼睛
            pygame.draw.circle(screen, COLOR_RED, (center_x - 2, center_y - 17), 2)
            pygame.draw.circle(screen, COLOR_RED, (center_x + 2, center_y - 17), 2)
        else:
            # 基地被摧毁的效果
            pygame.draw.rect(screen, COLOR_GRAY, self.rect)
            # 废墟效果
            for i in range(5):
                exp_x = self.x + pygame.time.get_ticks() % GRID_SIZE // 5 * i
                exp_y = self.y + pygame.time.get_ticks() % GRID_SIZE // 5 * i
                pygame.draw.circle(screen, COLOR_EXPLOSION,
                                 (exp_x, exp_y), 5)

    def destroy(self):
        """摧毁基地"""
        self.alive = False

    def get_rect(self):
        """获取碰撞矩形"""
        return self.rect
