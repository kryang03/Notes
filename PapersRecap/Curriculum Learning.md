---
tags:
  - paper
  - curriculum-learning
  - optimization
  - deep-learning
aliases:
  - Curriculum Learning
  - 课程学习
paper-year: 2009
read-date: 2026-01-31
venue: ICML 2009
paper-pdf: "[[Papers/Curriculum Learning.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
  - "[[RepresentationLearning]]"
---

# Curriculum Learning

> [!abstract] 核心概要
> 提出**课程学习**范式：像人类教育一样，从简单样本开始训练，逐渐增加难度。这是一种**延续方法 (Continuation Method)** 的实例，能帮助非凸优化找到更好的局部极小值，并加速收敛。

> [!tip] 与理论基础的关联
> - [[Optimization]] - 课程学习与非凸景观的深层联系
> - [[Optimization]] - 课程从凸子问题开始，渐进引入非凸性；这正是 continuation method 的精髓
> - [[Optimization]] - 课程学习与优化的 continuation 方法
> - [[ReinforcementLearning]] - RL中的课程学习应用
> - [[RepresentationLearning]] - 分布偏移问题
>
> **核心技术**: Continuation Methods, Non-convex Optimization, Training Distribution Scheduling

---

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**先学简单的，再学难的——这不仅加速学习，还能找到更好的解。**

### 直观隐喻
- **人类教育**：小学 → 中学 → 大学，而不是直接读博士论文
- **动物训练 (Shaping)**：训练海豚先学跳小圈，再逐渐增大圈的高度
- **登山**：先从缓坡热身，再攀登陡峭岩壁

### 领域定位
```
Shaping in Animal Training (Skinner, 1958)
        ↓
Starting Small (Elman, 1993) - 认知科学
        ↓
████████████████████████████████
█  Curriculum Learning (2009)  █
█  Bengio et al.               █
█  • 形式化课程策略             █
█  • 证明优化优势               █
████████████████████████████████
        ↓
Self-paced Learning (2010)
        ↓
Automatic Curriculum (RL, 2017+)
        ↓
EUREKA Curriculum (2023)
```

---

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
相比 Elman (1993) 的 "Starting Small"：
| 方面 | Elman 1993 | Curriculum Learning 2009 |
|-----|------------|-------------------------|
| 理论解释 | 认知发展假说 | **Continuation Method** |
| 实验范围 | 语法学习 | **视觉 + NLP** |
| 数学形式化 | 无 | **有（训练分布序列）** |

### 关键贡献点

1. **形式化框架**：将课程学习定义为训练分布 $Q_\lambda$ 的序列
2. **Continuation 假说**：课程学习是非凸优化的 continuation method
3. **双重效应**：
   - 加速收敛（凸问题也有效）
   - 找到更好的局部极小值（非凸问题的关键）
4. **实证验证**：在深度网络和 NLP 任务上验证

---

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 数学形式化

设 $z$ 为训练样本（可能是 $(x, y)$ 对），$P(z)$ 为目标训练分布。

**课程学习** 定义为一族分布 $\{Q_\lambda\}_{\lambda \in [0,1]}$：

$$Q_\lambda(z) \propto W_\lambda(z) P(z)$$

其中：
- $W_\lambda(z)$：样本 $z$ 在阶段 $\lambda$ 的权重
- $\lambda = 0$：只包含"简单"样本
- $\lambda = 1$：恢复原始分布 $P(z)$

**关键性质**：
1. $W_0(z) > 0$ 只对简单样本成立
2. $W_\lambda$ 随 $\lambda$ 递增（熵增加，多样性增加）
3. $Q_1 = P$（最终收敛到目标分布）

### 3.2 与 Continuation Method 的联系

**Continuation Method** 是全局优化的经典策略：

$$C_\lambda(\theta) \text{ where } C_0 \text{ is easy (e.g., convex)}, C_1 \text{ is target}$$

