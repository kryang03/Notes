---
tags: [insight, WMTS, real-robot-rl, autonomy, reset-free]
aliases: [Reset-Free WMTS, RF-WMTS]
created: 2026-04-27
status: draft
feasibility: B
novelty: A
target-venue: RSS / CoRL
related:
  - "[[Final_WMTS]]"
  - "[[WMTS_Reliability_Extensions]]"
  - "[[ANYmal Parkour Recap]]"
  - "[[Curiosity-Driven Exploration Recap]]"
---

# Idea-015: Reset-Free Real-Robot WMTS via WM-Estimated Recovery Policies

> [!abstract] 核心贡献（一句话）
> 我们消除真机 RL 的人工 reset 瓶颈：在 WMTS 中训练 **inverse 任务策略 $\pi_{recover}$**，每次任务 $z_{forward}$ 失败/完成后，$\pi_{recover}$ 把物体送回有效初始状态，全自主无人值守 24h 真机训练。

---

## 1. 问题定义与动机

### 1.1 大背景引入
真机 RL 最隐藏的成本是**reset**。每次掉落或任务完成都需要人工拾取物体放回手中，这使得 24h 自主训练几乎不可能。

### 1.2 现有方法的局限
- 工业机器人 reset：固定挡板/夹具，无法用于 in-hand reorientation。
- [[ANYmal Parkour Recap|locomotion]]：用恢复 controller 自动起立——可移植思想但 manipulation 没有等价物。

### 1.3 我们的洞见
> [!tip] Key Insight
> 在 [[Final_WMTS#一、 仿真隐空间任务生成器 (Latent Task Generator)|latent task space]] 中，"reset" 等价于一个 **inverse task** $z_{recover} = z_{home} - z_{forward}$。WMTS 已经能生成任意 $z$ 的 Oracle 策略——所以 $\pi_{recover}$ 是免费的副产品。再加桌面安全网（防掉落）+ 简单视觉 trigger 检测物体位置即可。

### 1.4 贡献声明
1. 我们提出 **Inverse-Task Recovery Policy**：在 latent task space 中定义 reset 任务，复用 Oracle/Generalist 框架训练。
2. 我们设计**最简硬件**安全网：桌面 + 单 RGB 相机 + Oracle 触发的 pick-up 子程序。
3. 我们展示 LinkerHand 实现 8 小时连续无人值守 RL 微调，等价于 ~100 次成功 + 失败 episode。

---

## 2. 方法论

### 2.1 问题形式化
Forward task $z_f$，target home state $z_{home}$。Recovery task: $z_r$ such that执行后状态接近 $z_{home}$。Two policies:

- $\pi_{forward}(a|s, z_f)$ — main task
- $\pi_{recover}(a|s, z_r)$ — bring back to home

Switch trigger: terminal condition (drop / complete) + simple object localization.

### 2.2 核心算法
```
Setup (one-time):
  Define z_home (e.g. object centered, fingers in nominal pose)
  Train Oracle for both forward and recover task families in sim
  Distill both into one Diffusion conditioned on task type token

Real Robot (autonomous loop):
  while True:
    Run π_forward until termination (drop or success or timeout)
    Detect object location via RGB cam (cheap method, e.g. blob detection)
    if object on table: pick-up subroutine
    Run π_recover to nominal pose
    Log transition to buffer
    Periodically update WM (Idea-008 PA-PER)
```

### 2.3 理论分析
Reset-free RL 的核心是保证 state 不漂移到 "absorbing dead state"。本设计通过物理安全网 + recovery policy 提供了**状态空间紧凑性**保证。Recovery policy 训练在 latent task space 自然受 [[WMTS_Reliability_Extensions|reliability constraint]] 约束，避免不安全 reset 动作。

### 2.4 实现细节
- 新增 `scripts/autonomous_real_loop.py`。
- 修改 `envs/real_robot/`：加入 `pickup_subroutine.py` 和 `simple_object_localizer.py`。
- 配置：`configs/real/Autonomous.yaml`。

---

## 3. 实验计划

### 3.1 Stage 0：仿真测试自治循环
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | recovery 策略类型 | reset success rate | {scripted, oracle, diffusion} | diffusion |
| E0.2 | trigger 灵敏度 | false reset rate | percentile | 95% |
| E0.3 | $z_{home}$ 选择 | reset 时间 | {centered, pose-1, pose-2} | centered |

### 3.2 Stage 1：真机 8 小时连续运行
指标：成功 / 失败 episode 数、人工干预次数、温度峰值、是否物理损伤。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| 物体掉桌面外 | 中 | 高 | 物理围栏 + 软垫 + 最大 episode 时长 cap |
| Recovery 策略本身导致掉落 | 中 | 中 | 用 Idea-004 WM-guided diffusion 加 safety guidance |
| 视觉触发误判 | 中 | 中 | 多模态确认（视觉 + 触觉接触图） |
| 长时间运行 actuator 过热 | 高 | 中 | 强制 5min 冷却 / 30min 工作循环 |

---

## 5. 知识库关联

- [[Final_WMTS]] — 复用 Oracle/Generalist 框架
- [[WMTS_Reliability_Extensions#2.5 Safety Filter：下置信界放行|Reliability §2.5]] — recovery 也受 LCB 保护
- 这是其它所有 Idea 真机阶段的基础设施 — 没有 reset-free，所有 real-robot RL ideas 都难规模化

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
