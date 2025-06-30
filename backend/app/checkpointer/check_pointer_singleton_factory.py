
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver    
DB_PATH = "app/checkpointer/sqlite.db"
DB_URI = "postgresql://postgres:root@localhost:5432/postgres"
class CheckpointerSingleton:
    
    instance = None

    @classmethod
    async def initialize(cls):
        if cls.instance is None:
            pool = AsyncConnectionPool(conninfo=DB_URI, max_size=10)
            async with pool.connection() as conn:
              await  conn.set_autocommit(True)
            saver=AsyncPostgresSaver(pool)
            await saver.setup()
            cls.instance=saver

    @classmethod
    def get(cls):
        if cls.instance is None:
            raise RuntimeError("Checkpointer not initialized yet")
        return cls.instance
   