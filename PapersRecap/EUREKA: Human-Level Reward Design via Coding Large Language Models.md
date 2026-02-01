---
tags:
  - paper
  - reward-design
  - llm
  - dexterous-manipulation
  - curriculum-learning
aliases:
  - EUREKA
  - LLM Reward Design
paper-year: 2023
read-date: 2026-01-31
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
---

# EUREKA: Human-Level Reward Design via Coding Large Language Models

> [!abstract] 核心概要
> 利用 GPT-4 的代码生成能力进行**进化式奖励函数搜索**，在 29 个 RL 环境（含 10 种机器人形态）上实现了超越人类专家的奖励设计，并首次实现了仿真灵巧手的高速转笔技能。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#4. Advanced State Space & Reward Engineering]] - 奖励设计是 RL 的核心瓶颈
> - [[Optimization#4. 核心算法实现：轨迹优化 (Implementation: Trajectory Optimization)]] - 奖励塑形与轨迹优化的关系
> - [[ControlTheory]] - 稳定性约束下的奖励设计
>
> **核心技术**: LLM Code Generation, Evolutionary Search, Reward Reflection, Curriculum Learning

---

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**用 LLM 写奖励函数代码，通过进化搜索迭代优化，自动化奖励工程。**

### 直观隐喻
想象你在教一个机器人转笔：
- **传统 RL**：你需要手工设计一个精密的评分系统（奖励函数），告诉机器人"笔转了多少度得多少分"、"笔掉了扣多少分"——这需要大量试错，92% 的 RL 研究者认为自己的奖励设计是次优的。
- **EUREKA**：你只需要告诉 GPT-4 "让机器人转笔"，它会自动写出一堆奖励函数代码，然后通过进化算法筛选出最好的，比人类专家还强。

### 领域定位
```
Reward Shaping (Ng et al. 1999)
        ↓
Human-in-the-loop Reward Design
        ↓
Language-to-Reward (L2R, Yu et al. 2023) ← 需要任务特定 prompt
        ↓
EUREKA (2023) ← 无需任务特定 prompt，进化搜索，超越人类
        ↓
未来: 完全自主的 Agent 自我改进
```

---

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
相比 L2R（Language-to-Reward）：
| 特性 | L2R | EUREKA |
|-----|-----|--------|
| 任务特定 prompt | 需要 | **不需要** |
| 奖励模板 | 预定义 | **自由生成** |
| 优化方式 | 单次生成 | **进化搜索** |
| 性能 | 接近人类 | **超越人类 52%** |

### 关键贡献点

1. **Environment as Context**: 直接将环境源代码作为 LLM 输入，零样本生成可执行奖励函数
2. **Evolutionary Search**: 批量采样 + 进化选择，克服单次生成的随机性
3. **Reward Reflection**: 基于训练统计的文本反馈，实现 in-context 奖励改进
4. **首次实现灵巧手转笔**: 结合 Curriculum Learning，Shadow Hand 高速转笔

---

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 问题形式化

**奖励设计问题 (Reward Design Problem)**：

$$P = \langle M, R, A_M(\cdot), F \rangle$$

其中：
- $M = (S, A, T)$：世界模型（状态空间、动作空间、转移函数）
- $R$：奖励函数空间
- $A_M(R) \to \pi$：学习算法，输出优化 $R$ 的策略
- $F: \pi \to \mathbb{R}$：适应度函数（真实任务指标）

**目标**：找到 $R^* = \arg\max_R F(A_M(R))$

### 3.2 EUREKA 算法流程

```python
# Algorithm 1: EUREKA
def eureka(task_desc, env_code, LLM, fitness_F):
    prompt = initial_prompt
    R_eureka, s_eureka = None, -inf
    
    for iteration in range(N):
        # 1. 批量采样奖励函数
        rewards = [LLM(task_desc, env_code, prompt) for _ in range(K)]
        
        # 2. GPU 加速评估（IsaacGym）
        scores = [fitness_F(R) for R in rewards]
        
        # 3. 选择最佳 + 反思
        best_idx = argmax(scores)
        if scores[best_idx] > s_eureka:
            R_eureka, s_eureka = rewards[best_idx], scores[best_idx]
        
        # 4. Reward Reflection → 更新 prompt
        prompt = prompt + Reflection(rewards[best_idx], scores[best_idx])
    
    return R_eureka
```

### 3.3 关键技术细节

#### Environment as Context
- 直接输入环境 Python 代码（去除原有奖励）
- LLM 可以理解变量语义（如 `fingertip_pos`）
- 无需人工抽象，最大化可扩展性

#### Evolutionary Search 的数学保证
- $K$ 个独立采样，执行错误概率指数衰减
- 实验表明 $K=16$ 即可在首次迭代获得可执行代码

#### Reward Reflection
将训练曲线和中间指标转化为文本反馈：
```
"The reward component 'distance_to_goal' converged quickly, 
but 'orientation_error' plateaued. Consider increasing its weight."
```

---

## 4. 实验与验证 (Experiments)

### 实验设置
- **29 个环境**：IsaacGym benchmark + Dexterity benchmark
- **10 种机器人**：四足、四旋翼、双足、机械臂、多种灵巧手
- **Baseline**：人类专家设计的奖励函数

### 关键结果

| 指标 | 数值 |
|-----|------|
| 超越人类专家的任务比例 | **83%** |
| 平均归一化提升 | **52%** |
| 转笔任务成功 | **首次实现** |

### 转笔任务详情
- **Curriculum**：逐步增加旋转速度和圈数
- **结果**：Shadow Hand 实现连续高速转笔
- **对比**：纯人类奖励设计从未成功

---

## 5. 批判性分析 (Critical Analysis)

### 优势
- **通用性极强**：无需任务特定工程
- **超越人类**：自动化超越手工设计
- **可解释**：生成的是代码，可审查
- **兼容 RLHF**：支持人类反馈微调

### 局限性
- **依赖 GPT-4**：需要强大的代码 LLM
- **计算开销**：进化搜索需要大量 GPU 评估
- **仿真依赖**：需要 IsaacGym 等高效仿真器
- **Sim-to-Real 未验证**：论文仅在仿真中验证

### 未来方向
- 结合可微物理实现奖励梯度
- 扩展到真实机器人（Sim-to-Real）
- 与 Foundation Model 结合实现零样本技能迁移

---

## 6. 对灵巧操作的启发 (Implications)

### 直接应用
1. **奖励自动化**：灵巧操作的奖励设计极其困难（力闭合、滑动避免等），EUREKA 可自动处理
2. **Curriculum 设计**：LLM 可同时生成课程学习策略
3. **多任务扩展**：无需为每个操作任务手工设计奖励

### 与知识库其他内容的连接
- [[ContactMechanics]] - EUREKA 可自动发现力闭合相关的奖励项
- [[ReinforcementLearning#3. Implementation: 核心算法细节分析]] - EUREKA 生成的奖励用于 PPO 训练
- [[Optimization#5. 实时控制：模型预测控制 (Real-Time Control: MPC)]] - 进化搜索思想与 MPPI 类似

---

## 7. 演进脉络定位 (Evolution Context)

```
Reward Shaping 理论 (Ng, 1999)
        ↓
Inverse RL (从演示推断奖励)
        ↓
Language-conditioned RL (语言指令转奖励)
        ↓
L2R (Yu et al., 2023): LLM + 奖励模板
        ↓
████████████████████████████████
█  EUREKA (2023)               █
█  • 无模板自由生成             █
█  • 进化搜索优化               █
█  • 超越人类专家               █
████████████████████████████████
        ↓
未来: 自主 Agent 自我奖励设计
```

---

## 8. 核心代码逻辑

```python
# EUREKA 生成的转笔奖励函数示例（简化）
def compute_reward(obs_dict):
    # 从环境观测中提取变量
    pen_pos = obs_dict["pen_pos"]
    pen_rot = obs_dict["pen_rot"]
    target_rot = obs_dict["target_rot"]
    fingertip_pos = obs_dict["fingertip_pos"]
    
    # 组件1: 旋转进度奖励
    rotation_progress = quaternion_distance(pen_rot, target_rot)
    rot_reward = torch.exp(-rotation_progress)
    
    # 组件2: 笔稳定性奖励（防止掉落）
    pen_height = pen_pos[:, 2]
    stability_reward = torch.where(pen_height > 0.1, 1.0, 0.0)
    
    # 组件3: 指尖接触奖励
    contact_reward = compute_fingertip_contact(fingertip_pos, pen_pos)
    
    # 加权组合（权重由进化搜索优化）
    total_reward = 0.5 * rot_reward + 0.3 * stability_reward + 0.2 * contact_reward
    
    return total_reward, {
        "rot_reward": rot_reward,
        "stability_reward": stability_reward,
        "contact_reward": contact_reward
    }
```
