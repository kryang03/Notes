---
tags:
  - paper
  - reinforcement-learning
  - sparse-reward
  - exploration
aliases:
  - HER
paper-year: 2017
read-date: 2026-02-02
venue: NeurIPS
paper-pdf: "[[Papers/Hindsight Experience Replay.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
---

# Hindsight Experience Replay

> [!abstract] 核心贡献
> 提出 **Hindsight Experience Replay (HER)**——一种从失败轨迹中学习的技术，将稀疏奖励问题转化为隐式课程学习，使得在二值奖励下也能高效学习机器人操作策略。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] - HER 解决稀疏奖励下的探索困难
> - [[ReinforcementLearning]] - HER 策略可直接 Sim-to-Real 部署
> - [[Optimization]] - 目标重标注作为隐式课程优化
>
> **核心技术**: Goal-conditioned RL, Experience Replay, Implicit Curriculum

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**人类能从失败中学到几乎和成功一样多的东西**——HER 让 RL 智能体具备这种能力，通过将失败轨迹的实际到达状态作为"假装的目标"进行重放学习。

### 直观隐喻
想象练习投篮：球没进但偏右。传统 RL 只记录"这次失败了"；HER 则额外记录"如果篮筐在右边一点，这次就进了"——==从同一次经历中提取两倍的学习信号==。

### 领域定位
- 开创性地解决了**稀疏奖励 + 连续控制**组合的探索难题
- 成为灵巧操作、接触丰富任务的**标准配置**
- 启发了后续的 Goal-conditioned RL 研究线

### 1.2 现有方法的局限

| 现有方法 | 核心困境 |
|---------|--------|
| **Dense Reward Shaping** | 需要大量人工设计奖励函数，且次优 shaping 可能引导策略进入局部最优 |
| **Curiosity-driven Exploration** | 内在奖励在高维连续动作空间中信噪比低，难以引导精确操作 |
| **Curriculum Learning** | 需要显式设计目标难度序列，对任务先验要求高 |
| **标准 Experience Replay** | 在稀疏奖励下 buffer 中几乎全是负样本，Q 函数无有效梯度信号 |

根本矛盾：**稀疏二值奖励** $r \in \{-1, 0\}$ 下，随机探索命中目标的概率随维度指数衰减 $P(\text{success}) \propto \epsilon^d / V_{\text{state}}$，导致 off-policy buffer 中正样本近乎为零。

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人工作 | 局限 | HER 的突破 |
|---------|------|-----------|
| Dense Reward Shaping | 需要大量工程 | 无需奖励工程 |
| Experience Replay | 仅重用已有经验 | 创造性地重标注目标 |
| Curriculum Learning | 需显式设计课程 | 自动形成隐式课程 |

### 关键贡献点
1. **Goal Relabeling**: 在回放时将轨迹末态作为新目标，将失败变成"成功"
2. **Universal Value Function**: 学习 $Q(s, a, g)$，目标 $g$ 作为条件输入
3. **无需额外样本**: 从已有数据中"创造"新的有效训练样本

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 数学建模

**目标条件强化学习框架**：

状态增广为 $(s, g)$，奖励函数为：
$$
r(s, a, g) = \begin{cases} 
0 & \text{if } \|s' - g\| < \epsilon \\
-1 & \text{otherwise}
\end{cases}
$$

**HER 核心算法**：

对于收集到的轨迹 $\tau = (s_0, a_0, s_1, \ldots, s_T)$：

1. **标准回放**: 存储 $(s_t, a_t, r_t, s_{t+1}, g)$
2. **Hindsight 回放**: 额外存储 $(s_t, a_t, r'_t, s_{t+1}, g')$
   - 其中 $g' = m(s_T)$ 是轨迹末态的映射
   - $r'_t = r(s_t, a_t, g')$ 重新计算奖励

### 3.2 核心代码逻辑

