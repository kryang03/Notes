---
tags:
  - paper
  - dexterous-manipulation
  - in-hand-manipulation
  - tactile-sensing
  - state-estimation
  - reinforcement-learning
aliases:
  - DLR Tactile Manipulation
  - Modular RL Architecture
paper-year: 2023
read-date: 2026-02-01
venue: RA-L 2023
paper-pdf: "[[Papers/Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[SignalProcessing]]"
  - "[[ControlTheory]]"
  - "[[StochasticProcess]]"
---

# Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture

> [!abstract] 核心概要
> 提出**模块化深度 RL 架构**，将策略学习与状态估计**解耦**：用可微分粒子滤波器从纯触觉（关节扭矩+位置）估计立方体状态，实现手朝下情况下的 **24 种目标方位重定向**，零样本 Sim2Real 迁移成功。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] - SAC 策略学习
> - [[SignalProcessing#5. 状态估计：从局部触觉到全局语义]] - 可微分粒子滤波器
> - [[StochasticProcess]] - 状态估计
> - [[ControlTheory]] - 扭矩控制 DLR-Hand II
>
> **核心技术**: Modular Architecture, Differentiable Particle Filter, Torque-Controlled Hand

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
将复杂的纯触觉手内操作任务**分解**为两个可独立训练的模块：**状态估计器**（从触觉推断物体状态）和**控制策略**（给定状态执行操作），通过迭代精化实现端到端性能。

### 直观隐喻
就像人类大脑分工——感知皮层负责"这个东西在哪、朝向哪"，运动皮层负责"怎么动手指"。模块化让每个子问题更容易学习和调试。

### 领域定位
```
OpenAI Dactyl (端到端, 视觉状态)
         ↓
本论文 (模块化, 触觉状态估计)
         ↓
后续: 端到端触觉策略 + 更复杂物体
```

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 维度 | 前人工作 (OpenAI/HORA) | DLR Modular |
|-----|----------------------|-------------|
| 手姿态 | 手朝上（重力辅助） | **手朝下**（永久力闭合） |
| 状态来源 | 视觉/假设已知 | **纯触觉估计** |
| 架构 | 端到端 | **模块化可解释** |
| 任务 | 连续旋转 | **24 种离散目标方位** |

### 关键贡献点
1. **模块化分离**: 状态估计与策略学习独立训练
2. **可微分粒子滤波**: 从关节扭矩/位置历史估计立方体 6-DoF 状态
3. **目标导向重定向**: 到达 π/2 栅格的 24 种目标方位（非无限旋转）
4. **零样本 Sim2Real**: 在 DLR-Hand II 上验证

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 模块化架构

```
┌────────────────────────────────────────────────────────────┐
│                    System Architecture                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Measured: (q, τ) ──→ Particle Filter ──→ (x̂, R̂)         │
│                            ↓                               │
│  Goal: R_goal ────────────────────────→ Policy Network    │
│                                              ↓             │
│                                         Δq (action)        │
│                                              ↓             │
│                           Impedance Controller → τ_cmd     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 3.2 可微分粒子滤波器 (DPF)

#### 标准粒子滤波
$$
p(x_t | z_{1:t}) \approx \sum_{i=1}^N w_t^{(i)} \delta(x_t - x_t^{(i)})
$$

#### 可微分版本
- **运动模型**: 可学习的神经网络 $f_\theta(x_{t-1}, a_{t-1})$
- **观测模型**: 可学习的似然 $g_\phi(z_t | x_t)$
- **重采样**: 软重采样保持可微性

#### 训练
- 用策略生成的仿真数据
- 监督学习: $\mathcal{L} = \|(\hat{x}, \hat{R}) - (x^*, R^*)\|^2$

### 3.3 策略网络

**观测空间**:
$$
o_t = [q_t, \bar{q}_{t-1}, \bar{q}_{t-1} - q_t, R_{\text{goal}}, (\hat{x}_t, \hat{R}_t), R_{\text{goal}}^{-1} \hat{R}_t]_{\text{stacked } 0.5s}
$$

**动作空间**: 关节角度增量
$$
\tilde{q}_{t+1} = \text{clip}(q_t + \pi(o_t) \cdot \frac{\tau_{\max}}{K_p}, q_{\min}, q_{\max})
$$

**奖励函数**:
$$
r_g = \begin{cases}
\lambda_{\text{drop}} & \text{if drop} \\
\frac{\lambda_\theta}{\theta + \theta_0^4} - \text{clip}(\lambda_{\text{pos}}\|x\|, 0, \lambda_{\text{clip}}) + \lambda_{\text{succ}} & \text{if success} \\
0 & \text{else}
\end{cases}
$$

### 3.3b 核心 PyTorch 代码逻辑

```python
# 可微分粒子滤波器 (DPF) 核心逻辑
class DifferentiableParticleFilter(nn.Module):
    def __init__(self, N_particles, state_dim, obs_dim, action_dim):
        super().__init__()
        self.N = N_particles
        self.motion_model = nn.Sequential(
            nn.Linear(state_dim + action_dim, 128), nn.ReLU(), nn.Linear(128, state_dim))
        self.obs_model = nn.Sequential(
            nn.Linear(state_dim + obs_dim, 128), nn.ReLU(), nn.Linear(128, 1))  # log-likelihood
    
    def forward(self, particles, weights, action, obs):
        # particles: (B, N, state_dim), weights: (B, N)
        # 1. Propagate: learned motion model
        a_expand = action.unsqueeze(1).expand(-1, self.N, -1)
        particles = particles + self.motion_model(torch.cat([particles, a_expand], -1))
        
        # 2. Update: learned observation likelihood
        obs_expand = obs.unsqueeze(1).expand(-1, self.N, -1)
        log_w = self.obs_model(torch.cat([particles, obs_expand], -1)).squeeze(-1)
        weights = F.softmax(log_w + torch.log(weights + 1e-8), dim=-1)
        
        # 3. Soft resample (保持可微性)
        indices = torch.multinomial(weights, self.N, replacement=True)
        particles = particles.gather(1, indices.unsqueeze(-1).expand_as(particles))
        weights = torch.ones_like(weights) / self.N
        
        # 4. 加权状态估计
        state_est = (particles * weights.unsqueeze(-1)).sum(dim=1)  # (B, state_dim)
        return particles, weights, state_est
```

### 3.4 迭代精化流程

```
Step 1: 用 Ground Truth 状态训练初始策略
    ↓
Step 2: 用策略生成数据训练粒子滤波器
    ↓
Step 3: 用估计状态继续训练策略
    ↓
Step 4: 重复 Step 2-3 直到收敛
```

### 3.5 立方体对称性利用

立方体有 **24 种等价方位**（八面体群）。利用对称性：
$$
R_{\text{sym}} = \text{reduce\_by\_octahedral\_group}(R)
$$

减少状态空间复杂度。

## 4. 实验与验证 (Experiments)

### 实验设置
- **硬件**: DLR-Hand II (扭矩控制, 4 指×3 主动关节)
- **任务**: 立方体重定向到 24 种目标方位
- **训练**: PyBullet, 120 并行 worker
- **算法**: SAC

### 训练超参数

| 参数 | 值 |
|------|------|
| 算法 | SAC (off-policy, 自动温度调节) |
| 仿真器 | PyBullet |
| 并行 Worker | 120 |
| Replay Buffer | 1M transitions |
| Batch Size | 256 |
| 学习率 (Actor/Critic) | 3e-4 (Adam) |
| 折扣因子 γ | 0.99 |
| 控制频率 | 20 Hz |
| 观测历史窗口 | 0.5s (10 帧堆叠) |
| DPF 粒子数 N | 100 |
| 迭代精化轮数 | 3-4 轮 (策略↔估计器交替) |
| 奖励系数 | $\lambda_{\text{drop}}=-10$, $\lambda_\theta=1$, $\lambda_{\text{pos}}=0.5$, $\lambda_{\text{succ}}=5$ |

### 关键结果

| 指标 | 仿真 | 真实世界 |
|-----|------|---------|
| 成功率 | 92% | 24/24 目标可达 |
| 平均时间 | ~15s | ~20s |
| 状态估计误差 | <1cm, <10° | 实时可用 |

### 消融实验
- **无状态估计**: 策略失效（无法判断何时停止）
- **端到端训练**: 更难调试，性能更差
- **短历史窗口**: 估计精度下降

> [!warning] Ablation 因果链
> - 去掉状态估计模块 → 策略无法感知物体朝向 → 无法判断"是否已到达目标" → 成功率趋近 0（**感知-控制解耦的必要性**）
> - 端到端替代模块化 → 梯度流过估计器和策略 → 优化困难（高维+稀疏奖励）→ 收敛慢 + 不可调试（**模块化的优化优势**）
> - 缩短观测历史窗口 (0.5s → 0.1s) → 粒子滤波缺乏时序信息 → 姿态估计方差增大 → 策略输入噪声增大 → 成功率下降 ~15%（**时序积分对状态估计的关键性**）

### 工程关键细节 (Engineering Tricks)

1. **八面体群对称性利用**: 立方体 24 种等价方位 → 减少策略输出空间 24 倍，避免多值歧义
2. **阻抗控制器作为安全层**: 动作空间为关节角度增量 → 通过 $\tilde{q} = \text{clip}(q + \pi(o) \cdot \frac{\tau_\max}{K_p})$ 转为扭矩 → 防止关节过力
3. **迭代精化避免鸡蛋问题**: 先用 GT 训练策略 → 用策略生成数据训练估计器 → 交替迭代，避免冷启动
4. **120 并行 worker**: PyBullet 多进程收集，SAC 的 replay buffer 需要大量多样数据
5. **手朝下设置**: 强制力闭合约束（重力不辅助），更接近实际应用但增加训练难度

## 5. 批判性分析 (Critical Analysis)

### 优势
- **可解释性**: 模块化允许独立分析和调试
- **纯触觉**: 无需外部摄像头，避免遮挡问题
- **力闭合**: 手朝下设置更接近实际应用

### 局限性
- **仅立方体**: 需要利用已知几何
- **离散目标**: π/2 栅格，非连续重定向
- **计算成本**: 粒子滤波实时性挑战

### 未来方向
- 扩展到未知几何物体
- 连续目标方位跟踪
- 与视觉融合的多模态估计

### 局限性深度分析（理论/算法/工程三维度）

| 维度 | 局限 | 根因 | 替代方案 |
|------|------|------|----------|
| **理论** | 假设已知物体几何（八面体群） | 对称性利用依赖先验几何 | 学习未知物体的隐式对称群 (Equivariant Networks) |
| **算法** | 离散目标集合（24种方位） | 策略输出为分类 + 到达判断 | 连续旋转目标 (如 AnyRotate 的轴角表示) |
| **算法** | DPF 粒子退化问题 | 高维状态空间中有效粒子数衰减 | Rao-Blackwellized PF / Normalizing Flow 后验 |
| **工程** | DLR-Hand II 非商用 | 扭矩控制手成本高 | 迁移至 Allegro Hand + 力/扭矩传感器 |

### 对转笔/Sim-to-Real 的启发

1. **模块化分离可直接应用于转笔**: 转笔中物体状态（笔的位姿+角速度）估计同样困难，可借鉴 DPF 从关节扭矩历史估计笔状态 → 比纯视觉更适合高速旋转下的遮挡场景
2. **迭代精化解决 Sim-to-Real 的估计器冷启动**: 仿真中 GT 可用 → 先训练策略 → 再用策略数据训练估计器 → 最终估计器可迁移到真实世界
3. **力闭合（手朝下）的操作范式**: 转笔需要在重力环境下保持笔不掉落，本文的手朝下设置直接相关——策略必须学会持续施加闭合力

## 6. 对灵巧操作的启发 (Implications)

> [!important] 核心启发
> **模块化 ≠ 性能损失**——恰当的任务分解可以让每个子问题更容易学习，同时保持端到端可训练性。

### 具体应用
1. **状态估计模块复用**: 粒子滤波器可用于其他触觉任务
2. **可解释调试**: 知道是估计器还是策略的问题
3. **数据效率**: 模块可以用不同数据独立预训练

### 方法论启示

| 设计选择 | 理由 |
|---------|------|
| 扭矩控制手 | 隐式触觉信息更丰富 |
| 可微分滤波 | 端到端梯度流动 |
| 迭代精化 | 打破估计-策略的鸡蛋问题 |

### 与 Foundations 的数学关联

**[[ReinforcementLearning|SAC]]**: 策略优化目标为最大熵 RL:
$$J(\pi) = \sum_t \mathbb{E}_{(s_t,a_t)\sim\rho_\pi}\left[r(s_t,a_t) + \alpha \mathcal{H}(\pi(\cdot|s_t))\right]$$
模块化架构中 $s_t = (\hat{x}_t, \hat{R}_t, q_t, R_\text{goal})$ 由 DPF 估计器提供。

**[[SignalProcessing|粒子滤波]]**: 贝叶斯递推中，后验 $p(x_t|z_{1:t})$ 通过粒子集合 $\{x_t^{(i)}, w_t^{(i)}\}_{i=1}^N$ 近似。DPF 用神经网络参数化运动/观测模型使整个滤波过程可微，梯度可反传至编码器。

**[[StochasticProcess|非连续性]]**: 接触状态切换导致状态转移非光滑 → EKF 线性化失效 → 粒子滤波天然适配多模态分布 → DPF 进一步通过软重采样保持梯度。

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── DPF (Jonschkowski 2018): 可微分粒子滤波
├── DLR-Hand 之前工作: 单轴连续旋转
└── OpenAI Dactyl: 视觉状态估计
    ↓
本论文 (2023):
├── 核心突破: 纯触觉 + 目标导向 + 模块化
├── 关键洞察: 扭矩控制手自带丰富触觉信息
└── 验证: 24 种目标方位 Sim2Real
    ↓
后续发展:
├── 更复杂物体（非立方体）
├── 连续目标跟踪
└── 视触觉融合估计
```

### 跨方法对比

| 方法 | 传感模态 | 架构 | 手姿态 | 目标类型 | Sim2Real |
|------|---------|------|--------|---------|----------|
| **OpenAI Dactyl** | 视觉（MoCap）| 端到端 LSTM | 手朝上 | 连续旋转 | DR |
| **HORA** | 视觉+本体 | 端到端 | 手朝上 | 连续旋转 | DR + Teacher-Student |
| **DLR Modular (本文)** | **纯触觉** | **模块化（DPF+SAC）** | **手朝下** | **24 离散方位** | **模块化迁移** |
| AnyRotate | 触觉+本体 | Teacher-Student | 手朝下 | 绕任意轴旋转 | DR + 触觉适应 |
| DexNDM | 视觉+本体 | 神经动力学 | 手朝上 | 连续旋转 | NDP |

---

## 参考信息

- **作者**: Johannes Pitz, Lennart Röstel, Leon Sievers, Berthold Bäuml
- **机构**: DLR (German Aerospace Center), TU Munich
- **项目页**: dlr-alr.github.io/dlr-tactile-manipulation
- **ArXiv**: 2303.04705
