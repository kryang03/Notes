---
description: 基于 JSON Canvas 规范和 Obsidian 知识图谱管理经验，生成和维护 KnowledgeGraph.canvas 的完整操作指南
mode: agent
tools:
  - read_file
  - create_file
  - replace_string_in_file
  - run_in_terminal
  - file_search
  - grep_search
  - semantic_search
---

# Canvas 知识图谱构建与维护 Prompt

> **适用场景**: 根据知识库内容构建/更新 `KnowledgeGraph.canvas`，保持布局美观、结构清晰、内容完整。

---

## 一、核心原则

### 1.1 设计理念

- **Projects 为绝对核心**：Projects 组放在 Canvas 视觉中心，使用最大 Group + 最醒目颜色 (`"1"` Red)
- **自上而下的层次流**：实验 → Ideas → **Projects** → 算法突破点 → Papers → Foundations
- **先输出再迭代**：不要过度思考布局细节；先按合理默认值生成完整 Canvas，然后根据反馈调整
- **每个节点都有意义**：Canvas 不是装饰，每个节点和边都应体现知识关联

### 1.2 绝对禁止

- ❌ 文字超出节点边框（宽度不够 → 增大 width）
- ❌ 节点重叠或距离 < 30px
- ❌ Group 无法容纳其子节点（Group 尺寸必须包含所有子节点 + padding）
- ❌ Edge 引用不存在的 Node ID
- ❌ 在 text 字段中使用 `\\n` 而非 `\n`（Obsidian 会渲染为字面 `\n`）

---

## 二、JSON Canvas 规范速查

### 2.1 文件结构

```json
{
  "nodes": [],
  "edges": []
}
```

### 2.2 节点类型

| 类型 | 必需字段 | 用途 |
|------|---------|------|
| `text` | `id, type, x, y, width, height, text` | Markdown 文本卡片 |
| `file` | `id, type, x, y, width, height, file` | 链接到 vault 中的文件 |
| `group` | `id, type, x, y, width, height` | 分组容器 (label 可选) |
| `link` | `id, type, x, y, width, height, url` | 外部链接 |

### 2.3 颜色方案

| Preset | 色系 | 本知识库用途 |
|--------|------|------------|
| `"1"` | Red | **Projects** (核心标识) |
| `"2"` | Orange | **算法突破点** (Key Technical Challenges) |
| `"3"` | Yellow | **Research Insights / Ideas** |
| `"4"` | Green | **Papers** (经典/基础方法) |
| `"5"` | Cyan | **Papers** (最新/前沿方法) + 实验数据 |
| `"6"` | Purple | **Foundations** (理论基础) |

### 2.4 边 (Edges)

```json
{
  "id": "edge_unique_id",
  "fromNode": "source_node_id",
  "fromSide": "bottom",
  "toNode": "target_node_id",
  "toSide": "top",
  "toEnd": "arrow",
  "color": "5",
  "label": "描述"
}
```

`fromSide`/`toSide`: `top | right | bottom | left`

---

## 三、布局数学公式

### 3.1 核心约束

```
节点最小宽度 = 320px（中文文本需更宽以避免溢出）
推荐文本节点宽度 = 340~400px
节点间最小水平间距 ≥ 50px
节点间最小垂直间距 ≥ 50px
Group 间最小垂直间距 ≥ 200px（推荐 250~300px）
Group 内部 padding ≥ 40px（每边）
```

### 3.2 列布局计算

对于 N 个等宽节点排列在同一行：

```
column_pitch = node_width + gap
total_width = N * node_width + (N-1) * gap
start_x = -total_width / 2  （居中对齐时）
column_i_x = start_x + i * column_pitch
```

**推荐参数**：
- 7 列布局: width=350, gap=50, pitch=400, total=2750
- 8 列布局: width=340, gap=50, pitch=390, total=3070

### 3.3 高度估算