1. 先优化 $C_0(\theta)$
2. 逐渐增加 $\lambda$，保持 $\theta$ 在 $C_\lambda$ 的局部极小值
3. $C_0$ 通常是 $C_1$ 的平滑版本

**课程学习 = 训练准则的 Continuation**：
- 简单样本 → 平滑的损失景观
- 难样本 → 复杂的损失景观（多局部极小值）

### 3.3 物理直觉

> [!tip] 为什么课程学习有效？
> **假说**：简单样本揭示了问题的"全局结构"，就像站在山顶看全貌。
> 
> - 简单样本：低频成分，大尺度模式
> - 难样本：高频细节，局部特征
> 
> 先学全局结构，再填充细节，避免一开始就陷入高频噪声的局部极小值。

---

### 3.4 核心代码逻辑 (PyTorch)

```python
import torch
import torch.nn as nn

class CurriculumScheduler:
    """课程学习训练分布调度器"""
    def __init__(self, dataset, difficulty_fn, n_stages=5):
        # difficulty_fn: sample -> float in [0,1]
        self.difficulties = torch.tensor([difficulty_fn(x) for x in dataset])
        self.thresholds = torch.linspace(0.2, 1.0, n_stages)  # λ schedule
        self.stage = 0

    def sample_weights(self) -> torch.Tensor:
        """Q_λ(z) ∝ W_λ(z) P(z): 返回当前阶段的样本权重"""
        lam = self.thresholds[self.stage]
        # W_λ(z) = 1 if difficulty(z) <= λ, else 0 (hard curriculum)
        weights = (self.difficulties <= lam).float()
        return weights / weights.sum()  # normalize to distribution

    def step(self, val_loss: float, patience_threshold: float):
        """当验证损失收敛时推进到下一阶段"""
        if val_loss < patience_threshold and self.stage < len(self.thresholds) - 1:
            self.stage += 1
            print(f"Curriculum → Stage {self.stage}, λ={self.thresholds[self.stage]:.2f}")


def train_with_curriculum(model, dataset, difficulty_fn, epochs=100):
    scheduler = CurriculumScheduler(dataset, difficulty_fn)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss(reduction='none')

    for epoch in range(epochs):
        weights = scheduler.sample_weights()  # Q_λ 分布
        # 加权采样 (importance sampling from curriculum distribution)
        indices = torch.multinomial(weights, num_samples=256, replacement=True)
        batch_x, batch_y = dataset[indices]

        logits = model(batch_x)
        per_sample_loss = loss_fn(logits, batch_y)
        loss = (per_sample_loss * weights[indices]).sum()  # weighted loss

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        scheduler.step(loss.item(), patience_threshold=0.1)
```

> [!note] 代码要点
> - `sample_weights()` 实现 $Q_\lambda(z) \propto W_\lambda(z) P(z)$，hard curriculum 通过阈值截断
> - 课程推进由验证损失触发，模拟 continuation method 的逐步推进
> - 实际应用中 `difficulty_fn` 可以是噪声水平、样本清晰度、损失值等

---

## 4. 实验与验证 (Experiments)

### 4.1 凸问题：形状识别

**设置**：线性分类器识别几何形状

**课程**：
1. 无噪声、大尺寸形状
2. 逐渐增加噪声、减小尺寸

**结果**：即使是凸问题，课程学习也**加速收敛 2-3 倍**

### 4.2 非凸问题：深度网络

**设置**：训练深度神经网络进行图像分类

**课程**：
1. 清晰、典型的样本
2. 模糊、边缘案例

**结果**：
- 训练误差：相近
- **测试误差：显著降低**（类似正则化效果）

### 4.3 语言模型

**设置**：训练神经语言模型

**课程**：
1. 短句、简单语法
2. 长句、复杂语法

**结果**：perplexity 显著降低

### 4.4 Ablation 因果链分析

> [!note] 2009 年论文 ablation 较为基础，以下为从实验中提取的因果链：

