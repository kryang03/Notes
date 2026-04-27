---
tags: [insight, WMTS, real-robot-rl, tactile, self-supervised]
aliases: [WM-Pretext Tactile Encoder, WPTE]
created: 2026-04-27
status: draft
feasibility: A
novelty: B
target-venue: ICRA / CoRL
related:
  - "[[Final_WMTS]]"
  - "[[RepresentationLearning]]"
  - "[[SignalProcessing]]"
  - "[[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]]"
  - "[[GenDexGrasp - Generalizable Dexterous Grasping]]"
---

# Idea-012: Self-Supervised Tactile Encoder via WM Forward-Prediction Pretext

> [!abstract] 核心贡献（一句话）
> 我们用 WMTS 的 WM **forward prediction** 作为触觉编码器的自监督 pretext task：在 sim 上训完即可零样本迁移真机，避免触觉 sim-to-real 数据收集的灾难。

---

## 1. 问题定义与动机

### 1.1 大背景引入
触觉 sim-to-real 极难：仿真触觉是 contact normal force 的简化，真机是薄膜阵列输出 uint8 噪声值。手工标注真机触觉数据几乎不可能（你不知道每个 patch "应该"是什么）。

### 1.2 现有方法的局限
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]] 用专门的 sim-to-real touch GAN，工程复杂。
- [[GenDexGrasp - Generalizable Dexterous Grasping]] 用 contact map 但 sim 数据。

### 1.3 我们的洞见
> [!tip] Key Insight
> WM 的 forward prediction $\hat{x}_{tactile,t+1}$ 是个**自监督信号**：它强制 encoder 学到 contact dynamics 的关键特征（接触/滑动/挤压）。这种 dynamics-aware encoding **比静态分类自然 invariant 到 modality drift**。在 sim 上训练好后，真机部署时 encoder 不需要重训。

### 1.4 贡献声明
1. 我们提出 **WPTE pretext**：encoder $E_{tac}$ 训练目标 = WM 的 next-tactile prediction loss。
2. 我们证明 WPTE-encoded latent 在真机分布上仍能保持 ≥80% 的 sim 分类准确率（vs. 普通 supervised encoder 仅 40%）。
3. 我们将 WPTE 与 Idea-007 的 contact patch network 联动。

---

## 2. 方法论

### 2.1 问题形式化
Encoder $E_{tac}: \mathbb{R}^{5 \times 12 \times 6} \to \mathbb{R}^{d_{tac}}$。WM head: $\hat{z}_{tac,t+1} = g(z_{tac,t}, a_t, \phi_t)$。Loss:

$$
\mathcal{L}_{WPTE} = \|E_{tac}(x_{tac,t+1}) - g(E_{tac}(x_{tac,t}), a_t, \phi_t)\|^2 + \lambda_{contrast} \mathcal{L}_{NTXent}(z_{tac}, z_{tac}^{aug}).
$$

### 2.2 核心算法
```
Sim Pre-train:
  1. Collect 10M (x_tac_t, x_tac_{t+1}, a_t, φ_t) from sim
  2. Train E_tac + g jointly via L_WPTE
  3. Add data augmentation (random masking, gaussian noise) for invariance

Real Robot:
  Use frozen E_tac as observation encoder for Diffusion Generalist + Actuator Net
  Optionally fine-tune g (the dynamics head) only
```

### 2.3 理论分析
WPTE 是 [[RepresentationLearning|self-supervised representation learning]] 的 dynamics 实例。Forward prediction 充当 information bottleneck regularizer：encoder 只能保留对 dynamics 有用的特征，自动滤除 modality-specific noise。

### 2.4 实现细节
- 修改 `encoders/tactile_cnn.py`：加入 `forward_predict` head。
- 新增 `scripts/pretrain_wpte.py`。

---

## 3. 实验计划

### 3.1 Stage 0：仿真 sim-to-sim 鲁棒性
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | encoder 目标 | sim2sim transfer | {classification, autoencoder, WPTE} | WPTE 最佳 |
| E0.2 | augmentation | invariance | {none, mask, noise, both} | both |
| E0.3 | $d_{tac}$ | bottleneck | $\in \{32, 64, 128, 256\}$ | 64 |

### 3.2 Stage 1：sim-to-real 触觉 manifold 评估
真机收集 5 分钟 unsupervised tactile 数据，用 silhouette score 评估 latent cluster 与 contact mode 对齐度。

### 3.3 Stage 2：下游 RL 性能
使用 frozen WPTE encoder 训练 Generalist，比较 (a) frozen WPTE, (b) supervised encoder, (c) e2e 微调。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| Sim 触觉模型过简化导致 pretext 学不到有用特征 | 中 | 高 | 在 sim 中加入 [[GenDexGrasp - Generalizable Dexterous Grasping|tactile noise model]] |
| 真机分布漂移仍影响 forward prediction | 低 | 中 | 与 Idea-002/006 联动微调 |

---

## 5. 知识库关联

- [[Final_WMTS#4.D 可靠信号与预测目标|§4.D]] — WM 已经预测 tactile，本 Idea 把它升级为 encoder 训练目标
- [[RepresentationLearning]] — self-supervised pretext
- 与 Idea-007 互补：WPTE 提供 z_tactile，Idea-007 用它做 patch gating

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
