"""
Map module - Handles level design and terrain
地图模块 - 处理关卡设计和地形
"""
import pygame
import json
import os
from config import *


class Obstacle:
    """障碍物基类"""

    def __init__(self, x, y, width, height, obstacle_type='brick'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.obstacle_type = obstacle_type
        self.rect = pygame.Rect(x, y, width, height)
        self.health = 1 if obstacle_type == 'brick' else 999
        self.active = True

    def take_damage(self, damage):
        """受到伤害"""
        if self.obstacle_type == 'brick':
            self.health -= damage
            if self.health <= 0:
                self.active = False
        # 石头和基地不受子弹伤害
        return not self.active

    def get_rect(self):
        """获取碰撞矩形"""
        return self.rect.copy()

    def draw(self, screen):
        """绘制障碍物"""
        if not self.active:
            return
        self._draw_specific(screen)

    def _draw_specific(self, screen):
        """绘制具体类型的障碍物"""
        if self.obstacle_type == 'brick':
            self._draw_brick(screen)
        elif self.obstacle_type == 'stone':
            self._draw_stone(screen)
        elif self.obstacle_type == 'water':
            self._draw_water(screen)
        elif self.obstacle_type == 'grass':
            self._draw_grass(screen)
        elif self.obstacle_type == 'base':
            self._draw_base(screen)

    def _draw_brick(self, screen):
        """绘制砖墙"""
        # 砖块背景
        pygame.draw.rect(screen, COLOR_BRICK, self.rect)

        # 绘制砖块纹理
        brick_height = 10
        brick_width = 20
        mortar_color = (100, 50, 50)

        for row in range(self.height // brick_height):
            offset = (row % 2) * (brick_width // 2)
            for col in range(self.width // brick_width + 1):
                x = self.x + col * brick_width + offset
                y = self.y + row * brick_height

                # 确保不超出边界
                draw_width = min(brick_width, self.x + self.width - x)
                draw_height = min(brick_height, self.y + self.height - y)

                if draw_width > 0 and draw_height > 0:
                    brick_rect = pygame.Rect(x, y, draw_width, draw_height)
                    pygame.draw.rect(screen, COLOR_DARK_BROWN, brick_rect, 1)

                    # 砖块高光
                    highlight_rect = pygame.Rect(x + 1, y + 1,
                                                 draw_width - 2, draw_height - 2)
                    pygame.draw.rect(screen, COLOR_LIGHT_BROWN, highlight_rect)

    def _draw_stone(self, screen):
        """绘制石头墙（钢铁）"""
        # 钢铁背景
        pygame.draw.rect(screen, COLOR_STEEL, self.rect)

        # 绘制钢铁纹理
        steel_size = 15
        for row in range(self.height // steel_size + 1):
            for col in range(self.width // steel_size + 1):
                x = self.x + col * steel_size
                y = self.y + row * steel_size

                steel_rect = pygame.Rect(x, y, steel_size, steel_size)
                pygame.draw.rect(screen, COLOR_DARK_STEEL, steel_rect, 2)

                # 铆钉效果
                center_x = x + steel_size // 2
                center_y = y + steel_size // 2
                pygame.draw.circle(screen, COLOR_GRAY, (center_x, center_y), 3)

    def _draw_water(self, screen):
        """绘制水域"""
        # 水背景
        pygame.draw.rect(screen, COLOR_WATER, self.rect)

        # 水波动画
        time_offset = pygame.time.get_ticks() / 500
        wave_count = 5
        for i in range(wave_count):
            wave_y = self.y + (i + 1) * (self.height // (wave_count + 1))
            wave_offset = math.sin(time_offset + i) * 5

            start_x = self.x + wave_offset
            end_x = self.x + self.width - wave_offset

            pygame.draw.line(screen, (100, 200, 255),
                           (start_x, wave_y),
                           (end_x, wave_y), 2)

    def _draw_grass(self, screen):
        """绘制草地"""
        # 草地背景
        pygame.draw.rect(screen, COLOR_DARK_GREEN, self.rect)

        # 草的细节
        grass_count = 10
        for i in range(grass_count):
            grass_x = self.x + (i * self.width // grass_count) + 5
            grass_height = 8 + int(abs(math.sin(pygame.time.get_ticks() / 500 + i)) * 5)
            pygame.draw.line(screen, COLOR_GREEN,
                           (grass_x, self.y + self.height),
                           (grass_x - 3, self.y + self.height - grass_height), 2)
            pygame.draw.line(screen, COLOR_GREEN,
                           (grass_x + 5, self.y + self.height),
                           (grass_x + 8, self.y + self.height - grass_height + 2), 2)

    def _draw_base(self, screen):
        """绘制基地"""
        # 基地背景
        pygame.draw.rect(screen, COLOR_DARK_STEEL, self.rect)

        # 鹰的图案
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2

        # 外框
        pygame.draw.rect(screen, COLOR_STEEL, self.rect, 3)

        # 内部装饰
        pygame.draw.circle(screen, COLOR_YELLOW, (center_x, center_y), 12)
        pygame.draw.circle(screen, COLOR_RED, (center_x, center_y), 8)
        pygame.draw.circle(screen, COLOR_YELLOW, (center_x, center_y), 4)


class Map:
    """地图类"""

    def __init__(self, level=1):
        self.level = level
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.obstacles = []
        self.water_obstacles = []
        self.grass_obstacles = []
        self.grid_size = GRID_SIZE
        self.base = None
        self.spawn_points = {'player': None, 'enemies': []}

        # 加载或生成地图
        self._generate_map()

    def _generate_map(self):
        """生成地图"""
        # 这里直接生成地图，后续可以从文件加载
        self._create_level_1()

    def _create_level_1(self):
        """创建第一关地图"""
        # 基地位置（底部中央）
        base_x = SCREEN_WIDTH // 2 - GRID_SIZE // 2
        base_y = SCREEN_HEIGHT - GRID_SIZE * 2
        self.base = Obstacle(base_x, base_y, GRID_SIZE, GRID_SIZE, 'base')

        # 基地周围的砖墙保护
        protection_positions = [
            (base_x - GRID_SIZE, base_y),
            (base_x + GRID_SIZE, base_y),
            (base_x - GRID_SIZE, base_y - GRID_SIZE),
            (base_x, base_y - GRID_SIZE),
            (base_x + GRID_SIZE, base_y - GRID_SIZE),
        ]

        for pos in protection_positions:
            self.obstacles.append(Obstacle(pos[0], pos[1], GRID_SIZE, GRID_SIZE, 'brick'))

        # 创建地图布局（0=空，1=砖墙，2=石头，3=水，4=草）
        level_layout = [
            # 16 列 x 12 行 (假设 GRID_SIZE=40, 1024x768)
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0],
            [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0],
            [0, 1, 1, 0, 0, 2, 2, 0, 0, 2, 2, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 2, 2, 0, 0, 2, 2, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 3, 3, 0, 0, 0, 0, 3, 3, 0, 1, 1, 0],
            [0, 1, 1, 0, 3, 3, 0, 0, 0, 0, 3, 3, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 2, 2, 1, 1, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 4, 4, 0, 1, 1, 0, 0, 1, 1, 0, 4, 4, 0, 0],
            [0, 0, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 0, 0],
        ]

        # 根据布局创建障碍物
        for row_idx, row in enumerate(level_layout):
            for col_idx, cell in enumerate(row):
                x = col_idx * GRID_SIZE
                y = row_idx * GRID_SIZE + GRID_SIZE * 2  # 向下偏移，给敌人生成位置留空间

                if cell == 1:
                    self.obstacles.append(Obstacle(x, y, GRID_SIZE, GRID_SIZE, 'brick'))
                elif cell == 2:
                    self.obstacles.append(Obstacle(x, y, GRID_SIZE, GRID_SIZE, 'stone'))
                elif cell == 3:
                    water = Obstacle(x, y, GRID_SIZE, GRID_SIZE, 'water')
                    self.water_obstacles.append(water)
                    self.obstacles.append(water)
                elif cell == 4:
                    grass = Obstacle(x, y, GRID_SIZE, GRID_SIZE, 'grass')
                    self.grass_obstacles.append(grass)
                    self.obstacles.append(grass)

        # 设置玩家出生点（基地左侧）
        self.spawn_points['player'] = (base_x - GRID_SIZE * 2, base_y)

        # 设置敌人出生点（顶部三个位置）
        self.spawn_points['enemies'] = [
            (GRID_SIZE, GRID_SIZE),  # 左上
            (SCREEN_WIDTH // 2 - GRID_SIZE // 2, GRID_SIZE),  # 中上
            (SCREEN_WIDTH - GRID_SIZE * 2, GRID_SIZE),  # 右上
        ]

    def get_all_obstacles(self):
        """获取所有障碍物（用于碰撞检测）"""
        return self.obstacles + [self.base] if self.base and self.base.active else self.obstacles

    def get_solid_obstacles(self):
        """获取固体障碍物（阻挡移动和子弹）"""
        solid = [o for o in self.obstacles if o.obstacle_type in ['brick', 'stone', 'base']]
        if self.base and self.base.active:
            solid.append(self.base)
        return solid

    def get_drawable_obstacles(self):
        """获取需要绘制的障碍物"""
        return self.obstacles

    def get_grass_obstacles(self):
        """获取草地障碍物（最后绘制，遮挡坦克）"""
        return self.grass_obstacles

    def draw(self, screen):
        """绘制地图"""
        # 绘制背景
        screen.fill(COLOR_BLACK)

        # 绘制地面网格（微弱效果）
        self._draw_grid(screen)

        # 绘制所有障碍物
        for obstacle in self.obstacles:
            if obstacle.active:
                obstacle.draw(screen)

        # 绘制基地
        if self.base and self.base.active:
            self.base.draw(screen)

    def _draw_grid(self, screen):
        """绘制网格线（装饰效果）"""
        grid_color = (30, 30, 30)
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y))

    def destroy_base(self):
        """摧毁基地"""
        if self.base:
            self.base.active = False
            self.base.health = 0

    def is_base_alive(self):
        """检查基地是否存活"""
        return self.base is not None and self.base.active and self.base.health > 0


# 导入 math 模块（在 Obstacle 类中使用）
import math
