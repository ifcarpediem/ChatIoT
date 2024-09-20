import sqlite3
import os

# 连接到数据库或创建数据库文件
database_path = os.path.join(os.path.dirname(__file__), 'yolo_model_zoo', 'yolo_database.db')
# 创建数据库
print(database_path)
conn = sqlite3.connect(database_path)

# 创建游标对象
cursor = conn.cursor()

# 创建模型表
# cursor.execute('''CREATE TABLE IF NOT EXISTS models (
#                   model_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   model_name TEXT NOT NULL
#                   )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS models (
                model_id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                model_accuracy FLOAT NOT NULL,
                model_output TEXT NOT NULL,
                model_num INTEGER NOT NULL,
                model_classes TEXT NOT NULL
                )''')

# 提交更改
conn.commit()

# 关闭数据库连接
conn.close()

# 添加模型到数据库
def add_model(model_name):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # 检查是否已存在具有相同名称的模型
    cursor.execute("SELECT model_id FROM models WHERE model_name=?", (model_name,))
    existing_model = cursor.fetchone()

    if existing_model:
        model_id = existing_model[0]
    else:
        cursor.execute("INSERT INTO models (model_name) VALUES (?)", (model_name,))
        conn.commit()
        model_id = cursor.lastrowid

    conn.close()
    return model_id

# 添加模型到数据库
def add_model_json(model_json):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # 检查是否已存在具有相同名称的模型
    cursor.execute("SELECT model_id FROM models WHERE model_name=?", (model_json['model_name'],))
    existing_model = cursor.fetchone()

    if existing_model:
        model_id = existing_model[0]
    else:
        cursor.execute("INSERT INTO models (model_name, model_accuracy, model_output, model_num, model_classes) VALUES (?,?,?,?,?)", (model_json['model_name'], model_json['model_accuracy'], model_json['model_output'], model_json['model_num'], model_json['model_classes'], ))
        conn.commit()
        model_id = cursor.lastrowid

    conn.close()
    return model_id

# 查询所有模型
def get_all_models():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM models")
    models = cursor.fetchall()
    conn.close()
    return models

# 删除模型
def delete_model(model_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM models WHERE model_id=?", (model_id,))
    conn.commit()
    conn.close()

# 通过模型 ID 查找模型名称
def get_model_name_by_id(model_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT model_name FROM models WHERE model_id=?", (model_id,))
    model = cursor.fetchone()
    conn.close()
    return model[0] if model else None

# 通过id获取模型信息
def get_model_massage_by_id(model_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM models WHERE model_id=?", (model_id,))
    model = cursor.fetchone()
    conn.close()
    return model if model else None

if __name__ == "__main__":
    print('test sqlite')
    print(get_model_massage_by_id(1))

    

