import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

DB_PATH = "app/checkpointer/sqlite.db"
class CheckpointerSingleton:
    
    instance = None

    @classmethod
    async def initialize(cls):
        if cls.instance is None:
            async with aiosqlite.connect(DB_PATH,check_same_thread=False) as sqlite_conn:
                cls.instance = AsyncSqliteSaver(sqlite_conn)

    @classmethod
    def get(cls):
        if cls.instance is None:
            raise RuntimeError("Checkpointer not initialized yet")
        return cls.instance
    @classmethod
    async def close(cls):
        if cls.instance is not None:
           await cls.instance.conn.close()