---
tags:
  - paper
  - control-barrier-function
  - safety-filtering
  - world-model
  - visuomotor-control
  - hamilton-jacobi-reachability
aliases:
  - LatentCBF
  - Latent Control Barrier Function
read-date: 2026-01-31
venue: arXiv 2511.18606
paper-year: 2025
authors:
  - Kensuke Nakamura
  - Arun L. Bishop
  - Steven Man
  - Aaron M. Johnson
  - Zachary Manchester
  - Andrea Bajcsy
institution: Carnegie Mellon University
paper-pdf: "[[Papers/How to Train Your Latent Control Barrier Function: Smooth Safety Filtering Under Hard-to-Model Constraints.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[StochasticProcess]]"
---

# How to Train Your Latent Control Barrier Function

> [!tip] 与理论基础的关联
> - [[ControlTheory|ControlTheory §7]] — CBF 形式化（安全集、Lie 导数、CBF-QP）；HJ 可达性构造 CBF
> - [[ReinforcementLearning|ReinforcementLearning §2.6]] — World Model (DINO-WM) 预测 + Actor-Critic 求 HJ 值
> - [[RepresentationLearning|RepresentationLearning §5]] — 视觉运动策略的潜空间
> - [[StochasticProcess]] — Hamilton-Jacobi 可达性与值函数
>
> **核心技术**: Latent-space CBF, WGAN-GP 光滑 Margin, 混合策略采样, 采样优化安全过滤

