"""
异环钓鱼自动化脚本
按 F9 启动/暂停，按 F10 退出
"""

import time

import keyboard

from state_machine import FishingStateMachine


def main():
    bot = FishingStateMachine()

    print("=" * 40)
    print("  异环钓鱼 Bot 已就绪")
    print("  F9  = 启动 / 暂停")
    print("  F10 = 退出")
    print("=" * 40)

    keyboard.add_hotkey("f9", bot.toggle)
    keyboard.add_hotkey("f10", lambda: os_exit())

    try:
        while True:
            bot.tick()
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass


def os_exit():
    print("\n[Bot] 退出。")
    # 用 os._exit 确保从 keyboard 热键线程也能立即终止进程
    import os
    os._exit(0)


if __name__ == "__main__":
    main()
