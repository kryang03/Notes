---
tags:
  - WMTS
  - insights-index
  - real-robot-rl
aliases:
  - WMTS Insights Index
date: 2026-04-27
related:
  - "[[Final_WMTS]]"
  - "[[WMTS_Reliability_Extensions]]"
  - "[[CodeStructure]]"
  - "[[_ExperimentResultsAll]]"
---

# WMTS Insights Index — Real-Robot RL Brainstorm Round 1 (15 Ideas)

> [!abstract] 核心定位
> 本批 Idea 全部围绕 **真机灵巧手强化学习 (Real-Robot RL on LinkerHand L25)** 的开放问题展开，与 [[Final_WMTS|五模块主架构]] 和 [[WMTS_Reliability_Extensions|可靠性扩展层]] 互补。三大主线：
>
> 1. **真机 reward / data efficiency** — Idea-001/008/011（无 GT pose、PER、IS 加权）
> 2. **Sim-to-Real gap 的物理诊断与修复** — Idea-002/003/007/010/012/013/014（actuator/contact/tactile/EBM/stick-slip/gradient DR）
> 3. **真机自主与 test-time 适应** — Idea-004/005/006/009/015（test-time guidance、active exploration、ICL、discrete tokens、reset-free）

---

## 总览（按优先级）

| ID | 标题 | 主线 | Feasibility | Novelty | 优先级 | HDC 关系 |
|----|------|------|:-:|:-:|:-:|------|
| [[Idea-001-Tactile-Anchored-Reward\|Idea-001]] | Tactile-Anchored Reward for Pose-Free Real-Robot RL | reward | A | A | **P0** | 互补（解锁真机闭环） |
| [[Idea-002-Latency-Aware-Actuator\|Idea-002]] | CAN-Latency-Conditioned Actuator Network | sim2real | A | A | **P0** | 直接增强 §4.A |
| [[Idea-003-Failure-Mode-Curriculum\|Idea-003]] | Real-Robot Failure-Mode Clustering for Curriculum | sim2real | A | A | **P0** | 增强 §一 调度 |
| [[Idea-004-WM-Guided-Diffusion\|Idea-004]] | WM-Guided Diffusion Refinement at Test-Time | test-time | A | A | **P0** | 升级 §5.1 |
| [[Idea-005-Saturation-Boundary-Active-Learning\|Idea-005]] | Active Real-Robot Data Collection at Actuator Boundary | data-eff | A | A | **P1** | 与 §一 Probe Queue 联动 |
| [[Idea-006-In-Context-Hypernet-Adapter\|Idea-006]] | In-Context Hypernet Adapter (zero-grad adapt) | autonomy | B | A | P1 | 长期方向 |
| [[Idea-007-Implicit-Explicit-Contact-WM\|Idea-007]] | Implicit-Explicit Contact World Model | sim2real | B | A | P1 | 重构 §4.B |
| [[Idea-008-Physics-Aware-PER\|Idea-008]] | Physics-Aware PER for WM Updates | data-eff | A | B | **P0** | 工具型增强 |
| [[Idea-009-Discrete-Task-Tokens\|Idea-009]] | VQ-Discrete Task Tokens for Replan Safety | autonomy | B | A | P2 | 替换 §一 |
| [[Idea-010-EBM-Mode-Mismatch\|Idea-010]] | Energy-Based Sim-to-Real Mode Mismatch Detector | sim2real | A | A | P1 | 调度其它 idea 触发 |
| [[Idea-011-WM-Importance-Weighted-Diffusion\|Idea-011]] | WM-IS-Weighted Off-Policy Diffusion RL | data-eff | B | A | P1 | 统一 §5.4 两选项 |
| [[Idea-012-WPTE-Tactile-Encoder\|Idea-012]] | WM-Pretext Tactile Encoder | sim2real | A | B | **P0** | 提供 z_tactile |
| [[Idea-013-Stick-Slip-Mode-Switching\|Idea-013]] | WM-Triggered Stick-Slip Mode Policy Switching | sim2real | A | A | P1 | 增强真机 robustness |
| [[Idea-014-WM-Gradient-Adaptive-DR\|Idea-014]] | WM-Gradient-Driven Adaptive DR | sim2real | A | A | P1 | 替代 ADR baseline |
| [[Idea-015-Reset-Free-Autonomy\|Idea-015]] | Reset-Free Real-Robot WMTS via Recovery Policy | autonomy | B | A | **P0** | 基础设施 |

---

## P0 推荐立即启动（4 个核心 + 1 基础设施）

