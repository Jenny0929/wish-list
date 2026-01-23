# Azure AI Search 数据结构说明

## 概述

本文档说明如何在 Azure AI Search 向量数据库中存储课程知识内容的数据结构。

## 数据字段

根据您的需求，数据结构包含以下字段：

| 字段名称 | 中文名称 | 数据类型 | 说明 |
|---------|---------|---------|------|
| `id` | 唯一标识符 | String | 文档的唯一ID（主键） |
| `course_id` | 课程ID | String | 课程的标识符 |
| `knowledge_point` | 知识点 | String | 主要知识点或主题 |
| `keywords` | 关键词 | Collection(String) | 相关关键词列表 |
| `keyword_synonyms` | 关键词的同义词 | Collection(String) | 关键词的同义词列表 |
| `content_summary` | 内容摘要 | String | 内容的简短摘要 |
| `content` | 内容 | String | 完整的内容文本 |
| `content_vector` | 内容向量 | Collection(Single) | 用于向量搜索的内容嵌入（可选） |

## 文件说明

### 1. `azure_search_schema.json`

这是 Azure AI Search 索引的完整架构定义文件，包含：

- **字段定义**：所有数据字段的类型、属性和分析器配置
- **语义搜索配置**：用于提升搜索相关性的语义配置
- **向量搜索配置**：用于向量相似度搜索的配置（HNSW算法）
- **建议器配置**：用于自动完成和建议功能

**关键特性：**
- 使用中文分析器 (`zh-Hans.microsoft`) 处理中文内容
- 支持向量搜索（维度：1536，适用于 OpenAI embeddings）
- 配置了语义搜索以提高搜索质量
- 支持过滤、排序和分面导航

### 2. `azure_search_models.py`

Python 数据模型定义，包含：

- **`CourseKnowledgeDocument` 类**：表示单个课程知识文档的数据结构
- **辅助方法**：
  - `to_dict()`: 转换为字典格式
  - `to_json()`: 转换为 JSON 字符串
  - `from_dict()`: 从字典创建实例
- **示例数据生成器**：`create_sample_documents()` 函数

**使用示例：**

```python
from azure_search_models import CourseKnowledgeDocument

# 创建文档
doc = CourseKnowledgeDocument(
    course_id="CS101",
    knowledge_point="Python基础语法",
    keywords=["Python", "变量", "数据类型"],
    keyword_synonyms=["Python编程", "变量定义"],
    content_summary="Python基础语法介绍",
    content="Python是一种高级编程语言..."
)

# 转换为 JSON
json_data = doc.to_json()
print(json_data)
```

### 3. `sample_data.json`

示例数据文件，包含三个示例文档，展示了数据的实际格式。

## 使用方法

### 步骤 1：创建 Azure AI Search 索引

使用 Azure Portal、REST API 或 SDK 创建索引：

**使用 REST API：**

```bash
curl -X PUT "https://<your-service-name>.search.windows.net/indexes/course-knowledge-index?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: <your-admin-key>" \
  -d @azure_search_schema.json
```

**使用 Python SDK：**

```python
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
import json

# 创建客户端
endpoint = "https://<your-service-name>.search.windows.net"
credential = AzureKeyCredential("<your-admin-key>")
client = SearchIndexClient(endpoint=endpoint, credential=credential)

# 加载架构
with open('azure_search_schema.json', 'r', encoding='utf-8') as f:
    index_schema = json.load(f)

# 创建索引
from azure.search.documents.indexes.models import SearchIndex
index = SearchIndex.deserialize(index_schema)
client.create_or_update_index(index)
```

### 步骤 2：准备数据

使用 Python 模型创建数据：

```python
from azure_search_models import CourseKnowledgeDocument

documents = [
    CourseKnowledgeDocument(
        course_id="CS101",
        knowledge_point="Python基础",
        keywords=["Python", "编程"],
        keyword_synonyms=["Python语言"],
        content_summary="Python基础知识",
        content="详细的Python基础内容..."
    )
]

# 转换为适合上传的格式
data_to_upload = [doc.to_dict() for doc in documents]
```

### 步骤 3：上传数据到 Azure AI Search

```python
from azure.search.documents import SearchClient

# 创建搜索客户端
search_client = SearchClient(
    endpoint=endpoint,
    index_name="course-knowledge-index",
    credential=credential
)

# 上传文档
result = search_client.upload_documents(documents=data_to_upload)
print(f"上传了 {len(result)} 个文档")
```

### 步骤 4（可选）：生成向量嵌入

如果需要使用向量搜索功能，需要生成内容的向量嵌入：

```python
import openai

def generate_embedding(text: str) -> list:
    """使用 OpenAI API 生成文本嵌入"""
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

# 为每个文档生成向量
for doc in documents:
    # 组合内容用于生成嵌入
    combined_text = f"{doc.knowledge_point} {doc.content_summary} {doc.content}"
    doc.content_vector = generate_embedding(combined_text)
```

## 搜索示例

### 全文搜索

```python
# 搜索特定关键词
results = search_client.search(
    search_text="Python函数",
    select=["course_id", "knowledge_point", "content_summary"],
    top=5
)

for result in results:
    print(f"课程: {result['course_id']}, 知识点: {result['knowledge_point']}")
```

### 向量搜索（语义搜索）

```python
# 使用向量进行相似度搜索
query_vector = generate_embedding("如何定义Python函数")

results = search_client.search(
    search_text=None,
    vector_queries=[{
        "vector": query_vector,
        "k": 5,
        "fields": "content_vector"
    }]
)

for result in results:
    print(f"知识点: {result['knowledge_point']}")
```

### 混合搜索

```python
# 结合全文搜索和向量搜索
results = search_client.search(
    search_text="Python",
    vector_queries=[{
        "vector": query_vector,
        "k": 5,
        "fields": "content_vector"
    }],
    select=["course_id", "knowledge_point", "content_summary"],
    top=10
)
```

## 注意事项

1. **中文支持**：架构使用 `zh-Hans.microsoft` 分析器来正确处理中文文本分词
2. **向量维度**：默认使用 1536 维度，适用于 OpenAI 的 text-embedding-ada-002 模型
3. **主键**：`id` 字段必须是唯一的，建议使用有意义的命名方式（如 "course-id-topic-name"）
4. **性能优化**：
   - 对于大量数据，使用批量上传（每批最多 1000 个文档）
   - 考虑使用分区键（partition key）来提高查询性能
   - 根据实际查询模式调整字段属性（searchable、filterable 等）

## 数据结构优势

这个数据结构设计具有以下优势：

1. **灵活的搜索能力**：支持全文搜索、向量搜索和混合搜索
2. **中文优化**：使用专门的中文分析器提高搜索准确性
3. **语义理解**：通过向量嵌入支持语义相似度搜索
4. **多维度检索**：可以通过课程、知识点、关键词等多个维度进行查询
5. **可扩展性**：易于添加新字段或调整现有字段配置

## 相关资源

- [Azure AI Search 文档](https://learn.microsoft.com/zh-cn/azure/search/)
- [向量搜索概述](https://learn.microsoft.com/zh-cn/azure/search/vector-search-overview)
- [Azure Search Python SDK](https://learn.microsoft.com/zh-cn/python/api/overview/azure/search-documents-readme)
