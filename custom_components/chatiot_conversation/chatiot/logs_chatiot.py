from loguru import logger as _logger

def define_log_level(print_level="INFO", logfile_level="DEBUG"):
    _logger.remove()
    # _logger.add(sys.stderr, level=print_level)
    _logger.add('./log_chatiot.txt', level=logfile_level)
    return _logger

_logger = define_log_level()
