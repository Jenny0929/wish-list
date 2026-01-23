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
    
    def search(self, query: str, top: int = 5) -> List[dict]:
        """
        执行搜索查询
        
        Args:
            query: 搜索查询文本
            top: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        print(f"\n搜索查询: '{query}'")
        
        try:
            results = self.search_client.search(
                search_text=query,
                top=top,
                select=["course_id", "knowledge_point", "content_summary", "keywords"]
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
    print("等待几秒让索引更新...")
    import time
    time.sleep(3)
    
    # 执行几个示例搜索
    test_queries = ["Python", "函数", "机器学习"]
    for query in test_queries:
        uploader.search(query, top=3)
    
    print("\n" + "="*60)
    print("✓ 完成!")
    print("="*60)


if __name__ == "__main__":
    main()
