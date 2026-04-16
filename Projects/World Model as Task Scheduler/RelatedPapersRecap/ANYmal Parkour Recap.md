---
tags: [paper, sim-to-real, actuator-model, WMTS]
aliases: [ANYmal Parkour]
paper-year: 2023
venue: Science Robotics
related: ["[[Dynamics]]", "[[ControlTheory]]", "[[Final_WMTS]]"]
paper-pdf: "[[ANYmal parkour Learning agile navigation for quadrupedal robots.pdf]]"
---

# ANYmal Parkour: Learning Agile Navigation for Quadrupedal Robots

> [!abstract] 核心贡献
> 四足跑酷系统，通过 **Actuator Network** 建模电机非线性（从指令力矩到实际力矩），实现极限 Sim-to-Real 迁移。自适应课程训练高难度地形。

## 核心方法 — Actuator Network

Actuator Network $f_{act}$：从力矩指令历史窗口到实际关节力矩的端到端映射：
$$\hat{\tau}_{link} = f_{act}(a_{t-H:t}, \phi_{t-H:t}, \dot{\phi}_{t-H:t})$$

- 在**真机数据**上训练（收集 指令-响应 对）
- 捕捉电机非线性：反电动势、摩擦力、温度漂移
- 嵌入仿真器取代理想的 $\tau = K_t \cdot I_q$ 映射

## 关键设计

- **Teacher-Student 蒸馏**：特权 teacher（地图 + 精确状态）→ 部署 student（仅 proprioception + 视觉）
- **自适应课程**：根据策略能力动态调整地形难度
- **硬接触刚体 WM**：不用 NN 拟合 non-smooth contact dynamics

## 与 WMTS 的关联

- **直接启发 WMTS §4.A Actuator Model**：WMTS 的 Actuator Model 架构直接继承 ANYmal 的设计，但增加了温度 $T_{motor}$ 和反馈力矩 $\tau_{fb}$ 作为额外输入
- **关键差异**：ANYmal 的 Actuator Net 嵌入仿真器做 domain randomization；WMTS 的 Actuator Model 是可微的 WM 组件，接收端到端梯度
- **Teacher-Student** 范式 → WMTS 的 Oracle-Generalist 架构
- **硬接触 WM vs 可微 WM**：ANYmal 选择硬接触（不可微），WMTS 选择 Physics-Informed Neural Dynamics（可微 + 残差）
