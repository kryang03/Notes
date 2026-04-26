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

## 颗粒度补强：Actuator Network 的可迁移边界

### 数学定义

ANYmal 的 actuator net 学习低层闭环从 joint target 到 torque 的映射：

$$
\hat{\tau}_t=f_{act}(a_{t-H:t},q_{t-H:t},\dot{q}_{t-H:t};\theta),\quad \mathcal{L}_{act}=\|\tau_t^{real}-\hat{\tau}_t\|_2^2.
$$

它把通信延迟、SEA 顺应性、低层控制器带宽、摩擦与 torque sensing 偏差都压缩进历史窗口。论文中 actuator net 为 3 hidden layers、每层 32 units 的 MLP，平均 torque prediction error 约 0.740 Nm。

### 精简代码逻辑

```python
act_hist = torch.cat([target_hist, q_hist, qd_hist], dim=-1)
tau_hat = actuator_net(act_hist)        # replaces ideal tau in simulator
q_next, qd_next = rigid_body_step(q, qd, tau_hat)
reward = track_velocity(q_next, command) - energy_cost(tau_hat)
ppo_update(policy, reward)
```

### Ablation 因果链

| 设计选择 | 现象 | 机制 |
|---|---|---|
| 解析 actuator model | 真机 torque 误差大 | 多源延迟与 SEA 顺应性很难精确建模 |
| learned actuator net | sim-to-real 明显稳定 | 学到的是 host-command 到 joint-torque 的端到端闭环映射 |
| 不做 dynamics randomization | 对参数漂移脆弱 | actuator net 修局部 gap，但质量/摩擦/地面差异仍需随机化覆盖 |

### WMTS 迁移

灵巧手中的 actuator model 不能只预测 $\tau$，还应输出 feasibility score：

$$
\rho_t=\frac{\|\hat{\tau}_{link,t}\|}{\|\tau_{cmd,t}\|+\epsilon},\quad u_t^{act}=\mathrm{Var}_{m}(f_{act}^{m}(x_{act,t})).
$$

$\rho_t$ 低说明温度/反电动势/丝杠摩擦导致命令无法落地；$u_t^{act}$ 高说明执行器模型认知不确定，应触发 WMTS 降级任务。
