---
tags:
  - WMTS
  - code-structure
  - server-sync
aliases:
  - WMTS Code Structure
date: 2026-04-27
related:
  - "[[Final_WMTS]]"
---

# WMTS 代码结构（本地/远端 Agent 共享上下文）

> [!important] 用途
> 本文件描述 WMTS 项目代码库结构与硬件约束，供本地 Agent 设计实验时确保可落地，供远端 Agent 找到正确文件实现实验。

---

## 1. 硬件约束

| 项目 | 规格 |
|------|------|
| 灵巧手 | LinkerHand L25 — 16 主动 DOF + 5 被动 DIP（PIP 耦合） |
| 总线 | CAN 1 Mbps，0.3 ms 帧间隔，2.5 ms 指间相位差 |
| 触觉 | 薄膜阵列 5 fingers × 12 × 6（uint8），360 字节/次 |
| 温度 | 16 × NTC 热敏电阻（°C） |
| 力矩 | 由 $K_t \cdot I_q$ 估算，**无独立 JTS** |
| 电机 | 空心杯 + 行星滚柱丝杠（Stribeck 摩擦显著） |
| 集群 | 8 × NVIDIA A100（80GB） |

详见 [[Actuator2RigidDynamicsModel_gap]] 与 [[FOC_Control]]。

---

## 2. 软件栈（推断结构，待用户确认）

```
wmts/
├── envs/
│   ├── isaac_gym/              # 仿真环境（Isaac Gym）
│   │   ├── linker_hand_env.py  # LinkerHand 21DoF 环境包装
│   │   ├── reorientation_task.py  # In-hand reorientation 任务
│   │   └── domain_randomization.py
│   └── real_robot/
│       ├── can_interface.py    # CAN 1Mbps 通信封装
│       ├── tactile_reader.py   # 触觉张量异步读取
│       └── safety_monitor.py   # 温度/电流/堵转监控
│
├── algos/
│   ├── oracle_ppo.py           # Oracle Specialist (PPO + privileged obs)
│   ├── diffusion_policy.py     # Generalist Diffusion (DiT-based)
│   ├── world_model/
│   │   ├── actuator_net.py     # f_act(a, φ, φ̇, τ_fb, T) → τ̂_link
│   │   ├── rigid_dyn_net.py    # f_dyn(s, τ̂_link, ξ̂_DR) → ŝ_{t+1}
│   │   ├── ensemble.py         # Probabilistic Ensemble
│   │   └── success_predictor.py
│   ├── task_generator/
│   │   ├── cvae.py             # 任务隐空间编解码
│   │   ├── cma_es.py           # 隐空间演化
│   │   └── risk_score.py       # 三重风险打分（见 Reliability Extensions）
│   └── safety_filter.py        # Look-ahead Safety Filter
│
├── encoders/
│   ├── pointnet.py             # 物体形状 → 100D
│   ├── tactile_cnn.py          # 触觉张量 → z_tactile
│   └── proprio_tcn.py          # 关节序列 → z_prop
│
├── configs/
│   ├── task/InHandReorient.yaml
│   ├── algo/PPO_Oracle.yaml
│   ├── algo/Diffusion_Generalist.yaml
│   ├── world_model/Ensemble.yaml
│   └── safety/SafetyFilter.yaml
│
├── scripts/
│   ├── train_oracle.py
│   ├── distill_generalist.py
│   ├── train_world_model.py
│   ├── deploy_real.py
│   └── eval/
│       ├── eval_drop_rate.py
│       └── eval_tracking_err.py
│
└── utils/
    ├── her_relabel.py
    ├── replay_buffer.py
    └── logger.py
```

> [!note] 实际目录待用户/服务器 Agent 在首次实验时校准。本地 Agent 设计实验时使用上述命名约定，服务器 Agent 在执行时若发现差异请同步更新本文件。

---

## 3. 关键技术约束（每个 Idea 必须遵守）

| 约束 | 含义 |
|------|------|
| **观测空间** | 仅可用 $\phi$（角度）、$\dot{\phi}$（速度，需滤波）、$\tau_{fb}$（仅 Actuator Model 输入）、tactile、$T_{motor}$、$O_{shape}$（仅 episode 起始） |
| **动作空间** | 关节目标位置增量 $\Delta\phi \in \mathbb{R}^{16}$，固定 PD 转换 |
| **力矩信号** | $\tau_{fb}$ **不可作为 reward 或 WM 预测目标**（reward hacking 风险） |
| **真机数据** | 极其昂贵；任何 Idea 的真机阶段必须 ≤ 1 小时实测 |
| **安全** | 真机部署必须经过 [[Final_WMTS#5.1 Look-ahead Safety Filter|Safety Filter]] |
| **训练框架** | PPO（rl_games / RSL-RL）+ Diffusion Policy（自实现 DiT） + Ensemble WM（自实现 PETS-style） |
| **GPU 预算** | 单实验 ≤ 1 周 × 8 A100，超过需拆 stage |

---

## 4. 当前已实现/待实现

| 模块 | 状态 |
|------|------|
| Oracle PPO | ✅ 已实现（基于 Isaac Gym + PPO） |
| Diffusion Generalist | 🟡 蒸馏框架待补全 HER 与异步 Worker-Learner |
| Ensemble World Model | 🟡 PETS 风格 ensemble 已搭，Actuator/Rigid 解耦未实现 |
| Latent Task Generator | 🔴 CVAE + CMA-ES 待实现 |
| Safety Filter | 🔴 仅有概念设计，未实现 LCB 计算 |
| Real Robot Stack | 🟡 CAN 接口 + 触觉异步读取已通，未集成 RL 推理回路 |

---

## 5. 与远端 Agent 的协作约定

1. 服务器 Agent 在 `MergeBuffer/all_Insights_server/_ExperimentResultsAll.md` 写入实验结果。
2. 服务器 Agent 若发现 Idea 中的代码路径与实际不符，应**先写入** `_ExperimentResultsAll.md` 的「执行偏差」节，由本地 Agent 同步后修正本文件。
3. 服务器 Agent 不得直接修改 `all_Insights_local/`（避免冲突）。
4. 任何涉及真机的实验，服务器 Agent 必须先在仿真完成 Stage 0 验证。
