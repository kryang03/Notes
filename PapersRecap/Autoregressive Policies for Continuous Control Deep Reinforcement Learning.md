---
tags:
  - paper
  - reinforcement-learning
  - exploration
  - temporal-coherence
  - autoregressive
aliases:
  - ARP
  - Autoregressive Policy
paper-year: 2019
read-date: 2026-01-31
venue: ICLR 2020
paper-pdf: "[[Papers/Autoregressive Policies for Continuous Control Deep Reinforcement Learning.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[SignalProcessing]]"
  - "[[ControlTheory]]"
---

# Autoregressive Policies for Continuous Control Deep Reinforcement Learning

> [!abstract] 核心概要
> 提出 **自回归策略 (Autoregressive Policy, ARP)**：用**平稳自回归高斯过程**替代白噪声探索，实现**时间一致**的探索轨迹。保持边缘分布为标准正态，同时提供可调的时间相关性，适用于真实机器人的安全探索。

> [!note] 教科书背景
> **时间一致探索的理论意义**：本文对标 SAC 的熵正则化（见 [[ReinforcementLearning|SAC 理论分析]]），但指出 SAC 的 Gaussian 探索在时间维度上是**不一致**的——这与 Deep RL 教科书中"最大熵 RL 鼓励探索"的理论相矛盾。
> 
> **Deep RL 教科书中的最大熵目标**：
> $$J(\pi) = \sum_t \mathbb{E}\left[r_t + \alpha H(\pi(\cdot|s_t))\right]$$
> 隐含假设是熵奖励能促进**状态空间**的探索，但白噪声探索只在**动作空间**添加方差，无法有效覆盖状态空间。
> 
> **本文 Delta**：将熵正则化的探索目标与随机过程的时间相关性显式解耦，提供了更精细的探索控制。

> [!tip] 与理论基础的关联
> - [[StochasticProcess]] - AR 过程的数学基础
> - [[ReinforcementLearning]] - SAC 熵正则化理论
> - [[SignalProcessing]] - 时间平滑的信号处理视角
> - [[ControlTheory]] - 高频动作的物理影响
>
> **核心技术**: AR-p Process, Stationary Gaussian, Temporal Coherence

---

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**探索噪声的时间结构很重要：平滑噪声 → 平滑轨迹 → 安全高效的探索**

### 直观隐喻
想象你在黑暗房间里找出口：
- **高斯白噪声探索**：每步随机转向（原地打转，效率极低）
- **ARP 探索**：保持大致方向，轻微调整（像醉汉走路，但能移动）

第二种方式更可能找到出口，而且不会反复撞墙。

### 领域定位
```
Exploration in RL
        ↓
ε-greedy (discrete)
        ↓
Gaussian noise (continuous, i.i.d.)
        ↓
Ornstein-Uhlenbeck (first-order AR)
        ↓
████████████████████████████████████████
█  ARP (2019)                          █
█  • 任意阶数 AR-p 过程                 █
█  • 保持标准正态边缘分布              █
█  • 可调时间相关性                     █
█  • 显式策略实现                       █
████████████████████████████████████████
        ↓
未来: 状态依赖的自适应探索平滑度
```

---

## 2. 核心创新与贡献 (Contributions & Novelty)

### 问题分析

**标准高斯策略**：
$$a_t = \mu_\theta(s_t) + \sigma_\theta(s_t) \cdot \epsilon_t, \quad \epsilon_t \sim \mathcal{N}(0, I)$$

**问题**：
1. **时间不一致**：连续两步的噪声无关，导致抖动
2. **高频率恶化**：控制频率越高，白噪声越像"原地震动"
3. **硬件损伤**：jerky 运动损坏机器人关节

### Delta 分析

| 方法 | 边缘分布 | 时间相关 | 阶数 | 策略感知 |
|-----|---------|---------|-----|---------|
| Gaussian | N(0,1) | ❌ | - | - |
| OU Process | 需调参 | ✅ | 1 | ❌ |
| Moving Average | 改变 | ✅ | 有限 | ❌ |
| **ARP** | **N(0,1)** | **✅** | **任意** | **✅** |

### 关键贡献

1. **C1**: 导出任意阶数的平稳 AR-p 高斯过程，保持 N(0,1) 边缘分布
2. **C2**: 提出显式策略结构实现 AR 计算
3. **C3**: 证明历史依赖策略包含最优马尔可夫策略

---

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 平稳自回归过程

**目标**：设计一个过程 $\{X_t\}$，满足：
1. $X_t \sim \mathcal{N}(0, 1)$ 对所有 $t$（平稳性）
2. $\text{Corr}(X_t, X_{t-k}) > 0$ 对近期 $k$（时间相关）

**AR-p 模型**：
$$X_t = \sum_{k=1}^{p} \phi_k X_{t-k} + \eta_t$$