```python
import torch
import numpy as np

def her_relabel(episode, k=4, strategy='future'):
    """HER 目标重标注核心逻辑
    episode: list of (obs, action, reward, next_obs, goal, achieved_goal)
    k: 每个 transition 额外产生的 hindsight 样本数
    """
    T = len(episode)
    augmented_transitions = []

    for t in range(T):
        obs, action, _, next_obs, goal, achieved = episode[t]
        
        # 1. 原始 transition（保留原始目标）
        reward = compute_reward(achieved, goal)  # 通常 -1 或 0
        augmented_transitions.append((obs, action, reward, next_obs, goal))
        
        # 2. Hindsight relabeling: 用未来达到的状态替换目标
        if strategy == 'future':
            # 从当前步之后随机采样 k 个时间步
            future_indices = np.random.choice(range(t, T), size=min(k, T - t), replace=False)
        elif strategy == 'final':
            future_indices = [T - 1] * k  # 只用最终状态
        
        for idx in future_indices:
            # 关键: 用 episode[idx] 的 achieved_goal 替换为新目标
            new_goal = episode[idx][5]  # achieved_goal of future step
            new_reward = compute_reward(episode[t][5], new_goal)  # 通常 = 0 (成功)
            augmented_transitions.append((obs, action, new_reward, next_obs, new_goal))
    
    return augmented_transitions  # 每个原始样本产生 1+k 个有效样本

def compute_reward(achieved_goal, desired_goal, threshold=0.05):
    """二值稀疏奖励: 达到目标附近 → 0, 否则 → -1"""
    dist = torch.norm(achieved_goal - desired_goal)
    return 0.0 if dist < threshold else -1.0
```

**物理量来源追踪**:
- `achieved_goal`: 来自环境步进后的实际状态（Rollout 阶段，detached）
- `new_goal`: 来自同一 episode 未来时步的 achieved_goal（Rollout 数据重组）
- `new_reward`: 基于重标注目标重新计算，不涉及网络前向传播

### 3.3 采样策略

论文提出多种目标采样策略：

| 策略 | 说明 | 适用场景 |
|-----|------|---------|
| **final** | 使用轨迹末态 | 最简单，适合大多数任务 |
| **future** | 采样同轨迹后续状态 | 默认推荐 |
| **episode** | 采样整个 episode 中的状态 | 长时程任务 |
| **random** | 从 buffer 随机采样 | 探索多样性 |

### 3.3 理论洞见

> [!note] 为什么 HER 有效
> **隐式课程学习**: HER 自动生成从易到难的目标序列。
> - 早期: 智能体随机探索，末态接近初态 → 学习短距离移动
> - 中期: 能力提升后末态更远 → 学习中距离操作
> - 后期: 逐渐接近真实目标分布

## 4. 实验与验证 (Experiments)

### 实验设置
- **平台**: Fetch 机器人仿真 (MuJoCo)
- **任务**: Push, Slide, Pick-and-Place
- **奖励**: 纯二值稀疏奖励
- **算法**: DDPG + HER

### 训练细节

| 配置 | 值 |
|------|----|
| 网络架构 | 3-layer MLP, hidden=256, ReLU |
| 优化器 | Adam, lr=1e-3 |
| Replay Buffer | 1e6 transitions |
| Batch Size | 256 |
| HER 采样策略 | future, k=4 |
| 目标阈值 $\epsilon$ | 0.05 (5cm) |
| Polyak 软更新 $\tau$ | 0.95 |
| Epochs | 50 |
| Rollout 长度 | 50 steps per episode |

### 关键结果
| 任务 | 无 HER | 有 HER |
|-----|-------|-------|
| Push | ~0% | ~100% |
| Slide | ~0% | ~100% |
| Pick-and-Place | ~0% | ~100% |

**Sim-to-Real**: 策略直接部署到真实 Fetch 机器人，无需微调即可完成任务。

### Ablation Study 因果链

| 消融配置 | 性能变化 | 因果机制 |
|---------|---------|--------|
| 去掉 HER (仅 DDPG) | ~0% 成功率 | 稀疏奖励下几乎无正样本 → Q 函数完全无法学习 |
| final → random 策略 | 收敛变慢 | random 样本与当前能力分布不匹配 → 难度过高 |
| k=1 (少补充) | 成功率降 ~20% | 正样本比例不足 → Q 值估计偏差 |
| k=8 (多补充) | 与 k=4 类似 | 边际收益递减，重标注目标开始重复 |
| 去掉目标条件 | 无法收敛 | 非目标条件 Q 无法区分不同目标 → 策略退化为均匀动作 |

## 4.5 工程关键细节 (Engineering Tricks)

- **目标空间归一化**: 目标 $g$ 和 achieved_goal 必须在同一尺度空间，否则距离阈值 $\epsilon$ 无意义
- **状态-目标拼接**: 输入网络的是 $[s; g]$ 而非 $s$ 单独，确保 Q 函数对目标敏感
- **重标注时机**: 在存入 buffer 时即完成重标注（而非采样时），避免重复计算
- **奖励符号**: 使用 $r = -1$（而非 $r = 0$）作为失败奖励，确保 Q 值有明确梯度方向
- **Episode 长度 vs 目标难度**: 过短的 episode 使得 HER 目标太简单，过长则浪费样本

