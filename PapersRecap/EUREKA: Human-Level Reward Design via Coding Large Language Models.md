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
venue: ICLR 2024
paper-pdf: "[[Papers/EUREKA: HUMAN-LEVEL REWARD DESIGN VIA CODING LARGE LANGUAGE MODELS.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
---

# EUREKA: Human-Level Reward Design via Coding Large Language Models

> [!abstract] 核心概要
> 利用 GPT-4 的代码生成能力进行**进化式奖励函数搜索**，在 29 个 RL 环境（含 10 种机器人形态）上实现了超越人类专家的奖励设计，并首次实现了仿真灵巧手的高速转笔技能。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] - 奖励设计是 RL 的核心瓶颈
> - [[Optimization]] - 奖励塑形与轨迹优化的关系
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

### 训练细节

- **RL 算法**: PPO (IsaacGym 内置 rl_games 库)
- **进化参数**: $K = 16$ 采样/轮, $N = 5$ 进化轮次 → 总计 80 个候选奖励函数
- **GPU 评估**: 每个候选奖励在 IsaacGym 上并行训练 ~$10^7$ 步 (数分钟/候选, A100)
- **LLM**: GPT-4 (temperature = 1.0 保证采样多样性)
- **Prompt 结构**: ~2K tokens (环境代码) + ~500 tokens (任务描述 + Reflection)
- **总计算量**: 29 个任务 × 80 候选 × ~5 min/候选 ≈ ~$10^3$ GPU-hours

### 转笔任务详情
- **Curriculum**：逐步增加旋转速度和圈数
- **结果**：Shadow Hand 实现连续高速转笔
- **对比**：纯人类奖励设计从未成功

### Ablation 因果链

| 去掉组件 | 效果 | 因果机制 |
|---------|------|--------|
| 进化搜索 (K=1) | 性能下降 ~40% | 单次 LLM 采样随机性高，缺乏多样性筛选 |
| Reward Reflection | 收敛轮次增加 2× | 无训练曲线反馈，LLM 无法识别奖励分量瓶颈 |
| Environment Context | 代码执行错误率 >80% | LLM 无法访问变量名/API，只能猜测 |
| 多组件分解 | 转笔任务失败 | 单一标量奖励无法区分旋转进度与稳定性 |

> [!note] 关键因果洞察
> 进化搜索 + Reflection 形成闭环：搜索提供多样性 (exploration)，Reflection 提供梯度方向 (exploitation)。缺少任一，搜索退化为随机采样或局部搜索。

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

### 工程关键细节 (Engineering Tricks)

1. **Temperature = 1.0**：低温生成的奖励函数高度相似，进化失去多样性；高温保证搜索空间覆盖
2. **奖励组件分解**：要求 LLM 输出 `reward_dict` 而非单一标量，便于 Reflection 定位瓶颈组件
3. **代码沙箱执行**：自动检测语法/运行时错误，过滤无效候选，减少 GPU 浪费
4. **Fitness z-score 归一化**：跨候选的适应度分数使用 z-score，避免绝对值尺度差异误导进化方向

> [!warning] 三维度局限性分析
> - **理论层面**：进化搜索缺乏收敛性保证——搜索空间是代码空间（无穷维），$K \times N$ 的有限采样无法保证全局最优；LLM 的 in-context learning 是否等价于奖励空间梯度下降缺乏理论分析
> - **算法层面**：外层评估依赖完整 RL 训练 ($10^7$ 步/候选)，样本效率极低；无法处理需要长期规划的稀疏奖励任务
> - **工程层面**：GPT-4 API 成本高、延迟大；环境代码长度受 context window 限制；无人工介入机制
>
> **替代方案**：Inverse RL 从演示推断奖励（无需 LLM）；可微分奖励模型替代代码生成；Text2Reward 用语言模型直接生成奖励参数（而非代码）

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
- [[ReinforcementLearning]] - EUREKA 生成的奖励用于 PPO 训练
- [[ReinforcementLearning]] - Mediator-based surrogate reward 提供因果推断视角补充 LLM 奖励搜索
- [[Optimization]] - 进化搜索思想与 MPPI 类似

### 对转笔 / Sim-to-Real 的具体启发

1. **转笔奖励的自动发现**：手工奖励需平衡旋转速度、笔稳定性、指尖接触力——权重组合空间巨大，EUREKA 的进化搜索天然能覆盖
2. **Curriculum 自动生成**：转笔任务中 $\omega_{target}: 0.5 \to 2.0$ rad/s 的自动 Curriculum，可直接迁移至灵巧手任务的难度递增
3. **Sim-to-Real 的奖励鲁棒性**：生成的奖励是代码可直接执行——但 sim 中 `fingertip_pos` 与真机有 gap，需配合域随机化

### 与 Foundation 的数学联系

**与 [[ReinforcementLearning]] 的联系**：EUREKA 外层进化等价于奖励函数空间 $\mathcal{R}$ 上的零阶优化：$R^{(k+1)} = R^{(k)} + \text{LLM\_mutation}(\text{Reflect}(F(A_M(R^{(k)}))))$，与 [[ReinforcementLearning]] 中 CMA-ES 等进化策略在结构上同构

