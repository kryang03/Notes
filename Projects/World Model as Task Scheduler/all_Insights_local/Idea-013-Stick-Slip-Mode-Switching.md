---
tags: [insight, WMTS, real-robot-rl, scheduler, multi-policy]
aliases: [Stick-Slip Mode Policy Switcher, SSMS]
created: 2026-04-27
status: draft
feasibility: A
novelty: A
target-venue: ICRA / CoRL
related:
  - "[[Final_WMTS]]"
  - "[[Actuator2RigidDynamicsModel_gap]]"
  - "[[FOC_Control]]"
  - "[[ControlTheory]]"
---

# Idea-013: WM-Triggered Stick-Slip Mode Policy Switching

> [!abstract] 核心贡献（一句话）
> 我们利用 [[Actuator2RigidDynamicsModel_gap#5.2 丝杠传动的 Stribeck 摩擦|Stribeck 摩擦的 stick-slip]] 物理特性，训练**两套互补的子策略**（slow-precision / dynamic-burst），用 WM 实时检测 $\dot{\phi} \approx 0$ 的 stick 状态触发 burst 子策略，避免单策略在两种工况下都不优。

---

## 1. 问题定义与动机

### 1.1 大背景引入
[[Actuator2RigidDynamicsModel_gap#5.2 丝杠传动的 Stribeck 摩擦|行星滚柱丝杠]] 在 $\dot{\phi}$ 过零点存在 stick-slip。单一 Diffusion 策略既要会"温柔精细操作"又要会"突破静摩擦的瞬时高力矩 burst"，是冲突目标——表现为常见的"卡死"现象。

### 1.2 现有方法的局限
- [[ControlTheory|阻抗控制]]：手工切换策略，无 RL 探索能力。
- [[Diffusion Policy: Visuomotor Policy|Diffusion Policy]]：单策略 multimodal 表达，但 burst 模式数据少，被均值化。

### 1.3 我们的洞见
> [!tip] Key Insight
> Stick-slip 是 actuator-level 物理现象，应该用 **actuator-level 调度**：WM 检测到 $|\dot{\phi}| < v_{slip}$ 且 $|\tau_{cmd}| < F_s$（即将 stick）时，自动切换到 burst sub-policy。这是 **physics-driven hierarchical control with RL**，比纯 hierarchical RL 更 grounded。

### 1.4 贡献声明
1. 我们提出 **SSMS** — 一对子策略 $\pi_{slow}, \pi_{burst}$ + WM-based dispatcher。
2. 我们证明 stick 状态识别准确率 > 95%（用 WM Actuator output + φ̇ 阈值）。
3. 我们在 LinkerHand 上展示 SSMS 减少卡死时长 ≥50%。

---

## 2. 方法论

### 2.1 问题形式化
Stick condition: $\mathcal{C}_{stick}(s_t) = \mathbb{1}[|\dot{\phi}_t| < v_{slip} \wedge \rho_{act,t} < \rho_{stuck}]$。

Dispatcher: $\pi(a|s) = (1 - \mathcal{C}_{stick}) \pi_{slow}(a|s) + \mathcal{C}_{stick} \pi_{burst}(a|s)$。

### 2.2 核心算法
```
Train (sim):
  Two PPO Oracles:
    π_slow trained with reward weighted toward smooth-low-jerk
    π_burst trained with reward weighted toward break-stiction-fast
  Distill into two Diffusion sub-policies via separate codebooks
  Train dispatcher on history + WM output → binary mode

Real Robot:
  Each step: WM computes ρ_act, detect stick → dispatch to burst (max 100ms)
  After break: smooth handover back to slow
```

### 2.3 理论分析
SSMS 是 **physics-grounded mode-switching control**——比通用 hierarchical RL 优势在于切换条件直接来自动力学方程而非学习的 termination function。

### 2.4 实现细节
- 修改 `algos/diffusion_policy.py` 支持 dual policy。
- 新增 `algos/ssms_dispatcher.py`：检测 + 调度。
- 配置：`configs/algo/SSMS.yaml` — `v_slip: 0.05, rho_stuck: 0.3, burst_duration: 0.1`。

---

## 3. 实验计划

### 3.1 Stage 0：仿真注入 stick-slip
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | $v_{slip}, \rho_{stuck}$ | stick detection F1 | grid | F1 > 0.9 |
| E0.2 | burst duration | smooth recovery rate | $\in \{50, 100, 200, 500\}$ ms | 100ms |
| E0.3 | dispatcher 类型 | switching smoothness | {hard, soft, learned gate} | soft |

### 3.2 Stage 1：仿真闭环
比较：(a) single Diffusion, (b) impedance + Diffusion, (c) SSMS。指标：卡死时长比例、jerk 峰值、success rate。

### 3.3 Stage 2：真机 5 分钟测试
真机执行精细抓取 + 快速翻转交替任务，记录 stick 频率与 SSMS 解锁时长。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| Burst 策略导致触觉传感器损坏 | 低 | 高 | burst 力矩 cap + 温度 monitor |
| Mode 切换过频繁产生 chattering | 中 | 中 | hysteresis + min-dwell 时间 |
| 真机 $\dot\phi$ 估计噪声触发误识别 | 中 | 中 | 卡尔曼滤波 + 多步 confirmation |

---

## 5. 知识库关联

- [[Actuator2RigidDynamicsModel_gap#5.2 丝杠传动的 Stribeck 摩擦|Stribeck 模型]] — 物理基础
- [[ControlTheory]] — 切换控制理论
- [[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|§4.A Actuator Model]] — $\rho_{act}$ 来源

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