其中 $\eta_t \sim \mathcal{N}(0, \sigma_\eta^2)$ 是白噪声。

### 3.2 系数设计

**命题**：对于 $\alpha_k \in [0, 1)$，$k = 1, \ldots, p$，定义：

$$\phi_k = (-1)^{k+1} \sum_{1 \leq i_1 < \cdots < i_k \leq p} \alpha_{i_1} \cdots \alpha_{i_k}$$

则：
$$\sigma_\eta^2 = \prod_{k=1}^{p} (1 - \alpha_k^2)$$

使得 $X_t \sim \mathcal{N}(0, 1)$。

**一阶 (p=1)** 简化：
$$X_t = \alpha X_{t-1} + \sqrt{1 - \alpha^2} \cdot \eta_t$$

**直觉**：$\alpha$ 控制"记忆"程度
- $\alpha \to 0$: 白噪声
- $\alpha \to 1$: 几乎恒定

### 3.3 时间相关性控制

**自相关函数**：
$$\rho(k) = \text{Corr}(X_t, X_{t-k})$$

**一阶 AR**：
$$\rho(k) = \alpha^k$$

**高阶 AR** 提供更丰富的相关结构（如振荡衰减）。

### 3.4 自回归策略

**策略结构**：

$$a_t = \mu_\theta(s_t) + \sigma_\theta(s_t) \cdot \xi_t$$

其中 $\xi_t$ 是 AR-p 过程：
$$\xi_t = \sum_{k=1}^{p} \phi_k \xi_{t-k} + \eta_t$$

**显式实现**：
```
┌─────────────────────────────────────────┐
│  Autoregressive Policy                  │
├─────────────────────────────────────────┤
│                                         │
│  Input: s_t, history (ξ_{t-1},...,ξ_{t-p})
│                                         │
│  1. μ, σ = PolicyNet(s_t)               │
│                                         │
│  2. η_t ~ N(0, σ_η²)                    │
│                                         │
│  3. ξ_t = Σ φ_k ξ_{t-k} + η_t          │
│                                         │
│  4. a_t = μ + σ · ξ_t                   │
│                                         │
│  Output: a_t                            │
│                                         │
└─────────────────────────────────────────┘
```

### 3.5 与最优策略的关系

**定理**：历史依赖策略类 $\Pi_H$ 包含马尔可夫确定性策略 $\Pi_M$。

$$\Pi_M \subset \Pi_H$$

由于最优策略在 $\Pi_M$ 中（Puterman），ARP 的策略空间不会损失最优性。

---

## 4. 实验与验证 (Experiments)

### 4.1 实验设置

**仿真任务**：
- MuJoCo: HalfCheetah, Ant, Humanoid
- 稀疏奖励变体

**真实机器人**：
- Kindred 机器人臂
- 抓取任务

**基线**：
- Gaussian policy
- OU process（一阶 AR）
- Moving average

### 4.2 主要结果

| 任务 | Gaussian | OU | **ARP (p=4)** |
|-----|----------|-----|--------------|
| HalfCheetah (sparse) | 1200 | 2100 | **3500** |
| Ant (sparse) | 800 | 1500 | **2800** |
| Humanoid | 5200 | 5400 | **5600** |

### 4.3 关键发现

1. **稀疏奖励优势显著**：ARP 在稀疏奖励任务上比 Gaussian 提升 2-3 倍
2. **高控制频率**：频率越高，ARP 优势越明显
3. **高阶 AR 更好**：p=4 优于 p=1 (OU)
4. **真实机器人**：ARP 轨迹更平滑，无抖动

### 4.4 控制频率实验

| 控制频率 | Gaussian | **ARP (α=0.9)** |
|---------|----------|-----------------|
| 25 Hz | 3000 | 3200 |
| 50 Hz | 2200 | 3100 |
| 100 Hz | 1500 | **3000** |
| 200 Hz | 800 | **2900** |

**发现**：Gaussian 性能随频率急剧下降，ARP 保持稳定。
### 4.5 Ablation 因果链分析

| 去掉/改变 | 结果变化 | 因果机制 |
|---------|---------|--------|
| 去掉 AR（退化为高斯白噪声） | 稀疏奖励性能 -60% | 时间不一致的噪声无法产生有意义的状态空间探索 |
| 降低 AR 阶数（p=4→p=1） | 性能下降 15-20% | 一阶 AR 只有指数衰减相关，无法描述更复杂的时间结构 |
| 增大 α（α=0.99） | 探索过度平滑，收敛变慢 | 变量几乎恍定，无法覆盖动作空间 |
| 降低 α（α=0.1） | 接近高斯策略 | 时间相关性过弱，失去 AR 优势 |
| 提高控制频率（固定 α） | Gaussian 崩溃，ARP 稳定 | 高频 + 白噪声 = “原地震动”，AR 的低通效应抑制抖动 |

