---
tags:
  - paper
  - manipulation
  - non-prehensile
  - extrinsic-dexterity
  - representation-learning
aliases:
  - DAPL
  - Emerging Extrinsic Dexterity
paper-year: 2026
read-date: 2026-03-13
venue: arXiv
paper-pdf: "[[Papers/Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[ComputationalGeometry]]"
---

# Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning

> [!abstract] 核心贡献
> 提出 DAPL（Dynamics-Aware Policy Learning）框架，通过学习物理世界模型的动力学表征来条件化 RL 策略，使 extrinsic dexterity 在杂乱场景中自然涌现，无需手工设计的接触启发式或复杂奖励塑形。在 Dense 场景中成功率（44.56%）是几何方法 CORN（22.22%）的 2 倍。

## 1. 问题设定与动机

### 1.1 核心洞察（一句话 + 直观隐喻）
像台球高手利用球间碰撞完成"K 球"——操作者不直接控制目标物体，而是通过预判接触链的动力学传递间接达成目标。关键不是几何上"能不能碰到"，而是动力学上"碰了之后会怎样"。

### 1.2 现有方法的局限
杂乱场景中的非抓取操作（pushing, sliding, toppling）需要选择性地利用或回避环境接触 — 即 **extrinsic dexterity**。已有方法的核心缺陷：

- **几何方法** (CORN, UniCORN): 仅建模静态形状，缺乏动力学推理 → 密集杂乱下失败
- **模型基规划**: 需精确物体位姿、不可扩展至复杂场景
- **通用 RL**: 接触采样效率低，难以学到选择性接触策略

## 2. 核心方法

> [!tip] Delta 分析：与 SOTA 的增量
> - vs CORN/UniCORN (几何方法): 引入动力学表征替代纯几何推理 → 密集场景 SR 翻倍
> - vs 端到端 RL: 世界模型预训练提供动力学先验 → 采样效率提升 3-4×
> - vs Model-based Planning: 不需要精确物体位姿，用点级隐表征替代解析动力学模型

### 2.1 Dynamics-Aware Policy Learning (DAPL) 框架

两阶段解耦设计 + 课程式迭代：

**Stage 1 — World Model 预训练**:
- **物理场景表征**: 每个点 $x_i = (p_i, m_i, v_i)$ — 位置 + 质量 + 速度
- **Patch-based Transformer**: FPS → kNN patch → PointNet 嵌入 → ViT → MLP 解码
- **训练目标**: 点级动力学预测（位置 + 速度）

$$\mathcal{L}_{\text{dyn}} = \sum_i \| \hat{p}_i^{t+1} - p_i^{t+1} \|_2^2 + \lambda \| \hat{v}_i^{t+1} - v_i^{t+1} \|_2^2$$

- **方差正则化**: $\mathcal{L}_{\text{var}} = \| \text{Std}\{\hat{v}_i^{t+1}\} - \text{Std}\{v_i^{t+1}\} \|^2$ — 防止速度预测坍缩到零

**Stage 2 — RL 策略学习**:
- 冻结 world model 的动力学特征 $f_{\text{dy}}$ 作为策略输入条件
- Actor-Critic + 本体感知 + 任务目标
- **课程学习**: 策略 rollout 数据反过来精炼 world model → 迭代 3 轮，成功率从 61.3% → 71.8%

### 2.x 核心伪代码

```python
# DAPL 双阶段核心逻辑
# ===== Stage 1: World Model 预训练 =====
class DynamicsWorldModel(nn.Module):
    def __init__(self, embed_dim=256, n_heads=8, n_layers=4):
        self.patch_embed = PointNetPatchEmbed(in_dim=7)  # (pos3 + mass1 + vel3)
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(embed_dim, n_heads), n_layers)
        self.pos_head = nn.Linear(embed_dim, 3)   # 预测下一步位置
        self.vel_head = nn.Linear(embed_dim, 3)   # 预测下一步速度

    def forward(self, points, actions):
        # points: (B, N, 7) = [pos, mass, vel]
        patches = fps_knn_patch(points, n_patches=64, k=32)  # FPS + kNN
        tokens = self.patch_embed(patches)                      # (B, 64, D)
        feat = self.transformer(tokens)                         # (B, 64, D)
        p_next = self.pos_head(feat)
        v_next = self.vel_head(feat)
        return p_next, v_next, feat  # feat = 动力学表征 f_dy

    def loss(self, p_pred, v_pred, p_gt, v_gt):
        l_pos = F.mse_loss(p_pred, p_gt)
        l_vel = F.mse_loss(v_pred, v_gt)
        l_var = F.mse_loss(v_pred.std(dim=1), v_gt.std(dim=1))  # 方差正则
        return l_pos + 0.1 * l_vel + 0.01 * l_var

# ===== Stage 2: RL 策略学习 =====
# 冻结 world model, 提取 f_dy 作为策略输入
def policy_input(world_model, obs_points, proprioception, goal):
    with torch.no_grad():
        _, _, f_dy = world_model(obs_points, actions=None)
    return torch.cat([f_dy.mean(dim=1), proprioception, goal], dim=-1)
```

