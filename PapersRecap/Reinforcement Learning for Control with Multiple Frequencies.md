---
tags:
  - paper
  - reinforcement-learning
  - control-frequency
  - multi-rate-control
  - factored-action
aliases:
  - AP-AC
  - Action-Persistent Actor-Critic
  - Multiple Control Frequencies
paper-year: 2020
read-date: 2026-01-31
venue: NeurIPS 2020
paper-pdf: "[[Papers/Reinforcement Learning for Control with Multiple Frequencies.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
---

# Reinforcement Learning for Control with Multiple Frequencies

> [!abstract] 核心贡献
> 针对"真实系统不同执行器需不同控制频率（机械臂 50Hz、抓手 10Hz），但单一平稳策略无法兼顾"这一瓶颈，提出 **AP-AC (Action-Persistent Actor-Critic)**：在 Factored-Action MDP 上让每个动作变量保持各自的持续时间 $c^k$，并证明此时最优策略**必然是周期非平稳的**（周期 $T=\mathrm{lcm}(c^1,\dots,c^m)$），用按相位分头的网络直接优化。结构性洞见：**当多个动作变量频率不同，"在同一状态下永远做同一件事"（平稳策略）会任意次优——最优性要求策略显式依赖"当前处在周期的哪个相位"。**

> [!tip] 与理论基础的关联
> - [[ControlTheory]] — 多速率采样系统：每个动作变量采样率 $f^k=f_{base}/c^k$ 须满足各自子系统的 Nyquist 约束 $f^k\ge2\,\mathrm{BW}_k$
> - [[ReinforcementLearning]] — 动作持续与 options/时间抽象互补；周期非平稳策略梯度是标准 PG 定理的多相位扩展
> - [[Dynamics]] — 快/慢子系统分解对应双时间尺度（奇异摄动）动力学
>
> **核心技术**: Factored-Action MDP, Action Persistence (多变量), Periodic Non-stationary Policy, AP-PI / AP-AC

## 1. 问题设定与动机 ← 逻辑与价值

### 1.1 一句话核心
不同动作需要不同控制频率 → **周期性非平稳策略 > 单一平稳策略**。

### 1.2 直观隐喻
开手动挡：方向盘需高频调（10Hz）、油门中频（2Hz）、挡位低频（0.1Hz）。强制同频：太快则换挡过频（损耗）、太慢则转向迟钝（危险）。AP-AC 让每个动作变量保持各自"最佳节奏"。

### 1.3 领域定位与现有方法局限
Multi-rate Control（经典）→ 标准 RL（单频）→ 时间抽象（Options/HRL）→ Action Persistence（单一 persistence）→ **AP-AC（多变量多持续时间 + 周期非平稳 + 理论保证）**。

| 方法 | 多持续时间 | 策略类型 | 最优性保证 |
|-----|----------|---------|----------|
| 标准 RL | ❌ | 平稳 | ✅（仅同频） |
| 单持续 RL（如 PFQI） | 单一 | 平稳 | ✅（单持） |
| **AP-AC** | **✅ 各变量 $c^k$** | **周期非平稳** | **✅** |

### 1.4 Delta 与贡献
- **C1**：形式化多动作持续时间问题，证明平稳策略的次优性（§2.3 反例）。
- **C2**：AP-PI，理论保证收敛到最优。
- **C3**：AP-AC，神经网络实现的可扩展算法。

## 2. 核心方法与理论 ← 原理与理论

### 2.1 核心符号溯源

