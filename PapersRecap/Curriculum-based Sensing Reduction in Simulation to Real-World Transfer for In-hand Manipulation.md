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
venue: ICRA 2024
paper-pdf: "[[Papers/Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[ContactMechanics]]"
---

# Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation

> [!abstract] 核心概要
> 提出 **CSR (Curriculum-based Sensing Reduction)**：解决 Sim2Real 中"仿真有丰富传感、真实难以复现"的矛盾。通过**课程式逐步移除特征**（而非一步裁剪），让策略从完整观测空间渐进适应到受限观测空间，提升训练效率和真实世界性能。ICRA 2024。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] - Asymmetric Actor-Critic 的改进
> - [[RepresentationLearning]] - 特征重要性评估
> - [[ContactMechanics]] - 触觉特征在操作中的作用
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

### 3.0 变量来源追踪

枢纽：**critic 全程完整观测、actor 渐进缩减**（mask + DRG 替代），以及"渐进 > 一步"、"DRG > 置零"两个核心设计。

| 变量 | 类型/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $o_{full}$ | 完整观测 | 仿真（特权） | 否 | 关节角/速/触觉/物体姿态 | 真实部分不可得 |
| $o^{critic}$ | 完整观测 | 仿真 | 否（输入） | critic 观测 | **全程不缩减**（稳定 value） |
| $o^{actor}_t$ | mask+DRG | 课程渐进 | 否 | actor 观测 | 随阶段缩减 |
| $I_i=\mathbb{E}[\|\partial\pi/\partial o_i\|]$ | scalar | 梯度计算 | — | 特征重要性 | 局部线性近似，不敏感非线性交互 |
| DRG | frozen MLP | 固定随机初始化 | **否（no grad）** | 随机替代信号 | **替代被移除特征 ≠ 置零** |
| $\text{mask}_{\lambda(t)}$ | 掩码 | 课程阶段 | 否 | 保留/替代特征选择 | 硬切换可能振荡 |

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

### 4.5 Ablation 因果链分析

| 移除的组件 (A) | 效果 (B) | 机制分析 (C) |
|---------------|----------|-------------|
| 移除渐进课程（一步裁剪到目标观测） | 成功率从 85% 降至 72% | 策略无法在单步中适应高维观测空间的突变；value function 估计崩溃 |
| 移除 DRG（用零值替代被删特征） | 成功率降低 8% | 零值是确定性信号，策略学会"零=某种状态"的虚假关联，迁移时分布外 |
| 移除特征重要性排序（随机顺序移除） | 收敛速度变慢 ~30% | 先移除重要特征破坏了已学到的策略结构，需要更多重新学习 |
| 移除多阶段（只保留 Stage 0 和最终 Stage） | 性能介于一步裁剪和完整课程之间 | 中间过渡阶段提供了梯度信号的平滑桥梁，减少了策略梯度方差 |

---

## 4.6 概念边界与符号陷阱

- **渐进缩减 > 一步裁剪**：一步致 actor 观测空间突变、value function 估计崩溃（§4 消融 85→72）。
- **DRG 随机替代 > 置零**：置零是确定性信号，策略学会"零=某状态"虚假关联，迁移时分布外（§4 消融 −8%）。
- **关节角度隐含接触信息** $f_{contact}=J_c^{-T}\tau$：移除显式触觉仍保 65%——本体感知部分替代触觉。
- **critic 全程完整观测**：不随课程缩减，提供稳定 value 估计（asymmetric AC 的核心）。
- **特征重要性 $I_i$ 是局部线性近似**：对非线性特征交互不敏感（§5 理论局限）。
- **阶段硬切换**：可能在临界点引起策略振荡 → 连续衰减 $\alpha_i(t)$ 更稳。

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

### 局限性（理论/算法/工程三维度）

| 维度 | 局限 | 替代方案 |
|-----|------|--------|
| **理论** | 梯度重要性 $I_i = \mathbb{E}[\|\partial\pi/\partial o_i\|]$ 是局部线性近似，对非线性特征交互不敏感 | 用 Shapley Value 或 permutation importance 做全局重要性评估 |
| **算法** | 阶段切换是硬切换，可能在临界点引起策略振荡 | 连续权重 $\alpha_i(t) \in [0,1]$ 渐进衰减被移除特征的权重 |
| **工程** | 多阶段训练增加总训练时间（虽然每阶段更快收敛）；仅在 cube rotation 上验证 | 异步课程（不同特征独立调度）、多任务验证 |

### 与其他方法的对比

| 方法 | CSR | DexNDM | Teacher-Student |
|-----|-----|--------|-----------------|
| 处理对象 | 观测空间 | 动力学 | 策略 |
| 核心思想 | 渐进缩减 | 关节分解 | 知识蒸馏 |
| 课程结构 | 特征移除 | 无 | 无 |

---

## 5.5 工程关键细节 (Engineering Tricks)

| 技巧 | 说明 |
|-----|------|
| **DRG 网络结构** | 使用小型 MLP（2层×64维），权重随机初始化后冻结；输出需匹配被替代特征的数值范围（用 tanh + scaling） |
| **阶段切换判据** | Episode 成功率在 patience window（~100 episodes）内变化 < 1% 时触发下一阶段 |
| **特征组粒度** | 按语义分组（关节角/速度/触觉/姿态）而非逐维移除，减少阶段数同时保持语义完整性 |
| **并行环境阶段同步** | Isaac Gym 中所有并行环境同步切换阶段，避免同批次内课程不一致 |
| **Critic 观测不变** | 全程保留 Critic 的完整观测（不随课程缩减），提供稳定的 value 估计 |

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

