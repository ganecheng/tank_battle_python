"""
Bullet module - Handles projectile mechanics
子弹模块 - 处理投射物机制
"""
import pygame
from config import *


class Bullet:
    """子弹类"""

    def __init__(self, x, y, direction, owner, speed=PLAYER_BULLET_SPEED):
        """
        初始化子弹
        :param x: x 坐标
        :param y: y 坐标
        :param direction: 方向 (UP, RIGHT, DOWN, LEFT)
        :param owner: 所有者 ('player' 或 'enemy')
        :param speed: 子弹速度
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.owner = owner
        self.speed = speed
        self.size = BULLET_SIZE
        self.damage = BULLET_DAMAGE
        self.active = True

        # 创建矩形
        self.rect = pygame.Rect(x - self.size // 2, y - self.size // 2,
                               self.size, self.size)

    def update(self):
        """更新子弹位置"""
        if not self.active:
            return

        if self.direction == UP:
            self.y -= self.speed
        elif self.direction == DOWN:
            self.y += self.speed
        elif self.direction == LEFT:
            self.x -= self.speed
        elif self.direction == RIGHT:
            self.x += self.speed

        # 更新矩形
        self.rect.topleft = (self.x - self.size // 2, self.y - self.size // 2)

        # 检查是否出界
        if (self.x < 0 or self.x > SCREEN_WIDTH or
            self.y < 0 or self.y > SCREEN_HEIGHT):
            self.active = False

    def draw(self, screen):
        """绘制子弹"""
        if not self.active:
            return

        # 子弹颜色根据所有者不同
        if self.owner == 'player':
            color = COLOR_BULLET
        else:
            color = (255, 100, 100)  # 红色系子弹

        # 绘制子弹（圆形）
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size // 2)

        # 绘制子弹轨迹效果
        trail_length = 10
        if self.direction == UP:
            pygame.draw.line(screen, color,
                           (self.x, self.y),
                           (self.x, self.y + trail_length), 2)
        elif self.direction == DOWN:
            pygame.draw.line(screen, color,
                           (self.x, self.y),
                           (self.x, self.y - trail_length), 2)
        elif self.direction == LEFT:
            pygame.draw.line(screen, color,
                           (self.x, self.y),
                           (self.x + trail_length, self.y), 2)
        elif self.direction == RIGHT:
            pygame.draw.line(screen, color,
                           (self.x, self.y),
                           (self.x - trail_length, self.y), 2)

    def collide_with_rect(self, rect):
        """检查与矩形的碰撞"""
        if not self.active:
            return False
        return self.rect.colliderect(rect)

    def deactivate(self):
        """使子弹失效"""
        self.active = False