| 符号 | 类型 | 来源 | 物理/算法意义 | 符号陷阱 |
|------|------|------|----------------|----------|
| $A=A^1\times\cdots\times A^m$ | 动作空间 | 问题设定 | 分解（factored）动作 | 各分量有独立持续时间 |
| $c=(c^1,\dots,c^m)$ | 持续向量 | **预先指定**（非学习） | 各变量持续步数（基础步为单位） | **固定不自适应**——与 [[Elastic Time Step Reinforcement Learning, VTS-RL\|VTS-RL]] 的可学 $\tau(s)$ 的关键分野 |
| $\phi(t,k)=t\bmod c^k$ | 相位 | 计算 | 周期内的相位索引 | 决定用哪个策略头 |
| $T=\mathrm{lcm}(c^1,\dots,c^m)$ | 周期 | 推导 | 策略周期 | **lcm 可爆炸**（$\mathrm{lcm}(3,7)=21$）→ 用 2 的幂频率比 |
| $\bar{\pi}_c$ | 策略 | 构造 | $c$-持续策略 | 周期非平稳、非马尔可夫 |
| $\pi^k_\phi$ | 策略头 | 学习 | 第 $k$ 变量、第 $\phi$ 相位的策略 | 每相位独立头，共 $\sum_k c^k$ 个 |
| $Q^{\bar{\pi}_c}$ | 值函数 | 学习 | $c$-持续策略的 Q | 评估须含相位信息 |

### 2.2 Factored-Action MDP 与动作持续
$M=\langle S,A,P,R,\gamma\rangle$，$A=A^1\times\cdots\times A^m$。动作持续 $c=(c^1,\dots,c^m)$，$c^k$ 是第 $k$ 个动作变量的持续时间。示例：机械臂 $c^{arm}=1$（50Hz），抓手 $c^{gripper}=5$（10Hz）。

$c$-持续策略：
$$\bar{\pi}_{c,t}(a\mid h_t)=\prod_{k=1}^m\bar{\pi}_{c,t}^k(a^k\mid h_t),\quad
\bar{\pi}_{c,t}^k(a^k\mid h_t)=\begin{cases}\pi_t^k(a^k\mid h_t) & t\bmod c^k=0\\ \delta_{a^k_{t-(t\bmod c^k)}}(a^k) & \text{otherwise}\end{cases}$$
即每 $c^k$ 步才重新决定 $a^k$，其余时间保持上次决定。

### 2.3 平稳策略的次优性（核心定理）

**定理（非正式）**：由平稳策略诱导的 $c$-持续策略可能**任意次优**。

**反例直觉**：取 $c=(2,3)$，最优轨迹要求 $a^1$ 在 $t=0$ 取 1（去 $s_1$）、在 $t=2$ 取 0（去终点 $s_3$）；但 $a^2$ 仍在持续期内。平稳策略在状态 $s_2$ 只能对 $a^1$ 选一个固定值 → 无法同时满足 $t=0$ 与 $t=2$ 的不同需求。**根因**：当 $c^1\neq c^2$，"还要等多久才能改 $a^2$"是决策的隐藏状态，平稳策略对它视而不见。

### 2.4 周期性非平稳策略
**关键洞察**：最优 $c$-持续策略是**周期性**的，周期 $T=\mathrm{lcm}(c^1,\dots,c^m)$。参数化：
$$\pi_t^k(a^k\mid s)=\pi^k_{\phi(t,k)}(a^k\mid s),\qquad \phi(t,k)=t\bmod c^k,$$
即用"相位"$\phi$ 索引周期内位置。这把"隐藏的等待状态"显式编码进策略，恢复最优性。

### 2.5 AP-PI 与 AP-AC
- **AP-PI**（表格）：策略评估算 $Q^{\bar\pi_c}$；策略改进对每个相位 $\phi$、变量 $k$：$\pi^k_\phi(s)\leftarrow\arg\max_{a^k}\mathbb{E}[Q^{\bar\pi_c}(s,a)]$。时间复杂度 $O(|S|^2|A|T)$，仅比标准 PI 多 $|A|$ 因子。
- **AP-AC**（神经网络）：共享 backbone，每个动作变量 $k$ 有 $c^k$ 个策略头，按当前相位 $\phi(t,k)$ 选头；Critic 为标准 Q 网络。策略梯度按相位分组（§5）。

### 2.6 概念边界与符号陷阱
- **$c$ 预先指定、非学习**：AP-AC 解决"给定多频率如何最优"，不解决"频率本身如何学"——后者是 [[Elastic Time Step Reinforcement Learning, VTS-RL|VTS-RL]] 的方向。
- **周期非平稳是方法本体**：同一状态、不同相位 $\phi$ 动作可不同；退化为平稳即 §2.3 的次优。
- **$T=\mathrm{lcm}$ 可爆炸**：频率比含互质数时策略头数量激增 → 实践用 $c\in\{1,2,4,8\}$。
- **策略头显存**：共 $\sum_k c^k$ 个头，$m$ 大时显存压力 → 相位 embedding + 权重共享缓解。
- **Replay buffer 须存时间步 $t$**：用于算 $\phi(t,k)=t\bmod c^k$，并行 env 中需仔细同步。

