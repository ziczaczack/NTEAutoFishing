"""
test_reel.py — 实时拉鱼控制测试（单独测“手”，不依赖抛竿/咬钩）

用法（【管理员】终端）：
    python test_reel.py

操作：
    1. 运行后切回游戏，正常抛竿钓鱼
    2. 拉鱼界面（青 bar）一出现，立刻按 F8 → 脚本开始按 A/D 控制黄针
    3. 本轮拉完按 F8 停止（或它检测到青 bar 消失会自动停）
    4. 按 F10 退出

它每帧打印 offset 和按的键，方便你调 KEY_PRESS_GAIN / DEAD_ZONE。
"""

import time

import keyboard

import config
import input_controller
import screen_reader

_active = False
_quit = False


def toggle():
    global _active
    _active = not _active
    print(f"\n[test_reel] 控制 {'开启 ▶' if _active else '停止 ⏸'}")


def do_quit():
    global _quit
    _quit = True


def main():
    print("=" * 52)
    print("  实时拉鱼控制测试")
    print("  F8 = 开始/停止控制    F10 = 退出")
    print("=" * 52)
    print(f"GAUGE_REGION = {config.GAUGE_REGION}")
    print(f"DEAD_ZONE={config.DEAD_ZONE}  GAIN={config.KEY_PRESS_GAIN}  "
          f"PRESS=[{config.KEY_PRESS_MIN},{config.KEY_PRESS_MAX}]s")
    print("切回游戏，拉鱼界面出现时按 F8。\n")

    keyboard.add_hotkey("f8", toggle)
    keyboard.add_hotkey("f10", do_quit)

    frame_interval = 1.0 / config.CONTROL_FPS
    lost = 0

    while not _quit:
        if not _active:
            time.sleep(0.02)
            continue

        loop_start = time.time()
        frame = screen_reader.capture_region(config.GAUGE_REGION)
        pointer_x = screen_reader.find_pointer_x(frame)
        bar = screen_reader.find_bar_range(frame)

        if pointer_x is None or bar is None:
            lost += 1
            print(f"  [miss] pointer={pointer_x} bar={bar}")
            if lost >= config.CONTROL_FPS:  # 约 1 秒看不到 -> 提示
                print("  (连续约1秒找不到针/bar，可能拉鱼已结束)")
                lost = 0
        else:
            lost = 0
            bar_center = (bar[0] + bar[1]) // 2
            offset = pointer_x - bar_center
            key = "-" if abs(offset) < config.DEAD_ZONE else ("A左" if offset > 0 else "D右")
            print(f"  pin={pointer_x:4d} bar=({bar[0]},{bar[1]}) center={bar_center:4d} "
                  f"offset={offset:+4d} -> {key}")
            input_controller.adjust_pointer(offset)

        sleep_time = frame_interval - (time.time() - loop_start)
        if sleep_time > 0:
            time.sleep(sleep_time)

    print("\n[test_reel] 退出。")


if __name__ == "__main__":
    main()
