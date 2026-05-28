#!/usr/bin/env python3
"""
Database initialization script for SentinelOS.

This script initializes the database with the schema and seed data.

Usage:
    python init_db.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import init_db, close_db, engine
from app.models.orm import Base, User
from app.utils.helpers import generate_id
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Initialize database schema."""
    settings = get_settings()
    
    logger.info("=" * 60)
    logger.info("SentinelOS Database Initialization")
    logger.info("=" * 60)
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info("")
    
    try:
        logger.info("Creating database schema...")
        await init_db()
        logger.info("✓ Database schema created successfully")
        logger.info("")
        
        logger.info("=" * 60)
        logger.info("✓ Database initialization complete!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("You can now:")
        logger.info("  1. Start the FastAPI server: uvicorn main:app --reload")
        logger.info("  2. Visit the API docs: http://localhost:8000/api/docs")
        logger.info("  3. Run tests: pytest")
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
        raise
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