## 3. 实验与验证 ← 实验与验证

### 3.1 设置
- 修改的 MuJoCo（HalfCheetah 躯干/腿分离、Ant 不同腿不同频）+ 交通信号控制 (SUMO，多路口不同切换频率)。
- 基线：标准 SAC（忽略多频）、Fast-Repeat（全高频重复）、Low-Freq（全用最低频）。

### 3.2 主要结果

| 任务 | SAC | Fast-Repeat | Low-Freq | **AP-AC** |
|-----|-----|-------------|----------|----------|
| HalfCheetah-MF | 5200 | 4800 | 3900 | **6100** |
| Ant-MF | 3800 | 3500 | 2900 | **4600** |
| Traffic | 78% | 72% | 65% | **85%** |

> [!important] 数字如何印证故事
> AP-AC 同时优于 Fast-Repeat 与 Low-Freq——这正是 §2.3 定理的实验体现：Fast-Repeat 强制低频变量高频更新（引入损耗噪声），Low-Freq 让高频变量反应迟钝，**两个极端都是"单一平稳频率"的牺牲品**；只有让每个变量保持各自相位才能两头兼顾。频率差异越大，AP-AC 优势越明显（15–25%）。

### 3.3 Ablation 因果链

| 去掉/改变 A | 结果 B | 因果机制 C | 启示 D |
|---------|---------|----------|--------|
| 周期策略 → 平稳策略 | 性能 −15~25% | 平稳无法区分不同相位的最优动作 | 周期非平稳是最优性必需（§2.3） |
| 全用最高频 (Fast-Repeat) | 下降 + 低频变量频繁切换损耗 | 强制高频更新低频变量引入噪声 | 高频不是"越多越好" |
| 全用最低频 (Low-Freq) | 最差 | 高频变量反应迟缓 | 低频牺牲精细控制 |
| 减少相位数（共享头） | 下降 | 不同相位需不同策略，共享致干扰 | 相位分头不可过度压缩 |

### 3.4 工程关键细节
- **相位索引存入 buffer**：每样本存时间步 $t$ 以算 $\phi$；并行 env 需同步。
- **频率比用 2 的幂**（$c\in\{1,2,4,8\}$）避免 lcm 爆炸。
- **相位 embedding 条件化** + 共享 backbone 压缩参数。
- **单元测试**：验证 $\phi=0$ 时动作变化、$\phi\neq0$ 时动作保持，防索引 bug。

## 4. 替代方案与理论局限 ← 未来与结合

| 维度 | 局限 | 替代方案 |
|------|------|----------|
| **理论** | 收敛证明依赖表格有限 MDP，未扩展连续状态；$T=\mathrm{lcm}$ 可爆炸 | 连续时间公式化（Hamilton-Jacobi）避免离散化 |
| **算法** | 频率向量 $c$ 须预先指定、不自适应 | 把 persistence 作为可学输出（[[Elastic Time Step Reinforcement Learning, VTS-RL\|VTS-RL]] 的 duration head） |
| **工程** | 多策略头增显存（$\sum_k c^k$ 头）；未处理连续时间/异步通信 | 权重共享 + 相位 embedding 压参 |

## 5. 与知识体系的联系 ← 未来与结合

### 与 [[ControlTheory]] 的联系
多频率控制对应多速率采样系统：动作变量采样率 $f^k=f_{base}/c^k$，Nyquist 约束 $f^k\ge2\,\mathrm{BW}(\text{subsystem}_k)$。快子系统（手指）需高频、慢子系统（手臂）可低频——这给"$c^k$ 该取多少"一个**控制论的先验**（按子系统带宽定），而非纯调参。

