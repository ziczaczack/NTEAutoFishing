# 异环钓鱼自动化脚本

为单机游戏《异环》钓鱼小游戏开发的**外部自动化辅助脚本**。基于屏幕截图分析 + 键鼠模拟，**不修改任何游戏文件**。

> ⚠️ 仅适用于单机版《异环》，请勿在联机/有反作弊的环境使用。

---

## 环境要求

- Windows 10 / 11
- 游戏分辨率 **1920 × 1080**（窗口或全屏，推荐窗口模式）
- Python 3.10+

## 安装

```bash
pip install -r requirements.txt
```

> 提示：`keyboard` 库注册全局热键、模拟按键通常需要**以管理员身份**运行终端，否则按键可能无效。

## 首次校准

进入游戏钓鱼界面，让衡量 UI 显示出来，然后运行：

```bash
python calibration.py
```

按提示截图、输入衡量 UI 的坐标（左 x、顶 y、宽、高），确认后会自动写回 `config.py` 的 `GAUGE_REGION`。

## 运行

```bash
python main.py
```

1. 启动游戏，进入钓鱼区域，站在水边
2. 运行脚本
3. 按 `F9` 启动 / 暂停 Bot
4. 按 `F10` 退出

---

## 工作流程（状态机）

```
IDLE → CASTING → WAITING_BITE → CONFIRMING → REELING → IDLE
```

| 状态 | 说明 |
|------|------|
| `IDLE` | 等待开始 / 每轮间隔（`ROUND_INTERVAL`） |
| `CASTING` | 按 `F` 抛饵 |
| `WAITING_BITE` | 监测 `BITE_DETECT_REGION` 亮度变化等待咬钩，超时（`CAST_WAIT_MAX`）重抛 |
| `CONFIRMING` | 延迟 `CONFIRM_DELAY` 后再按 `F` 确认中鱼 |
| `REELING` | 以 `CONTROL_FPS` 追踪指针并移动鼠标让范围 bar 跟随，超时或 UI 消失则结束 |

---

## 调参指南（`config.py`）

所有可调参数集中在 `config.py`：

- **找不到指针 / bar**：调整 `POINTER_HSV_LOWER/UPPER`、`BAR_HSV_LOWER/UPPER`。
- **咬钩检测不灵 / 误判**：调整 `BITE_DETECT_REGION`、`BITE_BRIGHTNESS_THRESHOLD`，以及 `CAST_WAIT_MIN`（抛竿动画期间不检测）。
- **bar 跟不上 / 抖动**：调整 `MOUSE_SENSITIVITY`、`DEAD_ZONE`、`CONTROL_FPS`。

### 颜色校准（查看像素 HSV）

```python
import pyautogui, cv2, numpy as np
img = pyautogui.screenshot(region=(760, 150, 400, 60))   # 改成你的 GAUGE_REGION
bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
print(hsv[30, 200])   # (y, x) 处的 HSV 值
```

### 实时 mask 可视化

把 `config.py` 里的 `DEBUG = True`，运行时会用 `cv2.imshow` 实时显示指针和 bar 的识别 mask，方便确认颜色阈值是否准确。

---

## 项目结构

```
NTEFishingScript/
├── main.py               # 主入口，热键 + 主循环
├── config.py             # 所有可调参数
├── screen_reader.py      # 屏幕截图与图像分析
├── input_controller.py   # 键盘/鼠标输入模拟
├── state_machine.py      # 钓鱼状态机
├── calibration.py        # 坐标校准工具
├── requirements.txt      # 依赖
└── README.md
```

## 注意事项

- 游戏分辨率必须为 1920×1080，其他分辨率需重新校准坐标与区域。
- 首次使用必须运行 `calibration.py`。
- 游戏版本更新若改变指针/bar 颜色，需重新校准 HSV 参数。
- `MOUSE_SENSITIVITY`、`DEAD_ZONE` 等需根据实际拉鱼手感微调。
