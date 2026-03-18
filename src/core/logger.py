import os
import sys
from loguru import logger

# Configure loguru for production-grade logging
def setup_logger():
    # Remove default handler
    logger.remove()
    
    # Add structured terminal output
    logger.add(
        sys.stderr, 
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=os.getenv("LOG_LEVEL", "INFO")
    )
    
    # Add persistent log file with rotation
    logger.add(
        "logs/osrs_platform_{time}.log", 
        rotation="1 week", 
        retention="1 month", 
        compression="zip",
        level="DEBUG"
    )

setup_logger()
logger.info("Market Intelligence Platform Logging Initialized")