### 与 [[ReinforcementLearning]] 的联系
周期非平稳策略梯度按相位分组：
$$\nabla_\theta J=\sum_{\phi=0}^{T-1}\mathbb{E}_{t:\,t\bmod T=\phi}\big[\nabla_\theta\log\pi_\phi(a_t\mid s_t)\cdot Q^{\bar\pi_c}(s_t,a_t)\big].$$
这是标准 PG 定理的多相位扩展，保持 Actor-Critic 无偏性。

### 与 [[Dynamics]] 的联系
快/慢子系统分解对应双时间尺度（奇异摄动）动力学：当 $c^{fast}\ll c^{slow}$，快变量在慢变量一个持续周期内多次更新，形成 $\dot x_{fast}=f(x_{fast},x_{slow})$ 的多尺度结构。

## 6. 簇定位与跨方法对比 ← 未来与结合

| 维度 | AP-AC | [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning\|PFQI]] | [[Elastic Time Step Reinforcement Learning, VTS-RL\|VTS-RL]] | FiGAR |
|-----|-------|------|------|-------|
| 频率维度 | **多变量各自 $c^k$** | 单一全局 $k$ | 单一 $\tau$ | 单一重复 $n$ |
| 固定/自适应 | 预设固定 | 离线选、固定 | **状态依赖可学** | 学重复数 |
| 理论保证 | **最优性 + 收敛** | Bellman 收缩 + 损失界 | Lyapunov（弱） | 无 |
| 时间抽象层级 | 低（动作级） | 低 | 低 | 中 |

> [!note] 领域级 insight：control frequency 簇的三维分解（与 [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning#6.4 领域级综述：control frequency / time-step 簇（本篇为理论锚点）|PFQI §6.4 簇综述]] 互参）
> 把 PFQI / VTS-RL / AP-AC 三篇并置，可把"控制频率问题"分解为**三个正交维度**：
> 1. **单一 vs 多变量频率**：PFQI/VTS-RL 单一；**AP-AC 多变量**。
> 2. **固定 vs 状态自适应**：PFQI/AP-AC 固定；**VTS-RL 状态依赖**。
> 3. **有无理论保证**：PFQI（收缩+界）、AP-AC（最优性）强；VTS-RL（Lyapunov）弱。
>
> 每篇占据不同组合：PFQI=⟨单一·固定·强保证⟩、VTS-RL=⟨单一·自适应·弱保证⟩、AP-AC=⟨多变量·固定·强保证⟩。**没有任何工作同时拿下"多变量 + 状态自适应 + 强保证"**——这是该簇最清晰的空白，也正是 WMTS task scheduling（手指/手腕/视觉异构频率 + 状态依赖调度 + 需要保证）的理论机会。AP-AC 把空白从二维（§6.4 综述的"状态依赖+保证"）精化到三维。

## 7. 对用户研究的启发（灵巧手转笔 / Sim-to-Real）

典型灵巧操作系统天然多频：视觉 30Hz · 高层规划 10Hz · 手臂 100Hz · 手指 500Hz · 触觉 1000Hz。

1. **多频率灵巧手控制**：转笔中手指 PD 可 500Hz（$c^{finger}=1$）、手腕 50Hz（$c^{wrist}=10$）、视觉 30Hz（$c^{vision}\approx16$），AP-AC 可统一处理这种异构频率。
2. **触觉-视觉异构采样**：触觉反应式动作设 $c=1$、视觉引导动作设 $c\approx33$，避免被最慢模态拖累。
3. **周期策略与转笔的天然契合**：转笔的"发力→空中→接住"本就周期，与 AP-AC 周期非平稳策略结构同构——相位 $\phi$ 可直接对应转笔阶段。
4. **与 WMTS 的接口**：AP-AC 的"按相位分头"是 WMTS 多时间尺度调度的一种具体实现；但 WMTS 还需 VTS-RL 式的状态依赖（何时进入下一相位由状态而非固定 $c^k$ 决定）——即上文三维空白。

## References
- [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning]] — 单一全局 persistence 的理论锚点（见其 §6.4 簇综述）
- [[Elastic Time Step Reinforcement Learning, VTS-RL]] — 状态依赖可学 $\tau$；本文的"自适应 $c$"方向
- Options (Sutton 1999) / FiGAR (Sharma 2017) — 时间抽象与单一动作重复的对比对象
