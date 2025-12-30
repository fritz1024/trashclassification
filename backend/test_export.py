"""
测试导出服务
"""
from app.services.export_service import export_service
from datetime import datetime

# 测试数据
test_data = [
    {
        'id': 1,
        'predicted_class': '可回收物',
        'confidence': 0.95,
        'created_at': datetime.now(),
        'image_path': 'test.jpg'
    }
]

# 定义列
columns = [
    {'key': 'id', 'label': 'ID'},
    {'key': 'predicted_class', 'label': '分类结果'},
    {'key': 'confidence', 'label': '置信度'},
    {'key': 'created_at', 'label': '识别时间'},
    {'key': 'image_path', 'label': '图片文件名'}
]

try:
    csv_data = export_service.export_to_csv(test_data, columns)
    print("导出成功！")
    print(f"数据长度: {len(csv_data)} 字节")
    print(f"前100字节: {csv_data[:100]}")
except Exception as e:
    print(f"导出失败: {str(e)}")
    import traceback
    traceback.print_exc()
