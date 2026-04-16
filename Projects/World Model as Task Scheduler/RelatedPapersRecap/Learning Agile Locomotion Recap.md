---
tags: [paper, sim-to-real, actuator-model, WMTS]
aliases: [ETH Locomotion]
paper-year: 2019
venue: Science Robotics
related: ["[[Dynamics]]", "[[ControlTheory]]", "[[Final_WMTS]]"]
paper-pdf: "[[Learning Agile and Dynamic Motor Skills for Legged Robots.pdf]]"
---

# Learning Agile and Dynamic Motor Skills for Legged Robots

> [!abstract] 核心贡献
> ETH Actuator Network 开山之作：学习从力矩指令历史到实际关节力矩的映射，嵌入仿真环境缩小 Sim-to-Real Gap，实现 ANYmal 敏捷运动。

## 核心方法

- **Actuator Network**：MLP 输入 $[a_{t-H:t}, \dot{\phi}_{t-H:t}]$ → 输出 $\hat{\tau}_{link}$
- 在仿真中替代理想力矩模型 $\tau = a$
- 真机数据上监督学习训练
- **域随机化**：物理参数（质量、摩擦、弹簧刚度）+ 延迟随机化

## 与 WMTS 的关联

- **Actuator Network 经典范式**——WMTS Actuator Model 的直接理论源头
- **关键启示**：即使简单 MLP 也能有效捕捉电机非线性，说明 WMTS 的 Actuator Model 不需要过于复杂的架构
- **WMTS 扩展**：增加温度输入、触觉输入、反馈力矩输入，应对灵巧手更复杂的 actuator 链路
