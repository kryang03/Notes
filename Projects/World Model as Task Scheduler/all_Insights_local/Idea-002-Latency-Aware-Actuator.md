---
tags: [insight, WMTS, real-robot-rl, actuator, sim-to-real]
aliases: [Latency-Aware Actuator Adaptation, LAAA]
created: 2026-04-27
status: draft
feasibility: A
novelty: A
target-venue: ICRA / RSS
related:
  - "[[Final_WMTS]]"
  - "[[Actuator2RigidDynamicsModel_gap]]"
  - "[[FOC_Control]]"
  - "[[ANYmal Parkour Recap]]"
  - "[[Learning Agile and Dynamic Motor Skills for Legged Robots]]"
  - "[[Finetuning Offline WM Recap]]"
---

# Idea-002: CAN-Latency-Conditioned Actuator Network for Online Real-Robot Adaptation

> [!abstract] 核心贡献（一句话）
> 我们将 [[Actuator2RigidDynamicsModel_gap#2.5 ms 指间相位差|CAN bus 指间相位差 (5–20 ms)]] 显式建模为一个**可观测的随机延迟变量**，让 Actuator Network 以 latency token 为条件进行 FiLM 调制，使真机 Actuator Model 能在不重训 Rigid 部分的前提下，用 ≤5 分钟真机数据完成在线适应。

---

## 1. 问题定义与动机

### 1.1 大背景引入
[[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|WMTS Actuator Model]] 与 [[ANYmal Parkour Recap|ANYmal Actuator Network]] 都假设指令到力矩的映射是 deterministic 的延迟函数。但灵巧手的 CAN 1Mbps 总线在 16 路并行写入下，延迟方差极大（[[Actuator2RigidDynamicsModel_gap#4.1 高频感知的总线瓶颈|2.5 ms 指间相位差]] + 仲裁不确定 5–20 ms）。仿真完全忽略此源，是 Actuator sim-to-real gap 的隐藏元凶。

### 1.2 现有方法的局限
- [[ANYmal Parkour Recap|ANYmal Actuator Network]]：固定 30 ms 历史窗口，假设延迟 stationary。
- [[Learning Agile and Dynamic Motor Skills for Legged Robots]]：测量延迟均值后做常量补偿。
- [[Finetuning Offline WM Recap|FOWM]]：真机微调整个 WM，破坏已学好的 Rigid 部分。

### 1.3 我们的洞见
> [!tip] Key Insight
> CAN 帧的发送时间戳 $t_{send}$ 与执行时间戳 $t_{exec}$ 的差值 $\delta_t$ 是**可观测**的（CAN driver 可读 timestamp）。如果把 $\delta_t$ 作为 conditioning token 馈入 Actuator Network 的 FiLM 层，网络在仿真就可以用 randomized latency 学到延迟相关的非线性补偿，真机部署时只需更新 latency-conditioned 子网（小参数量）。

### 1.4 贡献声明
1. 我们提出 **Latency-token FiLM Actuator Network**：$\hat{\tau}_{link} = f_{act}(x_{act}; \mathrm{FiLM}(z_\delta(\delta_{t-H:t})))$。
2. 我们证明仿真中加入 randomized latency 训练可使真机 Actuator MSE 降低 ≥40%（相对固定窗口基线）。
3. 我们提出 **Frozen-Rigid 在线适应**：仅更新 FiLM 参数，使 5 分钟真机数据足以收敛。

---

## 2. 方法论

### 2.1 问题形式化
扩展 [[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|Actuator Model 输入]]：

$$
\mathbf{x}_{act,t} = [a_{t-H:t}, \phi_{t-H:t}, \dot{\phi}_{t-H:t}, \tau_{fb,t-H:t}, T_{motor,t}, \boldsymbol{\delta}_{t-H:t}]
$$

其中 $\boldsymbol{\delta}_{t-H:t} \in \mathbb{R}^{16 \times (H+1)}$ 是每个关节最近 $H$ 帧的 CAN latency。FiLM 调制：

$$
h_l = \gamma_l(z_\delta) \odot \mathrm{MLP}_l(h_{l-1}) + \beta_l(z_\delta), \quad z_\delta = E_\delta(\boldsymbol{\delta}_{t-H:t}).
$$

### 2.2 核心算法
```
Stage A (sim, 1× train):
  - Domain randomize δ ~ Mixture(N(5, 2²), N(15, 5²)) per-frame, per-joint
  - Train f_act + E_δ + FiLM end-to-end with sim torque GT (since sim has true τ_link)
  - Train Rigid Dynamic Model conditioned on τ̂_link as before

Stage B (real, ≤5 min data):
  - Collect (a, φ, φ̇, τ_fb, T, δ) on real robot via slow scripted motions
  - Freeze MLP_l, only update γ_l, β_l, E_δ params (≤5% of total params)
  - Self-supervised loss: L = ‖φ_{t+1} - φ̂_{t+1}(rollout via f_dyn ∘ f_act)‖²
```

### 2.3 理论分析
FiLM 调制等价于在每层学习一个 latency-conditioned linear transform。由于 latency 影响主要是延迟相关的相位偏移（线性时变系统），FiLM 是最小充分参数化。Frozen-Rigid 保证了 sim 阶段学到的物理动力学不被真机噪声破坏（避免灾难性遗忘）。

### 2.4 实现细节
- 新增 `algos/world_model/latency_film_actuator.py`，含 `LatencyEncoder` 和 `FiLMBlock`。
- 修改 `envs/isaac_gym/domain_randomization.py` 加入 per-step latency 模拟（用 frame buffering 实现）。
- 真机端：`envs/real_robot/can_interface.py` 已有 timestamp，需 export 为 obs 字段。
- 配置：`configs/world_model/Ensemble.yaml` 新增 `latency_film: {enabled: true, hidden: 64}`。

---

## 3. 实验计划

### 3.1 Stage 0：仿真延迟分布敏感度
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | latency 分布 σ | Actuator MSE on held-out δ | σ ∈ {1, 3, 5, 10} ms | σ=5 最 robust |
| E0.2 | FiLM 层数 | 适应数据量 vs MSE | layers ∈ {1, 2, 4} | 2 层足够 |
| E0.3 | $E_\delta$ 编码器架构 | 适应速度 | {MLP, 1D-CNN, Transformer} | 1D-CNN |

8 A100 × 2 days。

### 3.2 Stage 1：真机适应曲线
- 数据量 ∈ {1, 2, 5, 10, 20} min
- 对照：(a) Frozen Rigid + Frozen Act, (b) 全 WM 微调, (c) Ours (Frozen Rigid + FiLM-only)
- 指标：Actuator MSE、Rigid Dynamic Forecast Error（评估是否破坏 Rigid 知识）

### 3.3 Stage 2：下游 RL 性能
将适应后的 WM 喂给 [[Final_WMTS#5.4 通才微调策略|AWAC 微调]]，看 Generalist drop rate 和 tracking error。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| CAN driver 无法稳定输出 timestamp | 低 | 高 | 在 `can_interface.py` 注入软件层时间戳；fallback 到 IMU 同步 |
| 真机 latency 分布在仿真 mixture 之外 | 中 | 中 | mixture 用宽 prior，必要时 Stage B 加入新 mode |
| FiLM 容量不足以表达高阶非线性 | 低 | 中 | 升级为 LoRA-style 残差 adapter |

---

## 5. 知识库关联

- [[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|§4.A]] — 直接扩展输入定义
- [[Actuator2RigidDynamicsModel_gap#三、 L25 灵巧手 CAN 协议与可读取量分析|L25 CAN 分析]] — latency 物理来源
- [[FOC_Control#5.2 电流环带宽|FOC §5.2]] — 电流环带宽与延迟的耦合关系
- 与 [[WMTS_Reliability_Extensions#2.4 Ensemble WM：Actuator-Rigid counterfactual loss|Reliability §2.4]] 互补：本 Idea 解决 Actuator 的 sim-to-real gap，counterfactual loss 解决两 head 互相背锅
- [[RepresentationLearning#6.3.7 神经正切核 (Neural Tangent Kernel, NTK)|NTK lazy training]] — 为“大 WM + < 1h 真机数据 + frozen-rigid + 5min 适配”提供严格理论依据：在 NTK 邻域内微调等价于固定 kernel 核回归，防止灾难性遗忘
- [[ControlTheory#12. 自适应控制与确定性等价原理 (Adaptive Control & Certainty Equivalence)|经典自适应控制]] — FiLM 隐变量 $z(t)$ 是 MRAC $\hat\theta(t)$ 的深度学习版；PE 条件（[[ControlTheory#12.4 PE 与参数收敛的桥梁|§12.4]]）给出了"采集多少分布的激励轨迹才能保证 5min 适配收敛"的理论判据
- [[ControlTheory#9.3.2 带噪声数据的鲁棒镇定|噪声数据鲁棒镇定]] — 把真机短轨迹视为 $X_+=AX_-+BU_-+W_-$，用 LMI 检查所有一致 actuator 模型是否共享稳定性证书；作为 Stage B 适配成功的安全判据

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