### 4.6 工程关键细节 (Engineering Tricks)

- **AR 过程重置**：每个 episode 开始时必须重置 AR 历史缓冲，否则跨 episode 的时间相关性会引入偏差
- **Log-prob 计算**：$\log \pi(a_t|s_t, \xi_{<t}) = \log \mathcal{N}(\xi_t | \sum_k \phi_k \xi_{t-k}, \sigma_\eta^2)$，注意用 $\eta_t$ 的分布而非 $\xi_t$ 的边缘分布
- **多维独立 AR**：每个动作维度独立运行 AR 过程（对角化），避免跨维相关矩阵的计算开销
- **数值稳定性**：$\sigma_\eta^2 = \prod_{k=1}^p (1-\alpha_k^2)$ 在 $\alpha \to 1$ 时趋近零，可能导致数值下溢。实践中应在 log 空间计算并 clamp $\alpha \in [0, 0.99]$
- **推理延迟**：高阶 AR 的顺序依赖增加推理延迟，对 1000Hz 控制器需评估实时性——p=4 在 GPU 上额外开销可忽略，但 CPU 推理需测试
---

## 5. 批判性分析 (Critical Analysis)

### 优势
- **理论完备**：保持标准正态边缘分布
- **实用性强**：可与任意现有算法结合
- **安全性**：平滑轨迹减少硬件损伤
- **可调性**：$\alpha$ 连续调节平滑度

### 局限性深度分析

**理论层面**：
- 平稳性要求固定 $\alpha$，无法根据状态自适应调整探索平滑度
- 历史依赖以 $p$ 阶截断，无法捕捉长程依赖（与 LSTM/Transformer 策略相比）
- **替代方案**：状态依赖的 $\alpha(s)$ 网络；用扩散过程替代 AR 实现时间相关探索

**算法层面**：
- $\alpha$ 和 $p$ 仍需调优，卧数优化硬监控显示区间为 $\alpha \in [0.85, 0.95]$, $p \in [2, 6]$
- 单一尺度平滑，不处理多频率动作（与 AP-AC 互补）
- **替代方案**：结合 AP-AC 的多频率框架，对不同动作变量用不同 $\alpha$

**工程层面**：
- AR 过程需存储历史 $\xi_{t-1}, \ldots, \xi_{t-p}$，在并行环境中需为每个 env 维护独立状态
- episode 边界的历史重置可能引入瞬态抢动
- **替代方案**：在 Isaac Gym 的向量化 env 中，用 tensor 批量维护 AR 状态

### 与其他方法的对比

| 方法 | ARP | Parameter Noise | Curiosity |
|-----|-----|-----------------|----------|
| 作用层级 | 动作空间 | 参数空间 | 奖励 |
| 时间一致性 | 显式控制 | 隐式 | 无 |
| 互补性 | 可叠加 | 可叠加 | 可叠加 |

---

## 6. 对灵巧操作的启发 (Implications)

### 灵巧手探索的挑战

```
灵巧手控制特点：
- 高维动作空间 (20+ DoF)
- 高控制频率 (>100 Hz)
- 安全敏感（手指脆弱）

高斯探索问题：
- 24 维独立噪声 → 手指乱抖
- 高频率 → 几乎不产生宏观运动

ARP 解决方案：
- 每个关节独立 AR 过程
- 或：任务空间 AR（更高效）
- 频率越高，α 可以越大
```

### 与其他论文的联系

- **VICES**：阻抗控制 + ARP 探索 = 安全的接触任务学习
- **AP-AC**：多频率动作可用不同 $\alpha$ 的 ARP
- **DexTrack**：跟踪控制器可用 ARP 做鲁棒性探索

---

## 7. 演进脉络定位 (Evolution Context)

```
Exploration in Continuous Control
        ↓
Gaussian White Noise
        ↓
Ornstein-Uhlenbeck (Lillicrap, 2015)
├── 连续时间扩散
└── 一阶 AR 的特例
        ↓
Parameter Space Noise (Plappert, 2017)
        ↓
████████████████████████████████████████
█  ARP (2019)                          █
█  • 任意阶 AR-p                        █
█  • 标准正态边缘分布                   █
█  • 显式策略实现                       █
████████████████████████████████████████
        ↓
未来: 状态自适应的探索平滑度
```

---

## 8. 核心代码逻辑