## 5. 批判性分析 (Critical Analysis)

### 优势
- **简洁**: 无需修改算法核心，仅增加数据预处理
- **通用**: 可与任意 off-policy 算法组合
- **高效**: 单次采样产生多个有效样本

### 局限性
- **目标空间假设**: 需要目标可以从状态空间中采样
- **奖励结构**: 假设奖励仅依赖于 $\|s - g\|$
- **长时程困难**: 对于需要复杂中间步骤的任务仍有挑战

### 理论/算法/工程三维分析

| 维度 | 局限 | 替代方案 |
|------|------|--------|
| 理论 | 目标重标注引入非平稳分布偏移（off-policy correction 缺失） | Importance sampling 修正，或用 Outcome-Driven RL 的理论框架 |
| 算法 | 仅适用于可重标注目标的任务（需 achieved_goal 接口） | Relay Policy Learning 层次化分解, Curriculum-guided HER |
| 工程 | k 倍内存开销（每个 transition 存 1+k 份） | 延迟重标注（采样时动态生成）减少 buffer 占用 |

### 与 DNPM 项目的关联

> [!warning] 与速度缩放方法的对比
> - HER 解决**稀疏奖励**问题
> - DNPM 的速度缩放解决**长因果链探索**问题
> - **组合方案**: HER 提供样本效率，速度缩放提供探索覆盖

## 6. 对灵巧操作的启发 (Implications)

1. **接触丰富任务**: HER 天然适合操作任务，因为末态往往反映有意义的物体配置
2. **灵巧手训练**: 手内操作的子目标（如特定抓取姿态）可作为 HER 目标
3. **与 DNPM 结合**: 速度缩放产生的"慢速成功轨迹"可为 HER 提供更多有效目标
### 对灵巧手转笔/Sim-to-Real 的启发

1. **转笔子目标设计**: 转笔可分解为多个子目标（抨起→旋转 90°→接住），HER 可为每个子目标提供隐式课程
2. **旋转角度作为目标**: achieved_goal = 笔的当前旋转角度，失败的轨迹仍可重标注为“到达某个中间角度”的成功经验
3. **Sim-to-Real 友好**: HER 减少对精确奖励函数的依赖，触觉/视觉反馈的 sim-real gap 影响较小
## 7. 演进脉络定位 (Evolution Context)

### 跨方法对比

| 方法 | 探索机制 | 奖励类型 | 样本效率 | 适用场景 |
|------|---------|---------|---------|--------|
| Dense Reward Shaping | 奖励梯度引导 | 稠密 | 低 | 需奖励工程 |
| Curiosity-driven (ICM) | 预测误差 | 内在 | 中 | 无明确目标 |
| **HER** (本文) | 目标重标注 | 二值稀疏 | 高 | 目标条件任务 |
| Curriculum Learning | 显式难度调度 | 任意 | 中 | 需设计课程 |
| [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]] | 示范引导 + 自动课程 | 稀疏 | 高 | 灵巧手 Sim-to-Real |

### 演进线路

```
前置工作: Universal Value Function Approximators (Schaul 2015)
    ↓
本论文: Hindsight Experience Replay (2017)
    ↓
后续发展:
├── Curriculum-guided HER (2019) - 结合显式课程
├── Relay Policy Learning (2019) - 层次化 HER
├── Outcome-Driven RL (2020) - 理论分析
└── 与 Diffusion Policy 结合 (2023+)
```

### 与 [[ReinforcementLearning]] 的联系

HER 的目标条件框架定义了增广 Q 函数 $Q(s, a, g)$，这是 [[ReinforcementLearning|DDPG]] 的直接扩展。重标注的数学本质是在 off-policy buffer 中构造新的 $(s, a, r', s', g')$ 元组，保持 Bellman 方程一致性：

$$
Q(s, a, g') = r(s, a, g') + \gamma \max_{a'} Q(s', a', g')
$$

### 与 [[Optimization]] 的联系

HER 的隐式课程可视为在目标空间上的自适应采样策略。早期，达到的目标集中在初始状态附近（简单目标）；随着能力提升，重标注目标渐进向真实目标分布靠拢。这与 [[Optimization]] 中的课程学习的优化视角等价，但无需显式设计：

$$
p_{\text{HER}}(g) \approx p_{\text{achieved}}(g) \xrightarrow{\text{training}} p_{\text{desired}}(g)
$$

---

**参考文献**:
- Andrychowicz, M. et al. "Hindsight Experience Replay." NeurIPS 2017.
