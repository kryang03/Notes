---
tags:
  - paper
  - dexterous-manipulation
  - sim-to-real
  - data-augmentation
  - imitation-learning
aliases:
  - CyberDemo
paper-year: 2024
read-date: 2026-02-01
venue: CVPR 2024
paper-pdf: "[[Papers/CyberDemo - Augmenting Simulated Human Demonstration.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
---

# CyberDemo: Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation

> [!abstract] 核心概要
> 提出在仿真中收集人类演示，通过大规模数据增强（视觉+物理+几何）生成多样化数据集，用课程学习训练策略后仅需少量真实数据微调即可实现 sim-to-real 迁移。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] - 行为克隆 + 课程学习
> - [[RepresentationLearning]] - R3M 等预训练表征对比
>
> **核心技术**: Simulation Data Augmentation, Auto Curriculum Learning, Minimal Real Fine-tuning

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
挑战"真实数据最好"的信念——在仿真中收集演示 + 大规模增强，比纯真实数据训练的策略更鲁棒。

### 直观隐喻
就像学钢琴时在电子琴上先练基本功（仿真），通过调节各种参数（增强）熟悉各种情况，最后在真钢琴上微调（少量真实数据）——比一开始就在真钢琴上硬练更高效。

### 领域定位
```
纯真实数据 IL: 昂贵，泛化差
    ↓
MimicGen: 仿真内数据合成（不迁移）
    ↓
CyberDemo: 仿真增强 + 少量真实微调 → 真实部署 ← 本文
```

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人工作 | 限制 | CyberDemo 突破 |
|---------|------|---------------|
| 纯真实 IL | 数据昂贵、泛化差 | 仿真数据增强 |
| MimicGen | 仅仿真内使用 | Sim-to-Real 迁移 |
| 图像级增强 | 不基于物理 | **物理+视觉+几何** |
| 固定课程 | 可能过难/过易 | **自动课程学习** |

### 关键贡献点
1. **四维数据增强**: 相机视角 + 光照纹理 + 物体几何 + 物体位姿
2. **Auto Curriculum Learning**: 根据任务成功率自动调整随机化强度
3. **最少真实数据**: 仅 3 分钟真实演示用于微调

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 数据增强策略

```
Level 1: Random Object Pose
         ├── 扰动初始物体位姿
         └── 重放并筛选成功轨迹

Level 2: Random Lightness & Texture  
         ├── 光源方向/颜色/阴影
         └── 物体材质（镜面/粗糙度/金属度）

Level 3: Random Target Pose
         ├── 目标位置随机化
         └── 策略需泛化到不同目标

Level 4: Largely Random Object Pose
         ├── 更大范围的位姿扰动
         └── 需要更强的适应能力
```

### 3.2 相机视角随机化

> [!important] 物理一致性
> 不是简单的图像裁剪，而是在仿真中重放状态并从新视角渲染——保持透视投影的物理正确性。

### 3.3 物体几何增强

```python
# 用不同形状物体替换原演示
# 但直接重放轨迹会失败
# 解决方案：扰动动作 + 筛选

for _ in range(num_attempts):
    perturbed_actions = original_actions + noise
    success = simulate(perturbed_actions, new_object)
    if success:
        add_to_dataset(perturbed_actions)
        break
```

**关键**: 仿真采样成本低，可大量尝试。

### 3.4 Auto Curriculum Learning

```python
# Algorithm 1: Auto Curriculum Learning
L = 0  # 当前难度等级
N_fail = 0

while not converged:
    # 训练当前等级
    train(policy, aug_L(D))
    
    # 评估
    success_rate = eval_L(policy)
    
    if success_rate > r_up:
        L += 1  # 提升难度
        N_fail = 0
    else:
        N_fail += 1
        if N_fail > N_max:
            break  # 达到瓶颈
```

### 3.5 轨迹敏感性分析

**问题**: 哪些轨迹段可以安全修改？

**解决方案**: 分析每个状态对动作扰动的敏感性
- 远离物体时敏感性低 → 可大幅修改
- 接触物体时敏感性高 → 需精细保留

