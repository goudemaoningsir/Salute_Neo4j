from neo4j import GraphDatabase

# 使用
uri = "bolt://172.29.0.104:7687"
user = "neo4j"
password = "12345678"
class Neo4jConnection:

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._session = None

    def __enter__(self):
        self._session = self._driver.session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
        self._driver.close()

    def run_query(self, query, parameters=None):
        return self._session.run(query, parameters)

    def show_databases(self):
        with self._session.begin_transaction() as tx:
            result = tx.run("SHOW DATABASES")
            return [record["name"] for record in result]

    def create_node(self, label, properties):
        query = f"CREATE (a:{label} $properties) RETURN a"
        return self.run_query(query, {"properties": properties})

    def create_relationship(self, start_node, rel_type, end_node, start_label, end_label):
        query = f"""
        MATCH (a:{start_label} {{name: $start_node}})
        MATCH (b:{end_label} {{name: $end_node}})
        CREATE (a)-[:{rel_type}]->(b)
        """
        return self.run_query(query, {"start_node": start_node, "end_node": end_node})

    def delete_node(self, label, properties):
        """
        删除具有给定标签和属性的节点。
        注意：这将删除与该节点相关的所有关系。
        """
        # 构建WHERE子句的条件部分
        conditions = " AND ".join([f"a.{key} = ${key}" for key in properties.keys()])

        query = f"MATCH (a:{label}) WHERE {conditions} DETACH DELETE a"
        return self.run_query(query, properties)


# 使用示例
with Neo4jConnection(uri, user, password) as conn:
    # 创建节点
    conn.create_node("Person", {"name": "Alice", "age": 30})
    conn.create_node("Person", {"name": "Bob", "age": 25})

    # 创建关系
    conn.create_relationship("Alice", "FRIENDS_WITH", "Bob", "Person", "Person")

    # 删除节点
    conn.delete_node("Person", {"name": "Alice"})



