
import logging

from rich.logging import RichHandler
from rich.console import Console

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S.%03d]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
    ],
)

logger = logging.getLogger("file_server")
logger.setLevel("INFO")
