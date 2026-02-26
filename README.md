# RealEstate-Agent

**上海商业地产智能分析助手**  
一个基于 RAG（检索增强生成）的问答系统，能够精准回答关于上海办公楼市场的复杂问题。系统结合向量检索、元数据过滤、意图解析和工具调用，将海量研报和交易数据转化为可交互的知识库。

## ✨ 功能特点

- **智能问答**：用自然语言提问，例如“2023-2024年静安区写字楼租金同比变化？”
- **意图解析**：利用 LLM 将问题结构化，提取区域、年份、行业等过滤条件。
- **混合检索**：同时支持语义相似度搜索和元数据精确过滤（如区域、年份）。
- **重排序**：交叉编码器提升检索结果的相关性。
- **工具调用**：精确计算同比、均值等数值，避免 LLM 幻觉。
- **增量更新**：支持动态添加新研报/交易数据，无需重建向量库。
- **缓存机制**：减少重复计算，提升响应速度。
- **评估框架**：量化检索质量（Hit Rate、MRR），便于持续优化。

## 🏗️ 系统架构
<img width="362" height="220" alt="image" src="https://github.com/user-attachments/assets/f18b2334-5fca-4001-8da0-4113a9385929" />




## 📁 项目结构
RealEstate-Agent/
├── rag_preprocess/ # 预处理模块
│ ├── chunking/ # 分块策略
│ ├── doc_parser.py # 解析 docx 文档
│ ├── table_parser.py # 解析交易表格
│ ├── incremental_updater.py # 增量更新
│ └── run.py # 预处理入口
├── rag_runtime/ # 运行时模块
│ ├── query_parser.py # 意图解析
│ ├── rag_retriever.py # 检索器
│ ├── rag_chain.py # 回答生成
│ ├── tools.py # 计算工具
│ ├── cache_manager.py # 缓存
│ ├── evaluation.py # 评估
│ └── config.py # 全局配置
├── requirements.txt # 依赖
└── README.md # 本文档


## 数据准备
将研报文档（.docx）放入 data/report.docx（或修改 run.py 中的路径）。
将交易表格（.xlsx）放入 data/transaction.xlsx（格式需与 table_parser.py 兼容）。
（可选）将其他 Excel 表格放入 data/other_table.xlsx 作为普通文档处理。

## 预处理：生成单元
python rag_preprocess/run.py
生成 units.json 文件。

## 构建向量库
python rag_runtime/embed_store.py
将单元向量化并存入 ./chroma_jll 目录。

## 运行查询
python rag_runtime/run_query.py "你的问题"
例如：
python rag_runtime/run_query.py "2023-2024年静安区写字楼租金同比变化？"


## 增量更新
将新文件放入 data/new/，然后运行：
python rag_preprocess/incremental_updater.py

## 📊 使用示例
问题：2023-2024年静安区写字楼租金同比变化？
输出：
2023-2024年静安区写字楼租金同比上涨11.85%。
租金呈现明显上升趋势，从2023年的平均5.74元/平方米/天增至2024年的6.42元/平方米/天。

问题：陆家嘴金融行业2024年的平均租金是多少？
输出：
2024年陆家嘴金融行业平均租金为9.17元/平方米/天（基于3个交易样本）。

## 🛠️ 技术栈
语言模型：DeepSeek API (deepseek-chat)
向量库：ChromaDB + BGE 嵌入模型
重排序：BGE-reranker-base
框架：LangChain, LangChain-Chroma
工具：Pandas, Numpy

## 📈 评估指标
通过 evaluation.py 可以评估检索质量，支持的指标：
Hit Rate@K
Mean Reciprocal Rank (MRR)
Precision@K

## 🔮 未来规划
多模态支持：整合卫星图像、户型图等非结构化数据。
实时数据接入：接入宏观经济指标、政策新闻。
决策建议：从问答升级到主动建议（如招商策略、租金调整）。
个性化助手：学习用户偏好，定制化推送。
