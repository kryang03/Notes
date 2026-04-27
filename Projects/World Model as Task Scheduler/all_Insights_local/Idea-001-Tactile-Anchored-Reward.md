---
tags: [insight, WMTS, real-robot-rl, world-model, sim-to-real]
aliases: [Tactile-Anchored Reward, TAR-WM]
created: 2026-04-27
status: draft
feasibility: A
novelty: A
target-venue: RSS / CoRL
related:
  - "[[Final_WMTS]]"
  - "[[WMTS_Reliability_Extensions]]"
  - "[[ContactMechanics]]"
  - "[[InformationTheory]]"
  - "[[Curiosity-Driven Exploration Recap]]"
  - "[[GenDexGrasp - Generalizable Dexterous Grasping]]"
  - "[[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]]"
---

# Idea-001: Tactile-Anchored World-Model Reward for Pose-Free Real-Robot RL

> [!abstract] 核心贡献（一句话）
> 我们提出 **Tactile-Anchored Reward (TAR)**，在真机上完全不依赖外部相机/Mocap 物体位姿的前提下，用**触觉接触图演化 + WM 隐空间预测一致性**作为强化学习信号，使 LinkerHand L25 上的真机 RL 微调首次得以无视觉、无 GT pose 闭环。

---

## 1. 问题定义与动机

### 1.1 大背景引入
真机灵巧操作 RL 的核心瓶颈不是策略表达力，而是**真机 reward 的可观测性**。仿真中可直接读取 $P_{obj}, R_{obj}$，真机端要么依赖外置 Mocap（侵入实验、丢失泛化）要么依赖 RGB-D + 实时位姿估计（受遮挡、物体外观变化、光照影响极大）。

### 1.2 现有方法的局限
- [[DeXtreme Recap|DeXtreme]] 真机依赖 Tracker + 8 路相机阵列；硬件成本高、移植困难。
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]] 用触觉做策略观测但 reward 仍来自仿真侧。
- [[DexterityGen Recap|DexterityGen]] 依赖人类演示 BC，无法在真机闭环优化。

