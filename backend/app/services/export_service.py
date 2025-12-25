"""
数据导出服务
支持导出为 CSV 和 Excel 格式
"""
import csv
import io
from typing import List, Dict
from datetime import datetime
from app.core.logger import logger


class ExportService:
    """数据导出服务类"""

    @staticmethod
    def export_to_csv(data: List[Dict], columns: List[Dict[str, str]]) -> bytes:
        """
        导出数据为 CSV 格式

        Args:
            data: 数据列表
            columns: 列定义 [{"key": "id", "label": "ID"}, ...]

        Returns:
            CSV 文件的字节数据
        """
        try:
            output = io.StringIO()
            writer = csv.writer(output)

            # 写入表头
            headers = [col['label'] for col in columns]
            writer.writerow(headers)

            # 写入数据
            for row in data:
                row_data = []
                for col in columns:
                    key = col['key']
                    value = row.get(key, '')

                    # 处理特殊类型
                    if isinstance(value, datetime):
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif value is None:
                        value = ''

                    row_data.append(str(value))

                writer.writerow(row_data)

            # 转换为字节
            csv_data = output.getvalue()
            output.close()

            # 添加 BOM 以支持 Excel 正确显示中文
            return '\ufeff'.encode('utf-8') + csv_data.encode('utf-8')

        except Exception as e:
            logger.error(f"导出 CSV 失败: {str(e)}", exc_info=True)
            raise


# 创建全局导出服务实例
export_service = ExportService()
