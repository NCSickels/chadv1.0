"""Basic logger test."""

from log.clogger import Logger


def test_logger() -> None:
    logger = Logger()
    print("\n================= Begin Unit Tests for Logger =================\n")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
    logger.sent_traffic("This is a sent traffic message.")
    logger.received_traffic("This is a received traffic message.")
    logger.ad_response("This is an Active Defense Response message.")
    print("\n================= End Unit Tests for Logger =================\n")


if __name__ == "__main__":
    test_logger()
