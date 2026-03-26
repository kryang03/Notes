---
tags:
  - paper
  - bimanual-manipulation
  - contact-rich-manipulation
  - diffusion-policy
  - planning-guided-learning
  - sim-to-real
  - point-cloud
date: 2025-02-02
paper-year: 2024
read-date: 2026-03-16
aliases:
  - GLIDE
  - Planning-Guided-Diffusion
paper-pdf: "[[Papers/GLIDE - Planning-Guided Diffusion Policy.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[EmbodiedAI]]"
  - "[[ComputationalGeometry]]"
  - "[[StochasticProcess]]"
---

# GLIDE: Planning-Guided Diffusion Policy Learning for Generalizable Contact-Rich Bimanual Manipulation

> [!note] Foundation 关联
> - **[[ReinforcementLearning]]**: Diffusion Policy 架构 (Section 6.2)
> - **[[ContactMechanics]]**: 接触密集操作的约束建模
> - **[[EmbodiedAI]]**: 规划与学习的集成范式 (Section 2: Robot Learning 范式)
> - **[[ComputationalGeometry]]**: 点云特征提取与 SDF 隐式表示

> **摘要**: 接触密集型双臂操作需要精确协调两臂通过策略性接触和运动改变物体状态。本文提出 GLIDE (Generalizable PLanning-GuIded Diffusion Policy LEarning)，利用基于模型的运动规划在高保真物理仿真中生成演示数据。通过高效规划在随机化环境中生成大规模高质量合成轨迹，训练任务条件扩散策略。通过特征提取、任务表示、动作预测和数据增强的关键设计，实现鲁棒的平滑动作序列预测和对未见场景的泛化。

---

## 1. 理论深潜 (Theoretical Deep Dive)

### 一句话核心与直观隐喻

接触密集型双臂操作是规划和学习的同盟——用规划器在仿真中自动"刷题"，然后把解题经验蒸馏为泛化策略。

> 就像考试前的"题海战术"——规划器在不同难度的仿真工况中自动生成 12,000 道"练习题"（轨迹），扩散策略从中提炼出通用解题思路（泛化技能），上考场（真实世界）时不再需要计算器（规划器）也能作答。

### 现有方法的局限

| 范式 | 关键局限 |
|-----|--------|
| 纯规划 | 需完整物体先验 + 在线计算成本高 → 无法泛化到新物体 |
| 纯学习 (BC) | 数据收集昂贵，双臂遥操作困难 |
| 端到端 RL | 接触动力学非光滑，探索空间指数爆炸 |
| 域随机化 | 参数化接触模态组合爆炸，难以覆盖 |

### 核心挑战: 接触密集双臂操作

**问题定义**: 
- 控制双臂操作大型/重型物体到目标位姿
- 物体无法直接被末端执行器抓取
- 需要通过多链节接触稳固持握
- 可能需要多阶段接触才能到达目标

**三重挑战**:
| 挑战 | 描述 |
|-----|------|
| 数据获取 | 遥操作数据收集困难且昂贵 |
| 复杂动力学 | 接触动力学非光滑、模态呈指数增长 |
| Sim-to-Real | 感知和动力学的现实差距 |

### 为什么规划+学习？

**纯规划方法局限**:
- 需要完整物体状态和环境几何知识
- 计算开销大，无法在线实时
- 难以应对新物体

**纯学习方法局限**:
- 需要大量高质量演示数据
- 数据收集成本高
- 泛化能力受限

**GLIDE 方案**: 规划生成数据 + 学习泛化策略

---

## 2. 方法论剖析 (Methodology Dissection)

### Delta 分析

| 维度 | 纯规划 (Contact-Implicit) | 纯学习 (BC/DP3) | GLIDE |
|-----|--------------------------|-----------------|-------|
| 数据来源 | 在线优化 | 人类遥操作 | **规划自动生成** |
| 物体先验 | 完整几何+质量 | 不需要 | **训练时需要，部署不需要** |
| 实时性 | 秒级规划 | 毫秒级推理 | **毫秒级推理** |
| 泛化性 | 仅已知物体 | 受限于演示覆盖 | **单策略处理多物体/位姿** |
| Sim-to-Real | N/A | 需域随机化 | **Flying Point Aug + 残差动作** |

### 2.1 问题公式化

**状态空间**: $S$ (环境状态)
**观测空间**: $O$ (点云 + 本体感知)
**动作空间**: $A$ (关节位置)
**任务空间**: $C$ (SE(2) 变换)
**时间范围**: $H$

**目标**: 学习单一策略 $\pi_\theta(a|o,c)$ 处理多样物体和目标位姿

### 2.2 演示合成流程

