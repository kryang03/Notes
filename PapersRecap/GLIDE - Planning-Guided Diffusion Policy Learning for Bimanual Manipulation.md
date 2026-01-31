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
aliases:
  - GLIDE
  - Planning-Guided-Diffusion
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

---

## 4. 批判性分析 (Critical Analysis)

### 创新贡献

1. **规划-学习解耦**: 规划解决数据生成，学习解决泛化
2. **高效接触规划**: 利用平滑线性近似显著提升效率
3. **关键设计选择**: 残差动作 + Flying Point Augmentation 缺一不可
4. **任务条件化**: 单一策略处理任意 SE(2) 目标

### 局限性

- **长视野困难**: Hard 任务成功率仍较低
- **仅限盒状物体训练**: OOD 泛化有限
- **3关节控制**: 未使用全臂自由度
- **静态场景**: 未考虑动态扰动

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
- [[TRANSIC]]（可组合 sim-to-real）
- [[HIL-SERL]]（人在环微调）

**技术相关**:
- [[Optimization#Trajectory Optimization]]
- [[ContactMechanics#Contact-Implicit Planning]]
- [[RepresentationLearning#Point Cloud Processing]]

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

## References

- Li et al. arXiv:2412.02676v2, Feb 2025
- Platform: 2× KUKA LBR iiwa, Drake simulator
- Project: https://glide-manip.github.io/