### 3.6 数学框架总结

**行为克隆目标**:
$$\mathcal{L}_{BC} = \mathbb{E}_{(o_t, a_t) \sim \mathcal{D}}\left[\|a_t - \pi_\theta(o_t)\|^2\right]$$

**增强数据集构建** — 级到级的增强算子迭代应用:
$$\mathcal{D}_{\text{aug}}^{(L)} = \bigcup_{k \in \mathcal{T}_L} T_k\bigl(\mathcal{D}_{\text{demo}}\bigr), \quad \mathcal{T}_L \subseteq \{T_{\text{pose}}, T_{\text{light}}, T_{\text{texture}}, T_{\text{geom}}, T_{\text{target}}\}$$

**课程转换规则** — 成功率驱动的自动升级:
$$L \leftarrow L + 1 \quad \text{if} \quad \hat{r}_L > r_{\text{up}}; \qquad \text{terminate if } N_{\text{fail}} > N_{\max}$$

**轨迹敏感性** — 状态 $s_t$ 对动作扰动的失败概率:
$$S(s_t) = \mathbb{E}_{\epsilon \sim \mathcal{N}(0,\sigma^2)}\left[\mathbb{1}[\text{fail}(s_t, a_t + \epsilon)]\right]$$
$S(s_t)$ 高的时间步（接触阻段）保留原始动作，$S(s_t)$ 低的时间步可安全大幅扰动。

### 3.7 核心 PyTorch 代码逻辑

```python
# CyberDemo: 物理一致性数据增强 + 自动课程学习
class CyberDemoTrainer:
    def __init__(self, encoder, policy_head, sim_env):
        self.encoder = encoder          # ResNet-18 visual encoder
        self.policy_head = policy_head  # MLP (256, 256) -> action
        self.level = 0
        self.n_fail = 0
        self.aug_configs = [
            {"pose_range": 0.02, "light": False, "geom": False},  # L0: 微小位姿扰动
            {"pose_range": 0.02, "light": True, "texture": True},   # L1: +视觉随机化
            {"pose_range": 0.05, "target_rand": True},               # L2: +目标位置随机
            {"pose_range": 0.10, "geom": True},                      # L3: 全随机化
        ]

    def augment_trajectory(self, traj, config):
        """Physics-consistent augmentation: re-render in sim, not image crop"""
        aug_trajs = []
        for _ in range(100):  # 仿真采样成本低，可大量尝试
            new_pose = traj.init_pose + torch.randn(6) * config["pose_range"]
            states, success = self.sim_env.replay(traj.actions, new_pose, config)
            if success:  # 仅保留成功轨迹
                obs = self.sim_env.render(states, randomize_camera=True)
                aug_trajs.append((obs, traj.actions))
        return aug_trajs

    def train_step(self, batch):
        obs, actions = batch  # (B, T, 3, H, W), (B, T, act_dim)
        feat = self.encoder(obs.flatten(0, 1))  # (B*T, feat_dim)
        pred = self.policy_head(feat).view_as(actions)  # (B, T, act_dim)
        loss = F.mse_loss(pred, actions)  # BC loss
        return loss

    def curriculum_update(self, success_rate, r_up=0.8, N_max=5):
        if success_rate > r_up:
            self.level = min(self.level + 1, len(self.aug_configs) - 1)
            self.n_fail = 0
        else:
            self.n_fail += 1
        return self.n_fail > N_max  # True = converged/stuck
```

## 4. 实验与验证 (Experiments)

### 任务
- **Pick and Place**: 准静态抓取放置
- **Rotate**: 旋转阀门（动态任务）
- **Pour**: 倒水

### 关键结果

| 方法 | Pick&Place | Rotate |
|-----|-----------|--------|
| Real Demo + R3M | 低 | 低 |
| Real Demo Only | 中 | 中 |
| **CyberDemo** | **高 (+35%)** | **高 (+20%)** |

