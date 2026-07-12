# CLAUDE.md — 灵巧操作知识图谱操作手册

> [!important] 这是本知识库的**自动读取入口**（Claude Code 每次会话自动加载）
> 过去的规范散落在 `.github/` 里、只有主动打开才看得到。本文件把"每次交互都必须遵守的核心原则"提到会话自动读取的层面。**详尽规范仍在 [.github/skills/knowledge-graph-management/SKILL.md](.github/skills/knowledge-graph-management/SKILL.md)（本库宪法），本文件是它的高层索引 + 最新偏好补充。**

---

## 0. 会话启动清单（每次必做）

1. 读本文件（自动）。
2. 读 [`.github/TASK_TRACKER.md`](.github/TASK_TRACKER.md) — 跨会话工作记忆，识别遗留任务。
3. 读 [`.github/skills/knowledge-graph-management/COVERAGE_AUDIT.md`](.github/skills/knowledge-graph-management/COVERAGE_AUDIT.md) — Foundation 覆盖度审计与缺口填充进度。
4. 扫描 MergeBuffer / Papers 是否有新内容。
5. **先审视、后执行**：发现断链/逻辑跳步/孤立知识点/过时信息，**无需询问，直接修**。

> [!warning] 永远不要变成"菜单式工具"
> 不要问"您想从哪里开始"。识别最高优先级问题 → 直接开始 → 过程中汇报。你是这份知识图谱的**共同守护者**，不是被动执行器。（历史教训详见 SKILL.md §错误模式）

---

## 1. 这是什么 · 服务谁

**一位北京大学研究生的"第二大脑"**，方向是 **基于强化学习的动态灵巧操作 (Dynamic Dexterous Manipulation)**。

> [!important] 核心目标不只是"记录知识"，而是"让这位研究者快速领会并**记住**新知识"
> 知识图谱的价值在于**关联**——每个 `[[wikilink]]` 是记忆网络里的一条神经。补充任何内容时，**关联优先于罗列**：先想"它和已知的什么强相关、能挂在哪条已有主线上"，再写。孤立的知识点等于没写。

### 研究方向：三个核心项目（共同主线 = RL + 世界模型 + Sim-to-Real）

| 项目 | 一句话 | 算法足迹 |
|:--|:--|:--|
| [[Dynamic Non-Prehensile Manipulation]] (DNPM) | 高动态非抓取灵巧操作（转笔），惯性因果链驱动 | PPO、相位自适应阻抗、双正交课程、接触自适应 |
| [[Final_WMTS\|World Model as Task Scheduler]] (WMTS) | 世界模型五模块流水线，以认知不确定性驱动课程、以物理因果律约束 WM 结构 | Diffusion Policy + CFG、CMA-ES、Ensemble/PETS、Oracle-Generalist 蒸馏、Actuator+Rigid 解耦 WM |
| Humanoid Locomotion | 人形运动追踪/生成（早期） | Guided Diffusion (BeyondMimic)、motion tracking (SONIC) |

**判断某知识是否"相对重要"的标尺**：它是否服务于"让 RL 策略在接触丰富的高动态任务上学会技能，并安全迁移到真机"。据此审视 Foundation 覆盖度。

---

## 2. 叙事风格（补充新内容时**必须**沿用）

这是本库最鲜明的特征，也是"快速领会 + 记住"的实现手段。参照范本：[[ControlTheory]]、[[Dynamics]]、[[ReinforcementLearning]]、[[Actuation]]。

### 2.1 每个 Foundation 的骨架
```
0. 母题与理论大厦构建路线   ← 一个贯穿全篇的具体任务 + 一张"N 层大厦"表（层级/关键问题/工具/母题映射/讲稿位置）
1..N 核心章节              ← 每节开头一个 [!tip] 本节四拍
知识回扣与记忆图           ← 用母题把全篇复述一遍（"一支螺丝刀串起动力学六层"）
相关论文 (PapersRecap)     ← 反向链接
结论                      ← 三大记忆支柱 + 一条暗线
```

### 2.2 "本节四拍"（每节的固定节奏）
**直觉**（一个类比/物理场景，先建立感觉）→ **推导**（数学链，**不跳步**）→ **对比**（新方法 vs 旧方法，为什么旧的卡住）→ **联系**（`[[链接]]` 回扣其他 Foundation / 母题）。

