import redis
import os

class RedisClient:
    _instance = None  # Class-level singleton instance

    def __init__(self):
        if RedisClient._instance is not None:
            raise Exception("Use RedisClient.get_instance() instead of instantiating directly.")

        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True
        )

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get(self, key: str) -> str:
        return self.client.get(key)

    def set(self, key: str, value: str, ttl_seconds: int = 86400):
        self.client.set(key, value, ex=ttl_seconds)

    def delete(self, key: str):
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        return self.client.exists(key) > 0
