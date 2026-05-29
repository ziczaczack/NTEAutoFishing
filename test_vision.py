"""
test_vision.py — 离线验证颜色识别（用已存的全屏截图，不开游戏）

它在 config.GAUGE_REGION 区域里：
  · 用黄色阈值找黄针 -> 画红色竖线标出针的位置
  · 用青色阈值找 bar -> 画蓝色方框标出 bar 边界，绿色竖线标 bar 中心
  · 打印 offset = 针x - bar中心x
并存出标注图，方便确认 config.py 里的 HSV 阈值准不准。

用法：
    python test_vision.py                 # 用“屏幕截图”文件夹里最新一张
    python test_vision.py 图片路径.png     # 指定截图
"""

import glob
import os
import sys

import cv2
import numpy as np

import config
import screen_reader as sr

SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
OUT = "vision_debug.png"
OUT_POINTER_MASK = "mask_pointer.png"
OUT_BAR_MASK = "mask_bar.png"


def find_latest_screenshot() -> str | None:
    if not os.path.isdir(SCREENSHOT_DIR):
        return None
    files = []
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        files.extend(glob.glob(os.path.join(SCREENSHOT_DIR, ext)))
    return max(files, key=os.path.getmtime) if files else None


def imread_unicode(path: str):
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def imwrite_unicode(path: str, img) -> None:
    cv2.imencode(".png", img)[1].tofile(path)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else find_latest_screenshot()
    if not path or not os.path.isfile(path):
        print(f"找不到截图：{path}")
        return

    full = imread_unicode(path)
    if full is None:
        print("无法读取图片。")
        return
    print(f"载入：{path}  尺寸 {full.shape[1]}x{full.shape[0]}")

    # 从全屏图里裁出 GAUGE_REGION
    left, top, w, h = config.GAUGE_REGION
    frame = full[top:top + h, left:left + w]
    if frame.size == 0:
        print("GAUGE_REGION 超出图片范围，请检查 config.py。")
        return

    # 识别
    pointer_x = sr.find_pointer_x(frame)
    bar = sr.find_bar_range(frame)
    offset = sr.get_pointer_bar_offset(frame)

    print(f"GAUGE_REGION = {config.GAUGE_REGION}")
    print(f"黄针 pointer_x = {pointer_x}   (None = 没找到，要调 POINTER_HSV)")
    print(f"青bar 范围     = {bar}          (None = 没找到，要调 BAR_HSV)")
    print(f"offset         = {offset}       (针x - bar中心x；正=针偏右,负=针偏左)")

    # 放大画图（原区域很扁，放大 4 倍便于看）
    scale = 4
    vis = cv2.resize(frame, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST)
    if bar is not None:
        cv2.rectangle(vis, (bar[0] * scale, 0), (bar[1] * scale, h * scale - 1), (255, 0, 0), 2)
        center = (bar[0] + bar[1]) // 2
        cv2.line(vis, (center * scale, 0), (center * scale, h * scale), (0, 255, 0), 1)
    if pointer_x is not None:
        cv2.line(vis, (pointer_x * scale, 0), (pointer_x * scale, h * scale), (0, 0, 255), 2)
    imwrite_unicode(OUT, vis)

    # 同时存两张 mask
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    pmask = cv2.inRange(hsv, np.array(config.POINTER_HSV_LOWER, np.uint8),
                        np.array(config.POINTER_HSV_UPPER, np.uint8))
    bmask = cv2.inRange(hsv, np.array(config.BAR_HSV_LOWER, np.uint8),
                        np.array(config.BAR_HSV_UPPER, np.uint8))
    imwrite_unicode(OUT_POINTER_MASK, cv2.resize(pmask, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST))
    imwrite_unicode(OUT_BAR_MASK, cv2.resize(bmask, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST))

    print()
    print(f"已保存：")
    print(f"  {OUT}             红线=黄针 / 蓝框=青bar / 绿线=bar中心")
    print(f"  {OUT_POINTER_MASK}   黄针 mask（白=识别到）")
    print(f"  {OUT_BAR_MASK}        青bar mask（白=识别到）")
    print("打开 vision_debug.png 看红线是否压在黄针上、蓝框是否框住青bar。")


if __name__ == "__main__":
    main()
