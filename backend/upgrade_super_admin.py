"""
升级管理员为超级管理员
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "trash_classify.db")

def upgrade_to_super_admin():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 查询所有管理员
        cursor.execute("SELECT id, username, role FROM users WHERE role = 'admin'")
        admins = cursor.fetchall()

        if not admins:
            print("没有找到管理员账号")
            return

        print("当前管理员列表：")
        for admin in admins:
            print(f"  {admin[0]}. {admin[1]} (role: {admin[2]})")

        # 选择要升级的管理员
        admin_id = input("\n请输入要升级为超级管理员的用户ID: ")

        # 升级为超级管理员
        cursor.execute("UPDATE users SET role = 'super_admin' WHERE id = ?", (admin_id,))
        conn.commit()

        # 验证
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (admin_id,))
        user = cursor.fetchone()

        if user and user[1] == 'super_admin':
            print(f"\n✓ 成功！用户 {user[0]} 已升级为超级管理员")
        else:
            print("\n✗ 升级失败")

    except Exception as e:
        print(f"错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_to_super_admin()
