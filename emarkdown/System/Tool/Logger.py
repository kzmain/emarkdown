import logging


class Logger:
    @staticmethod
    def error_logger(log_info):
        logging.error("[System Error]: %s" % log_info)