### 2.x 训练设定

| 项目 | 详情 |
|------|------|
| **仿真器** | Isaac Gym (GPU 并行) |
| **World Model 数据** | 随机策略 rollout 收集的点云动力学轨迹 |
| **RL 算法** | PPO (Actor-Critic) |
| **状态空间** | 动力学表征 $f_{\text{dy}}$ + 本体感知 + 目标 6DoF |
| **动作空间** | 末端执行器 SE(3) 位移 |
| **奖励** | 目标物体 6DoF 误差 + 碰撞惩罚 |
| **课程迭代** | 3 轮（World Model ↔ Policy 交替精炼） |
| **训练步数** | ~10⁴ 迭代即达 70% SR |
| **Sim-to-Real** | Student-teacher distillation + 观测噪声注入 |

### 2.2 Clutter6D Benchmark

- 3 密度等级: Sparse (4 objects), Moderate (8), Dense (12)
- 6D 物体重排任务（平移+旋转）

## 3. 实验结果

**仿真 (Clutter6D Sparse track)**:

| 方法 | Sparse SR | Moderate SR | Dense SR |
|------|:---------:|:-----------:|:--------:|
| **DAPL (Ours)** | **71.88%** | **51.04%** | **44.56%** |
| CORN | 46.63% | 45.83% | 22.22% |
| UniCORN | 20.61% | 11.67% | 5.81% |
| Teleoperation | 50.0% | 40.0% | 20.0% |
| GraspGen+CuRobo | 26.6% | 15.6% | 3.13% |

**真实世界** (10 scenes, zero-shot sim-to-real):
- DAPL: 48% SR, 平均执行时间 42.6s
- Human Teleoperation: 52% SR, 平均 55.9s
- DAPL 更高效但成功率略低于人类

**消融**: 去除速度/质量物理属性 → SR 从 71.88% 降至 42.00%；用 object-level 位姿预测替代 point-level → SR 降至 16.88%

**Ablation 因果链分析**:

| 消融条件 | SR 变化 | 因果机制 |
|---------|---------|--------|
| 去除速度属性 | 71.88→~55% | 丢失接触后运动趋势 → 策略无法预判"推了之后往哪倒" → [[Dynamics]] 中速度状态是动力学预测的必要输入 |
| 去除质量属性 | 71.88→~50% | 无法区分轻/重物体 → 推相同距离所需力不同 → [[ContactMechanics]] 中 $F = ma$ 的质量项缺失 |
| Object-level 替代 Point-level | 71.88→16.88% | 6DoF 位姿丢失接触点局部信息 → 物体间碰撞的精细传递无法建模 → 与 [[ComputationalGeometry]] 中点云 vs 位姿的表征粒度问题一致 |
| 去除课程迭代（仅 1 轮） | 71.88→61.3% | World model 在随机策略数据上训练 → 分布偏移 → 策略遇到新状态时动力学表征不准 |
| 去除方差正则 $\mathcal{L}_{\text{var}}$ | 速度预测坍缩到零 | 大部分点静止 → MSE 最优解是预测零速度 → 正则项强制保留运动信号 |

## 4. 核心洞见 (Insights)