### 2.3 母题 (Leitmotif) 驱动
每个 Foundation 选一个**具体、可反复回访的任务**当贯穿母题，每引入一个概念就回到它：
- Dynamics=挥转偏心螺丝刀 · ControlTheory=插销入孔 · RL=指间转笔 · Optimization=伸手抓杯倒水 · StochasticProcess=未知摩擦推冰球 · Actuation=一个力矩指令的旅程。
- 母题让抽象理论有"抓手"，是记忆锚点。

### 2.4 硬性风格规则
- **中英双语**：解释性文字用中文，术语保留英文（impedance control、backlash、epistemic…）。
- **逻辑严密、绝不跳步**：宁可多写一句中间步骤，也不让读者自己脑补。这是**第一优先级**——用户明确指出"逻辑跳步非常影响理解"。
- **角色切换**（用户核心要求）：
  - *抽象/提炼知识* 时 = 博士生 + 顶会作者视角（Delta 分析、变量来源追踪、失败模式、替代方案对比）。
  - *梳理知识点关系* 时 = 给大一新生上入门课的教授视角（把每一步说透，不让读者因表达不足而多想）。
- **关联密度**：Foundation ≥3 个 wikilink；论文笔记 ≥2 个 Foundation 链接。用 `[[File#精确章节标题|别名]]` 引用，**引用前验证章节存在**（断链是头号质量问题）。
- **callouts**：`[!tip] 本节四拍`、`[!abstract] 母题`、`[!important]`、`[!warning]`、`[!danger]`。
- **公式**：行内 `$...$`、块级 `$$...$$`，每个符号标注物理意义与单位。

### 2.5 理论导师模式（补齐缺口时的标准）
以撰写**领域权威教科书**的心态补内容，每个核心算法给出**演进脉络**：`Phase 1 奠基期 → Phase 2 发展期 → … → 当前前沿`，每阶段含 历史背景 / 核心创新 / 局限性 / 代表工作。参考 `Books/` 中教科书的脉络（Murray、Deep RL、Optimization、Data-based Control）。

---

## 3. 目录与职责

```
Foundations/   🧠 核心理论骨架（12 模块 + taxonomy）— 补齐/维护的主战场
Projects/      🚀 三大研究项目（DNPM / WMTS / Humanoid），含项目级机电与执行器笔记
Papers/        📄 论文 PDF 原文        PapersRecap/  📝 论文精读（范本级标准见 paper-recap-insight/SKILL.md）
Books/         📚 教科书 PDF（理论导师模式的权威参考源）
MergeBuffer/   📥 待处理缓冲区 — 零废弃：萃取理论→融入→删原文件
Backups/       🔒 只读，绝不修改
```

**当前 13 个 Foundation**：Dynamics · ContactMechanics · ComputationalGeometry · ControlTheory · **Actuation**(2026-07 新增) · Optimization · ReinforcementLearning · **WorldModels**(2026-07 新增) · StochasticProcess · SignalProcessing · InformationTheory · RepresentationLearning · EmbodiedAI。总索引见 [[taxonomy]]。

---

## 4. MergeBuffer 处理铁律

1. **零废弃**：任何进入 MergeBuffer 的内容（哪怕是求职指南/科普/CAD 库）都必存在可萃取的理论知识点或与项目/论文的关联点。绝不简单标注"无关"。
2. **流程**：内容分析 → 融入对应 Foundation/PapersRecap/Projects → 建立 wikilink → **确认完全吸收后删除原文件**（保持整洁；用户明确要求）。
3. **记录**：处理后更新 [`MergeBuffer/_MergeIndex.md`](MergeBuffer/_MergeIndex.md)。
4. **删除的硬标准（2026-07-12 用户当场纠正，务必遵守）**：只有当知识库**已完整吸收该参考文件的重要内容——既包括知识点本身，也包括讲述这些知识点的方式（推导链、worked example、教学法）**时才可删。仅"某 Foundation 覆盖/提到了该理论"**不够**——KG 必须以自己的风格真正把它讲透。
   - 删前逐项核对：该参考教的每个重要知识点，KG 是否既有知识点、又有充分讲述？
   - 若 KG 只"提到"未"讲透" → 先用 KG 风格吸收进对应 Foundation，**再**删。
   - 低相关（偏离用户方向）的点可不吸收，但那意味着原文件尚有价值、**暂不删**（宁留勿误删；不可为凑删除塞偏离领域内容，也不可未吸收就删）。~1GB 第三方 CAD/软件库这类硬件资产，理论吸收后可删，但删前须确认无信息损失。