```python
class ARProcess:
    """平稳自回归高斯过程"""
    
    def __init__(self, alpha, order=1, dim=1):
        """
        alpha: 相关系数 (标量或数组)
        order: AR 阶数
        dim: 动作维度
        """
        self.order = order
        self.dim = dim
        self.alpha = np.atleast_1d(alpha)
        
        # 计算 AR 系数
        self.phi = self._compute_phi()
        self.sigma_eta = np.sqrt(np.prod(1 - self.alpha**2))
        
        # 历史缓冲
        self.history = deque(maxlen=order)
        for _ in range(order):
            self.history.append(np.zeros(dim))
    
    def _compute_phi(self):
        """计算保持 N(0,1) 的 AR 系数"""
        # 使用论文中的递推公式
        phi = []
        for k in range(1, self.order + 1):
            coef = 0
            for combo in combinations(range(self.order), k):
                coef += np.prod([self.alpha[i] for i in combo])
            phi.append((-1)**(k+1) * coef)
        return np.array(phi)
    
    def sample(self):
        """生成下一个样本，保持时间相关性"""
        # 白噪声创新
        eta = np.random.randn(self.dim) * self.sigma_eta
        
        # AR 组合
        xi = eta.copy()
        for k, phi_k in enumerate(self.phi):
            xi += phi_k * self.history[-(k+1)]
        
        # 更新历史
        self.history.append(xi)
        
        return xi
    
    def reset(self):
        """重置历史（episode 开始时）"""
        for _ in range(self.order):
            self.history.append(np.random.randn(self.dim))


class AutoregressivePolicy(nn.Module):
    """自回归策略"""
    
    def __init__(self, obs_dim, act_dim, alpha=0.9, ar_order=4):
        super().__init__()
        self.mean_net = MLP(obs_dim, act_dim)
        self.log_std = nn.Parameter(torch.zeros(act_dim))
        self.ar_process = ARProcess(alpha, ar_order, act_dim)
        
    def forward(self, obs, deterministic=False):
        mean = self.mean_net(obs)
        
        if deterministic:
            return mean
        
        std = self.log_std.exp()
        # AR 噪声（时间一致）而非 i.i.d.
        xi = torch.from_numpy(self.ar_process.sample())
        action = mean + std * xi
        
        return action
    
    def reset(self):
        """Episode 开始时重置 AR 过程"""
        self.ar_process.reset()


# 与现有算法集成（以 SAC 为例）
def train_with_arp(env, policy, q_net, n_episodes):
    for ep in range(n_episodes):
        obs = env.reset()
        policy.reset()  # 重置 AR 历史
        
        while not done:
            action = policy(obs)  # AR 探索
            next_obs, reward, done, _ = env.step(action)
            
            # 标准 SAC 更新
            buffer.add(obs, action, reward, next_obs, done)
            update_sac(policy, q_net, buffer)
            
            obs = next_obs
```

---

## 9. 与知识体系的联系（含数学关联）

### 与 [[StochasticProcess]] 的联系

AR-p 过程是平稳高斯过程的子集，其功率谱密度为：
$$S(\omega) = \frac{\sigma_\eta^2}{|1 - \sum_{k=1}^p \phi_k e^{-ik\omega}|^2}$$
$\alpha \to 1$ 时谱集中于低频，对应时间平滑的探索轨迹。这与 [[StochasticProcess]] 中 Ornstein-Uhlenbeck 过程的离散化 $X_{t+1} = e^{-\theta \Delta t} X_t + \sigma \sqrt{\frac{1-e^{-2\theta\Delta t}}{2\theta}} \eta_t$ 是等价的（取 $\alpha = e^{-\theta \Delta t}$）。

### 与 [[ReinforcementLearning]] 的联系

ARP 的 log-prob 计算保持解析性，与 PPO/SAC 兼容：
$$\log \pi(a_t | s_t, \xi_{<t}) = \log \mathcal{N}\left(\eta_t \mid 0, \sigma_\eta^2\right) - \log \sigma_\theta(s_t)$$
其中 $\eta_t = \xi_t - \sum_k \phi_k \xi_{t-k}$ 是创新项。这保证了 ARP 可作为任意 on-policy/off-policy 算法的 drop-in 替换。

### 与 [[SignalProcessing]] 的联系

AR 过程的低通滤波效应：$\alpha = 0.9$ 时截止频率约为 $f_c \approx \frac{-\ln \alpha}{2\pi \Delta t}$，对于 100Hz 控制器 $f_c \approx 1.7\text{Hz}$。这自然地将探索频率限制在机械系统的有效带宽内，避免激发高频共振。

## 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **关节间的自回归依赖**: 转笔中 16-24 DoF 的灵巧手各关节存在强耦合，AR 策略可编码这种依赖关系（如拇指"发力"后食指"接住"的时序关系）
2. **时间一致探索**: 灵巧手的动作需要时间上的连贯性，AR 的时间相关噪声比 i.i.d. 高斯噪声更适合量化探索
3. **与 PPO 的兼容**: AR 策略的 log-prob 仍然解析可计算（链式法则分解），与 PPO 完美兼容，可直接替换当前的对角高斯输出头
4. **工程注意**: AR 增加推理延迟（顺序采样 N 次），对于 1000Hz PD 控制器的实时性需要评估