### 对灵巧手转笔 + Sim-to-Real 的具体启发

> [!tip] 关键迁移 Insight
> 1. **转笔的传感课程**：仿真中可获取笔的精确位姿和接触力，但真实中仅有关节编码器 + 有限触觉。CSR 提供了系统性方法：先用完整传感训练（含笔姿态、指尖法向力、切向力），再按重要性排序逐步移除——可能发现关节速度比触觉力更关键。
> 2. **DRG 对噪声传感器的启示**：真实触觉传感器噪声大、漂移严重。与其用噪声信号训练，不如用 DRG 生成的随机信号"遮蔽"触觉输入训练一个不依赖触觉的 fallback 策略——在触觉传感器故障时自动退化。
> 3. **最小可行传感配置**：CSR 实验发现仅用关节角度（16D）就能完成 cube rotation 的 65% 成功率。对转笔而言，关节本体感知可能是最核心的不可移除特征。

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

## 9. 与 Foundation 的数学对应

### [[ReinforcementLearning]] — Asymmetric Actor-Critic 的观测空间适应

CSR 扩展了 [[ReinforcementLearning]] 中的 Asymmetric AC 框架。标准 AAC 的观测空间划分是一步完成的：

$$\pi_\theta(a|o^{\text{actor}}), \quad V_\phi(o^{\text{critic}}) \quad \text{where } o^{\text{actor}} \subset o^{\text{critic}}$$

CSR 将此改为渐进过程，引入时间依赖的观测空间：

$$o^{\text{actor}}_t = \text{Mask}_{\lambda(t)}(o^{\text{full}}) + \text{DRG}(\bar{\text{Mask}}_{\lambda(t)}(o^{\text{full}}))$$

其中 $\text{Mask}_{\lambda(t)}$ 按课程阶段选择保留特征，$\bar{\text{Mask}}$ 选择被替代特征。

### [[ContactMechanics]] — 触觉特征在抓取中的信息论角色

CSR 的特征重要性排序隐含了一个接触力学 insight：关节角度 $q$ 通过 [[ContactMechanics#2.3 接触雅可比与对偶性：连接关节空间|接触雅可比]] 间接编码了接触状态：

$$f_{\text{contact}} = J_c(q)^{-T} \tau_{\text{joint}}$$

因此即使移除显式触觉特征，关节角度/力矩仍携带接触信息——这解释了 CSR 移除触觉后仍保持65%成功率的原因。

### [[RepresentationLearning]] — 特征选择与表征瓶颈

CSR 本质上是在学习一个 [[RepresentationLearning]] 中讨论的信息瓶颈：在保持任务性能的前提下，最小化策略所需的输入信息量。

---

## 10. 跨方法/跨范式对比

| 方法 | Sim-to-Real 策略 | 观测空间处理 | 课程机制 | 真实验证 |
|-----|-----------------|------------|---------|---------|
| **CSR (本文)** | 渐进特征移除 | Actor 逐步缩减 + DRG | 特征重要性排序 | Allegro cube rotation |
| **标准 AAC** | 一步裁剪 | Actor/Critic 不对称 | 无 | 多任务 |
| **Teacher-Student** | 知识蒸馏 | Teacher 全观测 → Student 受限 | 无 | 多任务 |
| **[[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]]** | 演示引导初始化 | 统一观测 | 状态初始化课程 | Allegro 多任务 |
| **[[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation\|Curriculum > Haptic]]** | 任务子目标课程 | 触觉可选 | 任务顺序 | 仿真三指手 |
| **[[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch\|AnyRotate]]** | 域随机化 + 触觉 | 触觉必选 | 无 | LEAP Hand |

> [!note] sim-to-real 簇收官：观测 gap ($\Delta_S$) 的"补 vs 减"两条路 + 全簇地图
> CSR 在 [[A Survey of Sim-to-Real Methods in RL|Survey]] MDP 四元素属 **$\Delta_S$ 的特例：仿真特权观测真实不可得**。把它与簇内其它 $\Delta_S$ 方法并置，浮现**观测 gap 的两条应对路线**：
> - **补/翻译观测**（让真实像仿真）：[[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map\|Tacmap]]（翻译触觉到 deform map）、[[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing\|Robot Synesthesia]]（点云统一）。
> - **减少观测依赖**（让策略不需仿真特权）：**CSR**（课程缩减 + DRG 遮蔽）。
> 前者"补足缺失观测"、后者"训练出不依赖该观测的策略"——$\Delta_S$ 的"补 vs 减"二分。
> **新 insight——本体感知部分替代触觉**：CSR 移除触觉仍 65%，因关节角度通过 $f_c=J_c^{-T}\tau$ 隐含接触信息。这给触觉表征谱（见 [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map\|Tacmap]]）补一个反向视角——**有时最鲁棒的"触觉表征"是没有触觉、靠本体隐式推断**，呼应 [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)|HORA]] 的纯本体+RMA 路线。
> **🎉 sim-to-real 簇收官（8 篇）**：A Survey（总纲）· RL Review（综述）· GAT（grounding）· DexNDM（神经动力学）· Tacmap（触觉几何）· RialTo（数字孪生）· TRANSIC（人类纠正）· CSR（观测缩减）。全簇可定位到"两综述 2D 网格"（(修什么 $\Delta$) × (怎么修)）。
