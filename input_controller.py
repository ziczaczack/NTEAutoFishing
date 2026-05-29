"""
input_controller.py — 键盘输入模拟模块

拉鱼阶段通过按住 A / D 键来左右移动黄针，按键时长与偏移量成正比。
"""

import random
import time

import keyboard
import pyautogui

import config

# 鼠标会被自动点击，关闭 pyautogui 移到屏幕角落自动中断的保护
pyautogui.FAILSAFE = False


def press_key(key: str = config.CAST_KEY, delay: float = 0.05) -> None:
    """模拟按一下键（抛饵/确认用），加入随机 ±10ms 抖动模拟人类操作。"""
    jitter = random.uniform(-0.01, 0.01)
    keyboard.press_and_release(key)
    time.sleep(max(0.0, delay + jitter))


def hold_key(key: str, duration: float) -> None:
    """按住某键一段时间再松开。"""
    keyboard.press(key)
    time.sleep(duration)
    keyboard.release(key)


def click(pos: tuple | None = None, jitter: int = 25) -> None:
    """在指定位置附近随机点一下（用于关闭战利品界面）。

    pos 为 None 时用 config.CLAIM_CLICK_POS。jitter 是随机偏移的像素半径。
    """
    if pos is None:
        pos = config.CLAIM_CLICK_POS
    x = pos[0] + random.randint(-jitter, jitter)
    y = pos[1] + random.randint(-jitter, jitter)
    pyautogui.click(x, y)


def adjust_pointer(offset: int) -> None:
    """根据黄针相对 cyan bar 中心的偏移，按 A/D 把针拉回中心。

    offset = 黄针x - bar中心x
    - abs(offset) < DEAD_ZONE：不动
    - offset > 0（针在右）：按 A 左移
    - offset < 0（针在左）：按 D 右移
    按键时长 = 偏移量 × KEY_PRESS_GAIN，并夹在 [MIN, MAX] 之间，偏得越远按得越久。
    """
    if abs(offset) < config.DEAD_ZONE:
        return

    key = config.LEFT_KEY if offset > 0 else config.RIGHT_KEY
    duration = abs(offset) * config.KEY_PRESS_GAIN
    duration = max(config.KEY_PRESS_MIN, min(config.KEY_PRESS_MAX, duration))
    hold_key(key, duration)
