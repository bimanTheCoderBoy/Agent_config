from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.memory import MemorySaver
import aiosqlite
DB_PATH = "app/checkpointer/sqlite.db"  

class CheckpointerSingleton:
    """
    Singleton for AsyncSqliteSaver with proper async initialization.
    """
    _instance: AsyncSqliteSaver | None = None

    @classmethod
    async def initialize(cls):
        """
        Initializes the async SQLite checkpointer singleton if not already set up.
        """
        if cls._instance is None:
            cls._instance=MemorySaver()
            # Use from_conn_string for file-based or in-memory SQLite
            # Example: ":memory:" for in-memory, or a file path for persistence
            # async with aiosqlite.connect(DB_PATH,check_same_thread=False) as conn:
                
            #     cls._instance =AsyncSqliteSaver(conn=conn)
            #     cls._instance=await cls._instance.setup()

    @classmethod
    def get(cls):
        """
        Returns the initialized AsyncSqliteSaver singleton.
        Raises if not yet initialized.
        """
        if cls._instance is None:
            raise RuntimeError("Checkpointer not initialized yet. Call await CheckpointerSingleton.initialize() first.")
        return cls._instance