```
Markdown 渲染高度估算:
- ## 标题行: ~35px
- 普通文本行: ~22px
- 空行: ~12px
- **粗体行**: ~24px
- 列表项: ~22px
- 表格行: ~26px
- 上下内边距: ~30px (total)

总高度 ≈ 30 + sum(各行高度)
安全系数: 实际设置高度 = 估算高度 × 1.15
```

### 3.4 Group 尺寸计算

```
group_x = min(所有子节点 x) - padding_left
group_y = min(所有子节点 y) - padding_top
group_width = max(子节点 x + width) - group_x + padding_right
group_height = max(子节点 y + height) - group_y + padding_bottom

推荐 padding: 40~60px (每边)
```

---

## 四、层次布局模板

### 4.1 六层结构

```
Y轴 (向下递增)
│
├── Layer 0: 实验状态 (孤立左上角)     color="5"   y ≈ -3300
│   └── 实验发现文本卡
│
├── Layer 1: Research Insights/Ideas   color="3"   y ≈ -2500
│   └── 8个 Idea 节点 + 最强组合节点
│
├── Layer 2: Projects (核心！最大！)    color="1"   y ≈ -1700
│   ├── 项目主文件 (file node)
│   ├── 核心洞见 (text node)
│   ├── 研究路线图 (file node)
│   └── 实验进度 (text node)
│
├── Layer 3: 算法突破点                 color="2"   y ≈ -700
│   └── 7个技术挑战节点
│
├── Layer 4: PapersRecap               color="4/5"  y ≈ 30
│   └── 论文按突破点列对齐 (每列 2-4 篇)
│
└── Layer 5: Foundations                color="6"   y ≈ 1400
    ├── Row 1: 6个核心领域 (file + note 对)
    └── Row 2: 5个支撑领域 (file + note 对)
```

### 4.2 列对齐原则

**论文列应与对应的突破点列在相同 x 位置**，这样从突破点到论文的边会自然垂直下落，视觉最清晰。

**Foundations Row 1 也应与论文列对齐**，体现论文→理论的向下流动。

---

## 五、关键经验教训

### 5.1 文字溢出防范

- **中文字符宽度 ≈ 2× 英文字符**：一行 350px 大约容纳 17-20 个中文字符
- **Markdown 表格需要更宽的节点** (≥500px)
- **wikilink `[[...]]` 渲染后比原文更宽**（因为变成蓝色可点击链接）
- **经验法则**: 取最长行的字符数 × 10px ≈ 最小宽度

### 5.2 Group 容纳验证

创建完 Canvas 后**必须运行 Python 验证脚本**：

```python
import json
with open('KnowledgeGraph.canvas') as f:
    data = json.load(f)

nodes = data['nodes']
edges = data['edges']
node_ids = {n['id'] for n in nodes}

# (1) 验证所有 edge 引用有效
for e in edges:
    assert e['fromNode'] in node_ids, f"Bad fromNode: {e['fromNode']}"
    assert e['toNode'] in node_ids, f"Bad toNode: {e['toNode']}"

# (2) 验证节点在 Group 内
groups = [n for n in nodes if n['type'] == 'group']
others = [n for n in nodes if n['type'] != 'group']
for g in groups:
    gx, gy, gw, gh = g['x'], g['y'], g['width'], g['height']
    for n in others:
        nx, ny, nw, nh = n['x'], n['y'], n['width'], n['height']
        if nx >= gx and ny >= gy and nx+nw <= gx+gw and ny+nh <= gy+gh:
            pass  # 在 group 内
        elif nx >= gx and ny >= gy and nx < gx+gw and ny < gy+gh:
            # 部分在内，检查溢出
            if nx+nw > gx+gw:
                print(f"⚠️ {n['id']} 右溢出 {g['id']} by {nx+nw-gx-gw}px")
            if ny+nh > gy+gh:
                print(f"⚠️ {n['id']} 下溢出 {g['id']} by {ny+nh-gy-gh}px")

print(f"✅ {len(nodes)} nodes, {len(edges)} edges")
```

