# 异环钓鱼自动化脚本项目

## 项目概述

为单机游戏《异环》的钓鱼小游戏开发一个外部自动化辅助脚本。该脚本使用屏幕截图分析和键盘模拟，**不修改任何游戏文件**，属于纯外部工具。

---

## 技术规格

- **目标平台**：Windows 10/11
- **屏幕分辨率**：1920 × 1080
- **游戏模式**：支持窗口模式（推荐）和全屏模式
- **开发语言**：Python 3.10+
- **核心依赖**：`pyautogui`、`opencv-python`、`numpy`、`keyboard`、`Pillow`

---

## 钓鱼玩法说明

| 阶段 | 操作 | 备注 |
|------|------|------|
| 1. 抛饵 | 按 `F` 键 | 将鱼竿抛出 |
| 2. 等待上钩 | 监测屏幕变化 | 等待鱼咬钩信号出现 |
| 3. 收线确认 | 再按 `F` 键 | 确认中鱼 |
| 4. 拉鱼阶段 | 持续操控衡量条 | 保持指针在范围 bar 内 |

### 拉鱼阶段详细说明

- 玩家头顶出现一个**横向衡量 UI**
- UI 内有一个**快速移动的指针**（细线或亮色标记）
- 还有一个可以被玩家控制的**范围 bar**（宽度约为指针的 3–5 倍）
- 玩家需要**移动鼠标（或按方向键）**，让范围 bar 跟随指针，确保指针始终在 bar 范围内
- 不同品质的鱼，指针移动速度不同（普通鱼慢，稀有鱼快）
- 若指针长时间在 bar 外，鱼会逃跑

---

## 项目结构

```
yihuan_fishing_bot/
├── main.py               # 主入口，状态机控制
├── config.py             # 所有可调参数（坐标、颜色、延迟等）
├── screen_reader.py      # 屏幕截图与图像分析模块
├── input_controller.py   # 键盘/鼠标输入模拟模块
├── state_machine.py      # 钓鱼状态机逻辑
├── calibration.py        # 首次运行坐标校准工具
├── requirements.txt      # Python 依赖列表
└── README.md             # 使用说明
```

---

## 各文件实现要求

### `requirements.txt`

```
pyautogui>=0.9.54
opencv-python>=4.8.0
numpy>=1.24.0
keyboard>=0.13.5
Pillow>=10.0.0
```

---

### `config.py` — 配置中心

所有硬编码坐标和参数都集中在此文件，方便调整。

```python
# 屏幕分辨率
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# 衡量 UI 区域（需通过 calibration.py 校准后填入）
# 格式：(left, top, width, height)，单位像素
GAUGE_REGION = (760, 150, 400, 60)

# 中鱼检测区域（鱼咬钩时出现变化的 UI 区域）
BITE_DETECT_REGION = (860, 100, 200, 80)

# 颜色阈值（HSV 格式）
# 指针颜色（亮白/黄色）
POINTER_HSV_LOWER = (0, 0, 220)
POINTER_HSV_UPPER = (180, 30, 255)

# 范围 bar 颜色（半透明蓝/绿色，需校准）
BAR_HSV_LOWER = (90, 50, 150)
BAR_HSV_UPPER = (130, 255, 255)

# 中鱼信号颜色变化阈值（像素亮度差异）
BITE_BRIGHTNESS_THRESHOLD = 30

# 操作按键
CAST_KEY = 'f'      # 抛饵/确认键

# 时间参数（秒）
CAST_WAIT_MIN = 4.0        # 抛饵后最短等待时间
CAST_WAIT_MAX = 15.0       # 抛饵后最长等待时间（超时重新抛）
CONFIRM_DELAY = 0.15       # 检测到咬钩后延迟确认（模拟人类反应）
FISHING_TIMEOUT = 20.0     # 拉鱼最长时间

# 拉鱼控制参数
MOUSE_SENSITIVITY = 0.5    # 鼠标移动速度系数（0.1 ~ 1.0）
CONTROL_FPS = 30           # 每秒检测帧率
DEAD_ZONE = 5              # 指针在 bar 内的死区像素（在此范围内不移动）

# 循环间隔
ROUND_INTERVAL = 1.5       # 每轮钓鱼结束后的等待时间
```

---

### `screen_reader.py` — 屏幕分析模块

实现以下函数：

#### `capture_region(region: tuple) -> np.ndarray`
- 截取指定屏幕区域
- 返回 BGR 格式的 numpy 数组
- 使用 `pyautogui.screenshot()` + `np.array()` 实现

#### `detect_bite(region: tuple) -> bool`
- 截取 `BITE_DETECT_REGION` 区域
- 与上一帧比较平均亮度变化
- 超过 `BITE_BRIGHTNESS_THRESHOLD` 则返回 `True`（表示咬钩）
- 需要维护一个 `prev_frame` 状态

#### `find_pointer_x(frame: np.ndarray) -> int | None`
- 输入衡量 UI 区域的截图（BGR）
- 转换为 HSV，用 `POINTER_HSV_LOWER/UPPER` 提取指针 mask
- 找到最大轮廓的中心 x 坐标（相对于截图左边）
- 未找到时返回 `None`

