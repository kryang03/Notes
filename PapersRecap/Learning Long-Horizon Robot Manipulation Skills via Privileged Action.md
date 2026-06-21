---
tags:
  - paper
  - reinforcement-learning
  - long-horizon
  - curriculum-learning
  - non-prehensile
aliases:
  - Privileged Action
  - Long-Horizon Manipulation
paper-year: 2025
read-date: 2026-02-02
venue: arXiv
paper-pdf: "[[Papers/Learning_Long-Horizon_Robot_Manipulation_Skills_via Privileged Action.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[Optimization]]"
---

# Learning Long-Horizon Robot Manipulation Skills via Privileged Action

> [!abstract] 核心贡献
> 提出**特权动作 (Privileged Action)** 概念——在仿真中使用真实世界不可能的动作（如禁用碰撞、施加虚拟力）来简化探索，配合课程学习逐步恢复真实约束，实现长时程接触丰富任务的端到端学习。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] - 特权信息从状态扩展到动作空间
> - [[ContactMechanics]] - 通过特权动作绕过接触边界导致的探索困难
> - [[Optimization]] - 课程学习作为约束松弛→收紧的优化策略
>
> **核心技术**: Privileged Actions, Curriculum Learning, Push-and-Grasp, Pivot Grasp

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**先在简化世界学会，再逐步面对真实约束**——通过在仿真中暂时"作弊"（禁用碰撞、添加虚拟力），让智能体先学会长时程任务的整体策略，再通过课程逐步恢复物理约束。

### 直观隐喻
学习骑自行车时先用辅助轮降低难度，熟练后再去掉。特权动作就是 RL 中的"辅助轮"——仿真中可以暂时穿透物体、悬浮物体，让智能体先理解任务结构。

### 领域定位
- **填补空白**: 解决长时程接触丰富任务中"物理边界阻碍探索"的核心问题
- **方法论创新**: 从"特权信息"（观测）扩展到"特权动作"（控制）
- **任务突破**: 首次端到端学习 Push-and-Grasp、Pivot Grasp 等复合技能

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人方法 | 问题 | 本文解决方案 |
|---------|------|-------------|
| 参考轨迹引导 | 需要预先收集 | 无需演示 |
| 子任务拼接 | 手工设计原语 | 自动发现行为 |
| 特权信息 | 仅辅助观测 | 扩展到动作空间 |
| 奖励塑形 | 任务相关设计 | 统一简洁奖励 |

### 关键贡献点
1. **特权动作定义**: 
   - 禁用手-物体碰撞 → 允许"穿透"抓取
   - 施加虚拟力 → 辅助物体移动
2. **课程学习框架**: 逐步恢复物理约束
3. **统一奖励**: 无需任务特定奖励塑形

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 特权动作形式化

**标准 MDP**: $(S, A, P, R, \gamma)$

**特权扩展 MDP**: $(S, A \cup A_{\text{priv}}, P_{\text{priv}}, R, \gamma)$

其中：
- $A_{\text{priv}}$: 特权动作空间（真实世界不可行）
- $P_{\text{priv}}$: 简化的转移动力学

### 3.2 特权动作类型

| 类型 | 实现方式 | 效果 |
|-----|---------|------|
| **碰撞禁用** | 关闭手-物体碰撞检测 | 允许"穿透"抓取 |
| **虚拟力** | 对物体施加额外力 | 辅助移动/抬升 |
| **约束松弛** | 临时禁用关节限位 | 扩大可达空间 |

### 3.3 课程学习策略

课程参数 $\lambda \in [0, 1]$:
- $\lambda = 0$: 完全特权（最简单）
- $\lambda = 1$: 完全真实（目标状态）

**渐进策略**:
$$
P_{\lambda} = (1 - \lambda) P_{\text{priv}} + \lambda P_{\text{real}}
$$

具体实现：
```
阶段 1 (λ=0): 碰撞完全禁用，虚拟力最大
阶段 2 (λ=0.3): 碰撞部分恢复，虚拟力减弱
阶段 3 (λ=0.7): 接近真实物理
阶段 4 (λ=1): 完全真实约束
```

### 3.4 与接触力学的联系

> [!note] 物理直觉
> 接触丰富任务的探索困难来自**接触边界的不连续性**:
> - 未接触 → 接触: 动力学突变
> - 特权动作的核心是**平滑化这一边界**
> 
> 参见 [[ContactMechanics]] 中软接触模型的思想

### 3.5 核心伪代码

