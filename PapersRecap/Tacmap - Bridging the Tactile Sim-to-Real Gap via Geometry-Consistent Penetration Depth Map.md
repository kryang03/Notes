---
tags:
  - paper
  - tactile-sensing
  - sim-to-real
  - manipulation
aliases:
  - Tacmap
paper-year: 2026
read-date: 2026-03-13
venue: arXiv
paper-pdf: "[[Papers/Tacmap- Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map.pdf]]"
related:
  - "[[ContactMechanics]]"
  - "[[SignalProcessing]]"
  - "[[ComputationalGeometry]]"
  - "[[ReinforcementLearning]]"
---

# Tacmap: Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map

> [!abstract] 核心贡献
> 提出统一的 deform map 表征作为触觉仿真与真实世界的"公共几何空间"，通过体积穿透深度计算（无需 FEM）实现高保真+高效率的触觉仿真，在 Isaac Lab 中支持大规模并行训练，并实现灵巧手 in-hand rotation 的 zero-shot sim-to-real 迁移。

## 1. 问题设定与动机

视觉触觉传感器 (VBTS, GelSight/DIGIT) 的 sim-to-real gap 三难困境：

| 方法类别 | 代表 | 保真度 | 效率 |
|---------|------|--------|------|
| 经验方法 | Taxim | 依赖数据分布 | 中 |
| 解析方法 | TACTO | 低（简化深度渲染） | 高 |
| 物理方法 | TacEx, Taccel | 高（FEM/IPC） | 低 |

**核心洞察**: 原始触觉图像是传感器特定的（光学复杂），但底层 **deform map** 是通用的接触物理代理。

### 直观隐喻
就像不同语言的人用一张地形图沟通——触觉传感器各有各的"语言"（光学图像），但底层的"地形"（变形深度图）是通用的物理真相。Tacmap 做的就是教每个传感器把自己的方言翻译成这张通用地形图，于是仿真和真实世界说的就是同一种话了。

## 2. 核心方法

### 2.0 变量来源追踪

枢纽：**deform map $M$ 是 sim/real 的"公共几何空间"**——解耦传感器光学（$I_{raw}$ 传感器特定），让仿真与真实在同一几何表征上对齐。

| 变量 | 类型/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $I_{raw}$ | 触觉图像 | 传感器观测 | 否 | 原始触觉图 | **传感器特定**（光学复杂）→ 不直接用 |
| $M$ / $d(u,v)$ | 深度场 | sim 射线投射 / real 翻译网络 | real 端翻译网带梯度 | **deform map（公共几何空间）** | sim/real 在此对齐——核心 |
| $z_s,z_u,z_o$ | 深度 | 几何（法线投射） | 否 | 感知面/未变形/物体交点坐标 | 法线空间投射（非平面假设） |
| $F$ | 力 | sim 引擎 / real 力传感回归 | real 端带梯度 | 净力 | 三流之一 |
| $P$ | 位置 | sim 引擎 / real deform 质心 | 否 | 接触位置 | real 端由 $M$ 几何质心导出 |
| Translator | ResNet enc-dec | 学习（real 端） | 是 | Image→Deform 映射 | **每传感器需独立标定** |

### Delta 分析

| 维度 | 前人工作 | Tacmap |
|-----|---------|--------|
| **方法类别** | FEM (TacEx/Taccel) 或 解析 (TACTO) | **射线投射穿透深度** |
| **表征空间** | 原始触觉图像 / 力分布 | **统一 deform map（几何空间）** |
| **曲面支持** | 假设平面传感器 | **法线空间投影 → 曲面指尖** |
| **并行效率** | FEM 内存指数增长 | **GPU 射线投射线性扩展** |
| **Sim-to-Real** | 需域适应或大量标定 | **deform map 作为公共空间 → zero-shot** |

### 2.1 统一 Deform Map 表征

**仿真端**: 不做 FEM，而是沿传感器表面法线投射射线，计算刚体与弹性体的 3D 穿透深度：

$$d(u,v) = \max(0, z_s - \max(z_u, z_o))$$

- $z_s$: 感知面坐标, $z_u$: 未变形面坐标, $z_o$: 物体交点坐标
- 支持 **曲面指尖** — 在法线空间计算，消除平面假设的投影畸变

**真实端**: 自动化数据采集台（3轴精密运动台）→ 结构光压入 → 配对数据集 $\{I_\text{raw}, M_\text{gt}\}$ → ResNet encoder-decoder 学习 Image→Deform Map 映射

