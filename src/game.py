"""
Tank Battle Game - Main Game Module
坦克大战 - 主游戏模块
"""
import pygame
import sys
import random
import math

from config import *
from tank import PlayerTank, EnemyTank
from bullet import Bullet
from map import Map, Obstacle
from base import Base
from effects import Explosion, Smoke, MuzzleFlash


class Game:
    """游戏主类"""

    def __init__(self):
        """初始化游戏"""
        pygame.init()
        pygame.mixer.init()

        # 创建窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tank Battle - 坦克大战")

        # 时钟
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.state = STATE_MENU
        self.level = 1
        self.score = 0
        self.lives = 3

        # 游戏对象
        self.player = None
        self.enemies = []
        self.bullets = []
        self.game_map = None
        self.base = None

        # 特效
        self.explosions = []
        self.smokes = []
        self.muzzle_flashes = []

        # 游戏变量
        self.enemies_spawned = 0
        self.enemies_to_spawn = MAX_ENEMIES_PER_LEVEL
        self.last_spawn_time = 0
        self.player_bullets = []
        self.enemy_bullets = []

        # 字体
        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

        # 菜单选项
        self.menu_options = ["START GAME", "OPTIONS", "EXIT"]
        self.menu_selected = 0

    def run(self):
        """运行游戏主循环"""
        running = True
        while running:
            self.clock.tick(FPS)
            running = self._handle_events()

            if self.state == STATE_MENU:
                self._update_menu()
                self._draw_menu()
            elif self.state == STATE_PLAYING:
                self._update_game()
                self._draw_game()
            elif self.state == STATE_PAUSED:
                self._draw_pause()
            elif self.state == STATE_GAME_OVER:
                self._draw_game_over()
            elif self.state == STATE_VICTORY:
                self._draw_victory()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == STATE_MENU:
                    self._handle_menu_input(event.key)
                elif self.state == STATE_PLAYING:
                    self._handle_game_input(event.key)
                elif self.state in [STATE_GAME_OVER, STATE_VICTORY]:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self._reset_game()
                        self.state = STATE_PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.state = STATE_MENU

        return True

    def _handle_menu_input(self, key):
        """处理菜单输入"""
        if key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
        elif key == pygame.K_SPACE or key == pygame.K_RETURN:
            if self.menu_selected == 0:
                self._start_game()
            elif self.menu_selected == 2:
                return False
        return True

    def _handle_game_input(self, key):
        """处理游戏输入"""
        if key in [pygame.K_ESCAPE, pygame.K_p]:
            if self.state == STATE_PLAYING:
                self.state = STATE_PAUSED
            elif self.state == STATE_PAUSED:
                self.state = STATE_PLAYING
        elif key == pygame.K_SPACE:
            # 玩家射击
            self.player_shoot()

    def _update_menu(self):
        """更新菜单状态"""
        pass

    def _start_game(self):
        """开始新游戏"""
        self._reset_game()
        self.state = STATE_PLAYING

    def _reset_game(self):
        """重置游戏"""
        self.level = 1
        self.score = 0
        self.lives = 3
        self._start_level()

    def _start_level(self):
        """开始新关卡"""
        # 创建地图
        self.game_map = Map(self.level)

        # 创建基地
        base_pos = self.game_map.base
        self.base = Base(base_pos.x, base_pos.y)

        # 创建玩家坦克
        player_pos = self.game_map.spawn_points['player']
        self.player = PlayerTank(player_pos[0], player_pos[1])

        # 重置敌人生成
        self.enemies = []
        self.enemies_spawned = 0
        self.enemies_to_spawn = MAX_ENEMIES_PER_LEVEL
        self.last_spawn_time = pygame.time.get_ticks()

        # 清空子弹和特效
        self.bullets = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.explosions = []
        self.smokes = []
        self.muzzle_flashes = []

    def _spawn_enemy(self):
        """生成敌人"""
        if self.enemies_spawned >= self.enemies_to_spawn:
            return

        if len(self.enemies) >= ENEMY_MAX_COUNT:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time < ENEMY_SPAWN_INTERVAL:
            return

        # 获取生成点
        spawn_points = self.game_map.spawn_points['enemies']
        spawn_point = random.choice(spawn_points)

        # 检查生成点是否被占用
        for enemy in self.enemies:
            if abs(enemy.x - spawn_point[0]) < GRID_SIZE and abs(enemy.y - spawn_point[1]) < GRID_SIZE:
                return

        # 随机选择坦克类型
        tank_type = random.choice(['normal', 'normal', 'normal', 'fast', 'heavy'])

        # 创建敌人
        enemy = EnemyTank(spawn_point[0], spawn_point[1], tank_type)
        self.enemies.append(enemy)
        self.enemies_spawned += 1
        self.last_spawn_time = current_time

        # 生成特效
        self.explosions.append(Explosion(spawn_point[0] + GRID_SIZE // 2,
                                        spawn_point[1] + GRID_SIZE // 2,
                                        'medium'))

    def _update_game(self):
        """更新游戏状态"""
        # 生成敌人
        self._spawn_enemy()

        # 更新玩家
        if self.player and self.player.active:
            self._update_player()

        # 更新敌人
        self._update_enemies()

        # 更新子弹
        self._update_bullets()

        # 更新特效
        self._update_effects()

        # 检查碰撞
        self._check_collisions()

        # 检查游戏状态
        self._check_game_state()

    def _update_player(self):
        """更新玩家坦克"""
        keys = pygame.key.get_pressed()

        dx, dy = 0, 0
        moving = False

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
            moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            moving = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            moving = True

        # 移动玩家
        if moving:
            obstacles = self.game_map.get_solid_obstacles()
            # 添加敌人作为障碍物
            for enemy in self.enemies:
                if enemy.active:
                    obstacles.append(enemy)
            self.player.move(dx, dy, obstacles)

        # 更新玩家状态
        self.player.update()

    def _update_enemies(self):
        """更新敌方坦克"""
        obstacles = self.game_map.get_solid_obstacles()

        for enemy in self.enemies:
            if not enemy.active:
                continue

            # AI 更新
            bullet = enemy.ai_update(obstacles, self.player, self.base)

            if bullet:
                bullet.speed = ENEMY_BULLET_SPEED
                self.enemy_bullets.append(bullet)

            enemy.update()

    def _update_bullets(self):
        """更新子弹"""
        # 更新玩家子弹
        for bullet in self.player_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.player_bullets.remove(bullet)

        # 更新敌人子弹
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.enemy_bullets.remove(bullet)

    def _update_effects(self):
        """更新特效"""
        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.active:
                self.explosions.remove(explosion)

        for smoke in self.smokes[:]:
            smoke.update()
            if not smoke.active:
                self.smokes.remove(smoke)

        for flash in self.muzzle_flashes[:]:
            flash.update()
            if not flash.active:
                self.muzzle_flashes.remove(flash)

    def _check_collisions(self):
        """检查碰撞"""
        # 玩家子弹碰撞
        for bullet in self.player_bullets[:]:
            if not bullet.active:
                continue

            # 击中敌人
            for enemy in self.enemies[:]:
                if enemy.active and bullet.collide_with_rect(enemy.get_rect()):
                    bullet.deactivate()
                    enemy.take_damage(bullet.damage)
                    if not enemy.active:
                        self.score += 100
                        self.explosions.append(Explosion(
                            enemy.x + enemy.width // 2,
                            enemy.y + enemy.height // 2,
                            'large'
                        ))
                        self.smokes.append(Smoke(
                            enemy.x + enemy.width // 2,
                            enemy.y + enemy.height // 2
                        ))
                    break

            # 击中障碍物
            if bullet.active:
                for obstacle in self.game_map.get_solid_obstacles():
                    if obstacle.active and bullet.collide_with_rect(obstacle.get_rect()):
                        bullet.deactivate()
                        obstacle.take_damage(bullet.damage)
                        self.explosions.append(Explosion(
                            bullet.x, bullet.y, 'small'
                        ))
                        break

            # 击中基地
            if bullet.active and self.base.alive:
                if bullet.collide_with_rect(self.base.get_rect()):
                    bullet.deactivate()
                    self.base.destroy()
                    self.game_map.destroy_base()
                    self.explosions.append(Explosion(
                        self.base.x + self.base.width // 2,
                        self.base.y + self.base.height // 2,
                        'large'
                    ))

        # 敌人子弹碰撞
        for bullet in self.enemy_bullets[:]:
            if not bullet.active:
                continue

            # 击中玩家
            if self.player and self.player.active and not self.player.invincible:
                if bullet.collide_with_rect(self.player.get_rect()):
                    bullet.deactivate()
                    self.player.take_damage(bullet.damage)
                    if not self.player.active:
                        self.lives -= 1
                        self.explosions.append(Explosion(
                            self.player.x + self.player.width // 2,
                            self.player.y + self.player.height // 2,
                            'large'
                        ))
                        if self.lives > 0:
                            # 重生玩家
                            player_pos = self.game_map.spawn_points['player']
                            self.player = PlayerTank(player_pos[0], player_pos[1])
                            self.player.set_invincible(180)  # 3 秒无敌
                    else:
                        self.player.set_invincible(120)  # 2 秒无敌
                    continue

            # 击中障碍物
            if bullet.active:
                for obstacle in self.game_map.get_solid_obstacles():
                    if obstacle.active and bullet.collide_with_rect(obstacle.get_rect()):
                        bullet.deactivate()
                        obstacle.take_damage(bullet.damage)
                        self.explosions.append(Explosion(
                            bullet.x, bullet.y, 'small'
                        ))
                        break

            # 击中基地
            if bullet.active and self.base.alive:
                if bullet.collide_with_rect(self.base.get_rect()):
                    bullet.deactivate()
                    self.base.destroy()
                    self.game_map.destroy_base()
                    self.explosions.append(Explosion(
                        self.base.x + self.base.width // 2,
                        self.base.y + self.base.height // 2,
                        'large'
                    ))

    def _check_game_state(self):
        """检查游戏状态"""
        # 检查基地是否被摧毁
        if not self.base.alive:
            self.state = STATE_GAME_OVER
            return

        # 检查玩家是否还有生命
        if self.lives <= 0 and (not self.player or not self.player.active):
            self.state = STATE_GAME_OVER
            return

        # 检查是否所有敌人都被消灭
        active_enemies = [e for e in self.enemies if e.active]
        if not active_enemies and self.enemies_spawned >= self.enemies_to_spawn:
            # 关卡完成
            self.level += 1
            if self.level > 5:  # 假设 5 关通关
                self.state = STATE_VICTORY
            else:
                self._start_level()

    def _draw_menu(self):
        """绘制菜单"""
        # 背景
        self.screen.fill(COLOR_BLACK)

        # 标题
        title = self.font_large.render("TANK BATTLE", True, COLOR_YELLOW)
        title_cn = self.font_medium.render("坦克大战", True, COLOR_RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        title_cn_rect = title_cn.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50))
        self.screen.blit(title, title_rect)
        self.screen.blit(title_cn, title_cn_rect)

        # 菜单选项
        for i, option in enumerate(self.menu_options):
            color = COLOR_YELLOW if i == self.menu_selected else COLOR_WHITE
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2,
                                             SCREEN_HEIGHT // 2 + i * 60))
            self.screen.blit(text, text_rect)

        # 版权信息
        copyright_text = self.font_small.render("Press SPACE to start", True, COLOR_GRAY)
        copyright_rect = copyright_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                         SCREEN_HEIGHT - 50))
        self.screen.blit(copyright_text, copyright_rect)

    def _draw_game(self):
        """绘制游戏画面"""
        # 绘制地图
        self.game_map.draw(self.screen)

        # 绘制基地
        if self.base:
            self.base.draw(self.screen)

        # 绘制玩家
        if self.player and self.player.active:
            self.player.draw(self.screen)

        # 绘制敌人
        for enemy in self.enemies:
            if enemy.active:
                enemy.draw(self.screen)

        # 绘制子弹
        for bullet in self.player_bullets:
            bullet.draw(self.screen)
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)

        # 绘制特效（在草地之前）
        for explosion in self.explosions:
            explosion.draw(self.screen)
        for smoke in self.smokes:
            smoke.draw(self.screen)
        for flash in self.muzzle_flashes:
            flash.draw(self.screen)

        # 绘制草地（遮挡坦克）
        for grass in self.game_map.get_grass_obstacles():
            if grass.active:
                grass.draw(self.screen)

        # 绘制 UI
        self._draw_ui()

    def _draw_ui(self):
        """绘制 UI"""
        # 分数
        score_text = self.font_small.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (20, 20))

        # 生命
        lives_text = self.font_small.render(f"LIVES: {self.lives}", True, COLOR_WHITE)
        self.screen.blit(lives_text, (20, 60))

        # 关卡
        level_text = self.font_small.render(f"LEVEL: {self.level}", True, COLOR_WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - 200, 20))

        # 剩余敌人
        remaining = self.enemies_to_spawn - self.enemies_spawned + len([e for e in self.enemies if e.active])
        enemy_text = self.font_small.render(f"ENEMIES: {remaining}", True, COLOR_RED)
        self.screen.blit(enemy_text, (SCREEN_WIDTH - 200, 60))

    def _draw_pause(self):
        """绘制暂停画面"""
        # 半透明覆盖
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        # 暂停文字
        pause_text = self.font_large.render("PAUSED", True, COLOR_YELLOW)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)

        # 提示
        hint_text = self.font_small.render("Press ESC to continue", True, COLOR_WHITE)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(hint_text, hint_rect)

    def _draw_game_over(self):
        """绘制游戏结束画面"""
        # 背景
        self.screen.fill(COLOR_BLACK)

        # 游戏结束文字
        game_over_text = self.font_large.render("GAME OVER", True, COLOR_RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)

        # 分数
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)

        # 提示
        hint_text = self.font_small.render("Press SPACE to restart or ESC for menu", True, COLOR_GRAY)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(hint_text, hint_rect)

    def _draw_victory(self):
        """绘制胜利画面"""
        # 背景
        self.screen.fill(COLOR_BLACK)

        # 胜利文字
        victory_text = self.font_large.render("VICTORY!", True, COLOR_YELLOW)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(victory_text, victory_rect)

        # 分数
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)

        # 提示
        hint_text = self.font_small.render("Press SPACE to play again or ESC for menu", True, COLOR_GRAY)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(hint_text, hint_rect)

    def player_shoot(self):
        """玩家射击"""
        if self.player and self.player.active:
            bullet = self.player.shoot()
            if bullet:
                self.player_bullets.append(bullet)
                self.muzzle_flashes.append(MuzzleFlash(
                    bullet.x, bullet.y, self.player.direction
                ))


def main():
    """主函数"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
