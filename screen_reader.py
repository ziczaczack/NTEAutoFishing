"""
screen_reader.py — 屏幕截图与图像分析模块

负责截取屏幕区域、检测咬钩信号、识别衡量 UI 中的指针与范围 bar。
"""

import cv2
import numpy as np
import pyautogui

import config


# detect_bite 需要维护的上一帧状态（模块级，保存 BITE_DETECT_REGION 的平均亮度）
_prev_brightness: float | None = None


def capture_region(region: tuple) -> np.ndarray:
    """截取指定屏幕区域，返回 BGR 格式的 numpy 数组。

    region: (left, top, width, height)
    """
    screenshot = pyautogui.screenshot(region=region)
    rgb = np.array(screenshot)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return bgr


def reset_bite_state() -> None:
    """重置咬钩检测的上一帧状态（每轮抛饵前调用，避免跨轮误判）。"""
    global _prev_brightness
    _prev_brightness = None


def detect_bite(region: tuple = config.BITE_DETECT_REGION) -> bool:
    """检测是否咬钩。

    截取 region，与上一帧比较平均亮度变化，超过阈值则返回 True。
    第一次调用只记录基准帧，返回 False。
    """
    global _prev_brightness

    frame = capture_region(region)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = float(gray.mean())

    if _prev_brightness is None:
        _prev_brightness = brightness
        return False

    diff = abs(brightness - _prev_brightness)
    _prev_brightness = brightness

    if config.DEBUG:
        print(f"[detect_bite] brightness={brightness:.1f} diff={diff:.1f}")

    return diff >= config.BITE_BRIGHTNESS_THRESHOLD


def _largest_contour_center_x(mask: np.ndarray) -> int | None:
    """在二值 mask 中找到最大轮廓的中心 x 坐标，无轮廓返回 None。"""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) <= 0:
        return None
    M = cv2.moments(largest)
    if M["m00"] == 0:
        x, _, w, _ = cv2.boundingRect(largest)
        return x + w // 2
    return int(M["m10"] / M["m00"])


def find_pointer_x(frame: np.ndarray) -> int | None:
    """输入衡量 UI 区域截图（BGR），返回黄针中心 x 坐标（相对截图左边），未找到返回 None。

    黄针是“又高又窄的竖线”，因此只接受满足形状条件的黄色轮廓，
    用以排除天空/太阳等块状或整条横带的黄色干扰。
    """
    h = frame.shape[0]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(
        hsv,
        np.array(config.POINTER_HSV_LOWER, dtype=np.uint8),
        np.array(config.POINTER_HSV_UPPER, dtype=np.uint8),
    )
    if config.DEBUG:
        cv2.imshow("pointer_mask", mask)
        cv2.waitKey(1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    min_h = config.POINTER_MIN_HEIGHT_FRAC * h
    # 只保留“足够高 + 足够窄”的竖线状轮廓
    candidates = []
    for c in contours:
        x, y, w, ch = cv2.boundingRect(c)
        if ch >= min_h and w <= config.POINTER_MAX_WIDTH:
            candidates.append((c, x, w))

    if not candidates:
        # 没有符合竖线特征的黄色块（多半是天空/太阳干扰），本帧判定看不到针
        return None

    # 取面积最大的候选作为黄针
    best, x, w = max(candidates, key=lambda t: cv2.contourArea(t[0]))
    M = cv2.moments(best)
    if M["m00"] == 0:
        return x + w // 2
    return int(M["m10"] / M["m00"])


def find_bar_range(frame: np.ndarray) -> tuple[int, int] | None:
    """输入衡量 UI 区域截图，返回范围 bar 的 (左边界, 右边界) x 坐标，未找到返回 None。"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(
        hsv,
        np.array(config.BAR_HSV_LOWER, dtype=np.uint8),
        np.array(config.BAR_HSV_UPPER, dtype=np.uint8),
    )
    if config.DEBUG:
        cv2.imshow("bar_mask", mask)
        cv2.waitKey(1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) <= 0:
        return None
    x, _, w, _ = cv2.boundingRect(largest)
    return (x, x + w)


def bar_visible(frame: np.ndarray, min_width: int | None = None) -> bool:
    """判断衡量 UI 是否出现：青 bar 存在且宽度足够（排除背景零星青色噪点）。

    用作“是否已进入拉鱼”的触发器。
    """
    bar = find_bar_range(frame)
    if bar is None:
        return False
    if min_width is None:
        min_width = config.MIN_BAR_WIDTH
    return (bar[1] - bar[0]) >= min_width


def get_pointer_bar_offset(frame: np.ndarray) -> int | None:
    """计算指针相对 bar 中心的偏移。

    offset = pointer_x - bar_center_x
    正值表示指针在 bar 右侧，负值表示指针在 bar 左侧。
    任一未找到返回 None。
    """
    pointer_x = find_pointer_x(frame)
    bar = find_bar_range(frame)
    if pointer_x is None or bar is None:
        return None
    bar_center_x = (bar[0] + bar[1]) // 2
    return pointer_x - bar_center_x