> [!note] 精确锚点与「价值即 Lyapunov」暗线
> - [[ControlTheory#9. 安全滤波：Control Barrier Function 与可达性]] — 本文把经典 CBF-QP $a^*=\arg\min_a\|a-\pi^{nom}\|\ \text{s.t.}\ B(f(s,a))\ge\alpha B(s)$ 搬进 DINO-WM 潜空间做部署时外挂滤波；HJ 值函数 $V^\diamond$ 充当 barrier $B$。
> - [[ControlTheory#10. 稳定性理论的统一基石]] — 核心 Theorem「margin 光滑性线性传到值函数」$L_{V^\diamond}\le L_\ell\max\{1,\tfrac{1-\gamma}{1-\gamma L_f}\}$ 是 Lipschitz/稳定性理论在安全证书上的应用：证书要能区分动作，其 Lyapunov 光滑性是前提。
> - **暗线/簇内 Delta**：$V^\diamond$ 是「价值即 Lyapunov」的 barrier 变体（cf. [[ReinforcementLearning#2.2 值函数与 Bellman 方程]]）。与 [[Reachability Constrained Reinforcement Learning|RCRL]] 的 Delta：RCRL 把安全训进策略（内禀、有形式保证），本文外挂在任意预训练策略上（灵活、但采样概率性无严格保证）——安全「实现位置谱」的两端。

> [!abstract] 核心贡献
> 提出 **LatentCBF**，解决了在隐空间中进行基于优化的安全过滤（CBF-style filtering）的两个关键挑战：(1) 分类器生成的 margin function 梯度饱和；(2) 安全策略与任务策略的分布失配导致值函数估计不准。

## 1. 问题设定与动机

### 核心洞察（直观隐喻）

**安全滤波器如同“AI 汽车副驾”**——名义策略（学员司机）负责完成任务，CBF 滤波器（副驾教练）只在即将撞车时轻微修正方向盘。Least-Restrictive 是“教练一把抢过方向盘”（急刜），LatentCBF 是“教练轻推一下方向盘”（微调），前者安全但任务失败，后者安全且任务继续。

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

### 1.3 变量来源追踪

枢纽：**CBF 是部署时外挂滤波器（非训练约束）**、在 **DINO-WM 潜空间** $z$ 上做，且 **margin 光滑性线性传递到值函数光滑性**（§2.1 Theorem）。

| 变量 | 类型/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $z$ | $\mathbb{R}^{64}$ | DINO-WM 编码（frozen） | 否（输入） | 隐状态 | CBF 在**潜空间**做，非显式状态 |
| $\ell(z)$ | scalar | WGAN 判别器（学习） | 是 | margin function | **无 sigmoid**（Wasserstein 实值）；硬分类器梯度饱和→失效 |
| $V^\diamond(z)$ | scalar | critic（HJ 值） | 是 | 安全值函数 = CBF $B$ | 光滑性线性继承 $\ell$（Thm） |
| $\pi^{nom}$ | 策略 | **给定**（如 Diffusion Policy） | — | 名义/任务策略 | 不重训，外挂过滤 |
| $\pi^\diamond$ | 策略 | 学习 | — | 安全策略 | 提供 fallback + 部分 buffer |
| $f(z,a)$ | 动力学 | DINO-WM（frozen） | 否 | 潜空间预测 | 安全保证受限于其精度 |
| $\beta$ | scalar | 超参 | 否 | 目标 Lipschitz（GP） | $\in[0.5,2]$；过大不光滑、过小无区分 |
| $\alpha,\gamma$ | scalar | 超参 | 否 | CBF/折扣系数 | 约束 $B(f(s,a))\ge\alpha B(s)$ |

## 2. 理论分析：为什么现有方法失效

### 2.1 Challenge 1: 光滑值函数需要光滑 Margin Function

**问题根源**：使用二分类器作为 margin function $\ell(z)$

分类器在安全/危险边界处产生**饱和梯度**，导致 CBF 无法评估动作的相对安全性。

> [!theorem] Margin-to-Value Lipschitz Bound
> 设 margin function $\ell(s)$ 和 HJ 值函数 $V^\diamond(s)$ 的 Lipschitz 常数分别为 $L_\ell$ 和 $L_{V^\diamond}$，动力学 $f(s,a)$ 对状态的 Lipschitz 常数为 $L_f$，且 $\gamma L_f < 1$，则：
> $$L_{V^\diamond} \leq L_\ell \cdot \max\left\{1, \frac{1-\gamma}{1-\gamma L_f}\right\}$$
> 
> **推论**：值函数的光滑性**线性依赖**于 margin function 的光滑性。

**图示说明**：左：分类器 margin → 饱和 CBF，所有采样动作安全值相似；右：光滑 margin → 有区分度的 CBF。

### 2.2 Challenge 2: 分布失配

**Actor-Critic RL 训练**：Replay Buffer 只包含安全策略 $\pi^\diamond$ 产生的状态-动作对

**部署时**：CBF 需要评估任务策略 $\pi^{\text{nom}}$ 的动作安全性

**结果**：Critic 对任务相关动作的值估计不准确——恰恰是 CBF 过滤最需要的地方！

---

### 2.3 概念边界与符号陷阱

- **CBF 是部署时滤波器、非训练约束**：最小修正名义动作 $a^*=\arg\min_a\|a-\pi^{nom}(s)\|\ \text{s.t.}\ B(f(s,a))\ge\alpha B(s)$——安全的"外挂"实现（vs 其它 safe-RL 训练出内禀安全策略，见 §5 子簇综述）。
- **隐空间 CBF（DINO-WM frozen）**：在潜空间过滤，适配视觉/Diffusion 策略；安全保证受 world model 预测精度限。
- **margin 用 WGAN 无 sigmoid**：硬分类器在安全边界梯度饱和 → CBF 无区分度 → 退化为离散切换（§3.6 消融 NoGP ↓35%）。
- **Margin 光滑性线性传递到值函数**（核心 Theorem）：$L_{V^\diamond}\le L_\ell\cdot\max\{1,\tfrac{1-\gamma}{1-\gamma L_f}\}$——**光滑性是 CBF 可用的前提**，把 CBF 与 Lipschitz 子簇连接。
- **混合 buffer 50:50**：解分布失配（critic 须在任务动作区域也准）。
- **采样优化（零阶）非凸**：7.6k 样本 / 10ms@7-DoF；**24-DoF 灵巧手指数增长不可行**（§6 局限）。
- **无形式化安全保证**：采样概率性，有限样本不覆盖全动作空间。

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

### 3.4 核心代码逻辑 (PyTorch)

```python
import torch
import torch.nn as nn

class WGANMarginFunction(nn.Module):
    """梯度惩罚 WGAN 判别器作为光滑 margin function"""
    def __init__(self, z_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(z_dim, 256), nn.ELU(),
            nn.Linear(256, 256), nn.ELU(),
            nn.Linear(256, 1)  # 无 sigmoid — Wasserstein 输出实数
        )
    def forward(self, z): return self.net(z)

def wgan_loss(margin_fn, z_safe, z_fail, lam_gp=10.0, beta=1.0):
    loss_w = margin_fn(z_fail).mean() - margin_fn(z_safe).mean()
    # 梯度惩罚：插值样本上约束 Lipschitz
    alpha = torch.rand(z_safe.size(0), 1, device=z_safe.device)
    z_interp = (alpha * z_safe + (1 - alpha) * z_fail).requires_grad_(True)
    grad = torch.autograd.grad(
        margin_fn(z_interp).sum(), z_interp, create_graph=True
    )[0]
    gp = ((grad.norm(2, dim=1) - beta) ** 2).mean()
    return loss_w + lam_gp * gp

def cbf_filter(nom_action, safe_actions, world_model, margin_fn, critic, z, gamma=0.9):
    """采样优化 CBF 过滤：选择最近的安全动作"""
    candidates = torch.cat([nom_action.unsqueeze(0), safe_actions], dim=0)
    z_next = world_model.predict(z.expand(len(candidates), -1), candidates)
    v_next = critic(z_next).squeeze(-1)
    v_curr = critic(z).squeeze(-1)
    feasible = v_next >= gamma * v_curr
    if feasible.any():
        dists = (candidates[feasible] - nom_action).norm(dim=-1)
        return candidates[feasible][dists.argmin()]
    return safe_actions[0]  # fallback
```

### 3.5 训练细节

| 维度 | 设定 |
|------|------|
| **World Model** | DINO-WM (预训练 frozen), z_dim=64 |
| **Margin 训练** | WGAN-GP, lr=1e-4, λ=10, 目标 Lipschitz β=1 |
| **Critic 训练** | SAC-style Actor-Critic, 混合 buffer (50% 安全/50% 任务) |
| **安全数据** | 仿真自动标注 / 真机人工标注 |
| **CBF 采样** | 7.6k 候选动作, GPU 并行, 推理 ~10ms |
| **硬件** | Franka Panda 7-DoF, Intel RealSense RGB |

### 3.6 Ablation 分析

| 消融项 | 安全任务成功率 | 因果机制 |
|--------|---------------|----------|
| 去掉梯度惩罚 (NoGP) | 45% (↓35%) | 分类器梯度饱和 → CBF 无法区分动作安全度 → 退化为离散切换 |
| 去掉混合采样 | 55% (↓25%) | Critic 在任务动作区域不准 → 误判安全动作为危险 → 过度保守 |
| 减少采样数 (1k) | 60% (↓20%) | 候选空间覆盖不足 → 难找到既安全又接近名义的动作 |
| 去掉 DINO 预训练 | 40% (↓40%) | 隐空间缺乏语义 → margin + 动力学预测均失效 |

### 3.7 工程实践要点 (Engineering Tricks)

1. **WGAN 判别器不加 sigmoid**: Wasserstein 输出无界实值，梯度惩罚约束 Lipschitz
2. **混合 Buffer 50:50 比例**: 过多安全数据 → Critic 对任务区域不准；过多任务数据 → 安全边界模糊
3. **采样策略**: 高斯扰动名义动作 + 安全策略采样的混合比纯均匀采样效果好 3×
4. **β 选择**: β 过大 → 不光滑；β 过小 → 无区分度。推荐 β ∈ [0.5, 2.0]
5. **World Model 冻结**: DINO-WM 参数冻结避免 margin 训练污染表征

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

> [!note] safe-RL 子簇综述：四证书 + 正交维度（训练时 vs 部署时安全）
> LatentCBF 补全安全 RL 子簇的 **CBF 格**，但它带出一个**正交维度**——之前四篇（[[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective|Stability-Cert RL]] IQC、[[Safe Model-based Reinforcement Learning with Stability Guarantees|Berkenkamp]] Lyapunov、[[Reachability Constrained Reinforcement Learning|RCRL]] 可达集、[[On Robust Reinforcement Learning with Lipschitz-Bounded Policy Networks|Lipschitz]] 架构）都把安全**训练进策略**（内禀）；LatentCBF 把 CBF 做成**部署时外挂滤波器**——给任意名义策略（含预训练 Diffusion Policy）加安全层、不重训。
> **① 安全的两种实现位置**：内禀（训练进策略，有形式化保证、但需重训）vs 外挂（部署时过滤，可加在任意策略上、但采样概率性无严格保证、高维不可行）。这是 safe-RL 被忽略的工程维度。
> **② 光滑性把 CBF 焊到 Lipschitz 子簇**：LatentCBF 的核心 Theorem（margin 光滑性线性传递到值函数）说明——**安全过滤的可用性取决于安全证书的 Lipschitz 光滑性**。于是 [[On Robust Reinforcement Learning with Lipschitz-Bounded Policy Networks|On Robust RL]]/[[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control|LipsNet]] 的 Lipschitz 工具不只用于鲁棒/精度，还是 CBF 区分动作的前提——Lipschitz 子簇 → safe-RL 子簇的桥就此打通。
> **③ WMTS 联系**：LatentCBF 在 world model 潜空间做安全过滤 → WMTS 的 world model 可同时承载**调度**（$m(s)$ 元控制）+ **安全过滤**（CBF）。这暗示 WMTS 的 world model 是一个多用途的"潜空间元控制器"。

---

## 6. 局限性深度分析

### 理论层面
- **无形式化安全保证**: 采样优化是概率性的，有限样本不能覆盖所有动作空间
- **Lipschitz bound 保守性**: 梯度惩罚仅近似约束 Lipschitz 常数，非严格上界
- **替代方案**: Hamilton-Jacobi 值迭代提供更严格安全证书，但计算成本指数增长；[[Optimization]] 中 SOS (Sum-of-Squares) 方法可用于低维精确 CBF 构造

### 算法层面
- **动作空间维度瓶颈**: 7-DoF 时 7.6k 样本可行，但 24-DoF 灵巧手需指数增长的采样量
- **World Model 依赖**: 安全保证受限于 DINO-WM 预测精度，模型外推区域可能失效
- **替代方案**: 基于梯度的 CBF-QP 求解（需可微 world model）可避免采样瓶颈

### 工程层面
- **实时性**: 10ms 推理在 1kHz 力控制循环中仍嫌慢（需 1ms 级）
- **标注成本**: 安全/危险二分类标签在真实场景中需人工标注，扩展性受限

## 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **安全滤波用于转笔探索**: RL 策略自由探索，但用 CBF 滤波防止关节超限/物体飞出，避免浪费 episode
2. **光滑 margin 的触觉应用**: 触觉信号天然具有连续梯度属性，比视觉更适合构建光滑 margin function
3. **关键瓶颈**: 24-DoF 灵巧手的高维动作空间导致采样优化不可行 → 需研究基于梯度的 CBF-QP 替代，或在降维动作空间（PCA synergies）中操作

---

## References

- [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] — 另一种将控制理论与 RL 结合的方法
- [[Reachability Constrained Reinforcement Learning]] — 使用可达性进行约束
- [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] — Lipschitz 约束网络设计
