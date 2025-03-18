from neo4j import GraphDatabase
from langchain_neo4j import Neo4jGraph
import os
from dotenv import load_dotenv

load_dotenv()



class Neo4jClient:
    _instance = None

    def __init__(self):
        if Neo4jClient._instance is not None:
            raise Exception("Use Neo4jClient.get_instance() instead of instantiating directly.")

        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "test")
        self.kg = Neo4jGraph(url=self.uri, username=self.username, password=self.password)
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def query_knowledge_graph(self, query: str, params: dict = None):
        return self.kg.query(query, params=params)

    def close(self):
        self.driver.close()

    def run_query(self, query: str, params: dict = None):
        with self.driver.session() as session:
            return session.run(query, params or {}).data()

    def validate_query(self, query: str) -> bool:
        try:
            self.run_query("EXPLAIN " + query)
            return True
        except Exception:
            return False

    def write_transaction(self, func, *args, **kwargs):
        with self.driver.session() as session:
            return session.write_transaction(func, *args, **kwargs)
