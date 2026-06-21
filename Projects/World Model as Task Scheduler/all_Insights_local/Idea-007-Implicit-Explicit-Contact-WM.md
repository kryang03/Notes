---
tags: [insight, WMTS, real-robot-rl, contact, world-model]
aliases: [Implicit-Explicit Contact WM, IECW]
created: 2026-04-27
status: draft
feasibility: B
novelty: A
target-venue: RSS / CoRL
related:
  - "[[Final_WMTS]]"
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
  - "[[Deep Dynamics Models for Learning Dexterous Manipulation]]"
  - "[[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]]"
  - "[[GenDexGrasp - Generalizable Dexterous Grasping]]"
---

# Idea-007: Implicit-Explicit Contact World Model with Tactile-Conditioned Patches

> [!abstract] 核心贡献（一句话）
> 我们将 [[Final_WMTS#4.B Rigid Dynamic Model：力矩 → 状态演进|Rigid Dynamic Model]] 拆为 **解析刚体动力学（基础项）+ tactile-conditioned 隐式接触补丁（残差项）**，让 contact patch 模型仅在触觉感知到接触时被激活，使 WM 在 contact-rich 时刻预测精度大幅提升而 free-flight 时不引入噪声。

---

## 1. 问题定义与动机

### 1.1 大背景引入
灵巧操作的核心难点在 contact mode switching。当前 WMTS Rigid Net 是 monolithic MLP，把 free-flight 与 contact-rich 混在同一网络学，其表达力被均摊。

### 1.2 现有方法的局限
- [[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]：纯神经，未利用解析先验。
- [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model|DexNDM]]：joint-wise 但仍 monolithic。
- [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|Semi-structured Dynamics]]：解析+残差但用于 legged，未做 contact-mode 分流。

### 1.3 我们的洞见
> [!tip] Key Insight
> Contact 与 non-contact 是**完全不同的动力学**（discontinuous LCP）。把它们建在同一网络是建模错配。我们用 tactile latent 做 soft gate $\sigma(z_{tactile})$，激活 contact patch network；free-flight 时 patch 输出近零，让解析刚体动力学接管。

### 1.4 贡献声明
1. 我们提出 **Implicit-Explicit Contact WM**：

   $$\hat{s}_{t+1} = \underbrace{f_{rigid}^{analytic}(s_t, \tau_{link})}_{\text{解析骨架}} + \sigma(z_{tactile}) \odot \underbrace{f_{patch}(s_t, \tau_{link}, z_{tactile})}_{\text{隐式补丁}}.$$

2. 我们证明该分解使 contact-rich 步预测精度提升 ≥35%，free-flight 步预测无退化。
3. 我们展示 Sim-to-Real 时仅需微调 $f_{patch}$（~10% 参数）即可适应。

---

## 2. 方法论

### 2.1 问题形式化
解析项 $f_{rigid}^{analytic}$ 来自 IsaacGym 的 articulated body equations（已知 mass / inertia）。Patch $f_{patch}$ 是 condition on $z_{tactile}$ 的 MLP，输出维度同 state。Gate $\sigma(\cdot)$ 是 tactile activation 的 sigmoid。

### 2.2 核心算法
```
Train (sim):
  L_total = ‖s_{t+1} - ŝ_{t+1}‖² + λ_gate · ReLU(σ(z_tactile) - σ_max)
  - λ_gate 鼓励 gate 稀疏（only activate on real contact）

Real-Robot Adapt:
  Freeze f_rigid^analytic (it's exact physics)
  Freeze gate σ
  Update only f_patch with real τ_fb-driven trajectories
```

### 2.3 理论分析
此分解直接对应 [[ContactMechanics|complementarity formulation]]：解析项是 frictionless 刚体演化，patch 是 contact wrench 残差。Gate 的稀疏正则保证不"借助"非接触状态做预测。

### 2.4 实现细节
- 新增 `algos/world_model/iecw.py`：包含 `AnalyticRigidLayer`（调 IsaacGym physics API 或 differentiable physics like Brax）和 `ContactPatchNet`。
- 修改 `world_model/ensemble.py` 用 `IECW` 替换默认 `RigidDynNet`。

---

## 3. 实验计划

### 3.1 Stage 0：仿真消融
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | architecture | contact-step MSE | {monolithic, IECW, IECW-no-gate} | IECW 最佳 |
| E0.2 | $\lambda_{gate}$ | gate sparsity vs accuracy | $\in \{0, 0.1, 1, 10\}$ | 1.0 |
| E0.3 | analytic backend | speed vs accuracy | {Brax, IsaacGym, MuJoCo} | Brax (differentiable) |

### 3.2 Stage 1：仿真 contact-rich benchmark
任务：物体形状切换、接触点切换、急停。指标：contact-step prediction NLL、free-flight prediction NLL、整体 success rate。

### 3.3 Stage 2：真机 patch 微调
真机 30 分钟，仅微调 $f_{patch}$，比较与 monolithic 全微调的 sample 效率。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| 解析项 IsaacGym 不可微，限制端到端训练 | 中 | 中 | 用 Brax 或 MuJoCo MJX 实现 differentiable 解析层 |
| Gate 学到 trivial constant | 中 | 中 | $\lambda_{gate}$ 调度 + tactile-content regularizer |
| Patch 网络过拟合 sim contact | 中 | 高 | DR 接触参数；与 Idea-003 失败模式课程联动 |

---

## 5. 知识库关联

- [[Final_WMTS#4.B Rigid Dynamic Model：力矩 → 状态演进|§4.B]] — 直接重构对象
- [[ContactMechanics]] — 理论基础
- [[WMTS_Reliability_Extensions#1.1 三类风险量|Reliability §1.1]] — Contact feasibility 与 patch 输出可联动

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