1. **动力学 > 几何**: 在接触丰富的杂乱场景中，物体"如何响应接触"比"长什么样"更关键 → 与 [[ContactMechanics]] 的核心论点一致
2. **自适应行为涌现**: 相同几何布局、不同质量分配 → 策略自动切换接触对象（利用重物作锚点 vs 回避轻物），表明 dynamics representation 成功编码了物理属性
3. **点级预测 >> 物体级预测**: 粗粒度 6DoF 位姿监督不足以捕获接触传播的精细物理 → 密集表示的优势
4. **训练效率优势**: 动力学先验使策略在 ~10⁴ 迭代即达 70% SR，而几何方法需 3-4× 更多迭代 → 与 [[ReinforcementLearning#5.1 域随机化 (Domain Randomization, DR) 与 自适应 (Adaptive DR)|DR]] 中 "好的表征减少采样需求" 的原理一致
5. **Zero-shot sim-to-real**: 通过 student-teacher distillation + 观测噪声注入实现 → 与 [[Dynamics#Sim-to-Real 与动力学迁移|System ID]] 互补的迁移方案

## 4.5 工程关键细节 (Engineering Tricks)

- **FPS + kNN Patch 构建**: Farthest Point Sampling 保证全局覆盖，kNN 捕获局部几何 → 对杂乱场景的不均匀点云分布鲁棒
- **方差正则化**: $\mathcal{L}_{\text{var}}$ 是关键 trick — 没有它，速度预测坍缩到全零（因大部分点静止）
- **课程迭代的收益递减**: 3 轮后继续迭代提升可忽略 → world model 和 policy 分布已对齐
- **Student-Teacher Distillation**: Teacher 使用特权信息（精确位姿+质量），Student 仅用点云 → 弥补 sim-to-real 的感知 gap
- **VLM 质量估计**: 用 GPT-4V 从 RGB 图像粗估物体质量 → 精度有限但"大致对"即足够（重/轻二分类精度 ~85%）

## 5. 与知识体系的联系

### 与 [[Dynamics]] 的联系
- World model 本质是学习场景级多体动力学的代理 — 不同于 analytical dynamics，此处用点级 Transformer 作为动力学近似器
- 质量+速度作为物理属性直接进入表征 → 与 [[Dynamics|Newton-Euler]] 中的质量/惯量平行

### 与 [[ContactMechanics]] 的联系
- Extrinsic dexterity 的核心是选择性利用接触力传递 → 接触链的合理"借力"
- Variance-aware regularization 处理的是接触稀疏性问题 — 大部分点静止，仅少数点上有接触力

### 与 [[RepresentationLearning]] 的联系
- 动力学表征 vs 几何表征 的核心对比 → 任务相关性决定表征质量
- Patch-based Transformer 上的 point cloud 表征学习

### 与 [[ReinforcementLearning]] 的联系
- 世界模型 → RL 条件化的两阶段范式 → 类似 model-based RL 但仅用表征而非直接做 planning
- 课程式迭代精炼 → 与 [[Curriculum Learning]] 理念一致

## 6. 局限与未来方向

- 6DoF pushing 仍局限于单目标 + 周围场景的设定，多目标联合重排更复杂
- 仅用 Franka 单臂 + 平行夹爪 → 与灵巧手的 extrinsic dexterity 尚未结合
- 真实世界依赖 FoundationPose + SAM2 追踪 → 感知失败会级联影响策略
- 质量由 VLM 粗估 → 物理属性精度有天花板

## 7. 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **接触链思维迁移**: 转笔本质是手指-笔-环境的接触链动力学 → DAPL 的"学动力学再做策略"范式可直接迁移 — 先学笔在手指间的滚动/滑动动力学，再让 RL 策略条件化于此
2. **质量/惯量感知**: 转笔对笔的质量分布（重心偏移）极敏感 → DAPL 将质量作为表征输入的做法值得借鉴
3. **Point-level 表征**: 笔的接触面积小、形状简单 → 点级表征可能过于精细，但手指-笔接触点的局部几何仍需精确捕获
4. **课程迭代**: 世界模型 ↔ 策略的交替精炼 → 可用于 sim-to-real 调参：先在仿真中学动力学，real-world 数据精炼后再优化策略

### 跨方法对比

| 维度 | DAPL (本文) | CORN | UniCORN | DexGraspNet | Contact-GraspNet |
|------|------------|------|---------|-------------|------------------|
| **接触建模** | 隐式（点级动力学） | 显式几何 | 几何+语义 | 分析接触模型 | 接触图回归 |
| **杂乱处理** | 选择性接触利用 | 碰撞回避 | 碰撞回避 | 无杂乱 | 无杂乱 |
| **物理推理** | ✅ (质量+速度) | ❌ | ❌ | 部分 | ❌ |
| **Non-prehensile** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Sim-to-Real** | Zero-shot | 无 | 无 | 无 | 有限 |
| **Dense SR** | 44.56% | 22.22% | 5.81% | — | — |
