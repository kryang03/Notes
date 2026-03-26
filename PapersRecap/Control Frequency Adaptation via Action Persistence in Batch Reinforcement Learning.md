---
tags:
  - paper
  - reinforcement-learning
  - control-frequency
  - action-persistence
  - batch-RL
  - FQI
aliases:
  - PFQI
  - Persistent FQI
  - Action Persistence
read-date: 2026-01-31
venue: ICML 2020
paper-year: 2020
authors:
  - Alberto Maria Metelli
  - Flavio Mazzolini
  - Lorenzo Bisi
  - Luca Sabbioni
  - Marcello Restelli
institution: Politecnico di Milano
paper-pdf: "[[Papers/Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[SignalProcessing]]"
---

# Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning

> [!note] Foundation 关联
> - **[[ReinforcementLearning#5. Bridging the Gap: Sim-to-Real & Offline RL]]**: Batch RL / FQI 算法基础
> - **[[ControlTheory]]**: 控制频率与采样定理
> - **[[SignalProcessing]]**: 信号采样与 Nyquist 频率

> [!abstract] 核心贡献
> 提出 **Action Persistence**（动作持续）的形式化框架：在 $k$ 个决策步内重复同一动作，等价于修改控制频率。证明了持续算子的收缩性质，导出最优性能损失界，并提出 **PFQI** (Persistent Fitted Q-Iteration) 算法。

## 1. 问题背景

### 1.0 核心洞察（一句话 + 直观隐喻）

**一句话**：动作持续重复 $k$ 步等价于降低控制频率，存在最优 $k^*$ 平衡策略空间与学习难度。

**直观隐喻**：想象你在写书法——“拉一竖”这个动作，你可以毫米级微调（$k=1$，每毫米重新决策），但这样笔画会护；也可以一口气写到底（$k=16$，一次决策执行到底），但遇转折时就会出界。最优的 $k^*$ 就是在“笔画流畅”和“转折可控”之间找到平衡点。

### 1.1 现有方法的局限

- **固定频率策略**：无法适应任务动力学复杂度的变化
- **人工调频**：需要多次实验确定最优频率，样本浪费严重
- **缺乏理论指导**：无法先验地分析最优频率与环境特性的关系

### 1.2 控制频率的权衡

**高频控制**：
- ✅ 策略空间更大，理论上能达到更优性能
- ❌ 单个动作效果微弱，难以从噪声中区分
- ❌ 样本复杂度高

**低频控制**：
- ✅ 动作效果明显，易于学习
- ✅ 样本复杂度低
- ❌ 策略空间受限
- ✅ 有助于克服部分可观测性（如执行延迟）

> [!question] 核心问题
> **什么是最优控制频率？**
> 答案取决于：(1) 任务特性；(2) 学习算法

---

## 2. 数学框架

### 2.1 Action Persistence 定义

**执行策略 $\pi$ at persistence $k$**：
- 在 $t = 0$ 选择 $A_0 \sim \pi(\cdot|S_0)$
- 保持 $A_0$ 固定 $k-1$ 步：$A_1 = \cdots = A_{k-1} = A_0$
- 在 $t = k$ 重新查询策略：$A_k \sim \pi(\cdot|S_k)$
- 循环...

### 2.2 两种等价视角

#### Policy View（策略视角）

**$k$-persistent policy**：非马尔可夫非平稳策略

$$\pi_{t,k}(B|H_t) = \begin{cases} \pi(B|S_t) & \text{if } t \mod k = 0 \\ \delta_{A_{t-1}}(B) & \text{otherwise} \end{cases}$$

#### Environment View（环境视角）

**$k$-persistent MDP** $M_k = (S, A, P_k, R_k, \gamma^k)$

- **转移核**：$P_k(B|s,a) = (P^\delta)^{k-1} P(B|s,a)$
- **奖励**：$R_k = \sum_{i=0}^{k-1} \gamma^i (P^\delta)^i R$
- **折扣因子**：$\gamma^k$（有效视野缩短）

> [!important] 对偶性
> 在 $M$ 中以 persistence $k$ 执行 $\pi$ ⟺ 在 $M_k$ 中以 persistence 1 执行 $\pi$

### 2.3 Persistent Bellman Operators

**$k$-persistent Bellman 期望算子**：
$$T_k^\pi f = T^\pi (T^\delta)^{k-1} f$$

**$k$-persistent Bellman 最优算子**：
$$T_k^* f = T^* (T^\delta)^{k-1} f$$

其中 $T^\delta$ 是动作不变的转移算子。

> [!theorem] 收缩性
> $T_k^\pi$ 和 $T_k^*$ 在 $L_\infty$ 范数下是 $\gamma^k$-收缩的，因此存在唯一不动点。

---

## 3. 性能损失分析

### 3.1 Lipschitz 条件下的界

设 MDP 是 $(L_P, L_r)$-Lipschitz 连续的：

$$\|Q_1^* - Q_k^*\|_\infty \leq C \cdot k \cdot \Delta t_0$$

其中 $C$ 取决于：
- 动力学的 Lipschitz 常数 $L_P$
- 奖励的 Lipschitz 常数 $L_r$
- 折扣因子 $\gamma$

> [!tip] 物理直觉
> 性能损失与**环境演化速度**成正比。对于"缓慢演化"的系统，增加 persistence 的代价更小。

---

## 4. Persistent Fitted Q-Iteration (PFQI)

### 4.1 算法思想

给定基础 MDP $M$ 中收集的数据集 $D = \{(s_i, a_i, r_i, s'_i)\}$：

1. 选择目标 persistence $k$
2. 使用 $k$-persistent Bellman 算子进行值迭代
3. 无需重新采集数据！

**关键观察**：可以用 persistence 1 的数据估计 persistence $k$ 的值函数

### 4.2 算法框架

```
输入: 数据集 D（persistence 1 采集），目标 persistence k
初始化: Q^(0) = 0
for j = 0, 1, 2, ... do
    Q^(j+1) = FQI_step(Q^(j), D, k)  // 使用 k-persistent Bellman 目标
return π_k = greedy(Q^*)
```

### 4.3 Persistence 选择启发式

**目标**：从候选集 $\mathcal{K} = \{1, 2, 4, 8, ...\}$ 中选择最优 $k^*$

**方法**：
1. 对每个 $k \in \mathcal{K}$ 运行 PFQI(k)
2. 使用价值函数估计比较性能
3. 无需额外环境交互

---

## 4.4 核心 PyTorch 代码逻辑

```python
def persistent_bellman_target(q_net, batch, k, gamma):
    """k-persistent Bellman 目标计算"""
    states, actions, rewards, next_states = batch
    B = states.shape[0]

    # 累積折扣奖励: R_k = sum_{i=0}^{k-1} gamma^i * r_{t+i}
    # 在 batch 数据中，用单步数据构造 k-step return
    discounted_reward = rewards  # 单步奖励作为近似
    for i in range(1, k):
        discounted_reward = discounted_reward + (gamma ** i) * rewards  # 简化: 假设保持同一动作时奖励近似不变

    # 下一状态的最优 Q 值（有效折扣因子为 gamma^k）
    with torch.no_grad():
        next_q = q_net(next_states).max(dim=-1).values    # (B,)
        target = discounted_reward + (gamma ** k) * next_q # (B,)
    return target


def pfqi_train(q_net, dataset, k_candidates, gamma, n_iters=100):
    """Persistent FQI: 用 persistence-1 数据估计任意 k 的值函数"""
    best_k, best_value = 1, -float('inf')

    for k in k_candidates:  # e.g. [1, 2, 4, 8, 16]
        q_net_k = copy.deepcopy(q_net)
        optimizer = torch.optim.Adam(q_net_k.parameters(), lr=1e-3)

        for _ in range(n_iters):
            batch = dataset.sample(256)
            target = persistent_bellman_target(q_net_k, batch, k, gamma)
            pred = q_net_k(batch.states).gather(1, batch.actions).squeeze()
            loss = F.mse_loss(pred, target)
            optimizer.zero_grad(); loss.backward(); optimizer.step()

        # 用估计的 V 选择最优 k
        avg_value = q_net_k(dataset.all_states).max(dim=-1).values.mean().item()
        if avg_value > best_value:
            best_k, best_value = k, avg_value

    return best_k
```

## 4.5 工程关键细节 (Engineering Tricks)

- **数据复用**：核心优势是用 $k=1$ 采集的数据估计任意 $k$ 的值函数，但需确保转移核估计 $(P^\delta)^{k-1}$ 的精度——当 $k$ 大且动力学非线性时，单步数据的 bootstrap 误差累积
- **候选 $k$ 的选择**：推荐二进制网格 $\{1, 2, 4, 8, 16\}$，而非线性扫描，防止计算量爆炸
- **值函数初始化**：可用小 $k$ 的训练结果暖启动大 $k$ 的训练，加速收敛
- **折扣因子调整**：注意 $\gamma^k$ 在 $k$ 大时会让有效视野大幅缩短，可能需要用更大的原始 $\gamma$ 补偿

---

### 5.1 Cartpole

| Persistence $k$ | Expected Return |
|-----------------|-----------------|
| 1 | 172.0 ± 6.8 |
| 2 | 178.4 ± 6.7 |
| **4** | **276.2 ± 3.8** |
| 8 | 284.3 ± 1.6 |
| 16 | 285.9 ± 1.1 |

**最优 persistence**：$k = 4 \sim 16$

### 5.2 关键发现

1. **过低的 persistence**（$k=1,2$）：动作效果不明显，学习困难
2. **过高的 persistence**（$k>32$）：策略空间过度受限
3. **最优点存在**：任务相关的"甜蜜点"

### 5.3 Ablation 因果链分析

| 去掉/改变 | 结果变化 | 因果机制 |
|---------|---------|--------|
| 不用 persistent Bellman 算子（直接 FQI） | 次优 k 选择，性能下降 | 忽略了动作持续期间的动力学演化 |
| 固定 k=1（标准 FQI） | Cartpole 性能 172 vs 285 | 单步动作效果微弱，样本复杂度高 |
| k 过大（k>32） | 性能下降 | 策略空间过度受限，无法应对快速变化 |
| 去掉 Lipschitz 平滑性假设 | 理论界失效 | 非光滑动力学中 k-step 误差累积不可控 |

---

### 6.1 与 Frame Skipping 的关系

深度 RL 中的 frame skipping（如 Atari 每 4 帧决策一次）本质上就是 action persistence

### 6.2 与 [[Elastic Time Step Reinforcement Learning, VTS-RL]] 的联系

- **VTS-RL**：动态调整时间步长
- **Action Persistence**：统一的理论框架
- 两者都关注**控制频率适配**问题

### 6.3 与 [[ReinforcementLearning]] 的联系

- **折扣因子调整**：persistence $k$ 等价于 $\gamma \to \gamma^k$
- **有效视野缩短**：$\frac{1}{1-\gamma^k} < \frac{1}{1-\gamma}$
- **样本效率**：低频 → 高样本效率，但受限策略空间

---

## 7. 核心洞见

> [!quote] Insight 1: 动作持续是可配置的环境参数
> $k$ 可以视为 Configurable MDP 的超参数，外部调节以优化学习

> [!quote] Insight 2: 性能-样本复杂度权衡
> 存在最优 persistence，平衡策略空间大小和学习难度

> [!quote] Insight 3: 可重用数据
> 用 persistence 1 收集的数据可用于估计任意 persistence $k$ 的值函数

---

## 8. 局限与扩展

**理论层面**：
- Lipschitz 连续性假设排除了接触不连续的操作任务（如灵巧手抓取）
- 性能损失界为 $O(k \cdot \Delta t_0)$ 线性增长，未考虑非线性动力学的误差累积
- **替代方案**：基于 [[Dynamics]] 的误差传播分析（敏感度方法）可给出更紧的界

**算法层面**：
- 仅限 Batch RL，未扩展到 Online RL
- $k$ 是全局固定的，不能根据状态自适应
- **替代方案**：状态依赖的 $k(s)$（如 [[Elastic Time Step Reinforcement Learning, VTS-RL|VTS-RL]] 的方法）

**工程层面**：
- persistence 改变采样分布的熵，影响探索质量
- 大 $k$ 时有效视野 $1/(1-\gamma^k)$ 大幅缩短，可能导致近视策略
- **替代方案**：在 $k$ 大时同时提升 $\gamma$ 以保持有效视野

## 9. 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **转笔任务的最优 persistence**：接触发力瞬间需要 $k=1$（高频控制），空中飞行段可用 $k=4{\sim}8$（低频节能）——这描述了一个状态依赖的 $k^*(s)$
2. **Batch 数据复用价值**：从Isaac Gym 采集的高频数据，可用 PFQI 离线评估多个 $k$ 的性能，避免重复运行昂贵的仿真
3. **Sim-to-Real 启示**：真实机器人的执行延迟和通信延迟等价于强制的最小 persistence，可将硬件延迟直接建模为 $k_{\min}$ 来缩小 sim-real gap

## 10. 与知识体系的联系（含数学关联）

### 与 [[ReinforcementLearning]] 的联系

Action persistence 将标准 Bellman 算子扩展为 $k$-persistent 形式：
$$T_k^* f = T^* (T^\delta)^{k-1} f$$
其中 $T^\delta$ 是动作不变的转移算子。这保持了 $\gamma^k$-收缩性，但有效视野从 $\frac{1}{1-\gamma}$ 缩短为 $\frac{1}{1-\gamma^k}$——这是 persistence 的核心 trade-off。

### 与 [[ControlTheory]] 的联系

$k$-persistent MDP 的转移核 $P_k(B|s,a) = (P^\delta)^{k-1} P(B|s,a)$ 等价于控制理论中的零阶保持器（ZOH）离散化，采样周期 $T_s = k \cdot \Delta t_0$。性能损失 $\|Q_1^* - Q_k^*\|_\infty \leq C \cdot k \cdot \Delta t_0$ 直接对应 Shannon 采样定理的频率约束。

### 与 [[SignalProcessing]] 的联系

动作持续的低通滤波效应：保持动作 $k$ 步等价于对动作信号施加截止频率 $f_c = \frac{f_s}{2k}$ 的低通滤波器，这自然抑制了高频噪声但也限制了快速环境变化的响应能力。

---

## References

- [[Elastic Time Step Reinforcement Learning, VTS-RL]] — 动态时间步长
- [[Reinforcement Learning for Control with Multiple Frequencies]] — 多频率控制
- [[ReinforcementLearning]] — 基础知识
