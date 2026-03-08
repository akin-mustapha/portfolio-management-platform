import os
import logging

def customer_logger (log_name):
  try:
    log_dir_name = 'logs'
    os.path.exists(log_dir_name) or os.makedirs(log_dir_name)
    log_name = log_name.lower()
    logging.basicConfig(
      level=logging.INFO,
      filename=f'{log_dir_name}/{log_name}.log',
      filemode='a',
      format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
      )
    return logging
  except Exception as e:
    raise