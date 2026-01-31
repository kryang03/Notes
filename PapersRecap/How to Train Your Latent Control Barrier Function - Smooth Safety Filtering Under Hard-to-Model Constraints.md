---
tags:
  - paper-recap
  - control-barrier-function
  - safety-filtering
  - world-model
  - visuomotor-control
  - hamilton-jacobi-reachability
aliases:
  - LatentCBF
  - Latent Control Barrier Function
created: 2026-01-31
venue: arXiv 2511.18606
year: 2025
authors:
  - Kensuke Nakamura
  - Arun L. Bishop
  - Steven Man
  - Aaron M. Johnson
  - Zachary Manchester
  - Andrea Bajcsy
institution: Carnegie Mellon University
---

# How to Train Your Latent Control Barrier Function

> [!abstract] 核心贡献
> 提出 **LatentCBF**，解决了在隐空间中进行基于优化的安全过滤（CBF-style filtering）的两个关键挑战：(1) 分类器生成的 margin function 梯度饱和；(2) 安全策略与任务策略的分布失配导致值函数估计不准。

## 1. 问题设定与动机

### 1.1 为什么需要隐空间 CBF？

现代视觉运动策略（如 Diffusion Policy）直接从 RGB 图像输入执行复杂任务，但传统安全滤波器假设：
- 完全可观测的状态空间
- 已知的动力学模型
- 可解析定义的安全约束

**实际场景挑战**：
- 状态表示复杂且部分可观测（如可变形物体）
- 动力学模型或仿真器不可用
- 安全约束极难解析指定（如"不洒出袋子里的东西"）

### 1.2 现有方法的局限

**Least-Restrictive Filtering（最小限制过滤）**：
- 在名义策略和安全策略之间**离散切换**
- 一旦切换到安全策略，任务性能严重下降（如机械臂停止抬起袋子）

**理想方案：CBF 优化式过滤**
$$a^* = \argmin_{a \in \mathcal{A}} \|a - \pi^{\text{nom}}(s)\|, \quad \text{s.t.} \quad B(f(s,a)) \geq \alpha B(s)$$

最小调整名义策略动作，同时满足安全约束。

---

## 2. 理论分析：为什么现有方法失效

### 2.1 Challenge 1: 光滑值函数需要光滑 Margin Function

**问题根源**：使用二分类器作为 margin function $\ell(z)$

分类器在安全/危险边界处产生**饱和梯度**，导致 CBF 无法评估动作的相对安全性。

> [!theorem] Margin-to-Value Lipschitz Bound
> 设 margin function $\ell(s)$ 和 HJ 值函数 $V^\diamond(s)$ 的 Lipschitz 常数分别为 $L_\ell$ 和 $L_{V^\diamond}$，动力学 $f(s,a)$ 对状态的 Lipschitz 常数为 $L_f$，且 $\gamma L_f < 1$，则：
> $$L_{V^\diamond} \leq L_\ell \cdot \max\left\{1, \frac{1-\gamma}{1-\gamma L_f}\right\}$$
> 
> **推论**：值函数的光滑性**线性依赖**于 margin function 的光滑性。

![[latent_cbf_smoothness.png]]
*左：分类器 margin → 饱和 CBF，所有采样动作安全值相似；右：光滑 margin → 有区分度的 CBF*

### 2.2 Challenge 2: 分布失配

**Actor-Critic RL 训练**：Replay Buffer 只包含安全策略 $\pi^\diamond$ 产生的状态-动作对

**部署时**：CBF 需要评估任务策略 $\pi^{\text{nom}}$ 的动作安全性

**结果**：Critic 对任务相关动作的值估计不准确——恰恰是 CBF 过滤最需要的地方！

---

## 3. LatentCBF 方法

### 3.1 光滑 Margin Function via WGAN

受 Wasserstein GAN 启发，使用梯度惩罚学习光滑判别器：