| # | Idea | 一句话价值 |
|---|------|------------|
| 1 | [[Idea-015-Reset-Free-Autonomy\|Idea-015 Reset-Free]] | **基础设施**：没有它其它真机 idea 都难规模化 |
| 2 | [[Idea-001-Tactile-Anchored-Reward\|Idea-001 TAR]] | 解锁真机 RL 闭环（无 GT pose） |
| 3 | [[Idea-002-Latency-Aware-Actuator\|Idea-002 LAAA]] | 解决 Actuator sim-to-real 最大已知 gap |
| 4 | [[Idea-008-Physics-Aware-PER\|Idea-008 PA-PER]] | 极简工程改动，立刻提升数据效率 |
| 5 | [[Idea-012-WPTE-Tactile-Encoder\|Idea-012 WPTE]] | sim 训练即可零样本迁移触觉 |

> [!tip] 推荐组合论文方向
> **Paper A (RSS/CoRL)**: TAR + Reset-Free + WPTE → "Pose-Free, Reset-Free Real-Robot RL for In-Hand Reorientation" — 完整真机 RL 系统论文。
>
> **Paper B (ICRA/RSS)**: LAAA + PA-PER + WG-Adaptive-DR → "Physics-Informed Sim-to-Real for Dexterous Hands" — 方法论侧重。
>
> **Paper C (NeurIPS/CoRL)**: WM-Guided Diffusion + WMID → "World-Model-Calibrated Diffusion Policies for Safe Real-Robot Learning" — 算法侧重。

---

## 三大主线交叉矩阵

```
                  reward   sim2real   autonomy
Idea-001 (TAR)      ★★★      ★         ★
Idea-002 (LAAA)              ★★★       
Idea-003 (FMC)               ★★★       ★
Idea-004 (WGDR)              ★         ★★
Idea-005 (SBAL)     ★        ★★        
Idea-006 (ICHA)              ★         ★★★
Idea-007 (IECW)              ★★★       
Idea-008 (PA-PER)   ★        ★         
Idea-009 (DTT)               ★         ★★
Idea-010 (EBM)               ★★        ★★
Idea-011 (WMID)     ★★       ★         
Idea-012 (WPTE)              ★★★       
Idea-013 (SSMS)              ★★        ★
Idea-014 (WG-ADR)            ★★★       
Idea-015 (Reset-Free)                  ★★★
```

---

## 与现有架构的关系图

```
                   [Final_WMTS 五模块]
                          │
                          ├─ §一 Latent Task Generator
                          │     ├─ Idea-003 失败模式驱动课程
                          │     ├─ Idea-009 离散 token 替换
                          │     └─ Idea-014 WM-gradient 调 DR 范围
                          │
                          ├─ §二 Oracle (PPO + privileged)
                          │     └─ Idea-013 双子策略 (slow/burst)
                          │
                          ├─ §三 Generalist Diffusion
                          │     ├─ Idea-004 test-time guidance
                          │     ├─ Idea-006 zero-grad ICL adapt
                          │     └─ Idea-011 WM-IS-weighted off-policy
                          │
                          ├─ §四 Ensemble World Model
                          │     ├─ Idea-002 latency FiLM Actuator
                          │     ├─ Idea-007 implicit-explicit contact
                          │     ├─ Idea-008 PA-PER for WM updates
                          │     └─ Idea-012 WPTE tactile encoder
                          │
                          └─ §五 真机闭环
                                ├─ Idea-001 TAR reward
                                ├─ Idea-005 SBSP active collection
                                ├─ Idea-010 EBM mismatch trigger
                                └─ Idea-015 reset-free autonomy
                                
[WMTS_Reliability_Extensions] — 与本批 Idea 并行的另一条线
```

---

## 实验资源汇总（8 × A100 假设）

| Stage | 总 GPU-days | 真机 hours | 所有 Idea 累积 |
|-------|------------|-----------|----------------|
| Stage 0 (各 idea Grid Search) | ~30 | 0 | 全部并行可在 2 周内完成 |
| Stage 1 (仿真闭环验证) | ~20 | 0 | 选出 P0 后 1 周完成 |
| Stage 2 (真机) | <5 | ~10 | 优先 Idea-015 → Idea-001 → Idea-002 |

---

## 状态追踪

| 日期 | 事件 |
|------|------|
| 2026-04-27 | 首批 15 ideas 生成完成，等待远端 Agent 拉取 Stage 0 实验 |
| 2026-06-16 | 新增 [[Rationale-Planner-Follower-Task-Definition]]——任务定义的 RL 理论依据（为何 goal-conditioning 必致 mode collapse → Planner-Follower），萃取自 ViserDex 对话 Turn 2-3，给 [[auto_taskgen]] 的 receding-horizon 设计补"why"。 |

> [!important] 远端协作
> 远端服务器 Agent 拉取本目录到 `all_Insights_server/` 后，应优先执行 **Idea-001 / 002 / 008 / 012 / 015** 的 Stage 0 Grid Search，结果写回 [[_ExperimentResultsAll]]。
