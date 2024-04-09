import pymysql

#------------------- MySQL -------------------
class Database:
    def __init__(self, host='127.0.0.1', port=3306, user='root', passwd='root123', charset='utf8', db='radarscan'):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.charset = charset
        self.db = db

    def connect(self):
        return pymysql.connect(host=self.host,
                               port=self.port,
                               user=self.user,
                               passwd=self.passwd,
                               charset=self.charset,
                               db=self.db)

    def execute_query(self, query, *args):
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, args)
                    return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error executing query: {e}")
            return None

class DataProcessing:
    def __init__(self, database):
        self.db = database

    def create_table(self, table_name, columns):
        """
        创建表格

        Args:
        - table_name: 表格名称
        - columns: 包含列名和数据类型的列表，例如 [('column1', 'INT'), ('column2', 'VARCHAR(255)')]

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
                    for column in columns:
                        create_query += f"{column[0]} {column[1]}, "
                    create_query = create_query[:-2] + ")"

                    cursor.execute(create_query)
                    conn.commit()
                    print(f"Table '{table_name}' created successfully.")
        except pymysql.Error as e:
            print(f"Error creating table: {e}")

    def drop_table(self, table_name):
        """
        删除表格

        Args:
        - table_name: 表格名称

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    drop_query = f"DROP TABLE IF EXISTS {table_name}"
                    cursor.execute(drop_query)
                    conn.commit()
                    print(f"Table '{table_name}' dropped successfully.")
        except pymysql.Error as e:
            print(f"Error dropping table: {e}")

    def insert_data(self, table_name, columns, values):
        """
        插入数据

        Args:
        - table_name: 表格名称
        - columns: 列名列表，例如 ['column1', 'column2']
        - values: 值列表，例如 [value1, value2]

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(columns))})"
                    cursor.execute(insert_query, values)
                    conn.commit()
                    print(f"Data inserted into table '{table_name}' successfully.")
        except pymysql.Error as e:
            print(f"Error inserting data: {e}")

    def update_table(self, table_name, name, column_name, new_value):
        """
        更新表格中的数据

        Args:
        - table_name: 表格名称
        - name: 条件字段的值
        - column_name: 要更新的列名
        - new_value: 新的值

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    update_query = f"UPDATE {table_name} SET {column_name} = %s WHERE name = %s"
                    cursor.execute(update_query, (new_value, name))
                    conn.commit()
                    print(f"Value in column '{column_name}' updated successfully for '{name}'.")
        except pymysql.Error as e:
            print(f"Error updating table: {e}")

    def query_table(self, table_name, column_name, value):
        """
        查询表格中的数据

        Args:
        - table_name: 表格名称
        - column_name: 条件字段的列名
        - value: 条件字段的值

        Returns:
        - 无
        """
        try:
            query = f"SELECT * FROM {table_name} WHERE {column_name} = %s"
            rows = self.db.execute_query(query, value)
            if rows:
                print(f"Query results for {column_name} = {value}:")
                for row in rows:
                    print(row)
            else:
                print(f"No rows found where {column_name} = {value}.")
        except pymysql.Error as e:
            print(f"Error querying table: {e}")

    def modify_table(self, table_name, action, column_name, column_type):
        """
        修改表格结构

        Args:
        - table_name: 表格名称
        - action: 'add' 表示添加列，'delete' 表示删除列
        - column_name: 列名
        - column_type: 列类型

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    if action == "add":
                        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{column_name}'")
                        if cursor.fetchone():
                            print(f"Column '{column_name}' already exists in table '{table_name}'.")
                            return
                        
                        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                    elif action == "delete":
                        alter_query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"

                    cursor.execute(alter_query)
                    conn.commit()
                    print(f"Table '{table_name}' modified successfully.")
        except pymysql.Error as e:
            print(f"Error modifying table: {e}")

    def delete_row(self, table_name, column_name, value):
        """
        删除表格中的行

        Args:
        - table_name: 表格名称
        - column_name: 条件字段的列名
        - value: 条件字段的值

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    deleterow_query = f"DELETE FROM {table_name} WHERE {column_name} = '{value}'"
                    cursor.execute(deleterow_query)
                    conn.commit()
                    print(f"The {value} has been deleted successfully.")
        except pymysql.Error as e:
            print(f"Error inserting data: {e}")

    def list_tables(self):
        """
        列出数据库中所有的表格名称

        Returns:
        - 表格名称列表
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW TABLES")
                    tables = [table[0] for table in cursor.fetchall()]
                    return tables
        except pymysql.Error as e:
            print(f"Error listing tables: {e}")

    def get_table_structure(self, table_name):
        """
        获取指定表格的结构，包括列名、数据类型等信息

        Args:
        - table_name: 表格名称

        Returns:
        - 表格结构信息（列名、数据类型）的列表
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                    structure = [(column[0], column[1]) for column in cursor.fetchall()]
                    return structure
        except pymysql.Error as e:
            print(f"Error getting table structure: {e}")

    def count_records(self, table_name):
        """
        获取指定表格中记录的数量

        Args:
        - table_name: 表格名称

        Returns:
        - 记录数量
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    return count
        except pymysql.Error as e:
            print(f"Error counting records: {e}")

    def delete_data_by_condition(self, table_name, condition):
        """
        根据指定条件删除表格中的数据

        Args:
        - table_name: 表格名称
        - condition: 删除条件，例如 "age > 30"

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    delete_query = f"DELETE FROM {table_name} WHERE {condition}"
                    cursor.execute(delete_query)
                    conn.commit()
                    print(f"Data matching condition '{condition}' deleted successfully.")
        except pymysql.Error as e:
            print(f"Error deleting data by condition: {e}")

    def update_data_by_condition(self, table_name, update_values, condition):
        """
        根据指定条件更新表格中的数据

        Args:
        - table_name: 表格名称
        - update_values: 要更新的值和列名的字典，例如 {"age": 25, "name": "John"}
        - condition: 更新条件，例如 "id = 1"

        Returns:
        - 无
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    set_clause = ", ".join([f"{column} = %s" for column in update_values.keys()])
                    update_query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
                    cursor.execute(update_query, list(update_values.values()))
                    conn.commit()
                    print(f"Data matching condition '{condition}' updated successfully.")
        except pymysql.Error as e:
            print(f"Error updating data by condition: {e}")

    def execute_sql(self, sql_query):
        """
        执行用户输入的任意SQL语句

        Args:
        - sql_query: 要执行的SQL语句

        Returns:
        - 查询结果（如果有）
        """
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    if sql_query.strip().split(" ", 1)[0].upper() == "SELECT":
                        return cursor.fetchall()
                    else:
                        conn.commit()
                        print("SQL query executed successfully.")
        except pymysql.Error as e:
            print(f"Error executing SQL query: {e}")


if __name__ == '__main__':
    db = Database()
    data_processor = DataProcessing(db)
    data_processor.create_table(table_name="radar_data", columns=[
        ('id', 'INT AUTO_INCREMENT PRIMARY KEY'),
        ('distance', 'FLOAT'),
        ('x_position', 'FLOAT'),
        ('y_position', 'FLOAT'),
        ('angle', 'FLOAT')]
        )
    










