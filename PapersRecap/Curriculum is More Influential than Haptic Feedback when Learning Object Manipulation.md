---
tags:
  - PaperRecap
  - RL/CurriculumLearning
  - DexterousManipulation
  - Tactile
  - InHand
date: 2026-02-01
---

# Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation

## 元信息
- **作者**: Pegah Ojaghi, Romina Mir, Ali Marjaninejad, Francisco J. Valero-Cuevas, et al.
- **机构**: USC, UCSC, University of Wisconsin-Madison
- **年份**: 2025 (Science Advances)
- **期刊**: Science Advances — 高影响力综合科学期刊

> [!important] 核心发现
> **课程设计比触觉信息更能影响灵巧操作学习**——这挑战了"触觉对操作至关重要"的传统观念。

---

## 问题设置

### 任务
- **三指机械手**在**向下朝向**（downward-facing）配置下进行 in-hand manipulation
- **目标**：抬升（Lift）和旋转（Rotate）一个球
- **无视觉**：仅依赖本体感知 + 可选触觉

### 为什么"向下朝向"更难？
传统研究多用向上朝向（手掌作为支撑平台），向下朝向需要：
- 持续对抗重力
- 更精确的力控制
- 任何错误都可能导致物体掉落

---

## 实验设计

### 两个变量

| 变量 | 条件 |
|-----|------|
| **触觉信息** | No-tactile vs 3D-force (指尖 3D 力向量) |
| **课程策略** | 5 种不同的 L/R 组合序列 |

### 课程策略示例
- **L→R**: 先学抬升，再学旋转
- **R→L**: 先学旋转，再学抬升
- **L+R**: 同时学习两者
- **L→L+R**: 先学抬升，再学组合
- **R→L+R**: 先学旋转，再学组合

---

## 核心发现

### 1. 课程 >> 触觉

> [!quote] 关键结论
> "The choice of curriculum biases the progression of learning for dexterous manipulation... Unexpectedly, learning is achieved even in the absence of haptic information."

**量化对比**：
- 不同课程策略导致的性能差异 **显著大于** 有/无触觉的差异
- 即使完全没有触觉反馈，某些课程仍能学习成功

### 2. "Waddington Landscape" 类比

作者用发育生物学的比喻描述学习过程：
- 初始状态是**多能的**（pluripotent）
- 课程像**山谷**引导发育方向
- 不同课程导向不同的技能组合

```
      [初始状态]
         /\
        /  \
       /    \
    [L优先] [R优先]
       \    /
        \  /
        [最终技能组合]
```

### 3. 触觉的微妙作用

虽然触觉不是"必需"的，但它**偏向**学习过程：
- **有触觉**：更倾向学习**力敏感**的技能组合
- **无触觉**：可能发展出不同的策略（如更依赖速度反馈）

---

## 方法细节

### 算法
- **PPO** (Proximal Policy Optimization)

### 状态空间
```python
state = {
    "joint_positions": q,      # 关节角度
    "joint_velocities": dq,    # 关节速度
    "ball_position": (x, z),   # 球的位置
    "ball_rotation": θ_y,      # 球的旋转角
    "tactile": [f_t1, f_t2, f_n]  # 可选：指尖 3D 力
}
```

### 奖励设计
$$R = c_R \cdot \theta_y - c_L \cdot |z_b - z_d|$$
- 旋转奖励正比于旋转角度
- 抬升惩罚正比于与目标高度的偏差

### 课程学习率调度器
作者提出了一个**基于课程的自适应学习率调度器**，加速收敛。

---

## 对传统观念的挑战

### 传统观念
> "触觉对灵巧操作至关重要"

### 本文发现
> "在某些任务和课程下，触觉可能是**锦上添花**而非**必需品**"

### 可能的解释
1. **信息冗余**：本体感知（位置、速度）可能隐含了部分接触信息
2. **策略适应**：无触觉时，策略可能发展出不依赖触觉的替代方案
3. **任务特异性**：对于特定的 Lift+Rotate 任务，触觉可能不是瓶颈

---

## 实验细节

### 对象变化实验
测试了不同重量和尺寸的球：
| 重量 | 半径 |
|-----|------|
| 50g | 35mm |
| 50g | 30mm |
| 5g  | 35mm |
| 5g  | 30mm |

结果表明学习具有**跨对象泛化**能力。

---

## 与相关工作的联系

### 与 [[Curriculum Learning]] 的关系
- 验证了课程学习在**机器人操作**领域的有效性
- 扩展：课程不仅加速学习，还**塑造**最终技能

### 与 [[Lessons from Learning to Spin Pens]] 的对比
| Spin Pens | 本文 |
|-----------|-----|
| 强调触觉重要性 | 发现课程 > 触觉 |
| 水平旋转 | 对抗重力旋转 |
| 复杂对象 (笔) | 简单对象 (球) |

### 与 [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References|DexTrack]] 的联系
- 两者都强调**设计选择**（课程/参考轨迹）对学习的深远影响
- 比单纯增加传感器可能更重要

---

## 对实践的启示

> [!tip] 设计启示
> 1. **优先设计好课程**：比堆传感器更有效
> 2. **不要过度依赖触觉**：本体感知可能足够
> 3. **课程即"先验"**：选择什么课程隐含了对任务的理解

> [!warning] 适用范围
> 本文结论主要适用于**模拟环境**和**特定任务**（Lift+Rotate 球）。
> 在更复杂任务或真实硬件上，触觉可能仍然重要。

---

## 关联笔记

- [[Curriculum Learning]] - 课程学习基础
- [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation]] - 课程学习在 Sim-to-Real 中的应用
- [[ReinforcementLearning]] - PPO 算法
- [[ContactMechanics]] - 接触力学基础
