---
tags:
  - paper
  - sim-to-real
  - curriculum-learning
  - dexterous-manipulation
  - tactile-sensing
aliases:
  - CSR
  - Curriculum Sensing Reduction
paper-year: 2024
read-date: 2026-01-31
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[ContactMechanics]]"
---

# Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation

> [!abstract] 核心概要
> 提出 **CSR (Curriculum-based Sensing Reduction)**：解决 Sim2Real 中"仿真有丰富传感、真实难以复现"的矛盾。通过**课程式逐步移除特征**（而非一步裁剪），让策略从完整观测空间渐进适应到受限观测空间，提升训练效率和真实世界性能。ICRA 2024。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#6.2 Sim-to-Real]] - Asymmetric Actor-Critic 的改进
> - [[RepresentationLearning#3.1 特征选择]] - 特征重要性评估
> - [[ContactMechanics#3.1 触觉感知]] - 触觉特征在操作中的作用
>
> **核心技术**: Asymmetric Actor-Critic, Curriculum Feature Reduction, Deep Random Generator

---

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**仿真中的"特权信息"不要一步扔掉，而是逐步移除——让策略有时间适应**

### 直观隐喻
想象你在学骑自行车：
- **传统 AAC**：第一天有辅助轮，第二天直接拆掉两个（摔惨了）
- **CSR**：先拆一个，适应后再拆另一个（平稳过渡）

策略学习也是如此：先用完整观测学会任务，再逐步移除难以获取的特征。

### 领域定位
```
Sim-to-Real for Manipulation
        ↓
Domain Randomization (blind transfer)
        ↓
Teacher-Student Distillation
        ↓
Asymmetric Actor-Critic (AAC)
├── Critic: full observation
└── Actor: reduced observation (one-step)
        ↓
████████████████████████████████████████
█  CSR (2024)                          █
█  • 课程式特征移除                     █
█  • Deep Random Generator             █
█  • 保持训练稳定性                     █
████████████████████████████████████████
        ↓
未来: 自动特征重要性发现
```

---

## 2. 核心创新与贡献 (Contributions & Novelty)

### 问题分析

**仿真的优势**：可以获取"上帝视角"信息
- 精确的物体位姿
- 完整的触觉分布
- 关节力矩、接触力等

**真实世界的限制**：
- 触觉传感器昂贵（单个 BioTac $15k）
- 视觉遮挡、噪声
- 某些量无法直接测量

**AAC 的问题**：

$$\text{Simulation: } o_{critic} = [o_{full}], \quad o_{actor} = [o_{reduced}]$$

**一步裁剪**的问题：
- 裁剪太少 → 真实部署仍困难
- 裁剪太多 → 训练困难、性能差

### Delta 分析

| 方法 | 特征过渡 | 训练稳定性 | 最终性能 |
|-----|---------|----------|---------|
| 标准 AAC | 一步 | 差 | 中 |
| Teacher-Student | 两阶段 | 中 | 中 |
| **CSR** | **渐进课程** | **好** | **高** |

### 关键贡献

1. **C1**: 课程式感知缩减——基于特征重要性逐步移除
2. **C2**: Deep Random Generator——用随机信号替代被移除特征
3. **C3**: 真实 Allegro 手验证——触觉特征缩减后仍能完成任务

---

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 特征重要性评估

**方法**：在早期训练阶段评估每个特征对输出的影响

$$I_i = \mathbb{E}\left[ \left| \frac{\partial \pi(o)}{\partial o_i} \right| \right]$$

**课程生成**：按重要性排序，从最不重要的开始移除

```
特征重要性排序:
  关节角度: ████████████ 高 (保留)
  关节速度: █████████ 中 (后期移除)
  触觉力: ██████ 中 (中期移除)
  物体姿态: ████ 低 (早期移除)
  
课程:
  Stage 0: 全部特征
  Stage 1: 移除物体姿态
  Stage 2: 移除触觉力
  Stage 3: 移除关节速度 (如需要)
```

### 3.2 Deep Random Generator (DRG)

**问题**：直接置零会创建新的依赖（策略学会"零 = 某种状态"）

**解决方案**：用随机信号替代被移除特征

$$o^{reduced}_i = \text{DRG}(z), \quad z \sim \mathcal{N}(0, I)$$

DRG 是一个固定权重的随机初始化神经网络：
- 输出随机但有结构
- 策略无法从中提取有用信息
- 迫使策略忽略这个特征

```
┌─────────────────────────────────────────┐
│  Deep Random Generator                  │
├─────────────────────────────────────────┤
│                                         │
│  z ~ N(0, I)                            │
│      │                                  │
│      ▼                                  │
│  ┌─────────────┐                        │
│  │ Random MLP  │  (weights frozen)      │
│  │ (no grad)   │                        │
│  └──────┬──────┘                        │
│         │                               │
│         ▼                               │
│  "Fake" feature signal                  │
│  (replaces removed feature)             │
│                                         │
└─────────────────────────────────────────┘
```

### 3.3 CSR 训练流程

```
Algorithm: Curriculum-based Sensing Reduction

1. 初始化 Actor 和 Critic（相同观测空间）
2. 早期训练阶段：评估特征重要性
3. 生成移除课程：{f_1, f_2, ..., f_k}

4. For stage in [0, 1, ..., k]:
   a. 移除特征 f_stage（用 DRG 替代）
   b. 继续训练直到收敛
   c. 评估性能，若合格进入下一阶段

5. 最终 Actor 只使用真实可获取的特征
```

### 3.4 与标准 AAC 的对比

**标准 AAC**：
```
Critic: [joint, tactile, object_pose, ...]
Actor:  [joint, image]  ← 一步缩减
```

**CSR**：
```
Stage 0: Actor = Critic = [joint, tactile, object_pose, ...]
Stage 1: Actor = [joint, tactile, DRG(object_pose)]
Stage 2: Actor = [joint, DRG(tactile), DRG(object_pose)]
Stage 3: Actor = [joint, image] (if needed)
```

---

## 4. 实验与验证 (Experiments)

### 4.1 实验设置

**平台**：
- 仿真：NVIDIA Isaac Gym
- 真实：Allegro Hand（16 DoF）

**任务**：In-hand cube rotation

**特征空间**：
- 关节角度 (16D)
- 关节速度 (16D)
- 指尖触觉 (4×3D = 12D)
- 物体姿态 (7D)

### 4.2 仿真结果

| 方法 | 训练步数 | 最终成功率 |
|-----|---------|----------|
| 标准 AAC | 5M | 72% |
| Teacher-Student | 8M | 75% |
| **CSR** | **4M** | **85%** |

### 4.3 真实世界结果

| 特征配置 | 成功率 |
|---------|-------|
| 全部特征（仿真） | 85% |
| 无物体姿态 | 78% |
| 无物体姿态 + 无触觉 | 65% |
| **CSR (无触觉)** | **72%** |

### 4.4 关键发现

1. **训练更快**：CSR 比标准 AAC 快 20%+
2. **性能更高**：最终成功率提升 13%
3. **真实迁移好**：触觉移除后仍保持较高性能
4. **DRG 有效**：比直接置零好 8%

---

## 5. 批判性分析 (Critical Analysis)

### 优势
- **渐进适应**：避免一步裁剪的性能崩溃
- **训练稳定**：DRG 防止虚假依赖
- **灵活性**：可针对不同真实配置定制课程
- **实用性强**：在真实 Allegro 手上验证

### 局限性
- **课程设计依赖先验**：特征重要性评估方法简单
- **计算开销**：多阶段训练
- **单一任务**：仅验证 cube rotation
- **特征粒度**：整体移除，未考虑部分移除

### 与其他方法的对比

| 方法 | CSR | DexNDM | Teacher-Student |
|-----|-----|--------|-----------------|
| 处理对象 | 观测空间 | 动力学 | 策略 |
| 核心思想 | 渐进缩减 | 关节分解 | 知识蒸馏 |
| 课程结构 | 特征移除 | 无 | 无 |

---

## 6. 对灵巧操作的启发 (Implications)

### 感知配置的成本-性能权衡

```
仿真（免费）         真实（昂贵）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
物体精确姿态    →    视觉估计（噪声）
完整触觉分布    →    稀疏触觉（成本）
接触点/力      →    间接推断

CSR 的价值：
  找到"最少需要什么信息"的答案
  最小化真实部署成本
```

### 与其他论文的联系

- **DexNDM**：CSR 可用于 DexNDM 的观测空间设计
- **DexTrack**：跟踪控制器可用 CSR 适应不同传感配置
- **Curriculum Learning**：CSR 是观测空间的 curriculum

---

## 7. 演进脉络定位 (Evolution Context)

```
Sim-to-Real for Manipulation
        ↓
Domain Randomization (Tobin, 2017)
        ↓
Teacher-Student (Chen, 2020)
        ↓
Asymmetric Actor-Critic (Pinto, 2017)
        ↓
████████████████████████████████████████
█  CSR (2024)                          █
█  • 课程式感知缩减                     █
█  • Deep Random Generator             █
█  • Allegro hand 真实验证             █
████████████████████████████████████████
        ↓
未来: 自动发现最优感知配置
```

---

## 8. 核心代码逻辑

```python
class CurriculumSensingReduction:
    """课程式感知缩减"""
    
    def __init__(self, full_obs_dim, feature_groups):
        """
        feature_groups: [{'name': 'object_pose', 'indices': [0:7]}, ...]
        """
        self.feature_groups = feature_groups
        self.drg = DeepRandomGenerator(full_obs_dim)
        self.removal_schedule = []
        
    def evaluate_feature_importance(self, policy, data):
        """评估每个特征组的重要性"""
        importance = {}
        for group in self.feature_groups:
            grad_sum = 0
            for obs, action in data:
                obs.requires_grad = True
                pred = policy(obs)
                pred.backward()
                grad_sum += obs.grad[group['indices']].abs().mean()
            importance[group['name']] = grad_sum / len(data)
        return importance
    
    def create_curriculum(self, importance, target_features):
        """创建移除课程（按重要性从低到高）"""
        sorted_features = sorted(importance.items(), key=lambda x: x[1])
        self.removal_schedule = [
            f for f, _ in sorted_features 
            if f not in target_features
        ]
        return self.removal_schedule
    
    def get_reduced_obs(self, obs, stage):
        """获取当前阶段的观测"""
        reduced_obs = obs.clone()
        for i, feature_name in enumerate(self.removal_schedule[:stage]):
            indices = self.feature_groups[feature_name]['indices']
            # 用 DRG 输出替代被移除特征
            reduced_obs[indices] = self.drg(torch.randn(len(indices)))
        return reduced_obs


class DeepRandomGenerator(nn.Module):
    """深度随机生成器"""
    
    def __init__(self, output_dim):
        super().__init__()
        # 随机初始化，权重冻结
        self.net = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )
        # 冻结权重
        for param in self.parameters():
            param.requires_grad = False
    
    def forward(self, z):
        """生成伪随机信号"""
        return self.net(z)


# 训练流程
def train_with_csr(env, policy, csr, n_stages):
    # 阶段 0：全特征训练
    train_stage(env, policy, csr, stage=0)
    
    # 评估特征重要性
    data = collect_data(env, policy)
    importance = csr.evaluate_feature_importance(policy, data)
    
    # 创建课程
    target_features = ['joint_pos', 'joint_vel']  # 真实可获取
    csr.create_curriculum(importance, target_features)
    
    # 逐阶段移除
    for stage in range(1, n_stages + 1):
        print(f"Stage {stage}: Removing {csr.removal_schedule[stage-1]}")
        train_stage(env, policy, csr, stage)
```

---

## 9. 与 Foundation 的链接更新

### 需要添加到 ReinforcementLearning.md
在"Sim-to-Real"部分添加"观测空间适应"作为除动力学适应外的另一维度。

### 需要添加到 RepresentationLearning.md
添加"特征重要性评估"用于感知配置优化。
