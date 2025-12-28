# MiroFishOpt（基于 MiroFish 的本地化优化版）

本项目目录为 `MiroFish-Optimize`，用于在保留原始 MiroFish 工作流的基础上，把 **图谱/记忆/向量存储本地化**，并提升在真实使用中的可运行性与稳定性。

## 项目来源

- 上游项目：`https://github.com/666ghj/MiroFish`
- 上游核心依赖：OASIS 模拟引擎（用于社媒多智能体模拟）
- 本优化版目标：允许继续调用云端 LLM（推理/抽取），但把 **存储** 全部落到本地（Neo4j + Qdrant），避免 Zep 免费版 429、并让“历史项目/历史图谱”可持续累积。

## 做了哪些优化（重点变更点）

### 1) 存储本地化：Neo4j + Qdrant 替代 Zep（可切换）

- 新增 `GRAPH_BACKEND`：
  - `local`：Neo4j 存图谱（节点/边/Chunk 关联），Qdrant 存向量（Chunk embeddings）
  - `zep`：继续使用上游 Zep Cloud（需要 `ZEP_API_KEY`，可能遇到 429）
- 新增 `VECTOR_BACKEND`：
  - `qdrant`：启用向量检索
  - `none`：关闭向量（纯图检索/纯规则兜底）
- 统一隔离策略：**共用一套库，用 `project_id`（以及 `graph_id`）隔离**，不再“每个项目覆盖前一个”。

### 2) LLM 结构化抽取可单独切换（应对审核/兼容性）

新增 `EXTRACT_API_KEY / EXTRACT_BASE_URL / EXTRACT_MODEL_NAME`：
- 用于“本体生成 / 实体关系抽取”等 JSON 结构化任务
- 当你遇到 `400 data_inspection_failed / inappropriate content`（某些供应商更严格）时，可只替换抽取模型，不影响主 LLM 配置。

同时做了兼容增强：
- `LLM_BASE_URL` 自动补全 `/v1`（部分 OpenAI-compatible 提供方要求）
- JSON 输出解析更健壮（部分提供方不支持 `response_format=json_object` 时自动降级）

### 3) 构图容错：单个 chunk 抽取失败不再导致整图失败

- 抽取触发提供方审核时会进入 safe-mode 重试
- 仍失败则跳过该 chunk 的实体/边抽取（chunk 文本仍会写入存储），避免整个任务失败

### 4) 节点重复优化：Person/Organization/Product/Location 类型归一

针对“同名但 entity_type 不同导致多个节点”的问题：
- 构图入库前对实体类型做归一映射（`Person/Organization/Product/Location`）
- 同时保留原始抽取类型到节点属性 `source_entity_types`，便于追溯

### 5) 模拟启动体验与兼容

- `GRAPH_BACKEND=local` 时不支持“模拟过程中实时回写图谱记忆”（原本给 Zep 用）：
  - 后端会自动降级关闭 `enable_graph_memory_update`，避免 400/500
  - 前端会显示 warning，而不是直接失败
- Step3 启动模拟前自动检测并执行 `prepare`（避免“未准备直接 start 导致 400”）

### 6) 报告工具链本地化补齐

ReportAgent 在本地模式下的工具服务由 `LocalToolsService` 提供，已补齐：
- `get_simulation_context`（与上游接口对齐）
- `interview_agents`：直接调用真实的 OASIS 采访批量接口（需要模拟环境仍在运行）

### 7) 历史项目列表页面

新增前端项目列表页：
- 路由：`/projects`
- 支持查看历史项目列表并点击进入对应项目流程页

## 数据存储位置（如何查阅历史项目）

### 项目元数据与上传文件（本地文件）

项目会以 `project_id` 持久化在后端 `uploads` 目录中：
- 项目目录：`MiroFish-Optimize/backend/uploads/projects/<project_id>/`
- 元数据：`MiroFish-Optimize/backend/uploads/projects/<project_id>/project.json`
- 原始文件：`MiroFish-Optimize/backend/uploads/projects/<project_id>/files/`
- 抽取文本：`MiroFish-Optimize/backend/uploads/projects/<project_id>/extracted_text.txt`