### 泛化测试
- 训练: 三瓣阀门 (tri-valve)
- 测试: 四瓣/五瓣阀门
- **成功率 42.5%**（baseline 接近 0）

### 训练设定

| 参数 | 值 |
|------|------|
| 策略网络 | ResNet-18 encoder + MLP (256, 256) |
| 预训练编码器 | R3M / ImageNet (对比实验) |
| 优化器 | Adam, lr = 1e-4 |
| Batch Size | 128 |
| 每级课程训练 | ~200 epochs |
| 仿真演示数 | 20-50 trajectories (原始) |
| 增强后数据量 | ~10K trajectories |
| 真实微调数据 | ~3 min (~20 trajectories) |
| 真实微调 | ~50 epochs, lr = 5e-5 |
| 仿真器 | SAPIEN |
| 观测空间 | RGB 图像 (84×84) × 2 视角 + 关节角 |
| 动作空间 | 末端执行器/关节位置增量 |

### Ablation 因果链

> [!warning] 关键消融
> - 去掉物理增强，仅用图像级增强 (color jitter/crop) → 视角/光照变化不符合物理投影 → 策略在真实世界的新视角下失败（**物理一致性增强 vs. 图像级增强的本质差异**）
> - 去掉课程学习，直接用最高增强等级 (L3) → 初始成功率过低 → BC 损失缺乏有效梯度信号 → 训练发散（**课程递进对 BC 的梯度信号保障**）
> - 去掉几何增强（物体形状多样性）→ 策略过拟合到训练物体形状 → 测试其他形状阀门成功率趋近 0（**形状泛化依赖几何增强**）
> - 去掉真实微调，纯仿真策略直接部署 → 视觉域差异 + 动力学误差累积 → 成功率下降 ~40%（**少量真实数据微调消除残余 sim-to-real gap**）
> - CyberDemo vs. 纯真实数据 (相同数据量) → CyberDemo 高 +35% → 仿真增强的多样性覆盖远超有限真实数据（**仿真可生成的条件远多于真实可采集的**）

### 工程关键细节 (Engineering Tricks)

1. **物理一致性渲染**: 不做图像级增强（crop/jitter），而是在仿真中重放状态并从新相机位姿渲染 → 保证透视投影正确性
2. **轨迹敏感性过滤**: 分析每个时间步对扰动的敏感性 → free-space 阶段可安全大幅修改，接触阶段保留原始动作
3. **仿真中成功筛选**: 物体几何增强后直接重放可能失败 → 加噪扰动 + 仿真验证 → 仅保留成功轨迹
4. **渐进难度增强**: L0 (微小位姿扰动) → L3 (大范围全随机) → 避免训练初期的灾难性遗忘
5. **双视角观测 + 视角随机化**: 固定相机在手腕/三方视角 → 仿真中随机化的相机在合理范围内 → 真实部署对相机位置鲁棒

## 5. 批判性分析 (Critical Analysis)

### 优势
- **低成本**: 仿真演示收集快速便宜
- **高鲁棒**: 增强覆盖多样条件
- **物理一致**: 增强基于物理仿真
- **自动调难度**: 无需手动设计课程

### 局限性

| 维度 | 局限 | 根因 | 替代方案 |
|------|------|------|----------|
| **理论** | BC 的分布漂移未根本解决 | 增强只扩大覆盖范围，不改变 BC 的模仿瓶颈 | DAgger 在线纠正 / 扩散策略建模多模态分布 |
| **理论** | 增强分布与部署分布的匹配无保证 | 随机化范围是启发式设定，无理论最优 | 自适应域随机化 (ADR) 自动搜索分布边界 |
| **算法** | 课程等级需手动设计 | 4 级增强的划分依赖人类先验 | ADR 自动调参 / 基于价值函数的难度调度 |
| **算法** | 几何增强依赖可参数化物体 | 需 CAD 模型 + 仿真渲染 | NeRF/3DGS 生成新视角/物体 |
| **工程** | 仿真器质量决定迁移上界 | SAPIEN 接触模型与真实世界仍有差异 | Isaac Lab/MuJoCo + 系统辨识 |