| 移除的组件 (A) | 效果 (B) | 机制分析 (C) |
|---------------|----------|-------------|
| 移除课程（随机顺序） | 测试误差显著上升 | 随机顺序使优化器陷入高频噪声主导的局部极小值 |
| 移除渐进性（直接从难样本开始） | 训练不收敛或极慢 | Continuation path 断裂，初始化不在目标函数的 basin of attraction 中 |
| 移除简单样本阶段 | 最终泛化性能下降 | 没有全局结构的"热启动"，丧失 regularization 效果 |

---

## 5. 批判性分析 (Critical Analysis)

### 优势
- **通用框架**：适用于各种学习问题
- **理论基础**：与优化理论的 continuation method 联系
- **经验有效**：多领域验证

### 局限性
- **如何定义"难度"？** 
  - 本文使用启发式（噪声、尺寸）
  - 没有自动难度估计方法
- **课程设计开销**：需要人工设计课程策略
- **非最优保证**：continuation method 不保证全局最优

### 局限性（理论/算法/工程三维度）

| 维度 | 局限 | 替代方案 |
|-----|------|--------|
| **理论** | Continuation method 不保证全局最优；课程从"简单→难"的假设缺乏严格定义 | Self-paced Learning 用模型当前损失自动定义"难度" |
| **算法** | 课程策略需要人工设计 `difficulty_fn`，难以推广到新任务 | Automatic Curriculum (Graves 2017)、POET (2019) 自动生成课程 |
| **工程** | 多阶段训练需要调节阶段切换时机，超参数增多 | 连续权重调度（如 $W_\lambda$ 用 sigmoid 软化）减少离散切换 |

### 后续发展
- **Self-paced Learning**：让模型自己决定样本顺序
- **Automatic Curriculum in RL**：基于学习进度自动调整
- **EUREKA**：LLM 自动生成课程

---

## 5.5 工程关键细节 (Engineering Tricks)

| 技巧 | 说明 |
|-----|------|
| **难度度量选择** | 论文使用噪声水平/样本尺寸作为难度代理；实际可用模型损失、预测不确定性 |
| **阶段切换策略** | 验证集性能饱和时切换，避免过早/过晚推进 |
| **分布平滑过渡** | $W_\lambda$ 使用 sigmoid 软化而非 hard cutoff，避免分布突变导致训练不稳 |
| **最终阶段训练** | 在 $\lambda=1$（完整分布）上额外训练若干 epoch，消除课程引入的分布偏差 |

---

## 6. 对灵巧操作的启发 (Implications)

### 直接应用场景

1. **技能学习课程**
   ```
   简单抓取 → 精细抓取 → 手内操作 → 动态操作
   ```

2. **仿真到真实 (Sim-to-Real) 课程**
   ```
   无噪声仿真 → 域随机化 → 真实环境
   ```

3. **接触复杂度课程**
   ```
   单点接触 → 多点接触 → 滑动接触 → 滚动接触
   ```

### 与 EUREKA 的结合
EUREKA 论文中，课程学习是实现转笔的关键：
- Phase 1：慢速旋转 90°
- Phase 2：旋转 180°
- Phase 3：连续旋转
- Phase 4：高速转笔

### 对灵巧手转笔 + Sim-to-Real 的具体启发

> [!tip] 关键迁移 Insight
> 1. **课程即先验**：转笔的课程设计隐含了对接触模式切换的理解——先学稳定抓取 → 单指推动 → 多指协调 → 连续旋转。这与 continuation method 从凸子问题渐进引入非凸性完全对应。
> 2. **Sim-to-Real 课程**：仿真中先关闭域随机化（"简单"仿真），学会基本技能后再逐步增加物理参数随机化（摩擦、质量、延迟），类比 $C_0 \to C_1$ 的 continuation path。
> 3. **触觉课程**：结合 [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation]] 的发现——先用完整传感学习再逐步退化，比一开始就在受限传感下训练效果更好。

