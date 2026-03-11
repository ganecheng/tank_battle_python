"""
Effects module - Handles visual effects (explosions, etc.)
特效模块 - 处理视觉效果（爆炸等）
"""
import pygame
import random
import math
from config import *


class Explosion:
    """爆炸效果类"""

    def __init__(self, x, y, size='medium'):
        """
        初始化爆炸
        :param x: x 坐标
        :param y: y 坐标
        :param size: 爆炸大小 ('small', 'medium', 'large')
        """
        self.x = x
        self.y = y
        self.size = size
        self.frame = 0
        self.active = True

        # 根据大小设置参数
        if size == 'small':
            self.max_radius = 20
            self.duration = 15
            self.particle_count = 10
        elif size == 'medium':
            self.max_radius = 40
            self.duration = 25
            self.particle_count = 20
        else:  # large
            self.max_radius = 60
            self.duration = 40
            self.particle_count = 30

        # 生成粒子
        self.particles = self._create_particles()

    def _create_particles(self):
        """创建粒子"""
        particles = []
        for _ in range(self.particle_count):
            angle = random.random() * 2 * math.pi
            speed = random.random() * 3 + 1
            particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'radius': random.random() * 4 + 2,
                'color': self._get_explosion_color(),
                'life': self.duration
            })
        return particles

    def _get_explosion_color(self):
        """获取爆炸颜色"""
        colors = [COLOR_EXPLOSION, COLOR_YELLOW, COLOR_RED, (255, 200, 0)]
        return colors[int(self.frame * 2) % len(colors)]

    def update(self):
        """更新爆炸效果"""
        self.frame += 1
        if self.frame >= self.duration:
            self.active = False
            return

        # 更新粒子
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vx'] *= 0.95  # 阻尼
            particle['vy'] *= 0.95
            particle['life'] -= 1
            particle['radius'] *= 0.95

    def draw(self, screen):
        """绘制爆炸效果"""
        if not self.active:
            return

        # 绘制爆炸冲击波
        progress = self.frame / self.duration
        current_radius = self.max_radius * progress * (1 - progress) * 4

        if current_radius > 1:
            # 外层冲击波
            shock_color = (255, int(200 * (1 - progress)), int(100 * (1 - progress)))
            pygame.draw.circle(screen, shock_color,
                             (int(self.x), int(self.y)),
                             int(current_radius), 3)

            # 内层闪光
            flash_radius = current_radius * 0.7
            flash_surface = pygame.Surface((int(flash_radius * 2), int(flash_radius * 2)), pygame.SRCALPHA)
            alpha = int(200 * (1 - progress))
            pygame.draw.circle(flash_surface, (*COLOR_EXPLOSION, alpha),
                             (int(flash_radius), int(flash_radius)),
                             int(flash_radius))
            screen.blit(flash_surface,
                       (int(self.x - flash_radius), int(self.y - flash_radius)))

        # 绘制粒子
        for particle in self.particles:
            if particle['life'] > 0 and particle['radius'] > 0.5:
                alpha = int(255 * (particle['life'] / self.duration))
                color = particle['color']
                pygame.draw.circle(screen, color,
                                 (int(particle['x']), int(particle['y'])),
                                 int(particle['radius']))

    def get_rect(self):
        """获取爆炸范围矩形"""
        return pygame.Rect(
            self.x - self.max_radius,
            self.y - self.max_radius,
            self.max_radius * 2,
            self.max_radius * 2
        )


class Smoke:
    """烟雾效果类"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.duration = 30
        self.active = True
        self.particles = []

        # 创建烟雾粒子
        for _ in range(15):
            self.particles.append({
                'x': x + (random.random() - 0.5) * 20,
                'y': y + (random.random() - 0.5) * 20,
                'vx': (random.random() - 0.5) * 2,
                'vy': -abs(random.random() * 2) - 1,  # 向上飘
                'radius': random.random() * 10 + 5,
                'alpha': 200
            })

    def update(self):
        """更新烟雾"""
        self.frame += 1
        if self.frame >= self.duration:
            self.active = False
            return

        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['radius'] *= 1.05
            particle['alpha'] -= 8

    def draw(self, screen):
        """绘制烟雾"""
        if not self.active:
            return

        for particle in self.particles:
            if particle['alpha'] > 0:
                smoke_surface = pygame.Surface((int(particle['radius'] * 2),
                                               int(particle['radius'] * 2)),
                                              pygame.SRCALPHA)
                alpha = max(0, min(255, particle['alpha']))
                pygame.draw.circle(smoke_surface, (100, 100, 100, alpha),
                                 (int(particle['radius']), int(particle['radius'])),
                                 int(particle['radius']))
                screen.blit(smoke_surface,
                          (int(particle['x'] - particle['radius']),
                           int(particle['y'] - particle['radius'])))


class MuzzleFlash:
    """枪口闪光效果"""

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.frame = 0
        self.duration = 5
        self.active = True

    def update(self):
        """更新闪光"""
        self.frame += 1
        if self.frame >= self.duration:
            self.active = False

    def draw(self, screen):
        """绘制枪口闪光"""
        if not self.active:
            return

        progress = self.frame / self.duration
        size = 15 * (1 - progress)

        # 根据方向确定位置
        if self.direction == UP:
            points = [
                (self.x, self.y - size),
                (self.x - size * 0.7, self.y),
                (self.x, self.y - size * 0.5),
                (self.x + size * 0.7, self.y)
            ]
        elif self.direction == DOWN:
            points = [
                (self.x, self.y + size),
                (self.x - size * 0.7, self.y),
                (self.x, self.y + size * 0.5),
                (self.x + size * 0.7, self.y)
            ]
        elif self.direction == LEFT:
            points = [
                (self.x - size, self.y),
                (self.x, self.y - size * 0.7),
                (self.x - size * 0.5, self.y),
                (self.x, self.y + size * 0.7)
            ]
        else:  # RIGHT
            points = [
                (self.x + size, self.y),
                (self.x, self.y - size * 0.7),
                (self.x + size * 0.5, self.y),
                (self.x, self.y + size * 0.7)
            ]

        # 绘制闪光
        pygame.draw.polygon(screen, COLOR_YELLOW, points)
        pygame.draw.polygon(screen, COLOR_WHITE, points, 2)
