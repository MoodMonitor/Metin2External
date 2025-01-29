import logging
import os


def init_logger(logs_dir, file_name):
    base_logger = logging.getLogger('logger')
    log_format = '%(asctime)s  %(levelname)-8s  %(module)s  %(name)s.%(funcName)s  %(message)s'
    base_logger.setLevel(logging.DEBUG)
    base_formatter = logging.Formatter(log_format)
    base_handler = logging.StreamHandler()
    base_handler.setFormatter(base_formatter)
    base_handler.setLevel(logging.INFO)
    log_number = len([file for file in os.listdir(logs_dir) if file_name in file])
    file_handler = logging.FileHandler(os.path.join(logs_dir, '{}{}.log'.format(file_name, log_number + 1)))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    base_logger.addHandler(base_handler)
    base_logger.addHandler(file_handler)