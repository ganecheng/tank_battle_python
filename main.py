"""
Tank Battle Game - Main Entry Point
坦克大战 - 主入口
"""
import sys
import os

# 添加 src 目录到路径
if getattr(sys, 'frozen', False):
    # 如果是打包后的可执行文件
    BASE_DIR = sys._MEIPASS
else:
    # 如果是源代码运行
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 将 src 目录添加到 Python 路径
src_path = os.path.join(BASE_DIR, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 导入并运行游戏
from game import Game

def main():
    """主函数"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