#### 核心代码逻辑：穿透深度射线投射

```python
# GPU 并行射线投射计算穿透深度 (Isaac Lab 集成)
def compute_deform_map(sensor_mesh, object_mesh, H, W):
    """
    sensor_mesh: 传感器弹性体网格
    object_mesh: 物体刚体网格
    """
    # 1. 沿每个传感面点的法线方向投射射线
    normals = compute_surface_normals(sensor_mesh)  # (H*W, 3)
    origins = sensor_mesh.vertices.reshape(H*W, 3)
    
    # 2. 射线-网格求交 (GPU 加速)
    z_o = ray_mesh_intersect(origins, normals, object_mesh)  # 物体交点深度
    z_s = sensor_surface_depth(origins, normals)              # 感知面坐标
    z_u = undeformed_surface_depth(origins, normals)          # 未变形面坐标
    
    # 3. 穿透深度 = max(0, z_s - max(z_u, z_o))
    deform_map = torch.clamp(z_s - torch.maximum(z_u, z_o), min=0)  # (H*W,)
    return deform_map.reshape(H, W)

# Image → Deform Map 翻译网络 (真实端)
class TactileTranslator(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = resnet18(pretrained=True)
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(512, 256, 4, 2, 1), nn.ReLU(),
            nn.ConvTranspose2d(256, 128, 4, 2, 1), nn.ReLU(),
            nn.ConvTranspose2d(128, 1, 4, 2, 1),   # 单通道 deform map
        )
    def forward(self, tactile_image):
        feat = self.encoder(tactile_image)             # (B, 512, h, w)
        return torch.clamp(self.decoder(feat), min=0)  # (B, 1, H, W) 非负穿透深度
```

### 2.2 三流触觉信息

| 信号 | 仿真获取 | 真实获取 |
|------|---------|---------|
| 净力 $F$ | 物理引擎接触传感器 | 力传感器监督的 ResNet 回归 |
| 接触位置 $P$ | 引擎报告精确位置 | Deform map 有效区域几何质心 |
| Deform Map $M$ | 穿透深度射线投射 | Image→Deform 翻译网络 |

### 2.3 集成与训练

- 集成至 **Isaac Lab** 和 **MuJoCo**
- 全 GPU 管线，与物理引擎同步
- PPO 训练 in-hand rotation，观测包含实时 Tacmap 流

### 训练与实现细节

**触觉翻译网络训练**:
- 数据采集: 3 轴精密运动台自动化压入 → ~10K 配对样本 $(I_\text{raw}, M_\text{gt})$
- 损失函数: $\mathcal{L} = \|M_\text{pred} - M_\text{gt}\|_2^2 + \lambda_\text{IoU}(1 - \text{IoU}(M_\text{pred}, M_\text{gt}))$
- 训练: ResNet-18 backbone, Adam, lr=1e-4, ~100 epochs

**RL 策略训练 (In-hand rotation)**:
- 算法: PPO (Isaac Lab 原生实现)
- 并行环境数: 8192
- 观测空间: 关节角 + 关节速度 + 物体朝向 + **实时 Tacmap 三流信号** $(F, P, M)$
- 动作空间: 关节位置目标 (PD 控制)
- 训练时长: ~2-4 小时 (单 GPU, A100)

## 3. 实验结果

**Sim-to-Real 几何一致性**:

| 物体 | 接触位置误差 | 变形深度误差 | 力 L2 误差 | Deform IoU |
|------|:-----------:|:-----------:|:----------:|:----------:|
| Square | 0.66mm | 18.53% | 0.28N | 88.21% |
| Cylinder | 0.96mm | 14.71% | 0.61N | 85.67% |

**计算效率**:
- GPU 内存线性增长（射线投射 vs FEM 指数增长）
- 8192 并行环境下仍保持合理渲染频率
- 触觉渲染对仿真速度的影响可忽略

**Zero-shot Sim-to-Real**: SharpaWave 灵巧手成功执行 in-hand rotation（球体），无任何真实世界微调。

### Ablation 因果链

> [!warning] 关键消融
> - 去掉 deform map，仅用力+接触位置 → 策略缺乏空间分布信息 → 旋转精度下降 ~30%（**deform map 提供接触几何的关键空间信息**）
> - 用 TACTO 式平面深度渲染替代射线投射 → 曲面指尖产生投影畸变 → Sim-to-Real gap 增大，zero-shot 失败（**法线空间投射对曲面的必要性**）
> - 减少并行环境数 8192 → 512 → PPO 样本多样性不足 → 训练不稳定，收敛变慢 ~5x（**大规模并行对触觉 RL 的效率保障**）
> - 不做 Image→Deform 域适应，直接用原始图像 → 光学伪影导致 sim/real 分布不匹配 → 策略无法迁移（**统一表征空间的 Sim-to-Real 关键性**）