```
环境随机化 ─→ 接触采样器 ─→ 无碰撞规划(RRT) ─→ 接触规划器 ─→ 轨迹过滤 ─→ 数据集 D
     ↓              ↓                ↓                ↓
  物体/位姿      生成抓握配置    规划到抓握点      贪婪靠近目标
```

**接触规划器核心** (来自 [4]):

使用局部接触动力学的线性近似 $f_{local}$:
$$\min_{q^u_+, a} (q^u_+ - q^u_{goal})^T Q (q^u_+ - q^u_{goal}) + (a - q^a)^T R (a - q^a)$$

其中 $q^u_+ = f_{local}(q^u, q^a, a)$ 为近似的物体配置

**过滤行为克隆**:
- 在高保真仿真器 (Drake) 中回放验证
- 丢弃未达目标或过长轨迹
- 重平衡使轨迹在物体间均匀分布

### 2.3 扩散策略设计

**特征提取**:
- 裁剪工作空间内点云
- 移除无关背景
- **Flying Point Augmentation**: 以小概率(0.5%)添加大高斯噪声

**任务表示**:
- 不假设已知物体形状
- 使用初始观测 $o_0$ + 增量变换 $c_0$ 隐式指定目标
- 每步重计算当前到目标的变换 $c_t$
- 通过开放词汇分割获取物体 mask
- 最远点采样选取关键点追踪

**动作预测**:
- 预测残差关节位置: $a_{t+1:t+T_a} = \{q_i - q_t\}_{i=t+1}^{t+T_a}$
- 训练 $T_a = 64$，测试 $T_a = 20$
- 残差动作在尺度和偏移上更一致

### 2.4 核心 PyTorch 逻辑

```python
# GLIDE Diffusion Policy — 残差动作预测 + Flying Point Augmentation
import torch
import torch.nn as nn

def flying_point_augmentation(points: torch.Tensor, prob: float = 0.005, sigma: float = 0.5):
    """以小概率对点云添加大高斯噪声，模拟 Real 世界噪点"""
    mask = torch.rand(points.shape[0], 1, device=points.device) < prob  # (N, 1)
    noise = torch.randn_like(points) * sigma  # (N, 3)
    return points + mask.float() * noise  # 仅 ~0.5% 点被扰动

class GLIDEDiffusionPolicy(nn.Module):
    def __init__(self, point_encoder, noise_pred_net, n_steps=100):
        super().__init__()
        self.point_encoder = point_encoder   # PointNet/DP3 backbone
        self.noise_pred_net = noise_pred_net # U-Net 1D for action sequence
        self.n_steps = n_steps

    def forward(self, points, q_current, task_cond, timestep):
        """
        points: (B, N, 3) — 裁剪后工作空间点云
        q_current: (B, D_q) — 当前关节位置
        task_cond: (B, D_c) — SE(2) 增量变换
        timestep: (B,) — 扩散时间步
        """
        # 点云特征提取
        feat = self.point_encoder(points)  # (B, D_feat)
        cond = torch.cat([feat, q_current, task_cond], dim=-1)  # (B, D_cond)

        # 预测残差动作序列的噪声
        # noisy_residual_actions: (B, T_a, D_q), 残差 = q_{t+i} - q_t
        noisy_residual_actions = torch.randn(points.shape[0], 20, q_current.shape[-1],
                                             device=points.device)
        noise_pred = self.noise_pred_net(noisy_residual_actions, timestep, cond)
        return noise_pred  # DDPM 去噪迭代

    def predict_action(self, points, q_current, task_cond):
        """DDPM 推理：迭代去噪得到残差动作序列"""
        x = torch.randn(points.shape[0], 20, q_current.shape[-1], device=points.device)
        for t in reversed(range(self.n_steps)):
            t_batch = torch.full((points.shape[0],), t, device=points.device)
            noise_pred = self.forward(points, q_current, task_cond, t_batch)
            x = self.ddpm_step(x, noise_pred, t)  # 标准 DDPM 去噪步
        # x: (B, T_a, D_q) 为残差动作
        return q_current.unsqueeze(1) + x  # 转换为绝对关节位置
```

> [!note] 残差动作的关键优势
> 预测 $\Delta q = q_{t+i} - q_t$ 而非绝对 $q_{t+i}$，使动作序列在尺度和偏移上更一致，降低了扩散模型的学习难度（类似于 [[StochasticProcess]] 中差分平稳化的思想）。

---

## 3. 实验验证与结果

### 3.1 实验设置

| 参数 | 值 |
|-----|-----|
| 机器人 | 2× KUKA LBR iiwa (7-DoF) |
| 仿真器 | Drake |
| 相机 | Realsense D455 (距桌面2m) |
| 控制关节 | 每臂3个 |
| 训练轨迹 | 12,000 条成功轨迹 |
| 物体资产 | 2,000 个随机化矩形盒 |
| 数据生成 | 96-CPU 机器约 2 天 |

