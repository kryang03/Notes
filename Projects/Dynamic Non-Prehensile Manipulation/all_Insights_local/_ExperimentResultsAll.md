---
tags:
  - experiment-results
  - sync
  - DNPM
aliases:
  - Experiment Results
  - 实验结果汇总
created: 2026-02-28
updated: 2026-02-28
sync-direction: remote → local
---

# 🔄 Experiment Results All — 远端服务器实验结果汇总

> [!important] 同步说明
> 本文件是远端训练服务器 (8×A100) 与本地知识库之间的**核心数据桥梁**。
> - **远端 Agent 写入**：每次实验完成后，远端 Agent 在本文件中追加结果条目
> - **本地 Agent 读取**：每次会话开始时检查本文件，将新结果同步到对应 Idea 的「动态迭代日志」
> - **格式约束**：严格遵循下方模板，确保两端 Agent 均可正确解析

---

## 📖 远端 Agent 操作指南

> [!warning] 远端 Agent 必读
> 你正在一个与本地 Obsidian 知识库同步的文件夹中工作。以下是你需要了解的关键信息：

### 你所在的文件夹结构

```
all_Insights/
├── _InsightsIndex.md          ← 所有 Idea 的总索引（阅读此文件获取全局视角）
├── _ExperimentResultsAll.md   ← 【你写入结果的位置】本文件
├── CodeStructure.md           ← ★ 代码库结构文档（理解代码架构的核心参考）
├── Idea-001-Phase-Adaptive Impedance.md
├── Idea-002-Autoregressive Exploration.md
├── Idea-003-Causal Mediator Reward.md
├── Idea-004-Convex Safe Set Bootstrapping.md
├── Idea-005-Test-Time Contact Adaptation.md
├── Idea-006-Adaptive Lipschitz Actor.md
└── Idea-007-Dual Orthogonal Curriculum.md
```

### 你需要做什么

1. **运行实验前**：阅读目标 Idea 文件的「3.0 Stage 0: Grid Search」或「3.1 核心消融实验」节，获取实验参数
2. **运行实验时**：参考 `CodeStructure.md` 了解代码结构、配置路径、启动命令
3. **实验完成后**：在本文件末尾按模板追加结果条目
4. **关键原则**：
   - 每个实验一个条目，不要合并多个实验
   - 记录所有定量指标（success rate、reward、training steps）
   - 记录你对结果的分析和对 Idea 假设的判断
   - 标注实验的 GPU 配置和运行时长，便于资源规划

### CodeStructure 快速参考

- **训练入口**: `python train.py` (Hydra 驱动)
- **核心环境**: `penspin/tasks/linker_hand_hora.py`
- **PPO 算法**: `penspin/algo/ppo/ppo_rl_teacher.py`
- **TWC 课程**: `penspin/utils/time_warping.py`
- **配置文件**: `configs/task/LinkerHandHora.yaml` + `configs/train/LinkerHandHora.yaml`
- **实验框架**: `experiments/` 目录（含 GPU 调度器和监控工具）
- **指标解析**: 训练输出 `[METRICS] step=X reward=Y success_rate=Z best_reward=W alpha=A`

### Idea 快速索引（实验参数位置）

| Idea | 核心实验参数位置 | 关键配置变量 |
|------|----------------|------------|
| 001 PAI | §3.0 Stage 0: Kp Grid | `task.env.controller.pgain` |
| 002 CA-ARP | §3.0 Stage 0: β Grid | 需新增 AR 噪声模块 |
| 003 CMR | §3.0 Stage 0: 手工 mediator reward | `task.env.reward.*` |
| 004 CSS | §3.0 Stage 0: δ 初始化 Grid | 初始状态分布参数 |
| 005 TTCA | §3.0 Stage 0: Oracle 参数输入 | `priv_info` 维度 |
| 006 ALA | §3.0 Stage 0: 全局 K Lipschitz | 网络架构修改 |
| 007 DOC | §3.0 Stage 0: δ 初始化混合 | `task.env.curriculum.*` |

---

## 📝 结果记录模板

> [!tip] 复制以下模板追加到本文件末尾

```markdown
---

## [EXP-YYYY-MM-DD-NNN] 实验标题

- **关联 Idea**: Idea-00X (<Idea 名称>)
- **Stage**: Stage 0 / Stage 0.5 / Stage 1
- **实验类型**: Grid Search / Ablation / Baseline 对比 / 完整算法
- **GPU 配置**: N × A100
- **训练步数**: X M steps
- **运行时长**: X hours
- **运行脚本/命令**:
  ```bash
  <完整的训练启动命令>
  ```

### 实验参数

| 参数 | 值 |
|------|------|
| ... | ... |

### 核心结果

| Config | Success Rate | Best Reward | Final Reward | Alpha 进度 | 备注 |
|--------|-------------|-------------|-------------|-----------|------|
| ... | ... | ... | ... | ... | ... |

### 训练曲线关键观察

- <描述 reward 曲线、success rate 曲线的关键特征>
- <是否有训练不稳定/崩溃/plateau 现象>

### 关键发现

1. **发现 1**: ...
2. **发现 2**: ...

### 对 Idea 假设的验证

- **核心假设**: <从 Idea 文档中提取的核心假设>
- **验证结果**: [✅ 成立 / ❌ 不成立 / ⚠️ 部分成立]
- **证据**: ...

### 下一步建议

- [ ] ...
- [ ] ...
```

