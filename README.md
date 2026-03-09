# BF768-Final-

## BF768_Final_Proposal_Workflow_Progress

```
BF768_Final_Proposal_Workflow_Progress/
├── 阶段零：选题与proposal框架确认
│   ├── 1. 明确最终研究主题
│   │   └── 主题确定为：激酶与特定生物分子缩合物（Biomolecular Condensates）的互作图谱
│   ├── 2. 明确proposal撰写原则
│   │   ├── 以当前主题为准
│   │   ├── 以当前目录树为准
│   │   ├── 若与draft内容冲突，则忽略draft中的冲突部分
│   │   └── 忽略draft中潜在的待补充或待修改内容
│   └── 3. 确认目录树是否适配final proposal
│       ├── 对照project proposal guidelines核查结构
│       ├── 确认目录树整体符合final proposal要求
│       └── 确认当前目录树可作为final proposal写作骨架
│
├── 阶段一：UniProt数据源定位与检索策略确定
│   ├── 1. 明确UniProt在项目中的定位
│   │   ├── 将UniProt定义为"激酶主数据层"来源
│   │   ├── 用于获取Protein / Gene / Function / Feature / External Reference骨架数据
│   │   └── 明确UniProt不作为condensate特异关系证据的唯一来源
│   ├── 2. 明确第一轮应获取的数据类型
│   │   ├── Protein基础信息
│   │   ├── Gene基础信息
│   │   ├── 序列信息
│   │   ├── 长度信息
│   │   └── 为后续功能注释、位点、结构域、外部链接打基础
│   └── 3. 确定第一轮检索目标
│       └── 先获取"人类 reviewed kinase 主集合（kinase backbone）"
│
├── 阶段二：UniProt检索式设计与合理性确认
│   ├── 1. 初步检索式提出
│   │   └── (taxonomy_id:9606) AND (keyword:KW-0418) AND (reviewed:true)
│   ├── 2. 检索式合理性评估
│   │   ├── 确认该检索式可用于提取人类reviewed kinase集合
│   │   ├── 确认其适合作为V1激酶主集合入口
│   │   └── 确认其不应被视为整个项目的最终唯一边界
│   ├── 3. 检索式标准化
│   │   └── 规范写法确定为：organism_id:9606 AND reviewed:true AND keyword:KW-0418
│   └── 4. 明确检索后下一步
│       ├── 固定accession/entry主集合
│       ├── 下载第一轮主表字段
│       └── 后续围绕accession开展第二轮注释抓取
│
├── 阶段三：第一轮导出字段设计
│   ├── 1. 确定第一轮导出的目标
│   │   └── 先建立可入库的激酶主表原始数据，而非一次性抓取全部注释
│   ├── 2. 初步推荐字段范围
│   │   ├── Entry / accession
│   │   ├── Entry Name
│   │   ├── Protein names
│   │   ├── Gene Names
│   │   ├── Organism
│   │   ├── Length
│   │   └── Sequence
│   ├── 3. 讨论Reviewed字段的必要性
│   │   ├── 识别到Reviewed在当前query下信息增量较小
│   │   └── 认为其可保留用于人工检查，但不是必须字段
│   └── 4. 明确第一轮不急于导出的字段
│       ├── 功能长文本
│       ├── 位点明细
│       ├── 结构域明细
│       └── 大量外部数据库交叉引用
│
├── 阶段四：网页端导出配置与问题排查
│   ├── 1. 在UniProt网页端设置导出方式
│   │   ├── 选择 Download all
│   │   ├── 选择 Format = TSV
│   │   └── 选择 Compressed = No
│   ├── 2. 尝试在Customize columns中配置字段
│   │   ├── 初始选择过 Reviewed
│   │   ├── 选择了 Entry Name
│   │   ├── 选择了 Protein names
│   │   ├── 选择了 Gene Names
│   │   ├── 选择了 Organism
│   │   ├── 选择了 Length
│   │   └── 选择了 Sequence
│   ├── 3. 遇到"Entry / Accession无法搜索到"的问题
│   │   ├── 搜索 Accession 未命中
│   │   ├── 搜索 entry 仅出现 Entry Name
│   │   └── 判断Customize columns未显式暴露Entry/Accession作为可添加列
│   ├── 4. 通过Preview验证默认列
│   │   ├── 使用 Preview 10 预览导出结果
│   │   ├── 确认第一列自动存在
│   │   └── 确认第一列即为 entry
│   └── 5. 得出网页端导出结论
│       ├── 无需强行在Customize columns里再找Entry/Accession
│       ├── 默认第一列已满足主键需求
│       └── 当前网页端导出配置可继续使用
│
├── 阶段五：第一轮TSV导出完成
│   ├── 1. 执行正式导出
│   │   └── 已将全部检索结果导出为TSV文件
│   ├── 2. 明确当前已获得的数据范围
│   │   ├── 人类
│   │   ├── reviewed
│   │   ├── kinase keyword匹配
│   │   └── 共632条结果
│   └── 3. 确认当前数据集的项目定位
│       ├── 这是项目的"kinase backbone"
│       ├── 这是Protein主表原始数据来源
│       └── 这不是最终的condensate关系证据数据
│
├── 阶段六：导出后数据组织方案确定
│   ├── 1. 明确当前阶段任务重心
│   │   └── 从"继续下载"转向"数据整理与schema对接"
│   ├── 2. 规划第一轮字段重命名
│   │   ├── entry → uniprot_accession
│   │   ├── Entry Name → entry_name
│   │   ├── Protein names → protein_name
│   │   ├── Gene Names → gene_names_raw
│   │   ├── Organism → organism_name
│   │   ├── Length → sequence_length
│   │   └── Sequence → sequence
│   ├── 3. 明确第一轮需要做的数据检查
│   │   ├── 检查uniprot_accession是否唯一
│   │   ├── 检查是否存在空值
│   │   ├── 检查Gene Names是否含多个名称
│   │   ├── 检查Protein names是否包含复杂别名结构
│   │   └── 检查Sequence长度是否与Length一致
│   ├── 4. 初步确定第一版数据库表方向
│   │   ├── Protein表
│   │   ├── Gene表
│   │   └── Protein_Gene关联表
│   └── 5. 明确当前清洗原则
│       ├── 先保留原始字段
│       ├── Gene Names后续拆分
│       ├── Protein names后续规范化
│       └── accession作为后续所有注释抓取和关联的核心键
│
└── 阶段七：下一阶段任务已明确但尚未执行
    ├── 1. 第二轮注释抓取规划
    │   ├── Function层
    │   │   ├── function
    │   │   ├── catalytic activity
    │   │   └── GO terms
    │   ├── Feature层
    │   │   ├── domain
    │   │   ├── binding site
    │   │   ├── active site
    │   │   └── 其他site/region/motif/PTM
    │   ├── Interaction层
    │   │   ├── subunit / complex
    │   │   ├── general interaction
    │   │   └── external PPI references
    │   └── ExternalReference层
    │       ├── IntAct
    │       ├── Complex Portal
    │       ├── InterPro
    │       ├── Pfam
    │       └── PDB
    ├── 2. 明确第二轮抓取原则
    │   ├── 不再按keyword大范围盲抓
    │   ├── 围绕第一轮得到的entry/accession集合开展
    │   └── 以accession为外键建立注释层
    └── 3. 明确后续与主题的衔接方向
        ├── 当前完成的是kinase主数据层
        ├── 下一步完成的是kinase annotation layer
        └── 再下一步才是condensate-specific relation layer
```