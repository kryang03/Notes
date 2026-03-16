---
tags:
  - paper
  - manipulation
  - tactile
  - imitation-learning
  - sim-to-real
aliases:
  - CGP
  - Contact-Grounded Policy
paper-year: 2026
read-date: 2026-03-13
venue: arXiv
paper-pdf: "[[Papers/Contact-Grounded Policy- Dexterous Visuotactile Policy with Generative Contact Grounding.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ContactMechanics]]"
  - "[[RepresentationLearning]]"
  - "[[SignalProcessing]]"
---

# Contact-Grounded Policy: Dexterous Visuotactile Policy with Generative Contact Grounding

> [!abstract] 核心贡献
> 提出 **Contact-Grounded Policy (CGP)**，将灵巧操作视为**接触基准化问题**：策略不仅预测运动轨迹，还同时预测耦合的触觉反馈，并通过学习的**接触一致性映射**将预测转换为顺应控制器可执行的目标状态，实现接触演化的闭环执行。

## 1. 问题设定与动机

灵巧手操作中，现有模仿学习策略的核心限制：
- **仅预测运动学轨迹**，缺乏显式的接触语义
- 触觉信号仅作为额外观测，而非建模接触状态与底层控制器动力学的交互
- 预测的接触模式无法被顺应控制器忠实执行→滑移、过刚交互

**核心洞察**：策略应产生**控制器兼容的目标**，而非仅预测触觉信号作为辅助任务。

## 2. 核心方法

### 2.1 框架架构

CGP 由两个核心组件构成：

1. **条件扩散模型**：在压缩潜空间中预测未来耦合的 (实际机器人状态, 触觉反馈) 轨迹
2. **接触一致性映射** (Contact-Consistency Mapping)：将预测的 (状态, 触觉) 对转换为顺应控制器的可执行目标状态

### 2.2 关键设计

- **触觉潜空间**：KL 正则化 VAE 压缩触觉观测，在紧凑潜空间中预测→运行时轻量级
- **接触基准化**：预测 actual state + tactile → 映射为 target state，使顺应控制器实现预期接触演化
- **支持多种触觉传感器**：密集触觉阵列 (Tesollo DG-5F 全手覆盖) 和视觉触觉 (Digit360 指尖)
- **解耦规划与执行**：16步预测，8步执行后重规划

### 2.3 数学建模

顺应控制器 (PD 控制器) 作为虚拟弹簧-阻尼系统：
$$\tau = K_p(q_{target} - q_{actual}) + K_d(\dot{q}_{target} - \dot{q}_{actual})$$

接触一致性映射 $g$：$(x_{actual}, u_{tactile}) \mapsto x_{target}$

> [!tip] 与 [[ControlTheory]] 的联系
> CGP 的顺应控制器本质上是 [[ControlTheory#2.1 阻抗控制 (Impedance Control)|阻抗控制]] 的简化形式。接触一致性映射可以理解为学习了一个从期望接触力到关节位移的逆映射，与 [[ControlTheory#9. 相关论文|FACET]] 的阻抗参考模型跟踪形成互补。

## 3. 实验结果

### 硬件平台
- **真机**: Allegro V5 四指手 + Digit360 触觉 + UR5 臂
- **仿真**: Tesollo DG-5F 五指手 + 密集全手触觉阵列

### 任务与性能
- 5 个任务: Box Flipping, Egg Grasping, Dish Wiping (仿真), Jar Opening, Real Box Flipping (真机)
- CGP **一致性优于**视觉运动扩散策略基线和视触觉扩散策略基线
- 在持续/精细接触任务 (dish wiping, box flipping, jar opening) 中优势尤为显著

### 消融实验
- **KL 正则化**对触觉压缩至关重要→稳定生成 + 下游策略性能提升
- **接触一致性映射**的必要性经隔离验证：跨多样接触配置泛化

## 4. 核心洞见 (Insights)

1. **接触是可预测并可执行的**：通过耦合预测 (状态, 触觉) 并映射到控制器目标，接触演化可被实时忠实再现
2. **触觉预测不应是辅助目标**：必须与控制栈紧密耦合，否则成为"脱节的接触意识"
3. **顺应控制器是桥梁**：PD 控制的虚拟弹簧-阻尼特性天然适合接触基准化

## 5. 与知识体系的联系

### 与 [[ControlTheory]] 的联系
- CGP 的核心创新在控制层面：**学习的接触一致性映射作为力-位耦合的替代方案**
- 与 FACET 的阻抗参考跟踪互补：CGP 从触觉预测→目标状态，FACET 从参考模型→阻抗参数

### 与 [[ContactMechanics]] 的联系
- 多点接触的连续演化建模——从离散接触切换到连续分布式接触表征
- 摩擦转变和滑移作为接触基准化需要处理的核心挑战

### 与 [[RepresentationLearning]] 的联系
- KL 正则化 VAE 的触觉潜空间压缩——信息瓶颈与生成质量的平衡
- 多模态 (视觉+触觉+本体感觉) 融合的扩散策略

### 与 [[SignalProcessing]] 的联系
- 密集触觉阵列 → 高维信号压缩 → 潜空间预测

## 6. 局限与未来方向

- **传感器-控制器特异性**：接触一致性映射绑定特定触觉传感器和控制器参数，跨平台需重训练
- **单任务训练**：未验证跨任务接触知识迁移
- **未来方向**：跨传感器/控制器联合训练；控制器参数条件化（$K_p$, $K_d$, 更新频率）→更好的部署泛化