查看历史项目有两种方式：
- 前端：打开 `http://localhost:3000/projects`
- 后端 API：`GET /api/graph/project/list`

### 图谱与向量（本地服务）

- 图谱：Neo4j（容器默认暴露 `bolt://localhost:7687`，浏览器 `http://localhost:7474`）
- 向量：Qdrant（默认 `http://localhost:6333`）
- Qdrant collection：由 `.env` 的 `QDRANT_COLLECTION_CHUNKS` 控制（默认 `mirofish_chunks`）

## 如何运行（Windows / macOS 通用）

### 0) 前置依赖

- Node.js 18+
- Python 3.11+
- `uv`（Python 依赖管理）
- Docker（推荐，用于一键启动 Neo4j/Qdrant）

### 1) 启动本地依赖（Neo4j + Qdrant）

```bash
docker compose -f docker-compose.local.yml up -d
```

默认 Neo4j 账号密码在 `docker-compose.local.yml` 中写死为：
- 用户：`neo4j`
- 密码：`mirofish`

对应 `.env` 里需要保持一致：`NEO4J_PASSWORD=mirofish`

### 2) 配置环境变量

```bash
cp .env.example .env
```

至少需要配置：

```env
# OpenAI-compatible LLM
LLM_API_KEY=你的key
LLM_BASE_URL=你的base_url
LLM_MODEL_NAME=你的模型名

# 本地化存储
GRAPH_BACKEND=local
VECTOR_BACKEND=qdrant

# Neo4j（与 compose 一致）
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=mirofish

# Qdrant
QDRANT_URL=http://localhost:6333
```

可选项（强烈建议了解）：

```env
# 抽取专用 LLM：解决 data_inspection_failed 等审核问题
# EXTRACT_API_KEY=...
# EXTRACT_BASE_URL=...
# EXTRACT_MODEL_NAME=...

# Embeddings：如果你的提供方支持 embeddings，建议配置；不支持则可 VECTOR_BACKEND=none
EMBEDDING_MODEL_NAME=...
# EMBEDDING_BASE_URL=...
# EMBEDDING_API_KEY=...
```

### 3) 安装依赖

在项目根目录执行：

```bash
npm run setup:all
```

### 4) 启动服务

```bash
npm run dev
```

访问：
- 前端：`http://localhost:3000`
- 后端：`http://localhost:5001`

## 如何驱动（推荐使用流程）

1. Step1 图谱构建：上传材料 → 生成本体 → 构图（本地写入 Neo4j，可选写入 Qdrant）
2. Step2 环境准备：基于图谱实体生成 Agent Profiles（写入 `backend/uploads/simulations/<simulation_id>/...`）
3. Step3 启动模拟：启动并行模拟（Twitter + Reddit），本地模式会自动关闭“图谱记忆实时回写”
4. Step4 生成报告：ReportAgent 调用本地工具（图 + 向量 + 采访）生成报告
5. Step5 交互：对报告与模拟世界进行交互式查询

## 常见问题（Troubleshooting）

- 报错 `400 data_inspection_failed / inappropriate content`：
  - 这是提供方的输出审核拦截；使用 `EXTRACT_*` 把“抽取模型”单独切换到更合适的提供方/模型。
- 启动模拟 `HTTP 400: 未准备好，请先 prepare`：
  - Step3 已增加自动 prepare；如果仍发生，请确认你启动的是 `MiroFish-Optimize` 这套后端（端口 5001）。
- 报错 `interview_agents ... env 未运行或已关闭`：
  - 采访工具需要模拟环境仍在运行；不要提前关闭环境（或先重新启动模拟）。
- 图谱里同名多节点：
  - 这是“类型抖动”引起的；本优化版已对 Person/Organization/Product/Location 做归一，需**重建图谱**后生效。

## License

遵循上游 MiroFish 的开源许可证（仓库根目录 `LICENSE`）。

