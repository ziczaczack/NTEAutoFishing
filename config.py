"""
config.py — 配置中心

所有硬编码坐标和参数都集中在此文件，方便调整。
首次使用请运行 calibration.py 来校准 GAUGE_REGION 等坐标。
"""

# ===== 屏幕分辨率 =====
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# ===== 衡量 UI 区域（需通过 calibration.py 校准后填入）=====
# 格式：(left, top, width, height)，单位像素
GAUGE_REGION = (600, 64, 730, 18)

# ===== 中鱼检测区域（鱼咬钩时出现变化的 UI 区域）=====
BITE_DETECT_REGION = (860, 100, 200, 80)

# ===== 颜色阈值（HSV 格式，OpenCV 色相范围 0~180）=====
# 指针颜色：黄针 #FEF69F → 实测 HSV≈(27, 95, 254)，注意饱和度偏低
POINTER_HSV_LOWER = (18, 40, 150)
POINTER_HSV_UPPER = (40, 200, 255)

# 范围 bar 颜色：青色 #33DEB9 → 实测 HSV≈(84, 196, 222)
BAR_HSV_LOWER = (75, 100, 120)
BAR_HSV_UPPER = (98, 255, 255)

# 指针形状过滤（排除天空/太阳等块状黄色干扰）：黄针是“又高又窄的竖线”
POINTER_MIN_HEIGHT_FRAC = 0.5   # 黄针高度至少要占 GAUGE 区域高度的这个比例
POINTER_MAX_WIDTH = 20          # 黄针最大宽度（像素），更宽的黄色块视为干扰（天空/太阳）

# 中鱼信号颜色变化阈值（像素平均亮度差异）
BITE_BRIGHTNESS_THRESHOLD = 30

# ===== 操作按键 =====
CAST_KEY = 'f'      # 抛饵/确认键
LEFT_KEY = 'a'      # 拉鱼阶段：让黄针左移
RIGHT_KEY = 'd'     # 拉鱼阶段：让黄针右移

# ===== 时间参数（秒）=====
CAST_WAIT_MAX = 15.0       # 抛竿后最长等待时间（超时还没出现青bar就重抛）
F_TAP_INTERVAL = 1       # 等待上钩期间，每隔多久点一次 F
FISHING_TIMEOUT = 20.0     # 拉鱼最长时间

# 判定“青bar已出现 = 进入拉鱼”的最小宽度（像素），用来排除背景里零星的青色噪点
MIN_BAR_WIDTH = 40

# ===== 拉鱼控制参数（A/D 按键控制黄针）=====
CONTROL_FPS = 30           # 每秒检测帧率
DEAD_ZONE = 8              # 黄针距 bar 中心多少像素以内就不动（防抖）
KEY_PRESS_GAIN = 0.004     # 每帧按键时长 = 偏移像素 × 此系数（秒/像素）
KEY_PRESS_MIN = 0.012      # 每次按键最短按住时间（秒）
KEY_PRESS_MAX = 0.060      # 每次按键最长按住时间（秒，防止过冲）

# ===== 战利品 / 重新开始 =====
# 出金鱼时战利品界面会有 2~3 秒动画，期间点击无效，所以把点击拉长间隔、多点几下，
# 保证动画结束后仍有点击落在界面上把它关掉。
LOOT_WAIT = 1.5            # 拉鱼结束后，等战利品界面弹出的时间（秒）
CLAIM_CLICK_POS = (960, 540)  # 关闭战利品界面的点击位置（默认屏幕中心，附近随机抖动）
CLAIM_CLICKS = 3          # 点几下（间隔较长，跨越整个动画时长）
CLAIM_CLICK_INTERVAL = 1.0    # 两次点击之间的间隔（秒）

# ===== 循环间隔 =====
ROUND_INTERVAL = 1.5       # 关闭战利品后、下一轮抛竿前的等待时间

# ===== 调试 =====
DEBUG = False              # True 时用 cv2.imshow 实时显示 mask，便于校准颜色
