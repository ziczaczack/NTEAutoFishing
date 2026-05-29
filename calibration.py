"""
calibration.py — 坐标校准工具（基于已存好的全屏截图）

工作方式：你在游戏【中鱼/衡量 UI 出现】时，用 Win+PrintScreen 截一张全屏图
（自动存到 图片\屏幕截图）。本工具读取那张图，让你框出衡量 UI 的坐标，
裁剪预览确认后写回 config.py 的 GAUGE_REGION。

用法：
    python calibration.py                 # 自动使用“屏幕截图”文件夹里最新的一张
    python calibration.py 图片路径.png     # 指定某张截图

注意：截图必须是【全屏】1920x1080，不能是框选裁剪过的图，否则坐标对不上。
"""

import glob
import os
import re
import sys

import cv2

import config

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")
PREVIEW = "gauge_preview.png"
SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")


def _ask_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("  ⚠ 请输入整数。")


def find_latest_screenshot() -> str | None:
    """返回 图片\屏幕截图 文件夹里最新的一张图片路径，没有则返回 None。"""
    if not os.path.isdir(SCREENSHOT_DIR):
        return None
    files = []
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        files.extend(glob.glob(os.path.join(SCREENSHOT_DIR, ext)))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def load_image(path: str):
    # 用 imdecode 以兼容中文路径（cv2.imread 对非 ASCII 路径会失败）
    import numpy as np
    data = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img


def update_config_gauge_region(region: tuple) -> None:
    """用正则替换 config.py 中的 GAUGE_REGION 赋值行。"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    new_line = f"GAUGE_REGION = {region}"
    pattern = r"^GAUGE_REGION\s*=.*$"
    if not re.search(pattern, content, flags=re.MULTILINE):
        raise RuntimeError("在 config.py 中找不到 GAUGE_REGION 赋值行。")

    content = re.sub(pattern, new_line, content, count=1, flags=re.MULTILINE)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ 已更新 config.py：{new_line}")


def main() -> None:
    print("=" * 52)
    print("  异环钓鱼 Bot — 坐标校准（基于全屏截图）")
    print("=" * 52)
    print(f"当前 GAUGE_REGION = {config.GAUGE_REGION}")
    print()

    # 1. 确定要用哪张截图
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        img_path = find_latest_screenshot()
        if img_path:
            print(f"自动选用最新截图：{img_path}")
            ans = input("用这张吗？(y=用 / 直接回车也表示用 / n=手动指定路径)：").strip().lower()
            if ans == "n":
                img_path = input("请粘贴截图完整路径：").strip().strip('"')
        else:
            print(f"未在 {SCREENSHOT_DIR} 找到截图。")
            img_path = input("请粘贴你的全屏截图完整路径：").strip().strip('"')

    if not img_path or not os.path.isfile(img_path):
        print(f"✗ 找不到文件：{img_path}")
        return

    img = load_image(img_path)
    if img is None:
        print("✗ 无法读取该图片，请确认是有效的 PNG/JPG。")
        return

    h, w = img.shape[:2]
    print(f"✓ 已载入截图，尺寸 {w}x{h}")
    if (w, h) != (config.SCREEN_WIDTH, config.SCREEN_HEIGHT):
        print(f"  ⚠ 注意：截图不是 {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}，")
        print("    可能是框选裁剪过的图，坐标会对不上。建议用 Win+PrintScreen 重截全屏。")

    # 2. 读取坐标
    print()
    print("请用【画图(Paint)】打开这张截图：鼠标移到衡量 UI 上时，")
    print("Paint 左下角会实时显示像素坐标 (x, y)。据此读出：")
    print("  · 左上角的 x、y    · 衡量 UI 的宽度、高度")
    print()
    left = _ask_int("左边界 x = ")
    top = _ask_int("顶边界 y = ")
    width = _ask_int("宽度 width = ")
    height = _ask_int("高度 height = ")
    region = (left, top, width, height)

    # 3. 从同一张图里裁剪预览
    crop = img[top:top + height, left:left + width]
    if crop.size == 0:
        print("✗ 裁剪区域为空，坐标可能超出图片范围，请重试。")
        return
    cv2.imencode(".png", crop)[1].tofile(PREVIEW)  # 兼容中文路径
    print(f"✓ 已保存区域预览：{PREVIEW}")

    # 4. 确认并写入
    print()
    confirm = input(
        f"区域 {region} 已裁剪。请打开 {PREVIEW} 确认是否正好框住衡量 UI。\n"
        "确认无误输入 y 写入 config.py，否则输入其它键放弃："
    ).strip().lower()

    if confirm == "y":
        update_config_gauge_region(region)
        print("\n校准完成！注意：之后【不要移动游戏窗口】，否则坐标会失效。")
    else:
        print("\n已放弃写入。可重新运行本工具再次校准。")


if __name__ == "__main__":
    main()