**与 [[Optimization]] 的联系**：适应度 $F(\pi) = \mathbb{E}[\sum_t r_{task}]$ 的外层优化是双层优化：$\max_R F(A_M(R))$，内层是标准 RL，外层是 LLM 进化。这与 [[Optimization]] 中 bi-level optimization 形式一致

**与 [[StochasticProcess]] 的联系**：$K=16$ 的批量采样本质是蒙特卡洛采样，进化选择是 importance sampling 的变体——高适应度候选被赋予更高权重，这与 [[StochasticProcess]] 中 MPPI 的轨迹加权思想完全一致

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

### 跨方法对比

| 维度 | EUREKA | L2R (Yu 2023) | Inverse RL | 手工奖励设计 |
|-----|--------|---------------|------------|-------------|
| 任务特定 Prompt | ❌ 不需要 | ✅ 需要 | N/A | N/A |
| 奖励模板 | 自由代码 | 预定义 | 隐式(判别器) | 手工公式 |
| 可解释性 | ✅ 代码可审查 | ✅ 模板化 | ❌ 黑盒 | ✅ 完全透明 |
| 扩展性 | ✅ 29+ 环境 | ⚠️ 模板限制 | ⚠️ 演示限制 | ❌ O(N) 人工 |
| Sim-to-Real | 未验证 | 未验证 | 已验证 | 已验证 |
| 计算成本 | 高 (GPU+API) | 低 | 中 | 零 |

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

---

## 9. 簇内坐标与 Foundation 锚点

> [!abstract] 暗线锚定：Continuation / 同伦 + 认知不确定性（该学处）
> EUREKA 触及本簇两条暗线：① **Continuation**——转笔任务里 EUREKA 生成的课程让 $\omega_{target}:0.5\to2.0$ rad/s（§6 具体启发），正是 [[Curriculum Learning#3.2 与 Continuation Method 的联系|Curriculum Learning 的 $Q_0\to Q_1$]] 的 RL 实例；② **零阶采样+加权**——外层 $K=16$ 采样→按 fitness z-score 加权→挪 prompt 分布，与 CMA-ES 结构同构，是"采样+加权统一优化"暗线的 LLM 版本。EUREKA 的独特位置：它把 continuation 的**难度轴**和奖励设计**同时**外包给 LLM，是 [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间|RL §7.3]] 谱系里"课程设计器自动化"的最激进端点。

**Foundation 精确锚点**（已 grep 验证章节存在）：

- [[ReinforcementLearning#8.2 奖励工程：最危险的自由度|RL §8.2 奖励工程]]：EUREKA 直接攻击的就是这一节的核心痛点——"92% 的 RL 研究者认为自己的奖励设计次优"。它把"最危险的自由度"从人工试错变成进化搜索的外层变量。
- [[Optimization#4.4 零阶与进化优化：当梯度根本求不出来（CMA-ES）|Optimization §4.4 CMA-ES]]：EUREKA 外层是奖励代码空间 $\mathcal{R}$ 上的零阶进化——$R^{(k+1)}=R^{(k)}+\text{LLM\_mutation}(\text{Reflect}(F(A_M(R^{(k)}))))$，与 CMA-ES "采样→按 fitness 加权→挪分布"完全同构（fitness 用 z-score 归一化 = CMA-ES 的 rank-based weighting）。这是本文与 §4.4 的**数学根**，不是装饰链接。

**簇内互链 + Delta**：

| 簇内论文 | 关系 | Delta |
|:--|:--|:--|
| [[Curriculum Learning\|Curriculum Learning]] | EUREKA 是其 2009 谱系的**LLM 端点** | Bengio 需人工 `difficulty_fn`；EUREKA 让 GPT-4 从环境源码**自动生成**奖励+课程，无需任务特定 prompt |
| [[Hindsight Experience Replay\|HER]] | 两文攻击**同一敌人**：sparse reward 下学不动 | EUREKA **加密奖励**（生成 dense reward code 让梯度出现）；HER **重标目标**（不改 reward 稀疏性，改条件变量 $g$）。一个改 $R$，一个改 $g$，正交互补 |
| [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]] | 都是"自动课程"，但作用空间不同 | EUREKA 在**奖励/reward-space**自动化；DemoStart 在**初始状态/reset-space**自动化（ZVF）。DemoStart 甚至能用**二值稀疏** reward，正因为它不靠 reward 设计而靠 frontier 选择 |
| [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation\|Curriculum > Haptic]] | 互补验证 reward-schedule 的威力 | Curriculum>Haptic 手工枚举 $c_R,c_L$ 时序证明"reward 时序 > 触觉"；EUREKA 则**自动搜索** reward 系数组合——若二者结合，可让 LLM 直接进化 $c_R,c_L$ 的**课程 schedule** 而非单一权重 |

> [!tip] 一句话记忆锚
> **EUREKA = 把"最危险的自由度"（奖励）交给 CMA-ES 式的 LLM 进化。** 它首次让仿真灵巧手转笔成功，靠的不是新 optimizer，而是 [[Optimization#4.4 零阶与进化优化：当梯度根本求不出来（CMA-ES）|零阶进化]] + [[Curriculum Learning\|continuation 课程]] + reward 分量分解三者合一。局限也清楚：外层评估要完整 RL 训练（$10^7$ 步/候选），样本效率极低，且 Sim-to-Real 未验证。
