"""
test_input.py — 单独测试键盘/鼠标模拟是否生效（不涉及游戏）

用法：
    1. 先打开记事本，鼠标点进编辑区
    2. 在【管理员】终端运行：python test_input.py
    3. 按提示在倒计时内切回记事本

预期：记事本里自动出现 "ffff"，鼠标会左右移动一下。
若没反应，多半是终端没用管理员身份运行。
"""

import time

import input_controller as ic


def countdown(seconds: int, msg: str) -> None:
    print(msg)
    for i in range(seconds, 0, -1):
        print(f"  {i} ...")
        time.sleep(1)


def main():
    print("=" * 48)
    print("  输入模拟测试")
    print("=" * 48)

    countdown(4, "请在倒计时内点进【记事本】编辑区，光标停在里面：")

    print(">> 模拟按 4 次 F 键")
    for _ in range(4):
        ic.press_key("f")
        time.sleep(0.3)

    print(">> 模拟鼠标右移 150 像素，再左移 150 像素")
    ic.move_mouse_relative(150)
    time.sleep(0.5)
    ic.move_mouse_relative(-150)

    print("\n完成。检查记事本里是否出现了 'ffff'，鼠标是否动过。")
    print("有 → 输入链路 OK；没有 → 用管理员身份重开终端再试。")


if __name__ == "__main__":
    main()
