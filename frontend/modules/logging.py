import logging
import warnings

def setup_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.simplefilter("ignore", category=ResourceWarning)

    return logging.getLogger(__name__)

logger = setup_logging()

    