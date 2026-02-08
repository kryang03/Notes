---
tags:
  - paper
  - curriculum-learning
  - multimodal
  - assembly
  - contact-rich
aliases:
  - Vision-Force Curriculum
  - VF-Assembly
paper-year: 2023
read-date: 2026-02-02
venue: Frontiers in Neurorobotics
related:
  - "[[ReinforcementLearning]]"
  - "[[SignalProcessing]]"
  - "[[RepresentationLearning]]"
  - "[[ContactMechanics]]"
---

# Vision-force-fused Curriculum Learning for Robotic Contact-rich Assembly Tasks

> [!abstract] 核心贡献
> 提出**视觉-力融合课程学习**框架，通过渐进式感知融合（先视觉引导，后力反馈精调），实现 0.1mm 间隙的高精度装配任务，并展示了强大的 Sim-to-Real 泛化能力。

> [!tip] 与理论基础的关联
> - [[SignalProcessing#4. 时序信号处理：滑移检测与摩擦估计]] - 力传感信号的特征提取与融合
> - [[RepresentationLearning]] - 多模态感知融合策略
> - [[ContactMechanics]] - 装配任务中的接触力学约束
> - [[ReinforcementLearning#4. Advanced State Space & Reward Engineering]] - 课程学习的状态空间设计
>
> **核心技术**: Vision-Force Fusion, Curriculum Learning, Peg-in-Hole Assembly

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**先用眼睛找位置，再用手感调细节**——模拟人类装配行为，先通过视觉定位粗略位置，再通过力反馈进行亚毫米级精调。

### 直观隐喻
像人类插 USB：先看着大致对准接口，接近后靠手感微调直到插入。纯视觉难以达到亚毫米精度，纯力控缺乏全局定位能力——融合才是关键。

### 领域定位
- **工业应用**: 直接面向精密装配场景（0.1mm 间隙）
- **方法论**: 提供视觉-力双模态的标准融合范式
- **课程设计**: 展示如何将感知复杂度纳入课程维度

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人方法 | 问题 | 本文解决方案 |
|---------|------|-------------|
| 纯视觉方法 | 遮挡+亚毫米精度不足 | 融合力反馈 |
| 纯力控方法 | 缺乏全局定位 | 融合视觉引导 |
| 直接融合 | 训练不稳定 | 课程式渐进融合 |

### 关键贡献点
1. **分阶段融合课程**: 视觉 → 视觉+力 → 力主导
2. **0.1mm 精度**: 首次在如此小间隙上实现 RL 装配
3. **零样本 Sim-to-Real**: 无需真机微调

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 感知融合架构

```
视觉编码器      力编码器
    ↓              ↓
  [CNN]        [MLP/1D-CNN]
    ↓              ↓
 视觉特征z_v    力特征z_f
    └──────┬──────┘
           ↓
    [融合网络 Φ]
           ↓
      融合特征 z
           ↓
      [策略网络 π]
           ↓
        动作 a
```

### 3.2 课程学习设计

**课程维度**: 感知模态的权重

| 阶段 | 视觉权重 $w_v$ | 力权重 $w_f$ | 训练目标 |
|-----|---------------|-------------|---------|
| Phase 1 | 1.0 | 0.0 | 学习粗定位 |
| Phase 2 | 0.7 | 0.3 | 开始感受接触 |
| Phase 3 | 0.3 | 0.7 | 精细力控 |
| Phase 4 | 0.2 | 0.8 | 最终策略 |

**数学形式**:
$$
z = w_v \cdot z_v + w_f \cdot z_f
$$

### 3.3 奖励函数设计

**分层奖励**:
$$
r = r_{\text{distance}} + r_{\text{alignment}} + r_{\text{force}} + r_{\text{success}}
$$

其中：
- $r_{\text{distance}}$: 距离孔的欧氏距离
- $r_{\text{alignment}}$: 轴向对准度
- $r_{\text{force}}$: 接触力惩罚（防止过大碰撞力）
- $r_{\text{success}}$: 成功插入奖励

## 4. 实验与验证 (Experiments)

### 任务设置
- **间隙**: 0.1mm（工业级精度要求）
- **形状**: 圆柱、方形、六角形
- **初始扰动**: 位置 ±5mm，姿态 ±5°

### 关键结果

| 方法 | 成功率 | 平均时间 |
|-----|-------|---------|
| 纯视觉 | 45% | 12.3s |
| 纯力控 | 32% | 15.7s |
| 直接融合 | 67% | 10.2s |
| **课程融合** | **92%** | **8.5s** |

### Sim-to-Real 验证
- 仿真训练 → 真机部署
- 无需微调，成功率 ~85%
- 对未见形状（三角形）泛化成功

## 5. 批判性分析 (Critical Analysis)

### 优势
- **实用性**: 直接解决工业装配问题
- **可解释性**: 课程阶段对应人类直觉
- **泛化性**: 对形状和初始位置泛化良好

### 局限性
- **传感器依赖**: 需要力/力矩传感器
- **静态孔位**: 假设孔位置固定
- **刚性物体**: 未考虑柔性件装配

### 与 DNPM 项目的关联

> [!note] 启发与借鉴
> 1. **课程设计思路**: 从简单感知到复杂感知的渐进
> 2. **力反馈重要性**: 接触丰富任务中力信号不可或缺
> 3. **融合时机**: 不是简单拼接，而是有意识地调度

## 6. 对灵巧操作的启发 (Implications)

1. **手内操作**: 触觉信号可类比力传感，应用相同融合思路
2. **动态操作**: 视觉捕捉全局状态，触觉处理接触细节
3. **课程扩展**: 感知课程 + 动力学课程（如速度缩放）组合

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── 视觉伺服装配 (2018) - 纯视觉方法
├── 力控装配策略 (2019) - 纯力控方法
└── 多模态感知 (2020) - 早期融合尝试

本论文: Vision-Force Curriculum (2023)

后续方向:
├── 触觉-视觉融合 - 扩展到 GelSight 等触觉传感
├── 动态装配 - 运动中的插入任务
└── 柔性件装配 - 可变形物体
```

---

**参考文献**:
- Jin, P. et al. "Vision-force-fused curriculum learning for robotic contact-rich assembly tasks." Frontiers in Neurorobotics, 2023.
