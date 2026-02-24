"""日志工具模块"""
from loguru import logger
import sys
from config import settings


def setup_logger():
    logger.remove()
    logger.add(sys.stdout, level=settings.log_level, colorize=True,
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> - <level>{message}</level>")
    logger.add(settings.log_file, level=settings.log_level, rotation="100 MB",
               retention="30 days", encoding="utf-8")
    logger.info(f"日志系统初始化完成，级别: {settings.log_level}")
