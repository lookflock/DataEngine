
def log_info(msg, logger=None):
    if logger:
        logger.info(msg)
    else:
        print(msg)

def log_error(msg, logger=None):
    if logger:
        logger.error(msg)
    else:
        print("ERROR:", msg)
