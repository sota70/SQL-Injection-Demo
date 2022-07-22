import json
import mysql.connector as m_connector
from typing import TypeVar, Generic


T = TypeVar("T")

class SQL:

    def __init__(self, host: str, user_name: str, password: str):
        self._host: str = host
        self._user_name: str = user_name
        self._password: str = password
        self.result: any = None
    
    def execute(self, database: str, command: str):
        raise NotImplementedError()

class MySQL(SQL):

    def __init__(self, host: str, user_name: str, password: str):
        super().__init__(host, user_name, password)
    
    def execute(self, database: str, command: str):
        with m_connector.connect(
            host=self._host,
            user=self._user_name,
            password=self._password
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"USE {database}")
                cursor.execute(command)
                self.result = cursor.fetchall()

class SQLFilter(Generic[T]):

    def filter(self) -> T:
        raise NotImplementedError()

class SQLInjectionFilter(SQLFilter):

    __sql_related_str: list[str] = [
        "OR",
        "AND",
        "=",
        "SELECT",
        "DROP",
        "INSERT"
    ]

    def __init__(self, input_text: str):
        super().__init__()
        self.__input_text: str = input_text

    def filter(self):
        injection_deleted_text: str = self.__input_text
        for sql_str in self.__sql_related_str:
            injection_deleted_text = injection_deleted_text.replace(sql_str, f'"{sql_str}"')
        return injection_deleted_text

def get_mysql_password(path: str) -> str:
    with open(path, "r") as file:
        data: dict[str, any] = json.load(file)
        return data["password"]

if __name__ == "__main__":
    mysql_password: str = get_mysql_password("src/sql_password.json")
    user_name: str = input("User Name: ")
    user_password: str = input("Password: ")
    # injection filter
    username_injection_filter: SQLFilter = SQLInjectionFilter(user_name)
    password_injection_filter: SQLFilter = SQLInjectionFilter(user_password)
    user_name = username_injection_filter.filter()
    user_password = password_injection_filter.filter()
    mysql: SQL = MySQL("localhost", "root", mysql_password)
    mysql_command: str = f"SELECT name, password FROM users WHERE name = '{user_name}' AND password = '{user_password}'"
    print(f"MySQL Command: {mysql_command}")
    mysql.execute("mysql", mysql_command)
    print(mysql.result)
