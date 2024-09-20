import logging
import os
 
if os.path.exists('./temp') is False:
    os.makedirs('./temp')

# 创建一个logger
logger = logging.getLogger('tencent_speech.log')
logger.setLevel(logging.INFO)  # 设置日志级别

# 创建一个handler，用于写入日志文件
file_handler = logging.FileHandler('./temp/tencent_speech.log')
file_handler.setLevel(logging.INFO)  # 只记录ERROR及以上级别的日志到文件

# 再创建一个handler，用于将日志输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # 控制台输出DEBUG及以上级别的日志

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 使用logger记录日志
# logger.debug('这是一个debug信息')
# logger.info('这是一个info信息')
# logger.warning('这是一个warning信息')
# logger.error('这是一个error信息')