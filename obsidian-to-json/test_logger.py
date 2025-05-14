from utils.logger import logger, log_processing_result, log_error

def test_logging():
    print("Starting logging test...")
    
    # Test basic logging
    logger.debug("This is a debug message", extra={"status": "test"})
    logger.info("This is an info message", extra={"status": "test"})
    logger.warning("This is a warning message", extra={"status": "test"})
    logger.error("This is an error message", extra={"status": "test"})
    
    # Test log_processing_result
    log_processing_result(
        status="test",
        duration_sec=1.23,
        files_scanned=100,
        files_indexed=50,
        destination_path="/test/path"
    )
    
    # Test log_error
    try:
        raise ValueError("Test exception")
    except ValueError as e:
        log_error("Test error occurred", exception=e)
    
    print("Logging test complete. Check your log file.")
    
    # Force flush all handlers
    for handler in logger.handlers:
        handler.flush()

if __name__ == "__main__":
    test_logging()
