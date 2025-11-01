"""
Logging configuration for UMIS RAG system.
"""

import sys
from pathlib import Path

from loguru import logger

from umis_rag.core.config import settings


def setup_logger() -> None:
    """Configure loguru logger with file and console handlers."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )
    
    # File handler
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
    )
    
    logger.info(f"Logger initialized. Log file: {settings.log_file}")


# Initialize on import
setup_logger()