### 对转笔/Sim-to-Real 的启发

1. **四维增强可直接迁移**: 转笔的 Sim-to-Real 同样面临视角/光照/笔形状的多样性问题 → CyberDemo 的物理增强可直接套用
2. **课程学习适配转笔难度递进**: 从简单 180° 翻转到复杂连续旋转 → 可设计类似 L0-L3 的课程递进
3. **轨迹敏感性对接触阶段的洞察**: 转笔中"拨动瞬间"是高敏感区 → 对这些关键帧保留精确动作，而对 free-flight 阶段放松约束
4. **仿真演示采集成本低**: 转笔的真实电教演示极难采集 → 在 Isaac Lab 中用 motion retargeting 解算仿真演示 + CyberDemo 增强，可能是更实际的数据采集路径

### 未来方向
- 更多任务类型验证
- 与 RL 结合进一步提升
- 减少真实微调数据需求

## 6. 对灵巧操作的启发 (Implications)

1. **仿真演示 > 真实演示**: 在有好仿真器的条件下
2. **增强的多样性**: 视觉+物理+几何全面覆盖
3. **课程学习必要**: 直接高难度增强会导致训练失败
4. **轨迹敏感性**: 分析哪些部分可安全修改

### 与 Foundations 的数学关联

**[[ReinforcementLearning|Behavioral Cloning]]**: BC 优化目标为最小化动作回归损失:
$$\mathcal{L}_{BC} = \mathbb{E}_{(o_t,a_t)\sim\mathcal{D}}\left[\|a_t - \pi_\theta(o_t)\|^2\right]$$
CyberDemo 的核心在于扩大 $\mathcal{D}$ 的分布覆盖: $\text{supp}(\mathcal{D}_{\text{aug}}) \gg \text{supp}(\mathcal{D}_{\text{real}})$，使得 $p_\mathcal{D}(o)$ 更接近部署时的真实分布 $p_{\text{deploy}}(o)$，缓解分布漂移。

**[[RepresentationLearning|视觉表征]]**: 物理一致性增强使得编码器 $\phi(o)$ 学到的视觉表征对光照/视角具有不变性:
$$d\bigl(\phi(T_k(o)),\, \phi(o)\bigr) \to 0, \quad \forall T_k \in \mathcal{T}$$
对比实验中 R3M 预训练 vs. 从头训练的差异反映了预训练表征对增强数据的兼容性——R3M 已学会视觉不变性，增强数据进一步强化了这一属性。

**[[EmbodiedAI]]**: CyberDemo 的“仿真演示 + 增强 + 少量真实微调”范式，是 VLA 模型“大规模预训练 + 少量微调”思路在操作领域的缩影。

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── MimicGen (2023): 仿真内演示扩增
├── Domain Randomization: 视觉随机化
└── R3M: 预训练视觉表征

本论文: CyberDemo (2024)
├── 仿真演示 + 物理增强
├── 自动课程学习
└── 最小真实微调

后续影响:
├── 物理驱动数据生成
├── 跨具身数据迁移
└── 大规模仿真预训练
```

### 跨方法对比

| 方法 | 数据来源 | 增强方式 | 训练方法 | Sim2Real | 泛化性 |
|------|---------|---------|---------|----------|--------|
| **BC from Real** | 真实演示 | 图像级 | BC | 直接部署 | 低 |
| **MimicGen** | 仿真生成 | 轨迹拼接 | BC | ❌ 仅仿真 | 中 |
| **DemoStart** | 仿真 + RL | DR | PPO+Demo Curriculum | ✅ DR | 中 |
| **CyberDemo (本文)** | **仿真演示** | **物理+视觉+几何** | **BC+课程** | **✅ 少量微调** | **高** |
| DexCap | 真实 + 手部重定向 | 有限 | BC | 直接部署 | 低 |
| DexMimicGen | 仿真 + 双手 | 轨迹拼接 | BC | ❌ 仅仿真 | 中 |