#### `find_bar_range(frame: np.ndarray) -> tuple[int, int] | None`
- 输入衡量 UI 区域的截图
- 用 `BAR_HSV_LOWER/UPPER` 提取范围 bar 的 mask
- 找到 bar 的左边界和右边界 x 坐标
- 返回 `(bar_left, bar_right)`，未找到返回 `None`

#### `get_pointer_bar_offset(frame: np.ndarray) -> int | None`
- 组合调用以上两个函数
- 计算：`offset = pointer_x - bar_center_x`
- 正值表示指针在 bar 右侧，负值表示指针在 bar 左侧
- 返回偏移像素值，任一未找到则返回 `None`

---

### `input_controller.py` — 输入控制模块

实现以下函数：

#### `press_key(key: str, delay: float = 0.05)`
- 使用 `keyboard.press_and_release(key)` 模拟按键
- 加入随机 ±10ms 抖动模拟人类操作

#### `move_mouse_relative(dx: int)`
- 使用 `pyautogui.moveRel(dx, 0, duration=0.02)` 水平移动鼠标
- `dx` 正值向右，负值向左

#### `adjust_bar(offset: int)`
- 根据 `offset` 决定鼠标移动方向和幅度
- 若 `abs(offset) < DEAD_ZONE`：不移动
- 若 `offset > 0`（指针在右）：向右移动 `offset * MOUSE_SENSITIVITY` 像素
- 若 `offset < 0`（指针在左）：向左移动

---

### `state_machine.py` — 状态机

定义以下状态：

```
IDLE → CASTING → WAITING_BITE → CONFIRMING → REELING → IDLE
```

| 状态 | 描述 | 退出条件 |
|------|------|---------|
| `IDLE` | 等待开始 | 用户按下启动快捷键 |
| `CASTING` | 按 F 抛饵 | 立即进入下一状态 |
| `WAITING_BITE` | 监听咬钩信号 | `detect_bite()` 返回 True，或超时重抛 |
| `CONFIRMING` | 延迟后按 F 确认 | 延迟 `CONFIRM_DELAY` 秒 |
| `REELING` | 循环追踪指针，调整 bar | 超时或检测到 UI 消失 |
| `IDLE` | 等待 `ROUND_INTERVAL` 后重新开始 | - |

**状态机要求：**
- 使用 `enum.Enum` 定义状态
- 在 `REELING` 状态中以 `1/CONTROL_FPS` 的间隔循环调用 `screen_reader.get_pointer_bar_offset()` 和 `input_controller.adjust_bar()`
- 每次状态变更打印日志到控制台

---

### `calibration.py` — 校准工具

交互式命令行工具，帮助用户首次校准坐标：

**功能流程：**
1. 提示用户："请在游戏中进入钓鱼界面，然后按 Enter 继续"
2. 全屏截图并保存为 `calibration_screenshot.png`
3. 提示用户："请用图片查看器打开 calibration_screenshot.png，找到衡量 UI 的坐标范围"
4. 引导用户输入：左边界 x、顶边界 y、宽度、高度
5. 截取该区域预览，保存为 `gauge_preview.png` 让用户确认
6. 确认后自动更新 `config.py` 中的 `GAUGE_REGION` 值

---

### `main.py` — 主入口

```python
"""
异环钓鱼自动化脚本
按 F9 启动/暂停，按 F10 退出
"""

import keyboard
import time
from state_machine import FishingStateMachine

def main():
    bot = FishingStateMachine()
    running = False

    print("=" * 40)
    print("  异环钓鱼 Bot 已就绪")
    print("  F9 = 启动 / 暂停")
    print("  F10 = 退出")
    print("=" * 40)

    keyboard.add_hotkey('f9', lambda: bot.toggle())
    keyboard.add_hotkey('f10', lambda: exit(0))

    while True:
        bot.tick()
        time.sleep(0.01)

if __name__ == "__main__":
    main()
```

**`FishingStateMachine` 需要实现：**
- `toggle()`：切换运行/暂停
- `tick()`：执行当前状态的逻辑，推进状态机

---

## 使用流程

### 安装

```bash
pip install -r requirements.txt
```

### 首次校准

```bash
python calibration.py
```

### 运行

```bash
python main.py
```

1. 启动游戏，进入钓鱼区域，站在水边
2. 运行脚本
3. 按 `F9` 启动 Bot
4. 按 `F9` 暂停，`F10` 退出

---

## 调试建议

### 颜色不准确时

在 Python 中截图后用以下代码查看 HSV 值：

```python
import pyautogui, cv2, numpy as np
img = pyautogui.screenshot(region=(760, 150, 400, 60))
bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
# 查看指定像素的 HSV
print(hsv[30, 200])  # (y, x)
```

### 检测可视化（开发模式）

在 `screen_reader.py` 中加入 `DEBUG = True` 开关，用 `cv2.imshow()` 实时显示 mask 结果，确认颜色识别是否准确。

---

## 注意事项

- 本脚本仅适用于**单机版《异环》**，不建议在联机/有反作弊的环境使用
- 游戏分辨率必须为 **1920×1080**，其他分辨率需重新校准坐标
- 首次使用必须运行 `calibration.py` 确定 UI 坐标
- 若指针或 bar 颜色版本更新后变化，需重新校准 HSV 参数