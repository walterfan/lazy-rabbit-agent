import mgclient

# Define the Memgraph connection class
class MemgraphConnection:

    def __init__(self, host, port, username, password, database):
        self._conn = mgclient.connect(host=host, port=port, username=username, password=password)
        self._cursor = self._conn.cursor()

    def close(self):
        self._cursor.close()
        self._conn.close()

    def execute_query(self, query):
        self._cursor.execute(query)
        return self._cursor.fetchall()

class KnowledgeGraphService:
    def __init(self):
        pass


