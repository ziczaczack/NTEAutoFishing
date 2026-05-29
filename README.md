<h1 align="center">🎣 异环钓鱼 Bot · NTEAutoFishing</h1>

<p align="center">
  为单机游戏《异环》的钓鱼小游戏打造的<b>外部自动化脚本</b><br>
  纯屏幕截图分析 + 键鼠模拟，<b>不修改任何游戏文件、不读写游戏内存</b>
</p>

<p align="center">
  <img alt="platform" src="https://img.shields.io/badge/platform-Windows%2010%2F11-0078D6?logo=windows">
  <img alt="python" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="resolution" src="https://img.shields.io/badge/分辨率-1920×1080-brightgreen">
  <a href="https://github.com/ziczaczack/NTEAutoFishing/releases/latest"><img alt="release" src="https://img.shields.io/github/v/release/ziczaczack/NTEAutoFishing"></a>
</p>

> ⚠️ **仅适用于单机版《异环》**，请勿在联机 / 有反作弊的环境使用。本项目仅供学习与个人单机使用。

---

## ✨ 特性

- **全自动循环**：抛竿 → 等上钩 → 拉鱼 → 关闭战利品 → 再抛竿，一条龙。
- **拉鱼自动操控**：实时识别黄色指针与青色范围 bar，按 `A` / `D` 把指针稳在 bar 中心。
- **抗背景干扰**：指针识别加了「又高又窄的竖线」形状判断，天空变色 / 太阳不会被误认成黄针。
- **稳健的阶段切换**：用「青 bar 是否出现」判断进入拉鱼，比检测咬钩文字更可靠。
- **战利品自适应**：拉长间隔多次点击，跨过出金鱼 2~3 秒的展示动画。
- **开箱即用**：提供打包好的 `.exe`，无需安装 Python。

---

## 📥 快速开始（普通用户）

> 不想装 Python，直接用成品：