### 1.3 我们的洞见
> [!tip] Key Insight
> WMTS 已经训练了一个能预测下一帧触觉张量 $\hat{z}_{tactile,t+1}$ 的 [[Final_WMTS#4.D 可靠信号与预测目标|Ensemble World Model]]。**WM 的预测准确性本身就是一个无需 GT 的稠密信号**：当真实触觉演化与 WM 预测一致时，说明系统状态在 WM 已知流形内（因此 Oracle 知识可外推）；不一致则说明系统脱离已知动力学（因此应该收敛回去）。配合接触拓扑的目标图，可构造完全 endogenous 的 reward。

### 1.4 贡献声明
1. 我们提出 **TAR（Tactile-Anchored Reward）** = α·接触拓扑相似度 + β·WM 触觉预测对数似然 + γ·信息增益惩罚。
2. 我们证明在 WMTS 架构下，TAR 与 GT-pose-based reward 的 Pearson 相关系数可超过 0.7（仿真 oracle 实验验证）。
3. 我们在 LinkerHand L25 上完成完全无视觉的 in-hand reorientation 真机微调，相对 zero-shot Diffusion 基线 drop rate 降低 ≥30%。

---

## 2. 方法论

### 2.1 问题形式化
给定真机轨迹 $\tau = (s_t, a_t, x_{tactile,t}, T_{motor,t})_{t=0}^{H}$，目标隐空间任务 $z_{task}$ 已知（来自 [[Final_WMTS#一、 仿真隐空间任务生成器 (Latent Task Generator)|Latent Task Generator]]），WM 给出 $(\mu_m, \Sigma_m)$。定义 reward：

$$
r_t^{TAR} = \alpha \cdot S_{topo}(x_{tactile,t}, \hat{\Omega}(z_{task},t)) + \beta \cdot \log \mathcal{N}(x_{tactile,t+1} | \mu_m, \Sigma_m) - \gamma \cdot \mathrm{tr}\,\mathrm{Cov}(\{\hat{x}_{tactile,t+1}^m\}_m)
$$

其中：
- $S_{topo}$：触觉激活 patch 与目标接触图 $\hat{\Omega}$ 的归一化交并比（IoU on binarized force map）。
- 第二项：WM 对触觉的对数似然，捕获"动力学一致性"。
- 第三项：高 ensemble disagreement 处惩罚，避免策略钻 WM 漏洞。

### 2.2 核心算法
```
Algorithm: TAR-Augmented Real-Robot AWAC
─────────────────────────────────────────
Input: pretrained Generalist π_θ, frozen WM ensemble {f_m}, Predictor P_ψ
For episode k = 1..K (real robot):
  1. Sample task z_task ~ Solve Queue (from Reliability Extensions §2.1)
  2. Compute target contact map: Ω̂_{1:H} = D_contact(z_task, o_shape)
  3. Rollout π_θ on real robot, collect τ
  4. For each t:  r_t = TAR(x_tactile,t, μ_m, Σ_m, Ω̂_t)
  5. Compute advantage A_t via WM-rolled value baseline V_φ(s_t)
  6. AWAC-update: L = E[exp(A_t/β) ‖ε - ε_θ‖²]
  7. Update WM with new transitions (Actuator Model only — see Idea-003)
```

### 2.3 理论分析
TAR 是 [[InformationTheory|Information-Theoretic]] 框架下的 surrogate reward：第一项是任务进度先验，第二项是数据流形上的负熵（保留在已知动力学内的 entropy bonus），第三项是认知不确定性惩罚。当 WM 校准良好时（calibrated ensemble），TAR 的期望与真实任务 reward 的差异可被 ensemble Bellman bound 控制。

### 2.4 实现细节
- 修改 `algos/diffusion_policy.py` 的 finetune loop：替换 sim reward query 为 `compute_tar_reward()`。
- 新增 `algos/tar_reward.py` 实现 TAR 三项与 contact map decoder $D_{contact}$。
- 配置：`configs/algo/Diffusion_Generalist.yaml` 新增 `tar: {alpha: 1.0, beta: 0.5, gamma: 0.2}` 字段。

---

## 3. 实验计划

### 3.1 Stage 0：仿真 Oracle 校准（Grid Search）
| 实验 ID | 自变量 | 因变量 | Grid 范围 | 预期 |
|---------|--------|--------|-----------|------|
| E0.1 | (α, β, γ) | Pearson(TAR, GT-reward) | α∈{0.5, 1, 2}, β∈{0.1, 0.5, 1}, γ∈{0, 0.2, 1} | (1, 0.5, 0.2) 最佳 |
| E0.2 | WM ensemble size $M$ | TAR 校准误差 | $M \in \{3,5,7\}$ | $M=5$ 拐点 |
| E0.3 | Contact map binarization 阈值 | $S_{topo}$ 区分度 | $\in \{0.05, 0.1, 0.2\}$ | 0.1 |

GPU: 27 configs × 3 seeds × 50M steps = ~3 days × 8 A100。

### 3.2 Stage 1：仿真闭环 AWAC 微调
对照：(a) GT-reward AWAC, (b) Sparse drop reward, (c) TAR (ours)。指标：success rate、tracking error、drop rate、与 GT-reward 训练的策略性能差距。

### 3.3 Stage 2：真机 30 分钟微调（4 物体，每物体 7 分钟）
指标：drop rate、平均连续旋转时长、温度峰值。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| WM 触觉预测在真机分布外（OOD）失效 | 中 | 高 | 用 Reliability Extensions §2.4 counterfactual loss 强化触觉 head；γ 项自动降低权重 |
| Reward Hacking：策略学会维持高接触但物体不动 | 中 | 高 | $S_{topo}$ 计算时归一化按接触面积；加入 task-progress soft floor |
| Contact map decoder $D_{contact}$ 训练数据不足 | 低 | 中 | 用 Oracle 仿真 rollout 离线训练 $D_{contact}$，作为 Stage 0 前置 |

---

## 5. 知识库关联

- [[Final_WMTS#5.4 通才微调策略|§5.4 AWAC]] — 直接替换 reward 来源
- [[WMTS_Reliability_Extensions#1.1 三类风险量|Reliability §1.1]] — γ 项与 dynamics epistemic uncertainty 同源
- [[GenDexGrasp - Generalizable Dexterous Grasping]] — Contact map decoder 设计参考
- [[Curiosity-Driven Exploration Recap]] — 信息增益项的理论依据

---

## 6. 动态迭代日志

> [!note] 🔄 实验结果追踪
> 实验结果由远端服务器 Agent 写入 `_ExperimentResultsAll.md`，本地 Agent 在每次会话同步到本节。

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 Grid Search | *待运行* | *待定* |

### 迭代记录
*实验结果到来后在此更新。*