### 3.2 任务难度分级

| 难度 | 旋转范围 $|\Delta\theta|$ | 特点 |
|-----|---------------------------|-----|
| Fixed 45° | 固定45° | 评估位置泛化 |
| Easy | ≤45° | 单阶段接触 |
| Medium | 45°-90° | 可能多阶段 |
| Hard | 90°-150° | 需多轮接近操作 |

### 3.3 核心结果

**分布内评估**:

| 任务 | Planner(Sim) | Policy(Sim) | Policy(Real) |
|-----|--------------|-------------|--------------|
| Fixed 45° | 0.337 | **0.740** | **0.800** |
| Random(Easy) | 0.227 | **0.610** | 0.600 |
| Random(Medium) | 0.141 | **0.410** | 0.360 |
| Random(Hard) | 0.099 | **0.180** | 0.200 |

**关键发现**: 策略显著超过规划器，同时更快且无需物体先验

**OOD 评估** (曲面容器、可变形物体):

| 条件 | Fixed 45° | Random |
|-----|----------|--------|
| 空容器 | 0.688 | 0.250 |
| 过满容器 | 0.625 | 0.313 |

### 3.4 消融实验

| 设计选择 | 对真实世界成功率影响 |
|---------|-------------------|
| 残差动作 | +28% (0.52→0.80) |
| Flying Point Aug | +48% (0.32→0.80) |
| 两者缺失 | 0% (完全失败) |

**动作步数消融**:
| $T_a$ | Fixed 45° | Random |
|-------|----------|--------|
| 8 | 0.440 | 0.270 |
| 20 | **0.740** | **0.400** |
| 40 | 0.760 | 0.340 |
| 64 | 0.770 | 0.200 |

#### 消融因果分析