1. 前往 **[Releases](https://github.com/ziczaczack/NTEAutoFishing/releases/latest)** 下载：
   - `NTEFishingBot.exe`
   - `USAGE.txt`（使用说明）
2. 把游戏分辨率设为 **1920 × 1080**（推荐窗口 / 无边框模式），进游戏走到水边。
3. **双击 `NTEFishingBot.exe`** → 弹出 UAC 时点 **「是」**（模拟按键需要管理员权限）。
4. 黑色窗口出现后，切回游戏：

   | 按键 | 作用 |
   |:---:|---|
   | `F9` | 启动 / 暂停 |
   | `F10` | 退出 |

> 💡 模拟键鼠的程序常被杀毒软件误报，需在杀软中 **允许 / 信任** 后才能运行。

---

## 🛠️ 从源码运行（开发者）

```bash
git clone https://github.com/ziczaczack/NTEAutoFishing.git
cd NTEAutoFishing
pip install -r requirements.txt

python main.py        # 需以【管理员身份】打开终端，否则模拟按键无效
```

打包成单文件 exe（含 UAC 管理员清单）：

```bash
build.bat             # 等价于 pyinstaller --onefile --uac-admin ...
# 产物：dist\NTEFishingBot.exe
```

---

## 🎯 校准

坐标 / 颜色按 1920×1080 已配好，**同分辨率同版本一般无需校准**。若识别不准再校准：

### 1. 衡量 UI 坐标（`GAUGE_REGION`）

拉鱼界面出现时按 **`Win`+`PrintScreen`** 截一张全屏图（自动存到「图片\屏幕截图」），然后：

```bash
python calibration.py            # 自动读取最新截图，按提示输入 UI 的 左x/顶y/宽/高
```

它会从同一张图裁剪预览供你确认，确认后自动写回 `config.py`。

### 2. 颜色 / 识别验证（离线，不开游戏）

```bash
python test_vision.py "你的全屏截图.png"
```

生成 `vision_debug.png`（红线=黄针 / 蓝框=青 bar / 绿线=中心）和两张 mask 图，确认识别是否准确。

---

## ⚙️ 配置参数（`config.py`）

<details>
<summary>点击展开主要参数</summary>

| 参数 | 默认 | 说明 |
|---|---|---|
| `GAUGE_REGION` | `(600,64,730,18)` | 衡量 UI 区域 `(left, top, w, h)` |
| `POINTER_HSV_LOWER/UPPER` | 黄 `(18,40,150)~(40,200,255)` | 黄针颜色阈值 |
| `BAR_HSV_LOWER/UPPER` | 青 `(75,100,120)~(98,255,255)` | 青 bar 颜色阈值 |
| `POINTER_MIN_HEIGHT_FRAC` / `POINTER_MAX_WIDTH` | `0.5` / `20` | 指针形状过滤（抗天空/太阳干扰） |
| `LEFT_KEY` / `RIGHT_KEY` | `a` / `d` | 拉鱼左移 / 右移键 |
| `DEAD_ZONE` | `8` | 指针距中心多少像素内不动（防抖） |
| `KEY_PRESS_GAIN` / `MIN` / `MAX` | `0.004` / `0.012` / `0.06` | 按键时长 = 偏移×GAIN，夹在 [MIN,MAX] |
| `CONTROL_FPS` | `30` | 拉鱼控制帧率 |
| `F_TAP_INTERVAL` | `1.0` | 等待上钩时点 F 的间隔 |
| `MIN_BAR_WIDTH` | `40` | 判定「进入拉鱼」的青 bar 最小宽度 |
| `LOOT_WAIT` / `CLAIM_CLICKS` / `CLAIM_CLICK_INTERVAL` | `1.5` / `3` / `1.0` | 战利品界面：等待、点击次数、间隔 |
| `CLAIM_CLICK_POS` | `(960,540)` | 关闭战利品的点击位置 |
| `DEBUG` | `False` | True 时用 `cv2.imshow` 实时显示 mask |

</details>

**调参速查：**
- 黄针被天空/太阳干扰 → 增大 `POINTER_MAX_WIDTH` 或检查 `POINTER_HSV`
- 指针追不上快鱼 → 增大 `KEY_PRESS_GAIN` / `KEY_PRESS_MAX`
- 指针来回抖 / 过冲 → 减小 `KEY_PRESS_GAIN`、增大 `DEAD_ZONE`
- 出金动画没关掉 → 增大 `CLAIM_CLICKS`

---

## 🔄 工作流程（状态机）

```
IDLE → CASTING → WAITING_BITE → REELING → CLAIMING → IDLE → (循环)
```

| 状态 | 行为 | 退出条件 |
|---|---|---|
| `IDLE` | 等待 `ROUND_INTERVAL` | 时间到 → 抛竿 |
| `CASTING` | 按 `F` 抛竿 | 立即进入下一状态 |
| `WAITING_BITE` | 每 `F_TAP_INTERVAL` 点一次 F，同时检测青 bar | 青 bar 出现→拉鱼；超时→重抛 |
| `REELING` | 30fps 按 A/D 把黄针拉回 bar 中心 | 青 bar 消失 或 超时 |
| `CLAIMING` | 点击关闭战利品界面 | 点击完毕 → IDLE |

---

## 🧪 测试工具

| 脚本 | 用途 |
|---|---|
| `test_input.py` | 在记事本里验证键鼠模拟是否生效（不开游戏） |
| `test_vision.py` | 用截图离线验证黄针 / 青 bar 识别是否准确 |
| `test_reel.py` | 实时测试拉鱼控制：游戏内按 `F8` 开始，打印每帧 offset 与按键 |

---

## 📂 项目结构

```
NTEAutoFishing/
├── main.py               # 主入口：F9/F10 热键 + 主循环
├── config.py             # 所有可调参数
├── screen_reader.py      # 屏幕截图与图像识别
├── input_controller.py   # 键盘(A/D/F) + 鼠标点击模拟
├── state_machine.py      # 钓鱼状态机
├── calibration.py        # 坐标校准工具
├── test_input.py         # 输入测试
├── test_vision.py        # 视觉识别测试
├── test_reel.py          # 实时拉鱼控制测试
├── build.bat             # 一键打包 exe
├── requirements.txt
└── PROJECT_OVERVIEW.md   # 详细设计文档
```

---

## ❓ 常见问题

- **按 F9 没反应、人物不动** → 没用管理员权限。重开终端 / exe，看到 UAC 弹窗点「是」。
- **黄针乱跑、战利品关不掉** → 分辨率不是 1920×1080，或游戏窗口被移动过。调成 1920×1080 重开游戏。
- **杀毒报毒** → 模拟键鼠工具的通病，需在杀软中「允许 / 信任」。

---

## ⚠️ 免责声明

本项目仅供 **学习交流** 与 **单机游戏个人使用**。请勿用于联机 / 竞技 / 有反作弊的环境。使用本工具产生的任何后果由使用者自行承担。
