"""
Tank module - Handles tank mechanics
坦克模块 - 处理坦克机制
"""
import pygame
import math
from config import *


class Tank:
    """坦克基类"""

    def __init__(self, x, y, color, speed, health):
        """
        初始化坦克
        :param x: x 坐标
        :param y: y 坐标
        :param color: 坦克颜色
        :param speed: 移动速度
        :param health: 生命值
        """
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.health = health
        self.max_health = health
        self.direction = UP  # 初始方向向上
        self.width = GRID_SIZE - 4
        self.height = GRID_SIZE - 4
        self.active = True
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 30  # 射击冷却时间（帧数）
        self.moving = False
        self.animation_frame = 0

        # 创建矩形
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def move(self, dx, dy, obstacles=None):
        """
        移动坦克
        :param dx: x 方向增量
        :param dy: y 方向增量
        :param obstacles: 障碍物列表
        :return: 是否成功移动
        """
        if not self.active:
            return False

        self.moving = True
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # 保存旧位置
        old_x, old_y = self.x, self.y

        # 更新位置
        self.x = new_x
        self.y = new_y
        self.rect.topleft = (self.x, self.y)

        # 边界检查
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
        if self.y + self.height > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.height

        self.rect.topleft = (self.x, self.y)

        # 障碍物碰撞检查
        if obstacles:
            for obstacle in obstacles:
                if self.rect.colliderect(obstacle.get_rect()):
                    self.x = old_x
                    self.y = old_y
                    self.rect.topleft = (self.x, self.y)
                    return False

        self.update_direction(dx, dy)
        return True

    def update_direction(self, dx, dy):
        """根据移动方向更新坦克朝向"""
        if dx > 0:
            self.direction = RIGHT
        elif dx < 0:
            self.direction = LEFT
        elif dy > 0:
            self.direction = DOWN
        elif dy < 0:
            self.direction = UP

    def shoot(self):
        """
        射击
        :return: 如果成功射击返回 True，否则返回 False
        """
        if self.shoot_cooldown > 0 or not self.active:
            return False

        self.shoot_cooldown = self.shoot_cooldown_max

        # 计算子弹发射位置
        bullet_x = self.x + self.width // 2
        bullet_y = self.y + self.height // 2

        # 根据方向调整子弹位置到坦克边缘
        if self.direction == UP:
            bullet_y = self.y - 5
        elif self.direction == DOWN:
            bullet_y = self.y + self.height + 5
        elif self.direction == LEFT:
            bullet_x = self.x - 5
        elif self.direction == RIGHT:
            bullet_x = self.x + self.width + 5

        from bullet import Bullet
        return Bullet(bullet_x, bullet_y, self.direction,
                     'player' if isinstance(self, PlayerTank) else 'enemy')

    def take_damage(self, damage):
        """
        受到伤害
        :param damage: 伤害值
        """
        self.health -= damage
        if self.health <= 0:
            self.active = False

    def update(self):
        """更新坦克状态"""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        self.moving = False
        self.animation_frame += 1

    def draw(self, screen):
        """绘制坦克"""
        if not self.active:
            return

        # 更新动画帧
        self.animation_frame += 0.15

        # 绘制坦克主体
        self._draw_tank_body(screen)

        # 绘制炮管
        self._draw_barrel(screen)

        # 绘制履带动画
        self._draw_tracks(screen)

        # 绘制生命值条（如果有伤害）
        if self.health < self.max_health:
            self._draw_health_bar(screen)

    def _draw_tank_body(self, screen):
        """绘制坦克主体"""
        # 坦克主体矩形
        body_rect = pygame.Rect(
            self.x + 4,
            self.y + 4,
            self.width - 8,
            self.height - 8
        )

        # 绘制主体（带渐变效果）
        pygame.draw.rect(screen, self.color, body_rect, border_radius=4)

        # 绘制高光
        highlight_rect = pygame.Rect(
            self.x + 6,
            self.y + 6,
            self.width - 12,
            self.height - 12
        )
        highlight_color = tuple(min(c + 40, 255) for c in self.color)
        pygame.draw.rect(screen, highlight_color, highlight_rect, border_radius=3)

    def _draw_barrel(self, screen):
        """绘制炮管"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        barrel_length = 20
        barrel_width = 8

        # 根据方向绘制炮管
        if self.direction == UP:
            barrel_rect = pygame.Rect(center_x - barrel_width // 2,
                                      center_y - barrel_length,
                                      barrel_width, barrel_length)
        elif self.direction == DOWN:
            barrel_rect = pygame.Rect(center_x - barrel_width // 2,
                                      center_y,
                                      barrel_width, barrel_length)
        elif self.direction == LEFT:
            barrel_rect = pygame.Rect(center_x - barrel_length,
                                      center_y - barrel_width // 2,
                                      barrel_length, barrel_width)
        else:  # RIGHT
            barrel_rect = pygame.Rect(center_x,
                                      center_y - barrel_width // 2,
                                      barrel_length, barrel_width)

        # 绘制炮管
        pygame.draw.rect(screen, COLOR_GRAY, barrel_rect, border_radius=3)

        # 炮管口
        if self.direction == UP:
            pygame.draw.circle(screen, COLOR_DARK_STEEL,
                             (center_x, center_y - barrel_length), 5)
        elif self.direction == DOWN:
            pygame.draw.circle(screen, COLOR_DARK_STEEL,
                             (center_x, center_y + barrel_length), 5)
        elif self.direction == LEFT:
            pygame.draw.circle(screen, COLOR_DARK_STEEL,
                             (center_x - barrel_length, center_y), 5)
        else:
            pygame.draw.circle(screen, COLOR_DARK_STEEL,
                             (center_x + barrel_length, center_y), 5)

    def _draw_tracks(self, screen):
        """绘制履带（带动画效果）"""
        track_width = 6
        track_color = COLOR_DARK_BROWN

        # 履带动画偏移
        track_offset = 0
        if self.moving:
            track_offset = math.sin(self.animation_frame) * 3

        # 左履带
        left_track = pygame.Rect(
            self.x,
            self.y + track_offset,
            track_width,
            self.height
        )
        pygame.draw.rect(screen, track_color, left_track, border_radius=2)

        # 右履带
        right_track = pygame.Rect(
            self.x + self.width - track_width,
            self.y - track_offset,
            track_width,
            self.height
        )
        pygame.draw.rect(screen, track_color, right_track, border_radius=2)

        # 履带细节
        for i in range(5):
            y_pos = self.y + i * (self.height // 5) + track_offset
            pygame.draw.line(screen, COLOR_BROWN,
                           (self.x + 1, y_pos),
                           (self.x + track_width - 1, y_pos), 2)

            y_pos = self.y + i * (self.height // 5) - track_offset
            pygame.draw.line(screen, COLOR_BROWN,
                           (self.x + self.width - track_width + 1, y_pos),
                           (self.x + self.width - 1, y_pos), 2)

    def _draw_health_bar(self, screen):
        """绘制生命值条"""
        bar_width = self.width
        bar_height = 4
        bar_x = self.x
        bar_y = self.y - 8

        # 背景
        pygame.draw.rect(screen, COLOR_RED,
                        (bar_x, bar_y, bar_width, bar_height))

        # 当前生命值
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, COLOR_GREEN,
                        (bar_x, bar_y, health_width, bar_height))

    def get_rect(self):
        """获取碰撞矩形"""
        return self.rect.copy()

    def destroy(self):
        """销毁坦克"""
        self.active = False


class PlayerTank(Tank):
    """玩家坦克类"""

    def __init__(self, x, y):
        super().__init__(x, y, COLOR_TANK_PLAYER, PLAYER_SPEED, PLAYER_HEALTH)
        self.bullet_speed = PLAYER_BULLET_SPEED
        self.max_bullets = PLAYER_MAX_BULLETS
        self.invincible = False
        self.invincible_timer = 0
        self.score = 0

    def update(self):
        """更新玩家坦克状态"""
        super().update()
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def set_invincible(self, duration=180):  # 3 秒 @ 60fps
        """设置无敌状态"""
        self.invincible = True
        self.invincible_timer = duration

    def draw(self, screen):
        """绘制玩家坦克"""
        if not self.active:
            return

        # 无敌状态闪烁效果
        if self.invincible and int(self.animation_frame * 2) % 2 == 0:
            # 闪烁时不绘制
            return

        super().draw(screen)

        # 绘制方向指示器
        self._draw_direction_indicator(screen)

    def _draw_direction_indicator(self, screen):
        """绘制方向指示器"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2

        if self.direction == UP:
            points = [(center_x, self.y - 5),
                     (center_x - 5, self.y + 5),
                     (center_x + 5, self.y + 5)]
        elif self.direction == DOWN:
            points = [(center_x, self.y + self.height + 5),
                     (center_x - 5, self.y + self.height - 5),
                     (center_x + 5, self.y + self.height - 5)]
        elif self.direction == LEFT:
            points = [(self.x - 5, center_y),
                     (self.x + 5, center_y - 5),
                     (self.x + 5, center_y + 5)]
        else:
            points = [(self.x + self.width + 5, center_y),
                     (self.x + self.width - 5, center_y - 5),
                     (self.x + self.width - 5, center_y + 5)]

        pygame.draw.polygon(screen, COLOR_YELLOW, points)