1. **残差动作 (+28%)**: 绝对关节位置在不同物体/位姿下偏移量变化大 → 扩散模型需要学习高方差分布 → 残差表示消除全局偏移，仅建模相对运动 → 方差降低 → 学习更稳定。这与 [[StochasticProcess]] 中差分序列降低非平稳性的原理一致。
2. **Flying Point Aug (+48%)**: Real 世界点云包含传感器噪声、反射伪影、遮挡伪点 → 仿真训练的策略对这些"飞点"毫无免疫力 → 0.5% 概率 + 大方差高斯噪声精确模拟了真实传感器的长尾噪声分布 → 策略学会忽略离群点。本质是对观测空间的 [[ReinforcementLearning#5. Bridging the Gap: Sim-to-Real & Offline RL|域随机化]]，但仅作用于点云而非物理参数。
3. **两者缺失 → 0%**: 说明 Sim-to-Real gap 的两个正交维度（动作空间偏移 + 观测空间噪声）都是致命的，必须同时解决。
4. **$T_a$ 非单调**: $T_a=20$ 在 Random 任务最优。$T_a$ 过小 → 无法表达多阶段接触序列；$T_a$ 过大 → 累积开环误差主导，闭环频率过低。最优 $T_a$ 取决于任务视野与闭环需求的 trade-off。

---

## 4. 批判性分析 (Critical Analysis)

### 创新贡献

1. **规划-学习解耦**: 规划解决数据生成，学习解决泛化
2. **高效接触规划**: 利用平滑线性近似显著提升效率
3. **关键设计选择**: 残差动作 + Flying Point Augmentation 缺一不可
4. **任务条件化**: 单一策略处理任意 SE(2) 目标

### 局限性（理论/算法/工程三维度）

| 维度 | 局限 | 根因 | 替代方案 |
|-----|------|------|--------|
| **理论** | 接触规划器依赖局部线性近似 $f_{local}$ | 真实接触为非光滑互补问题 → 线性化在大变形/滑动下误差大 | 可微仿真直接优化 ([[ContactMechanics#4. 计算动力学与求解器：从LCP到凸优化]]) |
| **理论** | 扩散策略无最优性保证 | BC 目标为似然最大化而非回报最大化 | RL 微调扩散策略 (DPPO) |
| **算法** | Hard 任务 (90°-150°旋转) 成功率仅 18% | 多阶段接触需长视野规划，行为克隆的复合误差 $\epsilon_{compound} \sim O(T^2 \epsilon_{single})$ | 层次化策略: 高层选择接触模式 + 低层执行 |
| **算法** | 仅限盒状物体训练 → OOD 泛化有限 | 接触规划器需已知几何，训练分布窄 | 引入物体形状随机化或基于 [[ComputationalGeometry]] 的 SDF 泛化 |
| **工程** | 仅控制每臂 3 关节 (共 6-DoF) | 降低规划复杂度但牺牲灵活性 | 冗余自由度可用于避障/力优化 |
| **工程** | 数据生成需 96-CPU × 2天 | 高保真仿真 (Drake) 计算成本高 | GPU 并行仿真 (Isaac Gym/MJX) |

### 失败案例分析

1. 物体滑脱导致感知-控制错位
2. 长视野累积误差
3. 复杂几何的接触点选择不当

### 未来方向

- 扩展到更多物体类型
- 增加全臂自由度控制
- 引入触觉反馈
- 在线规划纠错

---

## 5. 相关文献网络

**上游工作**:
- Diffusion Policy (Chi et al., 2023)
- Contact-implicit planning (Pang et al., 2023)
- DP3 (3D Diffusion Policy)

**同期工作**:
- [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction|TRANSIC]]（可组合 sim-to-real）
- [[HIL-SERL - Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning|HIL-SERL]]（人在环微调）

**技术相关**:
- [[Optimization#4. 核心算法实现：轨迹优化 (Implementation: Trajectory Optimization)]]
- [[ContactMechanics#4. 计算动力学与求解器：从LCP到凸优化]]
- [[RepresentationLearning#4. Point Cloud Representation: 3D 几何的深度学习基础 (Deep Learning on 3D Geometry)]]

---

## 6. 关键概念索引

### 接触规划效率演进

```
MIP (混合整数规划) → 采样规划 → 平滑接触近似
        ↓                 ↓              ↓
   指数模态增长      高计算成本     高效可微分
```

### 规划引导学习范式

```
传统流程:
  规划 → 执行 (需完整状态)
  
GLIDE 流程:
  规划(仿真,离线) → 数据 → 学习(泛化策略) → 执行(仅需观测)
```

### Sim-to-Real 关键设计

| 技术 | 作用 |
|-----|------|
| Flying Point Augmentation | 增强点云噪声鲁棒性 |
| 残差动作预测 | 减少绝对预测误差 |
| 点云裁剪/背景去除 | 聚焦任务相关区域 |

---

## 7. 演化脉络 (Evolution Context)

**双臂操作方法演进**:
```
手工规划 → 模型预测控制 → 端到端学习 → 规划引导学习
                                          ↓
                              结合规划精度与学习泛化
```

**与其他工作对比**:

| 方法 | 数据来源 | 物体先验 | 视觉反馈 |
|-----|---------|---------|---------|
| 纯规划 | 在线优化 | 需要 | 无 |
| 纯学习 | 人类演示 | 不需要 | 有 |
| GLIDE | 规划生成 | 训练时需要 | 有 |

---

## 与本仓库基础理论联系

- [[Optimization]]: 轨迹优化、接触隐式规划
- [[ContactMechanics]]: 接触动力学建模
- [[RepresentationLearning]]: 点云特征学习
- [[ReinforcementLearning]]: 行为克隆、扩散策略

---

## 实践启示

### 数据生成
- 高效规划器是合成数据的关键
- 轨迹过滤和重平衡提高数据质量
- 规模化(12k轨迹)显著提升性能

### Sim-to-Real
- 小技巧(Flying Point Aug)可能比复杂域随机化更有效
- 残差动作预测对真实部署至关重要
- 测试时动作步数需要调优

### 系统设计
- 开放词汇分割提供物体 mask
- 关键点追踪提供持续任务规格
- 无需手工设计物体坐标系

---

## 8. 与灵巧手转笔/Sim-to-Real 的启发

> [!important] 对灵巧手转笔研究的迁移价值

1. **规划引导数据生成范式可迁移**: 转笔任务同样面临遥操作困难（24-DoF 灵巧手），可借鉴 GLIDE 的"接触规划器自动生成轨迹 → 过滤后训练策略"流程。差异在于转笔涉及的重力+惯性动力学更复杂，需要 [[Dynamics]] 级别的 contact-implicit 规划器。
2. **Flying Point Augmentation 直接适用**: 灵巧手搭载的触觉/视觉传感器同样面临噪声 → 可在点云或触觉信号上施加类似的稀疏大噪声增强。
3. **残差动作表示启示**: 转笔的关节动作空间 (24-DoF) 更高维 → 残差表示的方差降低效果可能更显著 → 值得在扩散策略中测试。
4. **多阶段接触策略**: 转笔本质是多阶段接触切换（拇指推→食指接→中指稳）→ GLIDE 在 Hard 任务的低成功率提示需要更强的层次化策略设计。

---

## References

- Li et al. arXiv:2412.02676v2, Feb 2025
- Platform: 2× KUKA LBR iiwa, Drake simulator
- Project: https://glide-manip.github.io/
