"""
文档加载和分割工具
"""
import os
from typing import List, Dict
from app.core.logger import logger


class DocumentLoader:
    """文档加载器"""

    @staticmethod
    def load_markdown(file_path: str) -> str:
        """
        加载 Markdown 文件

        Args:
            file_path: 文件路径

        Returns:
            文件内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"成功加载文档: {file_path}")
            return content
        except Exception as e:
            logger.error(f"加载文档失败 {file_path}: {str(e)}")
            return ""

    @staticmethod
    def load_multiple_files(file_paths: List[str]) -> List[Dict[str, str]]:
        """
        加载多个文件

        Args:
            file_paths: 文件路径列表

        Returns:
            文档列表，每个文档包含 content 和 source
        """
        documents = []
        for file_path in file_paths:
            content = DocumentLoader.load_markdown(file_path)
            if content:
                documents.append({
                    'content': content,
                    'source': file_path
                })
        return documents


class TextSplitter:
    """文本分割器"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化文本分割器

        Args:
            chunk_size: 每个块的字符数
            chunk_overlap: 块之间的重叠字符数
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        按字符数分割文本

        Args:
            text: 要分割的文本

        Returns:
            分割后的文本块列表
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap

        return chunks

    def split_by_sections(self, text: str) -> List[str]:
        """
        按章节分割文本（基于 Markdown 标题）

        Args:
            text: 要分割的文本

        Returns:
            分割后的章节列表
        """
        if not text:
            return []

        # 按二级标题分割
        sections = []
        current_section = []
        lines = text.split('\n')

        for line in lines:
            # 检测标题
            if line.startswith('##') and not line.startswith('###'):
                # 保存上一个章节
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []

            current_section.append(line)

        # 添加最后一个章节
        if current_section:
            sections.append('\n'.join(current_section))

        # 过滤掉太短的章节
        sections = [s for s in sections if len(s.strip()) > 50]

        return sections

    def split_documents(self, documents: List[Dict[str, str]], by_section: bool = True) -> List[Dict]:
        """
        分割多个文档

        Args:
            documents: 文档列表
            by_section: 是否按章节分割（否则按字符数分割）

        Returns:
            分割后的文档块列表
        """
        all_chunks = []

        for doc in documents:
            content = doc['content']
            source = doc['source']

            # 选择分割方式
            if by_section:
                chunks = self.split_by_sections(content)
            else:
                chunks = self.split_text(content)

            # 为每个块添加元数据
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    'content': chunk,
                    'metadata': {
                        'source': source,
                        'chunk_id': i,
                        'total_chunks': len(chunks)
                    }
                })

        logger.info(f"文档分割完成，共 {len(all_chunks)} 个块")
        return all_chunks


def prepare_knowledge_base(project_root: str) -> List[Dict]:
    """
    准备知识库文档

    Args:
        project_root: 项目根目录

    Returns:
        处理后的文档块列表
    """
    # 要加载的文档列表
    doc_files = [
        os.path.join(project_root, 'README.md'),
        # 可以添加更多文档
        # os.path.join(project_root, 'docs', '开发方案.md'),
        # os.path.join(project_root, 'docs', '快速启动指南.md'),
    ]

    # 过滤存在的文件
    existing_files = [f for f in doc_files if os.path.exists(f)]

    if not existing_files:
        logger.warning("未找到任何文档文件")
        return []

    # 加载文档
    loader = DocumentLoader()
    documents = loader.load_multiple_files(existing_files)

    # 分割文档
    splitter = TextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(documents, by_section=True)

    return chunks