## 4. 核心洞见 (Insights)

1. **几何抽象胜过光学模拟**: 通过 deform map 解耦传感器光学特性 → sim-to-real gap 的本质是接触几何而非视觉外观
2. **穿透深度作为通用表征**: 与 SDF（[[ComputationalGeometry|签名距离场]]）思想类似 — 用标量场描述接触状态
3. **法线空间投影**: 支持曲面指尖的关键创新 → 对拟人灵巧手至关重要（现有方法多假设平面传感器）
4. **效率-保真平衡**: 射线投射介于解析着色器和 FEM 之间 → 实现了 RL 可用的触觉仿真

### 工程关键细节 (Engineering Tricks)

1. **法线空间投射消除曲面畸变**: 在传感器局部坐标系沿法线方向计算穿透深度 → 天然适配非平面指尖
2. **全 GPU 管线**: 射线投射与物理引擎同步运行在 GPU 上 → 避免 CPU-GPU 数据搬运瓶颈
3. **IoU 作为几何一致性度量**: $\text{IoU} = \frac{|M_\text{sim} \cap M_\text{real}|}{|M_\text{sim} \cup M_\text{real}|}$ 比 L2 误差更能反映接触形状匹配度
4. **自动化标定台**: 3 轴精密运动台 + 结构光 → 减少人工标定误差，可批量采集配对数据
5. **deform map 截断非负**: $d(u,v) = \max(0, \cdot)$ → 物理约束保证穿透深度非负，避免网络学习非物理值

## 5. 与知识体系的联系

### 与 [[ContactMechanics]] 的联系
- 穿透深度直接关联接触力学：$d(u,v)$ 是接触压力分布的几何代理
- Hertz 接触理论中，法向力与穿透量的关系为:
$$F_n = \frac{4}{3}E^*\sqrt{R^*}\,\delta^{3/2}$$
其中 $E^*$ 为等效弹性模量，$R^*$ 为等效曲率半径。Tacmap 的 $d(u,v)$ 即对应空间化的 $\delta(u,v)$，将标量穿透量泛化为 2D 穿透深度场
- 与 [[ContactMechanics|Hertz 理论]] 的穿透量 $\delta$ 概念直接对接
- Deform IoU > 85% 意味着仿真接触流形与真实世界高度一致

### 与 [[SignalProcessing]] 的联系
- Image→Deform Map 翻译网络本质是触觉信号的域适应/逆问题
- 从光学伪影中恢复几何信息 → 与触觉信号处理直接相关

### 与 [[ComputationalGeometry]] 的联系
- 射线投射 + 法线投影 → 经典的 ray-mesh intersection 优化
- Deform map 与 [[ComputationalGeometry|SDF]] 的数学关联：对传感器表面点 $\mathbf{p}$，穿透深度等价于 SDF 负值区域的截断:
$$d(u,v) = \max\!\left(0,\, -\phi_{\text{obj}}\bigl(\mathbf{p}(u,v)\bigr)\right)$$
其中 $\phi_{\text{obj}}$ 为物体 SDF。梯度 $\nabla d = -\nabla\phi_{\text{obj}}$ 在接触区域指向法向外侧，可直接用于基于梯度的操作优化
- Deform map 作为 2.5D 表征 → 与深度图、SDF 同族

### 与 [[ReinforcementLearning|Sim-to-Real]] 的联系
- 触觉 sim-to-real gap 可形式化为观测分布偏移 $D_{\text{KL}}\bigl(p_{\text{sim}}(o|s)\,\|\,p_{\text{real}}(o|s)\bigr)$。Tacmap 通过映射至公共 deform map 空间 $f_d$ 使该散度最小化:
$$o = f_d(I) \implies D_{\text{KL}}\bigl(p_{\text{sim}}(f_d(I)|s)\,\|\,p_{\text{real}}(f_d(I)|s)\bigr) \approx 0$$
- 这是 [[ReinforcementLearning|MDP Gap]] 中 **State Gap** 的子问题 — 传感器域移位
- Zero-shot 迁移验证了统一表征空间对消除域移位的有效性

### 5.5 概念边界与符号陷阱

