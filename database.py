import sqlite3

class DataBase:
    '''Класс для работы с базой данных sqlite3'''

    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.c = self.conn.cursor()

    def __executeQuery(self, query, args=None):
        if args != None: result = self.c.execute(query, args)
        else: result = self.c.execute(query)
        return result

    def getOne(self, query, args=None):
        return self.__executeQuery(query, args).fetchone()

    def getAll(self, query, args=None):
        return self.__executeQuery(query, args).fetchall()

    def edit(self, query, args=None):
        self.__executeQuery(query, args)
        self.conn.commit()

    def close(self):
        self.conn.close()