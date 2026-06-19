---
tags:
  - paper
  - safe-RL
  - lyapunov-stability
  - gaussian-process
  - model-based-RL
  - region-of-attraction
aliases:
  - Safe Model-based RL
  - Lyapunov RL
  - SafeOpt-RL
read-date: 2026-01-31
venue: NeurIPS 2017
paper-year: 2017
authors:
  - Felix Berkenkamp
  - Matteo Turchetta
  - Angela P. Schoellig
  - Andreas Krause
institution: ETH Zurich, University of Toronto
paper-pdf: "[[Papers/NIPS-2017-safe-model-based-reinforcement-learning-with-stability-guarantees-Paper.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[StochasticProcess]]"
---

# Safe Model-based Reinforcement Learning with Stability Guarantees

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#2.6 Model-Based RL (MBRL): 样本效率与世界模型|ReinforcementLearning §2.6]] — Model-based RL + GP 动力学；**价值函数天然是 Lyapunov 函数**（正定代价下 $V^\pi$）
> - [[ControlTheory#7. 鲁棒控制：对抗模型不确定性|ControlTheory §7]] — Lyapunov 稳定性、吸引域 (RoA)、把长期收敛化为单步下降条件
> - [[StochasticProcess]] — GP 后验不确定性 $\sigma_n$ 随数据单调减 → RoA 单调扩大
>
> **核心技术**: Lyapunov RoA, Gaussian Process 动力学, Safe Exploration, 概率稳定性保证

> [!abstract] 核心贡献
> 首次提出具有**可证明稳定性保证**的安全 RL 算法。利用 **Lyapunov 函数** 定义安全区域，结合 **Gaussian Process** 建模动力学不确定性，实现在不离开吸引域的前提下安全学习和策略优化。

## 1. 问题设定

### 1.0 核心直觉与隐喻

**一句话核心**：像在雾天开车——只能看见前方一小段（GP 不确定性），但只要每一步都处于「能刹住车」的状态（Lyapunov 吸引域内），就永远安全。随着观测增多（GP 不确定性缩小），“能见度”不断提升，安全区域自动扩大。

**现有方法局限**：
- **无约束 Model-based RL**：样本高效但在模型不准确的区域可能执行危险动作
- **仅基于约束的 RL (CMDP)**：期望累积代价约束无法保证“每一步”都安全
- **保守鲁棒控制**：安全但策略搜索空间极度受限，无法学习更优策略

### 1.0.1 Delta 分析

| 方法 | 安全保证 | 模型需求 | 探索能力 | 可扩展性 |
|------|---------|---------|---------|----------|
| 无约束 MBRL | 无 | 参数模型 | 无限 | 好 |
| CMDP-Lag | 期望安全 | 无需 | 良好 | 好 |
| 鲁棒控制 | 最差情况 | 精确模型 | 极保守 | 差 |
| **本文 (Lyapunov+GP)** | **概率安全** | **GP 动力学** | **安全探索** | **中等** |

**核心增量**：首次将 Lyapunov 安全保证与数据驱动的 GP 不确定性量化结合，实现「安全地探索并扩大吸引域」

### 1.1 安全的定义

**核心观点**：RL 中的安全 = 控制理论中的**稳定性**

**吸引域 (Region of Attraction, RoA)**：
- 状态空间的一个子集 $\mathcal{V}(c)$
- 前向不变：$x_0 \in \mathcal{V}(c) \Rightarrow x_t \in \mathcal{V}(c), \forall t > 0$
- 渐近收敛：$\lim_{t \to \infty} x_t = 0$

**安全约束**：
1. 适应策略时不得**缩小**吸引域
2. 探索动作不得**离开**吸引域

### 1.2 系统模型

$$x_{t+1} = f(x_t, u_t) = \underbrace{h(x_t, u_t)}_{\text{已知先验模型}} + \underbrace{g(x_t, u_t)}_{\text{未知模型误差}}$$

**假设**：
- **Lipschitz 连续性**：$h$, $g$ 和策略 $\pi$ 都是 Lipschitz 连续的
- **统计模型**：使用 GP 建模 $g$，提供校准的不确定性估计

---

### 1.3 变量来源追踪

本文枢纽：**Lyapunov 函数 $v$ 既可以是物理能量、也可以是 RL 价值函数**（连接 RL 与控制理论），以及 **GP 不确定性 $\sigma_n$ 单调减 → RoA 单调扩大**（安全探索的根据）。

| 变量 | 类型/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $x$ | $\mathbb{R}^{d_x}$ | 状态 | 否（输入） | 系统状态 | 假设完全可观 |
| $u=\pi(x)$ | $\mathbb{R}^{d_u}$ | 策略输出 | 是（策略） | 控制动作 | $\pi$ 须 Lipschitz |
| $f=h+g$ | 动力学 | $h$ 已知先验 + $g$ 未知 | — | 真实动力学 | 误差 $g$ 才是 GP 要学的 |
| $g$ | 模型误差 | **GP 建模** | GP 超参 | 未知部分 | 校准不确定性是安全前提 |
| $v(x)$ | $\mathbb{R}_{\ge0}$ | **设计/学习** | 否 | Lyapunov 函数 | **能量 or 价值函数**；$v(0)=0,v>0$ |
| $\mathcal{V}(c)=\{x:v(x)\le c\}$ | level set | 导出 | — | 吸引域 (RoA) | 前向不变 + 渐近收敛 |
| $\mu_n,\sigma_n$ | GP 后验 | 学习 | — | 均值/标准差 | $\sigma_n$ 随数据**单调减** |
| $\beta_n$ | scalar | 超参 | 否 | 置信缩放 | 实践 $\beta_n{=}2$ 比理论值激进 |
| $L_v$ | scalar | 估计 | 否 | $v$ 的 Lipschitz 常数 | 离散网格→连续外推 (Thm 2) 靠它 |
| $c_n$ | scalar | 优化 | 否 | 最大安全等值线 | 不得缩小（适应约束） |

## 2. 理论框架

### 2.1 Lyapunov 稳定性验证

**Lyapunov 函数** $v: \mathcal{X} \to \mathbb{R}_{\geq 0}$：
- $v(0) = 0$, $v(x) > 0$ for $x \neq 0$
- 连续可微

> [!theorem] Theorem 1 (Lyapunov 稳定性)
> 若对所有 $x \in \mathcal{V}(c)$ 有 $v(f(x, \pi(x))) < v(x)$，则 $\mathcal{V}(c)$ 是吸引域。

**关键洞见**：将复杂的收敛性验证转化为**单步下降条件**

### 2.2 基于统计模型的安全验证

**不确定性量化**：
$$Q_n(x,u) := [v(\mu_{n-1}(x,u)) \pm L_v \beta_n \sigma_{n-1}(x,u)]$$

其中：
- $\mu_n$, $\sigma_n$：GP 后验均值和标准差
- $\beta_n$：置信区间缩放因子
- $L_v$：Lyapunov 函数的 Lipschitz 常数

> [!theorem] Theorem 2 (离散化验证)
> 在 Lipschitz 假设下，只需在离散网格 $\mathcal{X}_\tau$ 上验证下降条件：
> $$u_n(x, u) < v(x) - L_{\Delta v} \tau$$
> 即可保证连续状态空间的稳定性。

### 2.3 策略优化

**安全策略空间**：
$$\mathcal{D}_n = \{(x, u) \in \mathcal{X}_\tau \times \mathcal{U} \mid u_n(x, u) - v(x) < -L_{\Delta v} \tau\}$$

**优化目标**：
$$\pi_n, c_n = \argmax_{\pi \in \Pi_L, c > 0} c \quad \text{s.t.} \quad \forall x \in \mathcal{V}(c) \cap \mathcal{X}_\tau: (x, \pi(x)) \in \mathcal{D}_n$$

**含义**：寻找使吸引域最大的策略，同时保证安全约束

### 2.4 安全探索

**安全探索集**：
$$\mathcal{S}_n = \{z' \in \mathcal{V}(c_n) \cap \mathcal{X}_\tau \times \mathcal{U}_\tau \mid u_n(z) + L_v L_f \|z - z'\|_1 \leq c_n\}$$

**探索策略**（最大化信息增益）：
$$(x_n, u_n) = \argmax_{(x,u) \in \mathcal{S}_n} u_n(x, u) - l_n(x, u)$$

选择**不确定性最大**的安全状态-动作对

---

### 2.5 概念边界与符号陷阱

- **$v$ 可以是物理能量 or 价值函数**：正定代价下 RL 价值函数 $V^\pi$ 天然是 Lyapunov（§6 Insight 3）——连接 RL 与控制理论的关键。
- **安全 = 吸引域前向不变（Lyapunov 下降 $v(f(x,\pi(x)))<v(x)$）**：区别于 [[Reachability Constrained Reinforcement Learning|RCRL]] 的可行集、[[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective|Stability-Cert RL]] 的 $\mathcal{L}_2$ 增益。
- **GP $\sigma_n$ 单调减 → RoA 单调扩大**：这是"安全探索扩展安全域"的数学根据，也是本篇区别于子簇其它（静态证书）的核心。
- **$\beta_n=2$ 是实践激进值**：比理论保证 $(1-\delta)$ 所需更乐观；过小→不安全探索、过大→RoA 不扩展（§4.5 消融）。
- **离散网格 $\mathcal{X}_\tau$ + Lipschitz 外推**：Theorem 2 只在网格验证下降条件，靠 $L_v,L_{\Delta v}$ 外推到连续——$\tau$ 太粗则保证失效。
- **model-based（需 GP）**：区别于子簇其它 model-free 方法；GP $O(n^3)$ 限制高维扩展。

## 3. 理论保证

> [!theorem] Theorem 4 (安全与探索保证)
> 在 GP 模型假设下，对任意 $\delta \in (0,1)$，以至少 $(1-\delta)$ 的概率：
> 
> (i) $\mathcal{V}(c_n) \subseteq \mathcal{R}_{\pi_n}$ — 估计的吸引域包含于真实吸引域
> 
> (ii) $f(x,u) \in \mathcal{R}_{\pi_n}, \forall (x,u) \in \mathcal{S}_n$ — 所有探索点都在吸引域内
> 
> (iii) 经过有限次探索后，达到最优探索性能

**核心含义**：可以**安全地学习**系统动力学，同时**扩大吸引域**

---

## 4. 实践算法

### 4.1 Algorithm 1: Safe Lyapunov Learning

```
输入: 初始安全策略 π₀, GP 动力学模型
for n = 1, 2, ... do
    1. 通过 SGD 优化策略 πₙ
    2. 计算最大安全等值线 cₙ
    3. 更新安全探索集 Sₙ
    4. 选择 (xₙ, uₙ) ∈ Sₙ 并收集数据
    5. 用新数据更新 GP 模型
```

### 4.2 实现细节

**策略表示**：神经网络（2 隐藏层，32 神经元，ReLU）

**Lyapunov 函数来源**：
- 物理能量（机械系统的动能+势能）
- **价值函数**！对于正定代价 $r(x,u)$，$V^\pi$ 天然是 Lyapunov 函数

**置信区间简化**：$\beta_n = 2$（实践中比理论值更激进）

### 4.3 核心 PyTorch 实现

```python
import torch
import torch.nn as nn
import gpytorch

class SafeLyapunovAgent:
    """基于 Lyapunov + GP 的安全 RL Agent"""
    def __init__(self, policy_net, lyapunov_fn, gp_model, L_v, beta=2.0):
        self.policy = policy_net       # 策略网络
        self.V = lyapunov_fn           # Lyapunov 函数 (e.g., 能量函数)
        self.gp = gp_model             # GP 动力学模型
        self.L_v = L_v                 # V 的 Lipschitz 常数
        self.beta = beta               # 置信区间缩放

    def is_safe(self, s, a, c_n):
        """检查 (s, a) 是否在安全集内"""
        with torch.no_grad():
            mu, sigma = self.gp.predict(s, a)  # GP 预测
            # Lyapunov 下降条件的上界
            v_next_upper = self.V(mu) + self.L_v * self.beta * sigma
            v_current = self.V(s)
            return v_next_upper < v_current  # 严格下降

    def safe_explore(self, s, c_n):
        """在安全集内选择不确定性最大的动作"""
        best_a, best_unc = None, -float('inf')
        for a in self.action_candidates(s):
            if self.is_safe(s, a, c_n):
                mu, sigma = self.gp.predict(s, a)
                # 上界 - 下界 = 不确定性宽度
                unc = 2 * self.L_v * self.beta * sigma
                if unc > best_unc:
                    best_a, best_unc = a, unc
        return best_a

    def update_roa(self, policy, gp_model, tau):
        """计算最大安全等值线 c_n"""
        # 在离散网格上验证 Lyapunov 下降条件
        c_max = 0
        for c in torch.linspace(0.01, 10.0, 100):
            level_set = self.get_level_set(c, tau)
            all_safe = all(
                self.is_safe(s, policy(s), c) for s in level_set
            )
            if all_safe:
                c_max = c
        return c_max
```

### 4.4 训练细节补充

| 超参数 | 值 |
|--------|-----|
| 策略网络 | 2×32 MLP + ReLU |
| GP 核函数 | Matérn 5/2 |
| 置信区间 $\beta_n$ | 2 |
| 状态空间离散化 $\tau$ | 0.01–0.1（任务相关） |
| 数据收集 | 每轮 1 个安全探索点 |
| Lyapunov 函数 | 能量函数（机械系统）/ 价值函数 |
| 总数据量 | 50 个交互点即可显著扩大 RoA |

### 4.5 Ablation 因果链分析

| 去掉的组件 | 结果变化 | 因果机制 |
|-----------|---------|----------|
| 去掉 GP 不确定性 → 仅用均值 | 安全性破坏（状态离开吸引域） | 忽略模型误差导致验证时低估 $v(f(x,\pi(x)))$ |
| 去掉安全探索 → 随机探索 | 吸引域扩展速度降 3× | 随机点多数落在已知区域，信息增益低 |
| $\beta_n$ 过小 (0.5) | 不安全的探索点出现 | 置信区间未完全覆盖真实动力学 |
| $\beta_n$ 过大 (10) | 吸引域几乎不扩展 | 过度保守，所有候选点都被判定为不安全 |

### 4.6 工程关键细节 (Engineering Tricks)

- **GP 计算加速**：GP 推断复杂度 $O(n^3)$，实际使用 sparse GP 或隔式归纳截断到 50–100 个诱导点
- **Lyapunov 函数选择**：对机械系统优先用能量 $v(x) = \frac{1}{2}x^T P x$；对无物理先验的系统可用学习到的价值函数
- **$L_v$ 估算**：对二次 Lyapunov $v(x) = x^T P x$，$L_v = 2\|P\| \cdot \|x\|_{\max}$，需确保 $\|x\|_{\max}$ 在感兴趣区域内有缓冲

---

## 5. 实验结果

### 5.1 倒立摆稳定

| 阶段 | 吸引域大小 | 控制性能 |
|------|-----------|---------|
| 初始策略 | 小（仅局部稳定） | 差 |
| 50 数据点后 | 显著扩大 | 大幅改善 |

**关键结果**：摆从未倒下——整个学习过程都是安全的

---

## 6. 核心洞见

> [!tip] Insight 1: Lyapunov 函数 = 安全证书
> Lyapunov 函数将"长期稳定性"转化为"单步可验证条件"，使安全约束可计算

> [!tip] Insight 2: GP 提供"诚实"的不确定性
> 校准的置信区间允许保守但有效的安全验证

> [!tip] Insight 3: 价值函数天然是 Lyapunov 函数
> 对于正定代价，RL 的价值函数可直接用作稳定性分析工具

> [!tip] Insight 4: 安全与探索可以兼得
> 在吸引域内探索不会破坏安全性，同时可以扩大吸引域

---

## 7. 与知识体系的联系

### 与 [[ControlTheory]] 的联系

- **Lyapunov 稳定性理论** 是本文的核心工具
- **吸引域 (RoA)** 概念来自非线性控制
- 将控制理论的安全保证引入 RL

### 与 [[ReinforcementLearning]] 的联系

- **Model-Based RL** + GP 动力学模型
- **Safe Exploration** 的形式化定义
- 价值函数与 Lyapunov 函数的对偶关系

### 与 [[Optimization]] 的联系

- **约束优化** 形式的策略更新
- Lipschitz 连续性假设的利用
- 信息论驱动的探索策略

### 与 Foundation 的数学联系

**与 [[ControlTheory]] 的数学联系 — Lyapunov 下降条件的概率化**：

经典 Lyapunov 稳定性要求 $v(f(x)) < v(x)$（确定性）。本文将其概率化：
$$\Pr\left[v(f(x, \pi(x))) < v(x)\right] \geq 1 - \delta$$
通过 GP 的后验均值和方差构造上界 $u_n = v(\mu_n) + L_v \beta_n \sigma_n$，将概率安全转化为确定性上界检查。

**与 [[StochasticProcess]] 的数学联系 — GP 后验不确定性**：

GP 后验方差 $\sigma_n^2(x) = k(x,x) - k_x^T (K + \sigma^2 I)^{-1} k_x$ 随数据增加单调递减→ 吸引域单调扩大。这是本文「安全探索扩展 RoA」的数学根据。

### 跨方法对比

| 维度 | 本文 (Lyapunov+GP) | [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective\|Stability-Cert. RL]] | [[On Robust Reinforcement Learning with Lipschitz-Bounded Policy Networks\|Lipschitz RL]] | [[Reachability Constrained Reinforcement Learning\|RCRL]] |
|------|----------------------|------------------------------|--------------------------|--------|
| 安全定义 | 吸引域前向不变 | $\mathcal{L}_2$ 增益有界 | 输出 Lip 有界 | 可行集内可达 |
| 安全证明工具 | Lyapunov + GP 置信区间 | SDP + 偏导数界 | 架构确保 | Safety Q-function |
| 探索能力 | 安全探索扩展 RoA | 无显式探索 | 无显式探索 | 无显式探索 |
| 模型依赖 | GP 动力学 | LTI 标称模型 | 无 | 无 |
| 可扩展性 | GP $O(n^3)$ 限制 | SDP 维度限制 | 良好 | 良好 |

> [!note] 安全 RL 子簇定位与新 insight
> Berkenkamp 在安全 RL 子簇占"**Lyapunov 吸引域**"格（与 [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective|Stability-Cert RL]] 的 $\mathcal{L}_2$、[[Reachability Constrained Reinforcement Learning|RCRL]] 的可行集、Lipschitz 架构并列；在 RCRL 的"安全强度谱"中：可行集 ⊃ **Lyapunov 稳定** ⊃ $\mathcal{L}_2$）。本篇带出两个新 insight：
> **① 静态安全证书 vs 动态安全探索**：子簇其它三篇都是"给定模型/约束，证明安全"（静态证书、不显式探索）；唯独 Berkenkamp 用 GP 不确定性单调减实现"**边学边安全地扩大安全域**"。这是 safe RL 一个被忽略的时间维度——安全不只是被验证，还可以是被主动扩张的可学习对象。
> **② "价值函数 = Lyapunov 函数"把探索簇与稳定簇焊死**：正定代价下 RL 价值函数天然是 Lyapunov 证书。这把本簇与 [[Dynamic Reinforcement Learning for Actors|Dynamic RL]] 的"Lyapunov 标尺"直接连通——Dynamic RL 调网络 Lyapunov 指数做**探索**（$\lambda_{max}>0$）、Berkenkamp 用价值函数作 Lyapunov 做**安全**（吸引域）。二者操作的是**同一个数学对象的两端**：探索与稳定其实是一枚硬币，都在调控系统的 Lyapunov 性质，只是符号相反。

---

## 8. 局限与后续

**局限**：
1. 需要 Lyapunov 函数（不总是容易获得）
2. 离散化带来计算开销
3. GP 在高维状态空间扩展性有限
4. 假设完全可观测状态

**后续工作**：
- [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] — 更一般的框架
- [[Reachability Constrained Reinforcement Learning]] — 可达性约束
- [[How to Train Your Latent Control Barrier Function - Smooth Safety Filtering Under Hard-to-Model Constraints]] — 隐空间安全过滤

---

## References

- [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] — Lipschitz 网络设计
- [[ControlTheory]] — Lyapunov 稳定性理论基础

## 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **安全探索边界**: 转笔训练中，策略探索可能导致灵巧手关节达到极限位置或产生过大力矩。Lyapunov 约束的 ROA（吸引域）可以为探索设置安全边界，避免物理损伤
2. **GP 动力学模型**: 用高斯过程建模接触动力学的不确定性（摩擦系数的不确定型），可作为 Sim-to-Real 中动力学 gap 的软补偿
3. **局限**: 基于 GP 的方法在高维动作空间（20+ 关节）上计算代价过高，需做 sparse GP 或局部近似