- **deform map 是公共几何空间**：sim/real 在此对齐，解耦传感器光学外观——"几何抽象胜过光学模拟"。
- **法线空间投射（非平面假设）**：曲面指尖（LEAP/Allegro）关键；平面渲染（TACTO）致投影畸变、zero-shot 失败（§Ablation）。
- **仅法向穿透深度、无切向/剪切**：incipient slip 检测受限（§6）。
- **$d=\max(0,\cdot)$ 截断非负**：物理约束，避免网络学非物理值。
- **deform map = 物体 SDF 负值截断** $\max(0,-\phi_{obj})$：与 SDF 同族的 2.5D 表征。
- **每传感器需独立标定** Image→Deform 翻译网络：换传感器需重采配对数据。

## 6. 局限与未来方向

- 仅建模法向穿透深度，不含切向力/剪切应变 → incipient slip 检测受限
- 仅在球体 in-hand rotation 上验证 zero-shot 迁移，更复杂任务待测
- 射线投射随物体网格复杂度增加而变慢 → 需要加速结构
- 数据采集依赖定制化硬件台 → 新传感器需重新标定

### 局限性深度分析（理论/算法/工程三维度）

| 维度 | 局限 | 根因 | 替代方案 |
|------|------|------|----------|
| **理论** | 仅建模法向穿透深度 | 忽略切向剪切应变 | 引入 2D 切向位移场 → 支持 incipient slip 检测 |
| **算法** | 射线投射随网格复杂度增长 | 每条射线需遍历三角面 | BVH 加速结构 / 隐式 SDF 查询替代 |
| **工程** | 每种传感器需独立标定 | Image→Deform 网络是传感器特定的 | 基于物理的 sim-to-real（如学习光学模型参数）|

### 对转笔/Sim-to-Real 的启发

1. **Deform map 可用于转笔的触觉观测**: 转笔过程中笔与指尖的接触 deform map 包含滑动/滚动信息 → 比原始触觉图像更有效、更 sim-to-real friendly
2. **法线空间投射对曲面指尖至关重要**: LEAP Hand / Allegro Hand 的指尖均为曲面 → 平面假设会导致边缘区域畸变 → Tacmap 的方法直接适用
3. **Zero-shot 迁移的关键**: 统一几何表征空间（而非视觉空间）是 zero-shot 成功的核心 → 转笔的 Sim-to-Real 也应寻找接触的“公共物理空间”

## 7. 跨方法对比

| 方法 | 传感器 | 仿真方法 | 保真度 | 效率 | Sim-to-Real |
|------|--------|---------|--------|------|-------------|
| TACTO | GelSight | 解析深度渲染 | 低 | 高 | 需域适应 |
| Taxim | GelSight | 经验映射 | 中 | 中 | 分布受限 |
| TacEx/Taccel | 通用 | FEM/IPC | 高 | 低 | 理论可行 |
| **Tacmap (本文)** | **通用** | **射线投射** | **中-高** | **高** | **Zero-shot** |
| DenseTact | 曲面传感器 | 光学仿真 | 中 | 中 | 需微调 |

> [!note] 跨簇综述：触觉 sim-to-real 的"表征选择谱"（连接 sim-to-real 簇 × in-hand rotation 触觉论文）
> Tacmap 在 [[A Survey of Sim-to-Real Methods in RL|Survey]] 的 MDP 四元素里属 **$\Delta_S$（传感 gap）的几何抽象**。把它与 in-hand rotation 簇触觉论文并置，浮现**触觉 sim-to-real 的表征选择谱**——都在回答"触觉的什么表征对 sim-to-real 不变"：
>
> | 论文 | 触觉表征 | 对什么不变 |
> |------|---------|----------|
> | [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch\|Touch Dexterity]] | 二值接触(1-bit) | 量化吸收力幅值差异 |
> | [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing\|Robot Synesthesia]] | 触觉点云 | 几何位置（去光学/力） |
> | [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch\|AnyRotate]] | 接触姿态+力 | 物理可解释中间量 |
> | **Tacmap** | **穿透深度场** | **几何变形（解耦光学外观）** |
>
> **统一 insight**：四者都把触觉从"原始光学/力读数"抽象到"几何/接触结构"——这正是 in-hand rotation 簇 meta-insight"**sim-to-real 本质是找对 gap 不变的观测子空间**"在触觉模态上的完整谱系。Tacmap 的 deform map 是其中**最接近连续接触物理**的一档（穿透深度 = Hertz $\delta$ 的空间化 = 物体 SDF 负值截断），故 zero-shot 迁移最彻底。
