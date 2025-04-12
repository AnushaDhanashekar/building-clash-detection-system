import json
import logging
from datetime import datetime, timezone

from typing import List, Optional

logger = logging.getLogger(__name__)

def get_wb_root_loggers() -> List[str]:
    # The manager field is monkey patched in logging package.
    # noinspection PyUnresolvedReferences
    return [
        key
        for key in logging.Logger.manager.loggerDict.keys()  # type: ignore
        if "." not in key and key.startswith("wb_")
    ]

def set_log_levels(extra_logger: Optional[logging.Logger] = None):
    """
    Set level on loggers so we get more log output from our own logging.

    The extra logger typically covers top level module loggers
    which does not follow the standard wb_xxx package structure.
    """

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    if extra_logger is not None:
        extra_logger.setLevel(logging.DEBUG)

    # Cover any logger used for in modules that are executed, so that
    # __name__ is __main__. This covers e.g. Glue scripts.
    main_logger = logging.getLogger("__main__")
    main_logger.setLevel(logging.DEBUG)

    # Configure level for all loaded top-level loggers that belong to us.
    for key in get_wb_root_loggers():
        logging.getLogger(key).setLevel(logging.DEBUG)


def configure_lambda_logging(logger: Optional[logging.Logger] = None):
    """
    Configure logging for a Lambda handler.

    Pass the logger of the Lambda handler if it exists.

    This should only be called inside a handler method to avoid
    side-effects during module loading.
    """

    # Lambda will pre-configure a handler, so if one is already configured
    # leave it as-is. It will not work to use .basicConfig unless more work
    # is done.
    # See https://stackoverflow.com/a/56579088
    # For the default logging format for Lambda, see:
    # https://gist.github.com/niranjv/fb95e716151642e8ca553b0e38dd152e#gistcomment-2389022
    if len(logging.getLogger().handlers) == 0:
        logging.basicConfig(
            format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
        )

    set_log_levels(logger)