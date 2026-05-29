"""
state_machine.py — 钓鱼状态机逻辑

流程（基于实际玩法）：
    IDLE → CASTING → WAITING_BITE → REELING → CLAIMING → IDLE

- 抛竿后可以一直点 F 直到上钩，所以 WAITING_BITE 期间持续点 F。
- 用“GAUGE_REGION 里青 bar 是否出现”来判断是否进入拉鱼（比检测咬钩文字更稳）。
- REELING 阶段按 A/D 把黄针拉回青 bar 中心；青 bar 消失即结束。
- CLAIMING：钓到鱼后出现战利品界面，随机点几下画面关闭，再进入下一轮。
"""

import enum
import time

import config
import input_controller
import screen_reader


class State(enum.Enum):
    IDLE = "IDLE"                 # 等待开始 / 每轮间隔
    CASTING = "CASTING"           # 按 F 抛竿
    WAITING_BITE = "WAITING_BITE" # 持续点 F，等青 bar 出现
    REELING = "REELING"           # 按 A/D 把黄针拉回青 bar 中心
    CLAIMING = "CLAIMING"         # 点击关闭战利品界面


class FishingStateMachine:
    """钓鱼状态机。

    - toggle(): 切换运行 / 暂停
    - tick():   执行当前状态逻辑，推进状态机
    """

    def __init__(self):
        self.state = State.IDLE
        self.running = False
        self._cast_time = 0.0       # 抛竿时刻
        self._last_f_tap = 0.0      # 上次点 F 的时刻
        self._idle_until = 0.0      # IDLE 状态等待至此时刻
        self._reel_end_time = 0.0   # 拉鱼结束（进入 CLAIMING）的时刻

    def toggle(self) -> None:
        self.running = not self.running
        print(f"[Bot] {'▶ 运行' if self.running else '⏸ 暂停'}")

    def _set_state(self, new_state: State) -> None:
        if new_state != self.state:
            print(f"[State] {self.state.value} → {new_state.value}")
        self.state = new_state

    def tick(self) -> None:
        """由主循环高频调用。暂停时不做任何事。"""
        if not self.running:
            return

        if self.state == State.IDLE:
            self._tick_idle()
        elif self.state == State.CASTING:
            self._tick_casting()
        elif self.state == State.WAITING_BITE:
            self._tick_waiting_bite()
        elif self.state == State.REELING:
            self._tick_reeling()
        elif self.state == State.CLAIMING:
            self._tick_claiming()

    # ----- 各状态实现 -----

    def _tick_idle(self) -> None:
        if time.time() >= self._idle_until:
            self._set_state(State.CASTING)

    def _tick_casting(self) -> None:
        input_controller.press_key(config.CAST_KEY)
        self._cast_time = time.time()
        self._last_f_tap = self._cast_time
        self._set_state(State.WAITING_BITE)

    def _tick_waiting_bite(self) -> None:
        now = time.time()

        # 先看青 bar 是否出现 —— 出现即说明进入拉鱼
        frame = screen_reader.capture_region(config.GAUGE_REGION)
        if screen_reader.bar_visible(frame):
            print("[WAITING_BITE] 检测到青 bar，进入拉鱼！")
            self._set_state(State.REELING)
            return

        # 超时还没上钩：重抛
        if now - self._cast_time > config.CAST_WAIT_MAX:
            print("[WAITING_BITE] 超时，重新抛竿")
            self._set_state(State.CASTING)
            return

        # 否则持续点 F（按固定间隔）
        if now - self._last_f_tap >= config.F_TAP_INTERVAL:
            input_controller.press_key(config.CAST_KEY)
            self._last_f_tap = now

    def _tick_reeling(self) -> None:
        """拉鱼阶段：以 CONTROL_FPS 的频率追踪黄针与青 bar，按 A/D 把针拉回 bar 中心。

        以阻塞循环执行整个拉鱼过程，每次迭代检查 running，使 F9 暂停即时生效。
        退出条件：超时，或连续多帧检测不到青 bar（视为拉鱼结束）。
        """
        frame_interval = 1.0 / config.CONTROL_FPS
        start = time.time()
        lost_ui_frames = 0
        lost_ui_limit = int(config.CONTROL_FPS * 1.0)  # 连续约 1 秒看不到青 bar 即结束

        while self.running:
            loop_start = time.time()

            if loop_start - start > config.FISHING_TIMEOUT:
                print("[REELING] 拉鱼超时，结束本轮")
                break

            frame = screen_reader.capture_region(config.GAUGE_REGION)
            offset = screen_reader.get_pointer_bar_offset(frame)

            if offset is None:
                # 找不到针或 bar：可能 bar 已消失（拉鱼结束）
                lost_ui_frames += 1
                if lost_ui_frames >= lost_ui_limit:
                    print("[REELING] 青 bar 消失，本轮结束")
                    break
            else:
                lost_ui_frames = 0
                input_controller.adjust_pointer(offset)

            # 控制帧率
            sleep_time = frame_interval - (time.time() - loop_start)
            if sleep_time > 0:
                time.sleep(sleep_time)

        # 拉鱼结束 -> 进入领取战利品阶段
        self._reel_end_time = time.time()
        self._set_state(State.CLAIMING)

    def _tick_claiming(self) -> None:
        """钓到鱼后等战利品界面弹出，随机点几下画面关闭，再回到 IDLE 等下一轮。"""
        # 等界面弹出
        if time.time() - self._reel_end_time < config.LOOT_WAIT:
            return

        for i in range(config.CLAIM_CLICKS):
            if not self.running:
                return
            input_controller.click()
            if i < config.CLAIM_CLICKS - 1:
                time.sleep(config.CLAIM_CLICK_INTERVAL)

        self._idle_until = time.time() + config.ROUND_INTERVAL
        self._set_state(State.IDLE)
