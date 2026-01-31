---
tags:
  - paper
  - dexterous-manipulation
  - pen-spinning
  - sim-to-real
  - reinforcement-learning
  - PPO
aliases:
  - Lessons from Pen Spinning
  - Pen Spinning
read-date: 2026-01-31
venue: CoRL 2024
paper-year: 2024
authors:
  - Jun Wang
  - Ying Yuan
  - Haichuan Che
  - Haozhi Qi
  - Yi Ma
  - Jitendra Malik
  - Xiaolong Wang
institution: UC San Diego, CMU, UC Berkeley
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
  - "[[EmbodiedAI]]"
---

# Lessons from Learning to Spin "Pens"

> [!note] Foundation 关联
> - **[[ReinforcementLearning#6. Sim-to-Real 与 Domain Randomization]]**: 三阶段 Sim-to-Real 流程
> - **[[ContactMechanics#3. 接触模型的演进]]**: 动态接触与 finger gaiting
> - **[[Dynamics]]**: 笔状物体的动态平衡控制
> - **[[EmbodiedAI]]**: 灵巧操作系统集成

> [!abstract] 核心贡献
> 首个实现**连续旋转笔状物体**的学习系统。通过 Oracle Policy + Open-loop Replay + Real-world Fine-tuning 的三阶段流程，仅用 **<50 条真实轨迹** 成功跨越 sim-to-real gap，实现 10+ 种不同物理属性的笔状物体多圈旋转。

## 1. 问题定位

### 1.1 为什么笔状物体如此困难？

**与传统 in-hand manipulation 的区别**：
- 立方体/球体有**自然支撑**（手掌、桌面、重力）
- 笔状物体需要**动态平衡** + **复杂手指协调**
- 需要 **finger gaiting**（手指交替接触/脱离）

**现有方法的失败原因**：

| 方法 | 问题 |
|------|------|
| 经典控制 | 需要精确模型，无法泛化 |
| Teleoperation + IL | 延迟太大，无法收集动态演示 |
| 纯 Sim-to-Real | Gap 太大，策略无法迁移 |

### 1.2 核心洞见

> [!tip] 关键思路
> **仿真中的 Oracle 轨迹可以作为 Open-loop Controller 直接在真机上执行**
> 
> 成功的真实轨迹 → 高质量演示数据 → Fine-tune 本体感知策略

---

## 2. 方法框架

```
(A) Oracle Policy Training (RL)
         ↓
    Sim Dataset
         ↓
(B) Pre-training Student Policy in Sim
         ↓
(C) Open-loop Replay → 真实成功轨迹
         ↓
(D) Fine-tuning with Real-world Data
```

### 2.1 Oracle Policy 设计

**观测空间**（特权信息）：
- 关节位置 $q_t$（历史 3 帧）
- 前一动作目标 $a_{t-1}$
- 二值触觉信号 $c_t$（每指尖 5 个传感器）
- 指尖位置 $p_t$
- 笔的位姿和角速度 $w_t$
- **点云** $\in \mathbb{R}^{100 \times 3}$（PointNet 编码）
- 物理属性（质量、质心、摩擦系数、尺寸）

**奖励函数**：
$$r = r_{\text{rot}} + \lambda_z r_z + \lambda_{\text{energy}} r_{\text{energy}}$$

> [!important] 关键设计：$r_z$ 惩罚
> 惩罚笔最高点和最低点的高度差，**强制笔保持水平**
> 
> 没有这个惩罚 → 笔倾斜 → 仿真可行但真机不稳定

**初始状态设计**：

```
⚠️ 不能随机采样！
```

人类启发的 **6 种 Canonical Grasp**：
- 每个是 finger gaiting 循环中的关键帧
- 每种加入噪声生成稳定初始状态集

![[pen_canonical_grasp.png]]

### 2.2 Sensorimotor Policy

**为什么不能用 DAgger 蒸馏？**
- 视觉触觉策略：sim-to-real gap 太大
- 纯本体感知策略：仿真中就无法收敛

**解决方案**：
1. 用 Oracle rollout 收集 $(s_t, a_t)$ 数据集
2. 预训练本体感知策略（获得 motion prior）
3. 用真实轨迹 fine-tune 适应真实动力学

**网络架构**：
- 输入：30 步 $q_t$, $a_{t-1}$ 历史
- Temporal Transformer 提取序列特征
- MLP 输出动作

### 2.3 Open-loop Replay

**流程**：
1. 选取 15 条持续 >800 步的仿真轨迹
2. 直接在真机上回放动作序列
3. Human-in-the-loop 筛选成功轨迹
4. 成功轨迹用于 fine-tuning

**为什么有效？**
- Open-loop controller 对 in-hand manipulation 出奇地鲁棒
- 虽然不能 zero-shot 迁移策略，但可以迁移**动作序列**

---

## 3. 实验结果

### 3.1 仿真消融

| 方法 | Episode Reward | 备注 |
|------|----------------|------|
| **Ours** | ~100 | 完整设计 |
| Single Canonical Pose | 不稳定 | 无 finger gaiting |
| No Tactile | 下降 | 触觉重要 |
| No Point Cloud | 下降 | 几何信息重要 |
| No Privileged Info | 下降 | 物理属性重要 |

### 3.2 真机性能

**指标**：
- **RR (Rotation Revolutions)**: 旋转圈数
- **Suc (Success Rate)**: 成功率

| 方法 | Object A | Object B | Object C |
|------|----------|----------|----------|
| Replay | 2.80/38% | 3.37/54% | 2.65/30% |
| V. Distill | 1.85/18% | - | - |
| P. Distill | 1.57/0% | 1.57/0% | 1.57/0% |
| **Ours** | **3.43/55%** | **3.38/70%** | **3.50/68%** |

**泛化到未见物体**（不同质量、摩擦、尺寸）：
- 成功率 50-80%
- 仅用 <50 条真实轨迹

---

## 4. 核心 Lessons

> [!quote] Lesson 1: 初始状态分布是关键
> 单一初始姿态无法学习 finger gaiting；需要人类启发的 canonical grasp 设计

> [!quote] Lesson 2: 水平约束 ($r_z$) 至关重要
> 没有显式惩罚笔倾斜，仿真中可行的行为在真机上会失败

> [!quote] Lesson 3: Open-loop Replay 出奇有效
> Oracle 轨迹作为 open-loop controller 可以产生高质量真实演示

> [!quote] Lesson 4: 仿真预训练提供 Motion Prior
> 使得策略可以用极少真实数据（<50 条）适应真实动力学

---

## 5. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系

- 使用 **PPO** 训练 Oracle Policy
- **Domain Randomization** 应用于感知输入和物理参数
- 体现了 **Imitation + RL** 的混合范式

### 与 [[Dynamics]] 的联系

- 笔旋转是典型的**混合动力学系统**（contact mode switching）
- Finger gaiting 涉及**滚动、滑动、脱离**的模式切换
- 验证了 RL 隐式学习模式调度的能力

### 与 Dynamic Non-Prehensile Manipulation 的联系

- 笔旋转本质上是**动态操作**（依赖惯性和动量）
- 不是静态抓取，而是持续的平衡和协调
- 是 [[Dynamic Non-Prehensile Manipulation]] 的重要 benchmark

---

## 6. 局限与未来

1. **仍需 Human-in-the-loop**：筛选成功的 open-loop 轨迹
2. **对象范围有限**：仅限笔状物体
3. **无 SO(3) 全姿态控制**：仅绕 z 轴旋转
4. **硬件要求**：Allegro Hand + 触觉传感器

---

## References

- [[EUREKA: Human-Level Reward Design via Coding Large Language Models]] — 同样研究笔旋转任务
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] — 追踪人类参考的灵巧操作
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] — RL 中的阻抗控制
