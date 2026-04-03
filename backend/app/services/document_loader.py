"""
文本分割工具
"""
from typing import List


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