---

## 📊 实验结果条目

> 以下为远端 Agent 按时间顺序追加的实验结果。
> 本地 Agent 读取后会将关键信息同步至对应 Idea 的「动态迭代日志」节。

---

## [EXP-2026-02-27-001] Smoke Test — 8卡并行验证

- **关联 Idea**: 全部 (基础设施验证)
- **Stage**: 预备
- **实验类型**: 基础设施验证
- **GPU 配置**: 8 × A100
- **训练步数**: 1M steps (每 run)
- **运行时长**: ~2 min/run

### 核心结果

| 测试名 | 状态 | 耗时(s) | GPU |
|--------|------|---------|-----|
| exp1_ta_twc_kp12_kd0.3_as0.7 | ✅ PASS | 128 | 0 |
| exp1_tp_twc_kp12_kd0.2_as1.0 | ✅ PASS | 132 | 1 |
| exp2_ta_heavy_twc | ✅ PASS | 130 | 2 |
| exp2_ta_light_twc | ✅ PASS | 133 | 3 |
| exp3a_ta_alpha0.5 | ✅ PASS | 133 | 4 |
| exp3b_tp_cfc_dec5 | ✅ PASS | 131 | 5 |
| exp1_ta_base_kp12_kd0.3 | ✅ PASS | 135 | 6 |
| gpu_sched_test_tp_gpu7 | ✅ PASS | 133 | 7 |

### 关键发现
- 8/8 全部通过，确认 8 卡并行调度正常，所有配置可正确解析

---

## [EXP-2026-02-27-002] Exp2 TA 奖励参数搜索 (Heavy/Medium/Light/Reduced × BASE/TWC)

- **关联 Idea**: Idea-003 (CMR), Idea-006 (ALA)
- **Stage**: 前置实验 (奖励基线建立)
- **实验类型**: Grid Search (奖励配置 × 方法)
- **GPU 配置**: 8 × A100
- **训练步数**: 300M steps
- **运行时长**: ~24h (总共 24 runs, 3 seeds × 4 configs × 2 methods)

### 实验参数

| 参数 | 值 |
|------|------|
| Kp | 12 |
| Kd | 0.3 |
| AS | 0.6 |
| numEnvs | 8192 |
| Seeds | 42, 123, 456 |
| 奖励配置 | Heavy (6 shaping), Medium (4), Light (3), Reduced (2) |

### 核心结果

| 奖励配置 | 方法 | SR (mean±std) | Best Reward | 最终 α | 关键观察 |
|---------|------|--------------|-------------|--------|---------|
| Heavy | BASE | 0.000±0.000 | 24.08 | 1.00 | 完全无法学习 |
| Heavy | TWC | 0.000±0.000 | 34.16 | 0.50 | 完全无法学习，α 卡 0.5 |
| Medium | BASE | 0.040±0.023 | 1181.43 | 1.00 | 勉强可探索但 SR 极低 |
| Medium | TWC | 0.060±0.001 | 1509.18 | 0.50 | SR 略高于 BASE |
| **Light** | **BASE** | **0.825±0.040** | **293.11** | 1.00 | ⚡ **最高 SR！BASE > TWC** |
| Light | TWC | 0.723±0.153 | 284.41 | 0.98 | SR 低于 BASE |
| **Reduced** | **BASE** | **0.789±0.083** | **413.34** | 1.00 | ⚡ SR 仅次于 Light |
| Reduced | TWC | 0.135±0.187 | 80.37 | 0.50 | TWC 极差, 2/3 seeds 失败 |

### 关键发现
1. ⚡ **Light/Reduced 奖励下 BASE 显著优于 TWC** — 与预期完全相反
2. ⚡ **Heavy 奖励完全无法训练** — 过多 shaping reward 导致 reward hacking plateau
3. Medium TWC 略优于 BASE 但两者 SR 都极低 (<7%)
4. TWC 在 TA 任务下 α 推进能力有限: Heavy/Medium/Reduced 配置下 α 均卡在 0.50

### 对 Idea 假设的验证
- **Idea-003 (CMR)**: ⚠️ 部分成立 — Heavy 失败证明"需因果链而非堆砌奖励"，但 Light 成功说明简洁奖励已足够好，CMR 需在此基线上证明增益
- **Idea-006 (ALA)**: ⚠️ 部分成立 — Heavy 失败可能包含 reward hacking 的快速抨动机制，ALA 可作为对抗手段测试