### 5.3 边的最佳实践

- **核心连接用 `label` + `color`** 突出显示（如 `label: "⭐"`）
- **同一类连接用相同颜色**：Ideas→Projects 用 `"1"` (Red), Ideas→BT 用 `"3"` (Yellow)
- **避免过多交叉边**：如果 Ideas→Breakthroughs 的边要穿过 Projects 层，只保留"核心"连接
- **Paper→Paper 演进边**用 `"3"` (Yellow) + `label` 描述关系（如 "演进"、"互补范式"）
- **Paper→Foundation 边**统一用 `"6"` (Purple)

### 5.4 内容选择策略

不需要把所有 57 篇 PapersRecap 都放进 Canvas。选择标准：

1. **与 Projects 直接相关**的论文（被 Ideas 引用的）
2. **每个算法突破点的代表性论文**（2-4 篇/突破点）
3. **有明确演进关系**的论文对（如 VICES→FACET）
4. **最新前沿**（color="5" Cyan 标识）vs **经典基石**（color="4" Green 标识）

### 5.5 ID 命名规范

```
节点 ID:
- Group: xxx_group (如 papers_group, foundations_group)
- Text: xxx_xxx (如 idea_001, bt_frequency, paper_tarc)
- File: found_xxx, proj_xxx
- 描述性附注: xxx_note, xxx_insight

边 ID:
- e_源缩写_目标缩写 (如 e_bt1_tarc, e_proj_bt3)
- 避免超长 ID，使用缩写
```

---

## 六、迭代优化检查清单

每次更新 Canvas 后，检查：

- [ ] JSON 语法有效（`python3 -c "import json; json.load(open('KnowledgeGraph.canvas'))"`）
- [ ] 所有 edge 引用的 node ID 存在
- [ ] 所有子节点在其 Group 边界内
- [ ] 相邻节点间距 ≥ 50px
- [ ] 相邻 Group 间距 ≥ 200px
- [ ] 文本节点宽度足够容纳最长文本行
- [ ] 文本节点高度足够容纳全部文本（用行数×行高估算）
- [ ] Canvas 中的 wikilinks `[[...]]` 对应的文件确实存在
- [ ] File 节点的 `file` 路径正确（相对于 vault 根目录）
- [ ] File 节点的 `subpath` 引用的标题确实存在于目标文件中
- [ ] Projects 组在视觉上最突出（最大、居中、红色）
- [ ] 新增的 Paper/Idea 已反映在 Canvas 中
- [ ] 实验状态节点已更新为最新实验结果

---

## 七、从零构建 Canvas 的步骤

1. **收集信息**：读取 Projects/, Foundations/, PapersRecap/ 的完整结构
2. **确定层次**：根据上面的六层模板规划 Y 坐标
3. **计算列布局**：根据每层节点数确定 X 坐标
4. **计算 Group 尺寸**：基于子节点位置 + padding
5. **编写节点 JSON**：Groups 在前（底层），Content 在后（顶层）
6. **编写边 JSON**：按层次关系（Exp→Ideas→Projects→BT→Papers→Foundations）
7. **验证**：运行 Python 脚本检查 JSON 有效性和布局合规性
8. **在 Obsidian 中打开**：肉眼确认无溢出、无重叠
9. **迭代修复**：根据用户反馈调整

---

## 八、实际案例参考

当前知识库的 `KnowledgeGraph.canvas` 使用以下参数：

| 参数 | 值 | 备注 |
|------|-----|------|
| 总节点数 | 69 | 包括 6 个 Group |
| 总边数 | 73 | |
| 总垂直跨度 | ~5600px | 从 y=-3600 到 y=2080 |
| 总水平跨度 | ~3400px | 从 x=-1600 到 x=1660 |
| 文本节点宽度 | 340~620px | 短文本用 340，表格用 620 |
| 列间距 | 50~80px | |
| 层间距 | 250~300px | |
| Group padding | 40~60px | |
