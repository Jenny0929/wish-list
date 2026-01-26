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
