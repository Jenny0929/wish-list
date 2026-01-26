# Azure AI Search 数据结构完整文件内容

本文档包含所有修改后的文件的完整内容，方便查看和使用。

---

## 目录

1. [azure_search_schema.json](#1-azure_search_schemajson) - Azure AI Search 索引架构定义
2. [azure_search_models.py](#2-azure_search_modelspy) - Python 数据模型
3. [sample_data.json](#3-sample_datajson) - 示例数据
4. [upload_to_azure_search.py](#4-upload_to_azure_searchpy) - 上传工具脚本
5. [requirements.txt](#5-requirementstxt) - 依赖包列表
6. [AZURE_SEARCH_README.md](#6-azure_search_readmemd) - 使用说明文档
7. [.gitignore](#7-gitignore) - Git 忽略文件配置

---

## 1. azure_search_schema.json

**文件说明**：Azure AI Search 的完整索引架构定义，包含所有字段定义、中文分析器配置、向量搜索配置和语义搜索配置。

```json
{
  "name": "course-knowledge-index",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "searchable": false,
      "filterable": true,
      "sortable": true,
      "facetable": false,
      "retrievable": true
    },
    {
      "name": "course_id",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "sortable": true,
      "facetable": true,
      "retrievable": true,
      "analyzer": "standard.lucene"
    },
    {
      "name": "knowledge_point",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "sortable": false,
      "facetable": true,
      "retrievable": true,
      "analyzer": "zh-Hans.microsoft"
    },
    {
      "name": "keywords",
      "type": "Collection(Edm.String)",
      "searchable": true,
      "filterable": true,
      "sortable": false,
      "facetable": true,
      "retrievable": true,
      "analyzer": "zh-Hans.microsoft"
    },
    {
      "name": "keyword_synonyms",
      "type": "Collection(Edm.String)",
      "searchable": true,
      "filterable": false,
      "sortable": false,
      "facetable": false,
      "retrievable": true,
      "analyzer": "zh-Hans.microsoft"
    },
    {
      "name": "content_summary",
      "type": "Edm.String",
      "searchable": true,
      "filterable": false,
      "sortable": false,
      "facetable": false,
      "retrievable": true,
      "analyzer": "zh-Hans.microsoft"
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true,
      "filterable": false,
      "sortable": false,
      "facetable": false,
      "retrievable": true,
      "analyzer": "zh-Hans.microsoft"
    },
    {
      "name": "content_vector",
      "type": "Collection(Edm.Single)",
      "searchable": true,
      "filterable": false,
      "sortable": false,
      "facetable": false,
      "retrievable": true,
      "dimensions": 1536,
      "vectorSearchProfile": "default-vector-profile"
    }
  ],
  "semantic": {
    "configurations": [
      {
        "name": "default-semantic-config",
        "prioritizedFields": {
          "titleField": {
            "fieldName": "knowledge_point"
          },
          "prioritizedContentFields": [
            {
              "fieldName": "content"
            },
            {
              "fieldName": "content_summary"
            }
          ],
          "prioritizedKeywordsFields": [
            {
              "fieldName": "keywords"
            },
            {
              "fieldName": "keyword_synonyms"
            }
          ]
        }
      }
    ]
  },
  "vectorSearch": {
    "algorithms": [
      {
        "name": "default-algorithm",
        "kind": "hnsw",
        "hnswParameters": {
          "metric": "cosine",
          "m": 4,
          "efConstruction": 400,
          "efSearch": 500
        }
      }
    ],
    "profiles": [
      {
        "name": "default-vector-profile",
        "algorithm": "default-algorithm"
      }
    ]
  },
  "suggesters": [
    {
      "name": "sg",
      "searchMode": "analyzingInfixMatching",
      "sourceFields": [
        "knowledge_point",
        "keywords"
      ]
    }
  ]
}
```

---

## 2. azure_search_models.py

**文件说明**：Python 数据模型定义，包含 `CourseKnowledgeDocument` 类和示例数据生成函数。

```python
"""
Azure AI Search data models for course knowledge storage.

This module defines the data structure for storing course content
in Azure AI Search vector database.
"""

from typing import List, Optional
from dataclasses import dataclass, field, asdict
import json


@dataclass
class CourseKnowledgeDocument:
    """
    Data model for course knowledge documents in Azure AI Search.
    
    Attributes:
        id: Unique identifier for the document (generated or provided)
        course_id: Course identifier (课程ID)
        knowledge_point: Main knowledge point or topic (知识点)
        keywords: List of keywords related to the content (关键词)
        keyword_synonyms: List of synonyms for the keywords (关键词的同义词)
        content_summary: Brief summary of the content (content summary)
        content: Full content text (content)
        content_vector: Vector embedding of the content for semantic search (optional, generated)
    """
    
    course_id: str
    knowledge_point: str
    keywords: List[str]
    keyword_synonyms: List[str]
    content_summary: str
    content: str
    id: Optional[str] = None
    content_vector: Optional[List[float]] = None
    
    def __post_init__(self):
        """Generate ID if not provided."""
        if self.id is None:
            # Generate ID from course_id and knowledge_point using SHA-256
            import hashlib
            hash_input = f"{self.course_id}_{self.knowledge_point}".encode('utf-8')
            self.id = hashlib.sha256(hash_input).hexdigest()[:32]  # Use first 32 chars for readability
    
    def to_dict(self) -> dict:
        """Convert the document to a dictionary for Azure AI Search."""
        data = asdict(self)
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
    
    def to_json(self) -> str:
        """Convert the document to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CourseKnowledgeDocument':
        """Create a CourseKnowledgeDocument from a dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


def create_sample_documents() -> List[CourseKnowledgeDocument]:
    """
    Create sample documents to demonstrate the data structure.
    
    Returns:
        List of sample CourseKnowledgeDocument instances
    """
    samples = [
        CourseKnowledgeDocument(
            course_id="CS101",
            knowledge_point="Python基础语法",
            keywords=["Python", "变量", "数据类型", "语法"],
            keyword_synonyms=["Python编程", "变量定义", "数据结构", "基本语法"],
            content_summary="本节介绍Python编程语言的基础语法，包括变量定义、数据类型和基本运算符的使用。",
            content="Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。在本节中，我们将学习Python的基础语法，包括如何定义变量、使用不同的数据类型（整数、浮点数、字符串、列表等），以及如何使用基本的运算符进行计算。Python使用缩进来表示代码块，这使得代码更加清晰易读。"
        ),
        CourseKnowledgeDocument(
            course_id="CS101",
            knowledge_point="Python函数定义",
            keywords=["函数", "def", "参数", "返回值"],
            keyword_synonyms=["方法", "函数定义", "形参", "返回"],
            content_summary="学习如何在Python中定义和使用函数，包括参数传递和返回值。",
            content="函数是Python中组织代码的重要方式。使用def关键字可以定义一个函数，函数可以接收参数并返回值。函数的定义格式为：def function_name(parameters): 函数体。函数可以有多个参数，也可以没有参数。使用return语句可以返回函数的结果。函数使代码更加模块化和可重用。"
        ),
        CourseKnowledgeDocument(
            course_id="CS102",
            knowledge_point="机器学习基础",
            keywords=["机器学习", "监督学习", "特征工程", "模型训练"],
            keyword_synonyms=["ML", "有监督学习", "特征提取", "训练模型"],
            content_summary="介绍机器学习的基本概念，包括监督学习、特征工程和模型训练过程。",
            content="机器学习是人工智能的一个重要分支，它使计算机能够从数据中学习并做出预测。监督学习是最常见的机器学习方法，需要使用标记的训练数据。特征工程是从原始数据中提取有用特征的过程，这对模型性能至关重要。模型训练包括选择合适的算法、调整参数和评估模型性能。"
        )
    ]
    
    return samples


if __name__ == "__main__":
    # Example usage
    print("=== Azure AI Search 数据结构示例 ===\n")
    
    # Create sample documents
    documents = create_sample_documents()
    
    # Display the first document
    print("示例文档 1:")
    print(documents[0].to_json())
    print("\n" + "="*50 + "\n")
    
    # Display all documents in a compact format
    print("所有示例文档:")
    for i, doc in enumerate(documents, 1):
        print(f"\n文档 {i}:")
        print(f"  课程ID: {doc.course_id}")
        print(f"  知识点: {doc.knowledge_point}")
        print(f"  关键词: {', '.join(doc.keywords)}")
        print(f"  文档ID: {doc.id}")
```

---

## 3. sample_data.json

**文件说明**：包含三个示例文档的 JSON 数据文件，展示了数据的实际格式。

```json
[
  {
    "id": "cs101-python-basics",
    "course_id": "CS101",
    "knowledge_point": "Python基础语法",
    "keywords": [
      "Python",
      "变量",
      "数据类型",
      "语法"
    ],
    "keyword_synonyms": [
      "Python编程",
      "变量定义",
      "数据结构",
      "基本语法"
    ],
    "content_summary": "本节介绍Python编程语言的基础语法，包括变量定义、数据类型和基本运算符的使用。",
    "content": "Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。在本节中，我们将学习Python的基础语法，包括如何定义变量、使用不同的数据类型（整数、浮点数、字符串、列表等），以及如何使用基本的运算符进行计算。Python使用缩进来表示代码块，这使得代码更加清晰易读。"
  },
  {
    "id": "cs101-python-functions",
    "course_id": "CS101",
    "knowledge_point": "Python函数定义",
    "keywords": [
      "函数",
      "def",
      "参数",
      "返回值"
    ],
    "keyword_synonyms": [
      "方法",
      "函数定义",
      "形参",
      "返回"
    ],
    "content_summary": "学习如何在Python中定义和使用函数，包括参数传递和返回值。",
    "content": "函数是Python中组织代码的重要方式。使用def关键字可以定义一个函数，函数可以接收参数并返回值。函数的定义格式为：def function_name(parameters): 函数体。函数可以有多个参数，也可以没有参数。使用return语句可以返回函数的结果。函数使代码更加模块化和可重用。"
  },
  {
    "id": "cs102-ml-basics",
    "course_id": "CS102",
    "knowledge_point": "机器学习基础",
    "keywords": [
      "机器学习",
      "监督学习",
      "特征工程",
      "模型训练"
    ],
    "keyword_synonyms": [
      "ML",
      "有监督学习",
      "特征提取",
      "训练模型"
    ],
    "content_summary": "介绍机器学习的基本概念，包括监督学习、特征工程和模型训练过程。",
    "content": "机器学习是人工智能的一个重要分支，它使计算机能够从数据中学习并做出预测。监督学习是最常见的机器学习方法，需要使用标记的训练数据。特征工程是从原始数据中提取有用特征的过程，这对模型性能至关重要。模型训练包括选择合适的算法、调整参数和评估模型性能。"
  }
]
```

---

## 4. upload_to_azure_search.py

**文件说明**：完整的上传工具脚本，包含 `AzureSearchUploader` 类和演示程序。

```python
"""
Azure AI Search 数据上传示例脚本

这个脚本演示如何将课程知识数据上传到 Azure AI Search。
需要先安装: pip install -r requirements.txt
"""

import os
import json
from typing import List, Optional

# 尝试导入 Azure SDK
try:
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import SearchIndex
    from azure.core.credentials import AzureKeyCredential
    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False
    print("⚠️  Azure SDK 未安装")
    print("请运行: pip install -r requirements.txt")
    print()

# 导入数据模型
from azure_search_models import CourseKnowledgeDocument, create_sample_documents


class AzureSearchUploader:
    """Azure AI Search 数据上传工具类"""
    
    def __init__(self, endpoint: str, admin_key: str, index_name: str = "course-knowledge-index"):
        """
        初始化上传器
        
        Args:
            endpoint: Azure Search 服务端点 (例如: https://your-service.search.windows.net)
            admin_key: Azure Search 管理密钥
            index_name: 索引名称
        """
        self.endpoint = endpoint
        self.credential = AzureKeyCredential(admin_key)
        self.index_name = index_name
        self.index_client = SearchIndexClient(endpoint=endpoint, credential=self.credential)
        self.search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=self.credential
        )
    
    def create_index(self, schema_file: str = "azure_search_schema.json"):
        """
        创建或更新 Azure Search 索引
        
        Args:
            schema_file: 索引架构 JSON 文件路径
        """
        print(f"正在创建/更新索引: {self.index_name}")
        
        try:
            # 加载索引架构
            with open(schema_file, 'r', encoding='utf-8') as f:
                index_definition = json.load(f)
            
            # 创建索引对象
            index = SearchIndex.deserialize(index_definition)
            
            # 创建或更新索引
            result = self.index_client.create_or_update_index(index)
            print(f"✓ 索引 '{result.name}' 创建/更新成功")
            return True
            
        except Exception as e:
            print(f"✗ 创建索引失败: {str(e)}")
            return False
    
    def upload_documents(self, documents: List[CourseKnowledgeDocument]) -> bool:
        """
        上传文档到 Azure Search
        
        Args:
            documents: CourseKnowledgeDocument 列表
            
        Returns:
            bool: 是否成功
        """
        if not documents:
            print("警告: 没有要上传的文档")
            return False
        
        print(f"\n正在上传 {len(documents)} 个文档...")
        
        try:
            # 转换为字典格式
            docs_to_upload = [doc.to_dict() for doc in documents]
            
            # 批量上传
            result = self.search_client.upload_documents(documents=docs_to_upload)
            
            # 检查结果
            succeeded = sum(1 for r in result if r.succeeded)
            failed = len(result) - succeeded
            
            print(f"✓ 成功上传: {succeeded} 个文档")
            if failed > 0:
                print(f"✗ 上传失败: {failed} 个文档")
            
            return failed == 0
            
        except Exception as e:
            print(f"✗ 上传文档失败: {str(e)}")
            return False
    
    def upload_from_json(self, json_file: str) -> bool:
        """
        从 JSON 文件加载并上传文档
        
        Args:
            json_file: JSON 文件路径
            
        Returns:
            bool: 是否成功
        """
        print(f"正在从文件加载数据: {json_file}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 转换为文档对象
            documents = [CourseKnowledgeDocument.from_dict(item) for item in data]
            print(f"✓ 成功加载 {len(documents)} 个文档")
            
            # 上传
            return self.upload_documents(documents)
            
        except Exception as e:
            print(f"✗ 从文件加载失败: {str(e)}")
            return False
    
    def search(self, query: str, top: int = 5, select_fields: Optional[List[str]] = None) -> List[dict]:
        """
        执行搜索查询
        
        Args:
            query: 搜索查询文本
            top: 返回结果数量
            select_fields: 要返回的字段列表，默认返回主要字段
            
        Returns:
            搜索结果列表
        """
        print(f"\n搜索查询: '{query}'")
        
        # 使用默认字段如果未指定
        if select_fields is None:
            select_fields = ["course_id", "knowledge_point", "content_summary", "keywords"]
        
        try:
            results = self.search_client.search(
                search_text=query,
                top=top,
                select=select_fields
            )
            
            result_list = []
            for i, result in enumerate(results, 1):
                print(f"\n结果 {i}:")
                print(f"  课程ID: {result.get('course_id', 'N/A')}")
                print(f"  知识点: {result.get('knowledge_point', 'N/A')}")
                print(f"  摘要: {result.get('content_summary', 'N/A')[:100]}...")
                result_list.append(result)
            
            return result_list
            
        except Exception as e:
            print(f"✗ 搜索失败: {str(e)}")
            return []


def main():
    """主函数 - 演示使用方法"""
    
    print("="*60)
    print("Azure AI Search 课程知识数据上传工具")
    print("="*60)
    
    # 检查 Azure SDK 是否可用
    if not AZURE_SDK_AVAILABLE:
        print("\n" + "="*60)
        print("演示模式 - 显示数据结构")
        print("="*60)
        
        # 创建示例数据并显示
        documents = create_sample_documents()
        print(f"\n✓ 创建了 {len(documents)} 个示例文档\n")
        
        # 显示第一个文档的详细信息
        print("示例文档结构:")
        print("-"*60)
        print(documents[0].to_json())
        print("-"*60)
        return
    
    # 配置信息（需要替换为实际值）
    ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://your-service.search.windows.net")
    ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY", "your-admin-key")
    
    # 检查配置
    if "your-service" in ENDPOINT or "your-admin-key" in ADMIN_KEY:
        print("\n⚠️  请先配置 Azure Search 服务信息!")
        print("设置环境变量:")
        print("  export AZURE_SEARCH_ENDPOINT='https://your-service.search.windows.net'")
        print("  export AZURE_SEARCH_ADMIN_KEY='your-admin-key'")
        print("\n或者直接在代码中修改 ENDPOINT 和 ADMIN_KEY 变量")
        print("\n继续使用示例数据进行演示...\n")
        
        # 创建示例数据并保存
        print("="*60)
        print("生成示例数据")
        print("="*60)
        
        documents = create_sample_documents()
        print(f"\n✓ 创建了 {len(documents)} 个示例文档\n")
        
        # 显示第一个文档的详细信息
        print("示例文档结构:")
        print("-"*60)
        print(documents[0].to_json())
        print("-"*60)
        
        return
    
    # 创建上传器
    uploader = AzureSearchUploader(ENDPOINT, ADMIN_KEY)
    
    # 1. 创建索引
    print("\n" + "="*60)
    print("步骤 1: 创建索引")
    print("="*60)
    if not uploader.create_index():
        print("无法创建索引，退出")
        return
    
    # 2. 准备数据
    print("\n" + "="*60)
    print("步骤 2: 准备数据")
    print("="*60)
    
    # 选项 A: 使用示例数据
    documents = create_sample_documents()
    print(f"✓ 创建了 {len(documents)} 个示例文档")
    
    # 选项 B: 从 JSON 文件加载（如果文件存在）
    # if os.path.exists("sample_data.json"):
    #     uploader.upload_from_json("sample_data.json")
    
    # 3. 上传数据
    print("\n" + "="*60)
    print("步骤 3: 上传数据到 Azure Search")
    print("="*60)
    if not uploader.upload_documents(documents):
        print("数据上传失败")
        return
    
    # 4. 测试搜索（等待索引更新）
    print("\n" + "="*60)
    print("步骤 4: 测试搜索功能")
    print("="*60)
    # 等待索引更新 (Azure Search 通常需要几秒钟)
    INDEX_UPDATE_WAIT_SECONDS = 3
    print(f"等待 {INDEX_UPDATE_WAIT_SECONDS} 秒让索引更新...")
    import time
    time.sleep(INDEX_UPDATE_WAIT_SECONDS)
    
    # 执行几个示例搜索
    test_queries = ["Python", "函数", "机器学习"]
    for query in test_queries:
        uploader.search(query, top=3)
    
    print("\n" + "="*60)
    print("✓ 完成!")
    print("="*60)


if __name__ == "__main__":
    main()
```

---

## 5. requirements.txt

**文件说明**：Python 依赖包列表。

```txt
# Azure AI Search 相关依赖
azure-search-documents>=11.4.0
azure-core>=1.29.0

# 可选: 用于生成向量嵌入
# openai>=1.0.0
```

---

## 6. AZURE_SEARCH_README.md

**文件说明**：详细的使用说明文档（由于篇幅较长，请查看原文件）。

文档包含以下内容：
- 数据字段说明表格
- 各文件的详细说明
- 使用方法分步指南
- 代码示例（索引创建、数据上传、搜索）
- 注意事项和最佳实践
- 相关资源链接

---

## 7. .gitignore

**文件说明**：Git 忽略文件配置，用于排除 Python 编译文件和 IDE 配置。

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
```

---

## 使用说明

### 快速开始

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **查看数据结构**
   ```bash
   python3 azure_search_models.py
   ```

3. **运行上传工具（演示模式）**
   ```bash
   python3 upload_to_azure_search.py
   ```

4. **配置 Azure 并上传数据**
   ```bash
   export AZURE_SEARCH_ENDPOINT="https://your-service.search.windows.net"
   export AZURE_SEARCH_ADMIN_KEY="your-admin-key"
   python3 upload_to_azure_search.py
   ```

### 数据结构说明

所有文件遵循以下数据结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | String | 文档唯一标识符（自动生成） |
| `course_id` | String | 课程ID |
| `knowledge_point` | String | 知识点 |
| `keywords` | Array[String] | 关键词列表 |
| `keyword_synonyms` | Array[String] | 关键词同义词列表 |
| `content_summary` | String | 内容摘要 |
| `content` | String | 完整内容 |
| `content_vector` | Array[Float] | 向量嵌入（可选，1536维） |

### 关键特性

✅ 完整的数据结构定义
✅ 中文语言支持（zh-Hans.microsoft 分析器）
✅ 向量搜索支持（HNSW 算法，cosine 相似度）
✅ 语义搜索配置
✅ 自动完成建议器
✅ 安全的 ID 生成（SHA-256）
✅ 灵活的搜索选项

---

**注意**：所有文件已经过测试验证，包括：
- ✅ JSON 架构验证
- ✅ Python 代码测试
- ✅ 代码审查通过
- ✅ CodeQL 安全扫描通过（0 个漏洞）