---

## 7. 演进脉络定位 (Evolution Context)

```
动物行为塑形 (Shaping, Skinner 1958)
        ↓
Starting Small (Elman, 1993)
        ↓
██████████████████████████████████
█  Curriculum Learning (2009)    █
█  • 形式化为训练分布序列         █
█  • Continuation method 假说    █
██████████████████████████████████
        ↓
Self-paced Learning (Kumar et al., 2010)
        ↓
Automatic Curriculum in RL (Graves et al., 2017)
        ↓
Reverse Curriculum (Florensa et al., 2017)
        ↓
Goal-conditioned Curriculum (Sukhbaatar et al., 2018)
        ↓
LLM-based Curriculum (EUREKA, 2023)
```

---

## 8. 与 Foundation 的数学对应

### [[Optimization]] — Continuation Method

课程学习的核心数学对应是 [[Optimization]] 中的非凸景观理论：

$$C_\lambda(\theta) = \mathbb{E}_{z \sim Q_\lambda}[\ell(\theta, z)]$$

- $\lambda=0$: $Q_0$ 集中在简单样本 → $C_0$ 接近凸函数（对应 [[Optimization]]）
- $\lambda \to 1$: $Q_\lambda \to P$ → $C_\lambda$ 逐渐引入非凸性
- Continuation 保证：若 $\theta^*(\lambda)$ 在 $C_\lambda$ 的局部极小 basin 中，则小步推进 $\lambda$ 后 $\theta^*(\lambda+\delta)$ 仍在"好"的 basin 中

### [[ReinforcementLearning]] — 课程 RL

在 RL 中，课程学习对应奖励/环境的渐进调度（[[ReinforcementLearning]]）：

$$R_\lambda(s,a) = (1-\lambda) R_{\text{easy}}(s,a) + \lambda R_{\text{target}}(s,a)$$

或环境参数的渐进调整：