$$\mathcal{L}_{\text{WGAN}} = \lambda_{zs} \cdot \left(\mathbb{E}_{z^- \sim \mathcal{D}_{\text{fail}}}[\ell_\mu(z^-)] - \mathbb{E}_{z^+ \sim \mathcal{D}_{\text{safe}}}[\ell_\mu(z^+)]\right) + \lambda_{gp} \cdot \mathbb{E}_{\hat{z} \sim \mathcal{D}_{\text{interp}}}\left[(\|\nabla_{\hat{z}} \ell_\mu(\hat{z})\|_2 - \beta)^2\right]$$

其中：
- $\hat{z}$ 是安全/危险样本的线性插值
- 梯度惩罚正则化 Lipschitz 常数趋向 $\beta$

**关键优势**：**无需额外标注**，仅用二分类标签即可获得光滑 margin

### 3.2 混合策略采样

同时从安全策略和任务策略采集轨迹填充 Replay Buffer：

$$\mathcal{B} = \{(z, a, \ell, z', a')_i\}$$

其中 $a, a'$ 以 50% 概率来自 $\pi^\diamond$ 或 $\pi^{\text{nom}}$

**效果**：Critic 学习在任务相关动作区域的准确安全估计

### 3.3 采样优化安全过滤

离散时间 CBF 优化是非凸问题，使用零阶优化：

1. 从 $\pi^{\text{nom}}$ 和 $\pi^\diamond$ 混合分布采样动作
2. 筛选满足 CBF 约束的动作子集 $\mathcal{A}_{\text{CBF-Safe}}$
3. 返回与名义动作最接近的安全动作

**性能**：7.6k 样本在 7-DoF 机械臂上仅需 10ms

---

## 4. 实验结果

### 4.1 仿真基准（3D Dubins' Car）

| 方法 | 安全率 | 干预平滑度 |
|------|--------|-----------|
| Least-Restrictive | 100% | 基准 |
| CBF (NoGP) | 100% | 较差 |
| **LatentCBF (Ours)** | 100% | **↓45% 更平滑** |

### 4.2 视觉操作硬件实验（Franka + Bag Pickup）

| 方法 | 安全任务成功率 |
|------|----------------|
| Least-Restrictive | 38% |
| **LatentCBF** | **80%** (2.1×↑) |

**定性结果**：
- Least-Restrictive 一旦检测到风险就切换到安全策略并**停止**
- LatentCBF **引导** Diffusion Policy 调整抓取位置，成功完成任务

---

## 5. 核心洞见

> [!tip] 设计光滑安全滤波器的关键
> 1. **Margin function 的光滑性传递到值函数** — 使用梯度惩罚而非硬分类器
> 2. **值函数需要在部署分布上准确** — 混合任务策略数据进行训练
> 3. **CBF 优化式过滤优于离散切换** — 保持任务性能的同时确保安全

### 与 [[ControlTheory]] 的联系

- **Control Barrier Function** 是保证安全不变集的经典工具
- 本文将 CBF 扩展到**隐空间**，适配现代端到端视觉策略
- **Hamilton-Jacobi Reachability** 提供了构造有效 CBF 的数学基础

### 与 [[ReinforcementLearning]] 的联系

- 使用 **Actor-Critic RL** 在隐空间求解 HJ 值函数
- **World Model**（DINO-WM）提供隐状态表示和动力学
- 分布失配问题是 **Offline RL** 的核心挑战，本文给出了特定场景的解决方案

---

## 6. 局限与未来方向

1. **计算开销**：采样优化在高维动作空间可能受限
2. **World Model 质量**：隐空间安全依赖于世界模型的准确性
3. **形式化保证**：神经网络近似缺乏严格的安全证明

---

## References

- [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] — 另一种将控制理论与 RL 结合的方法
- [[Reachability Constrained Reinforcement Learning]] — 使用可达性进行约束
- [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] — Lipschitz 约束网络设计
