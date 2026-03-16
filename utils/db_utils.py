"""
Database connection utilities with connection pooling and context management.
"""
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2 import pool, extras
from psycopg2.extensions import connection as PGConnection

from config.settings import db_config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Connection pool (singleton)
_connection_pool: Optional[pool.ThreadedConnectionPool] = None


def get_connection_pool(min_conn: int = 2, max_conn: int = 10) -> pool.ThreadedConnectionPool:
    """
    Get or create a connection pool.
    
    Args:
        min_conn: Minimum connections in pool
        max_conn: Maximum connections in pool
        
    Returns:
        ThreadedConnectionPool instance
    """
    global _connection_pool
    
    if _connection_pool is None:
        logger.info(f"Creating connection pool (min={min_conn}, max={max_conn})")
        _connection_pool = pool.ThreadedConnectionPool(
            min_conn,
            max_conn,
            host=db_config.host,
            port=db_config.port,
            database=db_config.database,
            user=db_config.user,
            password=db_config.password
        )
    
    return _connection_pool


@contextmanager
def get_connection() -> Generator[PGConnection, None, None]:
    """
    Context manager for database connections.
    Automatically returns connection to pool on exit.
    
    Yields:
        Database connection
    """
    conn_pool = get_connection_pool()
    conn = conn_pool.getconn()
    
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn_pool.putconn(conn)


@contextmanager
def get_cursor(cursor_factory=None):
    """
    Context manager for database cursors.
    
    Args:
        cursor_factory: Optional cursor factory (e.g., RealDictCursor)
        
    Yields:
        Database cursor
    """
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=cursor_factory or extras.RealDictCursor)
        try:
            yield cursor
        finally:
            cursor.close()


def execute_query(query: str, params: tuple = None, fetch: bool = False):
    """
    Execute a single query with optional parameters.
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch: Whether to fetch results
        
    Returns:
        Query results if fetch=True, else None
    """
    with get_cursor() as cursor:
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        return cursor.rowcount


def execute_batch(query: str, data: list, page_size: int = 1000) -> int:
    """
    Execute batch insert/update using execute_values for better performance.
    
    Args:
        query: SQL query string with %s placeholders
        data: List of tuples containing data
        page_size: Batch size for inserts
        
    Returns:
        Number of rows affected
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            extras.execute_batch(cursor, query, data, page_size=page_size)
            return cursor.rowcount


def close_pool():
    """Close all connections in the pool."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
        logger.info("Connection pool closed")