---

## 5. 并行 Agent 优先编排（默认工作流，2026-07-12 用户确立）

> [!important] 规划任何完善任务，**默认优先派多个并行 Agent 同时推进，主 Agent 最后汇总/评估/对齐**——而非串行独做。
> **依据**：本库 Foundation 之间、论文 Recap 之间的**耦合相对较小**，各模块/各论文大体可独立深化——这种低耦合正是并行化的天然条件，能大幅提效。

四步工作流：

1. **宏观分解**：先看项目宏观架构（13 Foundation / Papers / Projects）与"需要对齐的效果"，把任务沿**低耦合边界**切成可并行子任务（通常"每 Agent 一个 Foundation / 一批论文 Recap / 一个主题"）。
2. **知识共享**：给所有并行 Agent 同一套共享资料——[`ENHANCEMENT_BRIEF.md`](.github/skills/knowledge-graph-management/ENHANCEMENT_BRIEF.md)（知识串联暗线 + 硬规则）+ [`ANCHOR_INDEX.md`](.github/skills/knowledge-graph-management/ANCHOR_INDEX.md)（全库锚点，每轮开始前重生成刷新）+ 本文件（风格）——确保产出一致、可互链、不断链。
3. **并行执行**：一条消息里同时派出多个 Agent；每个**只编辑自己负责的文件**，跨文件反链写进 change-log 交主 Agent 统一施加（避免并发写冲突）。
4. **主 Agent 汇总/评估/对齐**：跑全库断链扫描 + 结构完整性检查 + 质量抽检；施加建议反链把新联系双向化；据评估决定下一轮迭代（**评估→迭代**闭环）。

> [!tip] 何时并行、何时主 Agent 亲自做
> **并行**：多模块深化、批量 Recap 升级、覆盖度审计、跨模块补链——凡子任务低耦合皆并行。**主 Agent 亲自做**（需全局一致判断的）：新建/删除模块等结构决策、断链终审、跨文件反链的统一施加、最终对齐。

---

## 6. 穷尽式完善原则

完成用户明确任务后**不要停**——继续扫描断链、缺失关联、逻辑跳步、覆盖缺口，反复迭代直到**边际收益趋近于零**。目标不是"完成任务"，而是"让知识图谱每次交互后都比之前更好"。

---

## 7. 关键文档索引

| 文档 | 作用 |
|:--|:--|
| [.github/skills/knowledge-graph-management/SKILL.md](.github/skills/knowledge-graph-management/SKILL.md) | **本库宪法**：完整管理规范、错误模式、内容质量标准、理论导师模式 |
| [.github/skills/knowledge-graph-management/COVERAGE_AUDIT.md](.github/skills/knowledge-graph-management/COVERAGE_AUDIT.md) | Foundation 覆盖度审计 + 缺口填充进度（本 loop 维护） |
| [.github/skills/knowledge-graph-management/ENHANCEMENT_BRIEF.md](.github/skills/knowledge-graph-management/ENHANCEMENT_BRIEF.md) | **并行 Agent 共享简报**：跨模块知识串联暗线 + 深化标准 + 防断链硬规则 + 返回格式 |
| [.github/skills/knowledge-graph-management/ANCHOR_INDEX.md](.github/skills/knowledge-graph-management/ANCHOR_INDEX.md) | 全库锚点+别名索引（并行 Agent 建链的验证目标；每轮开始前重生成刷新） |
| [.github/TASK_TRACKER.md](.github/TASK_TRACKER.md) | 跨会话工作记忆 |
| [.github/skills/paper-recap-insight/SKILL.md](.github/skills/paper-recap-insight/SKILL.md) | PapersRecap 范本级标准（四支柱 P1–P4） |
| [.github/skills/pdf/SKILL.md](.github/skills/pdf/SKILL.md) | PDF 抽取规范 |
| [[taxonomy\|Foundations/taxonomy.md]] | 领域分类、交叉关系、理论大厦骨架索引 |
