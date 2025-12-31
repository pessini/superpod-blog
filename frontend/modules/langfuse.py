from langfuse import get_client
from .logging import logger

langfuse = get_client()

try:
    if langfuse.auth_check():
        logger.info("✅ Langfuse connection successful!")
    else:
        logger.error("❌ Langfuse authentication failed. Check credentials.")
except Exception as e:
    logger.error(f"❌ Langfuse connection error: {str(e)}")