```python
# Privileged Action 训练框架 (PyTorch-style)
class PrivilegedActionEnv:
    """IsaacGym 环境包装，支持课程参数 lambda"""
    def __init__(self, base_env):
        self.env = base_env
        self.lam = 0.0  # 课程参数: 0=完全特权, 1=完全真实
    
    def step(self, action):
        # 1. 根据 lambda 设置碰撞检测
        self.env.set_collision_mask(
            hand_object=self.lam > 0.3  # lambda<0.3 时禁用手-物体碰撞
        )
        # 2. 虚拟力缩放
        virtual_force = action[:, -3:] * (1.0 - self.lam)  # lambda↑ 虚拟力↓
        self.env.apply_external_force(virtual_force)
        
        # 3. 执行动作
        obs, reward, done, info = self.env.step(action[:, :-3])
        return obs, reward, done, info
    
    def update_curriculum(self, success_rate):
        # 成功率超过阈值时提升 lambda
        if success_rate > 0.7:
            self.lam = min(1.0, self.lam + 0.05)

# 训练循环
env = PrivilegedActionEnv(IsaacGymEnv("PushAndGrasp"))
policy = PPO(obs_dim=env.obs_dim, act_dim=env.act_dim + 3)  # +3 为虚拟力

for epoch in range(N_EPOCHS):
    rollout = collect_rollout(env, policy)
    policy.update(rollout)
    env.update_curriculum(rollout.success_rate)
```

---

## 工程关键细节 (Engineering Tricks)

- **碰撞掩码渐进恢复**: 不是单纯开/关，而是通过 contact stiffness 渐变（从软接触到硬接触）
- **虚拟力的方向限制**: 只允许竖直方向的虚拟力（抗重力），避免策略利用水平虚拟力“作弊”
- **成功率统计窗口**: 使用近 100 episodes 的滑动平均而非单 epoch，避免课程抢进
- **动作空间分离**: 特权动作（虚拟力）和真实动作（关节执行）分开网络头，便于部署时丢弃特权头

## 4. 实验与验证 (Experiments)

### 任务设置
1. **Push-and-Grasp**: 物体初始不可抓取位置 → 推动 → 抓取
2. **Pivot Grasp**: 利用边缘旋转物体 → 抓取

### 关键结果

| 方法 | Push-and-Grasp | Pivot Grasp |
|-----|---------------|-------------|
| PPO (baseline) | ~0% | ~0% |
| + Dense Reward | ~20% | ~15% |
| + 特权信息 | ~35% | ~30% |
| **+ 特权动作** | **~85%** | **~80%** |

### Ablation 因果分析

| 去掉组件 | 效果变化 | 因果机制 |
|---------|---------|----------|
| 去掉碰撞禁用 | 成功率 -50% | 手无法穿透物体到达抓取位置 → 探索空间崩溃 |
| 去掉虚拟力 | 成功率 -30% | 推动阶段物体无法辅助移动 → 前置条件不满足 |
| 去掉课程 (直接 λ=1) | ~0% | 等价于无特权基线，探索过难 |
| 去掉课程 (固定 λ=0) | 仅在特权内成功 | 策略依赖虚拟力，无法迁移到真实物理 |

### Sim-to-Real
- 真机部署成功率: ~75%
- 关键发现: 学到的非抓取操作行为**自发涌现**，无需显式奖励

## 5. 批判性分析 (Critical Analysis)

### 优势
- **通用性**: 相同框架适用于不同任务
- **简洁性**: 无需手工设计子任务或奖励
- **涌现行为**: 非抓取操作自然出现

### 局限性深度分析

| 维度 | 局限 | 替代方案 |
|------|------|----------|
| **理论** | 特权 MDP 与真实 MDP 的策略对齐无理论保证，可能存在不可迁移的局部最优 | 双向策略蓏馏 (bi-level distillation) 约束特权/真实匹配 |
| **算法** | 课程 $\lambda$ 的调度需要手动设计，且切换时可能 catastrophic forgetting | ADR (Automatic Domain Randomization) 自动调节 $\lambda$ |
| **工程** | 特权动作类型需领域知识手动设计；仅限于仿真中可方便修改物理的场景 | HumanoidBench 等自动特权发现方法 |

### 与 DNPM 项目的关联

> [!warning] 直接应用价值
> **DNPM 痛点**: 长因果链任务（甩动→惯性阶段→接住）探索困难
> 
> **特权动作方案**:
> 1. **惯性阶段特权**: 暂时允许物体"悬浮"，让策略先学会整体协调
> 2. **接触切换特权**: 允许穿透接触，降低时序精度要求
> 3. **课程恢复**: 逐步恢复重力和碰撞约束

## 6. 对灵巧操作的启发 (Implications)

1. **手内操作**: 特权动作可让手指暂时"穿透"物体，学习复杂的指尖切换
2. **动态抛接**: 空中阶段可暂时"冻结"物体，让策略先学习接住位置
3. **与速度缩放结合**: 特权动作简化空间约束，速度缩放简化时间约束

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── Privileged Information (2019) - 观测层面的特权
├── Curriculum Learning (Narvekar 2020) - 任务难度调度
└── Contact-Rich RL (2022) - 接触任务的挑战分析

本论文: Privileged Action (2025)

后续方向:
├── 自动特权发现 - 学习哪些约束应该松弛
├── 特权-真实对齐 - 确保特权策略可迁移
└── 与 Diffusion Policy 结合 - 特权演示生成
```

---

**参考文献**:
- Mao, X. et al. "Learning Long-Horizon Robot Manipulation Skills via Privileged Action." arXiv:2502.15442, 2025.