$$p_\lambda(s'|s,a) \text{ with } p_0 \text{ (simplified dynamics)} \to p_1 \text{ (full dynamics)}$$

这与 [[ReinforcementLearning]] 中的域随机化调度直接对应。

---

## 9. 关键数学总结

| 概念 | 数学表达 | 物理意义 |
|-----|---------|---------|
| 课程分布 | $Q_\lambda(z) \propto W_\lambda(z) P(z)$ | 按难度加权的训练分布 |
| 熵增加 | $H(Q_{\lambda_1}) < H(Q_{\lambda_2})$ if $\lambda_1 < \lambda_2$ | 多样性逐渐增加 |
| Continuation | $C_\lambda(\theta)$: $C_0$ smooth → $C_1$ target | 从平滑损失到目标损失 |

---

## 10. 跨方法/跨范式对比

| 方法 | 课程来源 | 难度定义 | 自动化程度 | 适用场景 |
|-----|---------|---------|-----------|--------|
| **Curriculum Learning (本文)** | 人工设计 | 噪声/尺寸/复杂度 | 低 | 监督学习通用 |
| **Self-paced Learning** | 模型损失 | 当前损失值 | 中 | 噪声标签场景 |
| **Reverse Curriculum (Florensa 2017)** | 目标状态回溯 | 到目标的距离 | 高 | RL 目标达成任务 |
| **[[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]]** | 演示轨迹 | 距演示起点的步数 | 中 | Sim-to-Real 灵巧操作 |
| **EUREKA** | LLM 生成 | 奖励函数复杂度 | 高 | RL 奖励设计 |
| **[[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation\|CSR]]** | 特征重要性 | 观测维度 | 中 | Sim-to-Real 传感缩减 |

---

## 11. 簇内坐标：本文是"课程学习簇"的总纲，也是 continuation 暗线的源头

> [!abstract] 暗线锚定：Continuation / 同伦 / 平滑化
> 本库有一条贯穿多个 Foundation 的暗线——**"先解平滑近凸子问题、再逐步引入真难度"**：接触平滑（[[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|Optimization §5.4]]）、课程学习的任务分布 $Q_0\to Q_1$、扩散的噪声→数据，都是同一思想的不同投影。本文 2009 年把"课程 = continuation method"这一等式**第一次形式化**（§3.2），因此它是这条暗线在 RL 侧的**源头文献**。簇内其余 8 篇都可读成"把 $Q_\lambda$ 的 $\lambda$ 换成不同物理量"的具体实例。

本文的 $Q_\lambda(z)\propto W_\lambda(z)P(z)$ 直接对应 [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间|RL §7.3 自动课程]] 的开篇：该节的 [[ReinforcementLearning#Phase 1 — 手工课程与 continuation：先解平滑子问题|Phase 1 手工课程与 continuation]] 正是本文思想的 RL 化，随后 Phase 2–6（Learning Progress / PLR / ADR / POET / Generalist-Specialist）是"如何自动选 $\lambda$"的演进。本文只做到 Phase 1（人工设 `difficulty_fn`），簇内其它论文分别推进了自动化：

| 簇内论文 | 把 $\lambda$（难度轴）换成了什么 | 相对本文的 Delta | 自动化到哪个 RL Phase |
|:--|:--|:--|:--|
| [[EUREKA: Human-Level Reward Design via Coding Large Language Models\|EUREKA]] | 奖励函数代码 + 转笔 $\omega_{target}:0.5\to2.0$ | 用 LLM 进化搜索**自动生成**课程与奖励，不再人工 `difficulty_fn` | Phase 1→自动（LLM 当课程设计器） |
| [[Hindsight Experience Replay\|HER]] | achieved-goal 分布 $p_{\text{achieved}}(g;\pi_t)$ | 课程**隐式**涌现于 relabeling，无需显式排序难度 | Phase 2（能力边界自随策略推进） |
| [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]] | demonstration reset states + ZVF success-variance | ZVF（$0<\hat p<1$）用 learning-progress **自动**选"该学处" | Phase 2/3（variance≈learning frontier） |
| [[DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills\|DeepMimic]] | reference motion 的相位 $\phi$（RSI 初始分布 $\rho_0$） | 把 continuation 从"样本难度"搬到"初始状态相位覆盖" | Phase 1（相位课程仍需 reference clip） |
| [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References\|DexTrack]] | 任务同伦路径 $T_K\to\cdots\to T_0$ | homotopy generator 从数据**学**"哪个易任务能给难任务当 baseline" | Phase 3+（conditional diffusion 生成 parent task） |
| [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation\|Curriculum > Haptic]] | reward 系数 $c_R,c_L$ 的两阶段时序 | 把 continuation 上升为"决定 PPO learning basin 的先验"，比触觉更主导 | Phase 1（手工枚举 C1–C5） |
| [[Vision-force-fused Curriculum Learning for Robotic Assembly\|VF-Assembly]] | 感知模态权重 $w_v,w_f$（视觉→力） | 在**观测/感知**维度做 continuation，而非样本难度 | Phase 1（预设 epoch 比例） |
| [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation\|CSR]] | 观测特征保留比例（DRG 逐步遮蔽） | 反向 continuation：从"全特权观测"平滑退化到"真实可得观测" | Phase 1（特征重要性排序） |

> [!tip] 一句话记忆锚
> **本文给了 continuation 的"公式" $Q_\lambda$，簇内每篇都在回答"$\lambda$ 是什么、谁来调 $\lambda$"。** 从人工（本文/VF/CSR/Curriculum>Haptic）→ 半自动（DemoStart/HER/DeepMimic）→ 学习式（DexTrack homotopy / EUREKA LLM），正是 [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间|RL §7.3]] Phase 1→6 的完整轨迹。这条"谁来调 $\lambda$"的自动化，最终与 [[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成|WorldModels §6.3 无知即课程]] 汇合——用认知不确定性（该学处）反向驱动任务生成。