class EnemyTank(Tank):
    """敌方坦克类"""

    def __init__(self, x, y, tank_type='normal'):
        """
        初始化敌方坦克
        :param x: x 坐标
        :param y: y 坐标
        :param tank_type: 坦克类型 ('normal', 'fast', 'heavy')
        """
        self.tank_type = tank_type

        # 根据类型设置属性
        if tank_type == 'fast':
            color = (255, 100, 100)
            speed = ENEMY_SPEED * 1.5
            health = 1
        elif tank_type == 'heavy':
            color = (139, 0, 0)
            speed = ENEMY_SPEED * 0.7
            health = 3
        else:  # normal
            color = COLOR_TANK_ENEMY
            speed = ENEMY_SPEED
            health = ENEMY_HEALTH

        super().__init__(x, y, color, speed, health)
        self.move_timer = 0
        self.move_duration = 60
        self.change_direction_timer = 0

    def ai_update(self, obstacles, player, base):
        """
        AI 更新逻辑
        :param obstacles: 障碍物列表
        :param player: 玩家坦克
        :param base: 基地
        """
        if not self.active:
            return

        self.change_direction_timer -= 1

        # 改变方向
        if self.change_direction_timer <= 0:
            self._change_direction(player, base)
            self.change_direction_timer = 30 + int(self.animation_frame % 60)

        # 移动
        if self.direction == UP:
            self.move(0, -1, obstacles)
        elif self.direction == DOWN:
            self.move(0, 1, obstacles)
        elif self.direction == LEFT:
            self.move(-1, 0, obstacles)
        elif self.direction == RIGHT:
            self.move(1, 0, obstacles)

        # 如果无法移动，改变方向
        if not self.moving:
            self._change_direction(player, base)

        # 尝试射击
        if self._can_shoot_at_target(player, base):
            return self.shoot()

        return None

    def _change_direction(self, player, base):
        """改变移动方向"""
        # 有一定概率朝向基地或玩家
        if base and base.alive and int(self.animation_frame) % 3 == 0:
            # 朝向基地
            dx = base.x - self.x
            dy = base.y - self.y
        else:
            # 朝向玩家
            dx = player.x - self.x
            dy = player.y - self.y

        # 选择主要方向
        if abs(dx) > abs(dy):
            self.direction = RIGHT if dx > 0 else LEFT
        else:
            self.direction = DOWN if dy > 0 else UP

        # 添加一些随机性
        if int(self.animation_frame) % 5 == 0:
            directions = [UP, DOWN, LEFT, RIGHT]
            self.direction = directions[int(self.animation_frame) % 4]

    def _can_shoot_at_target(self, player, base):
        """检查是否可以射击目标"""
        # 检查与玩家或基地是否在同一行或列
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2

        player_center_x = player.x + player.width // 2
        player_center_y = player.y + player.height // 2

        # 检查是否与玩家对齐
        if self.direction == UP or self.direction == DOWN:
            if abs(center_x - player_center_x) < GRID_SIZE:
                if self.direction == UP and player_center_y < self.y:
                    return True
                if self.direction == DOWN and player_center_y > self.y:
                    return True
        elif self.direction == LEFT or self.direction == RIGHT:
            if abs(center_y - player_center_y) < GRID_SIZE:
                if self.direction == LEFT and player_center_x < self.x:
                    return True
                if self.direction == RIGHT and player_center_x > self.x:
                    return True

        # 检查是否与基地对齐
        if base and base.alive:
            base_center_x = base.x + base.width // 2
            base_center_y = base.y + base.height // 2

            if self.direction == UP or self.direction == DOWN:
                if abs(center_x - base_center_x) < GRID_SIZE:
                    if self.direction == UP and base_center_y < self.y:
                        return True
                    if self.direction == DOWN and base_center_y > self.y:
                        return True

        return False

    def draw(self, screen):
        """绘制敌方坦克"""
        if not self.active:
            return

        super().draw(screen)

        # 绘制坦克类型标识
        if self.tank_type == 'heavy':
            # 重型坦克有红色标记
            pygame.draw.circle(screen, COLOR_RED,
                             (self.x + self.width // 2, self.y + self.height // 2), 5)
        elif self.tank_type == 'fast':
            # 快速坦克有黄色标记
            pygame.draw.circle(screen, COLOR_YELLOW,
                             (self.x + self.width // 2, self.y + self.height // 2), 5)