---

## [EXP-2026-02-28-003] Exp2 TP 奖励参数搜索 (Heavy/Medium/Light/Reduced × BASE/TWC)

- **关联 Idea**: Idea-001 (PAI), Idea-007 (DOC)
- **Stage**: 前置实验 (奖励基线建立)
- **实验类型**: Grid Search (奖励配置 × 方法)
- **GPU 配置**: 8 × A100
- **训练步数**: 300M steps
- **运行时长**: ~24h (24 runs)

### 实验参数

| 参数 | 值 |
|------|------|
| Kp | 12 |
| Kd | 0.2 |
| AS | 0.8 |
| numEnvs | 8192 |
| Seeds | 42, 123, 456 |

### 核心结果

| 奖励配置 | 方法 | SR (mean±std) | Best Reward | 最终 α | 关键观察 |
|---------|------|--------------|-------------|--------|---------|
| Heavy | BASE | 0.000±0.000 | 19.49 | 1.00 | 完全无法学习 |
| Heavy | TWC | 0.182±0.258 | 208.08 | 0.56 | 1/3 seed 成功 (s123 SR=0.54) |
| Medium | BASE | 0.000±0.000 | 374.86 | 1.00 | 完全无法学习 |
| **Medium** | **TWC** | **0.856±0.022** | **1337.98** | 1.00 | ⚡ **TWC 最高 SR, α→1.0** |
| Light | BASE | 0.864±0.021 | 596.11 | 1.00 | SR 最高但 reward 低 |
| Light | TWC | 0.803±0.007 | 528.23 | 1.00 | SR 略低于 BASE |
| Reduced | BASE | 0.536±0.384 | 63.11 | 1.00 | 方差极大 (1/3 seed 失败) |
| Reduced | TWC | 0.870±0.020 | 145.28 | 1.00 | TWC 稳定优于 BASE |

### 关键发现
1. ⚡ **TP Medium TWC 是最佳配置**: SR=0.856, reward=1338, α→1.0, TWC 展现决定性优势
2. ⚡ **TP Heavy 下 TWC 部分成功**: 1/3 概率 SR=0.54, BASE 完全失败
3. TP Light 下 BASE 略优于 TWC (与 TA 类似)
4. **TP Reduced TWC 极稳定**: SR=0.87±0.02 vs BASE SR=0.54±0.38, 方差降 19×

### 对 Idea 假设的验证
- **Idea-001 (PAI)**: ⚠️ 需重新评估 — Kp=12 在 TP Medium TWC 中已获 SR=0.86, PAI 需证明时变 Kp 在此高基线上仍有增益
- **Idea-007 (DOC)**: ✅ 部分成立 — TWC 在 TP Reduced 上方差降 19×, 物理轴课程确实平滑了 Value Landscape; 但 TA 上 TWC 优势有限, 说明状态轴课程对 TA 更关键

---

## [EXP-2026-01-XXX] 历史 Kp×AS 网格搜索 (TP 任务)

- **关联 Idea**: Idea-001 (PAI)
- **Stage**: 历史前置数据
- **实验类型**: Grid Search (Kp × AS)
- **GPU 配置**: 1~8 × A100 (分批进行)
- **训练步数**: 不等

### 核心结果

| Kp 范围 | AS | 方法 | 最佳 SR | 最佳 Kp |
|---------|-----|------|---------|---------|
| 1.0~9.0 | 1.0 | BASE | 0.277 | 8.5 |
| 3.5~6.5 | 1.0~1.05 | TWC+BASE | 0.234 | 3.5 TWC |
| 16.0 | 1.05 | TWC | 0.0002 | — (失败) |

### 关键发现
1. ⚡ **TP 最优 Kp 在低区**: Kp=3.5~8.5 时 SR 最高, Kp>12 后急剧下降
2. Kd 未作为独立维度搜索, AS 覆盖范围窄

---

## [EXP-2026-02-28-004] Exp3a: Alpha 直接训练 (🔄 运行中)

- **关联 Idea**: Idea-007 (DOC), Idea-001 (PAI)
- **Stage**: 前置实验 (α-SR 曲线)
- **实验类型**: α 消融
- **GPU 配置**: 8 × A100
- **训练步数**: 300M steps × 16 runs
- **状态**: 🔄 运行中 (启动 2026-02-28 09:28)

### 实验参数

| 参数 | 值 |
|------|------|
| α 值 | {0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0} |
| 任务 | TA + TP |
| curriculum_enabled | False (固定 α) |

### 预期产出
- SR vs α 完整曲线 (TA + TP 各 8 点)
- 直接展示 Value Landscape 随 α 的变化趋势
- 为 DOC 物理轴课程提供量化基线
