---
tags:
  - WMTS
  - experiment-results
  - server-sync
aliases:
  - WMTS 实验结果汇总
date: 2026-04-27
related:
  - "[[Final_WMTS]]"
  - "[[_InsightsIndex]]"
---

# WMTS 实验结果汇总（远端服务器双向同步）

> [!important] 同步协议
> 本文件由 **远端服务器 Agent (8×A100)** 写入实验结果，由 **本地 Agent** 读取并合并到对应 Idea 的 §6 迭代日志。
>
> **写入格式**：参见下方「实验结果条目模板」。每个条目以 `[EXP-YYYYMMDD-NNN]` 唯一标识。
> **同步路径**：远端 → `MergeBuffer/all_Insights_server/_ExperimentResultsAll.md` → 本地合并 → 删除 MergeBuffer 内容。

---

## 状态追踪

| 状态 | 数量 |
|------|------|
| 待运行实验 | 0 |
| 已完成实验 | 0 |
| 失败/废弃实验 | 0 |

---

## 实验结果条目（按时间倒序）

> *暂无实验结果。本地 Agent 已完成首批 Idea 的 Stage 0 实验计划设计，等待远端 Agent 拉取执行。*

---

## 实验结果条目模板（远端 Agent 写入参考）

```markdown
## [EXP-YYYYMMDD-NNN] <实验标题>

- **关联 Idea**: Idea-00X
- **Stage**: Stage 0 / Stage 0.5 / Stage 1
- **实验类型**: Grid Search / Ablation / Baseline 对比
- **GPU 配置**: N × A100
- **训练步数**: X M steps
- **运行时长**: X hours
- **代码 commit**: <git hash>

### 实验参数
| 参数 | 值 |
|------|----|
| ... | ... |

### 核心结果
| Config | Success Rate | Reward | Drop Rate | Tracking Error | 备注 |
|--------|-------------|--------|-----------|----------------|------|
| ... | ... | ... | ... | ... | ... |

### 关键发现
- 发现 1: ...
- 发现 2: ...

### 对 Idea 的影响
- 假设验证: [成立/不成立/部分成立]
- 下一步建议: ...
```
