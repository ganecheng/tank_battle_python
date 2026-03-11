"""
Test script for Tank Battle Game
测试脚本 - 验证游戏基本功能
"""
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

from config import *
from tank import PlayerTank, EnemyTank
from bullet import Bullet
from map import Map, Obstacle
from base import Base
from effects import Explosion, Smoke, MuzzleFlash


def test_config():
    """测试配置"""
    print("Testing config...")
    assert SCREEN_WIDTH == 1024
    assert SCREEN_HEIGHT == 768
    assert FPS == 60
    print("  Config OK!")


def test_player_tank():
    """测试玩家坦克"""
    print("Testing player tank...")
    player = PlayerTank(100, 100)
    assert player.x == 100
    assert player.y == 100
    assert player.health == PLAYER_HEALTH
    assert player.active == True

    # 测试移动
    result = player.move(1, 0)
    assert result == True
    assert player.x > 100

    # 测试射击
    bullet = player.shoot()
    assert bullet is not None
    assert bullet.direction == RIGHT

    print("  Player tank OK!")


def test_enemy_tank():
    """测试敌方坦克"""
    print("Testing enemy tank...")
    enemy = EnemyTank(200, 200, 'normal')
    assert enemy.x == 200
    assert enemy.y == 200
    assert enemy.active == True

    # 测试不同类型
    fast_enemy = EnemyTank(300, 300, 'fast')
    assert fast_enemy.speed > enemy.speed

    heavy_enemy = EnemyTank(400, 400, 'heavy')
    assert heavy_enemy.health > enemy.health

    print("  Enemy tank OK!")


def test_bullet():
    """测试子弹"""
    print("Testing bullet...")
    bullet = Bullet(100, 100, UP, 'player')
    assert bullet.x == 100
    assert bullet.y == 100
    assert bullet.direction == UP
    assert bullet.owner == 'player'
    assert bullet.active == True

    # 测试更新
    old_y = bullet.y
    bullet.update()
    assert bullet.y < old_y  # 向上移动

    print("  Bullet OK!")


def test_map():
    """测试地图"""
    print("Testing map...")
    game_map = Map(1)
    assert game_map.level == 1
    assert game_map.base is not None
    assert game_map.is_base_alive() == True
    assert len(game_map.spawn_points['enemies']) > 0

    # 测试障碍物
    obstacles = game_map.get_all_obstacles()
    assert len(obstacles) > 0

    print("  Map OK!")


def test_base():
    """测试基地"""
    print("Testing base...")
    base = Base(100, 100)
    assert base.x == 100
    assert base.y == 100
    assert base.alive == True

    # 测试摧毁
    base.destroy()
    assert base.alive == False

    print("  Base OK!")


def test_effects():
    """测试特效"""
    print("Testing effects...")

    # 测试爆炸
    explosion = Explosion(100, 100, 'medium')
    assert explosion.active == True
    explosion.update()
    assert explosion.frame > 0

    # 测试烟雾
    smoke = Smoke(200, 200)
    assert smoke.active == True

    # 测试枪口闪光
    flash = MuzzleFlash(300, 300, RIGHT)
    assert flash.active == True

    print("  Effects OK!")


def test_collisions():
    """测试碰撞"""
    print("Testing collisions...")

    # 创建测试对象
    player = PlayerTank(100, 100)
    enemy = EnemyTank(200, 100)

    # 测试矩形碰撞
    obstacle = Obstacle(300, 100, 40, 40, 'brick')
    bullet = Bullet(250, 120, 1, 'player')  # 在障碍物左边，RIGHT=1

    # 更新子弹位置使其进入障碍物区域
    for _ in range(8):  # 增加更新次数
        bullet.update()

    # 检查是否碰撞
    collided = bullet.collide_with_rect(obstacle.get_rect())
    assert collided == True, f"Bullet should collide with obstacle, bullet=({bullet.x}, {bullet.y}), obstacle={obstacle.get_rect()}"

    print("  Collisions OK!")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("Tank Battle Game - Test Suite")
    print("=" * 50)

    try:
        test_config()
        test_player_tank()
        test_enemy_tank()
        test_bullet()
        test_map()
        test_base()
        test_effects()
        test_collisions()

        print("=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        return True
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        pygame.quit()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
