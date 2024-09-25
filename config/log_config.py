import logging
import os
import socket
import sys
from logging.handlers import TimedRotatingFileHandler

# 获取本地IP地址
local_ip = socket.gethostbyname(socket.gethostname())

# 如果是打包后的环境，使用 sys._MEIPASS 获取资源路径
base_dir = getattr(sys, 'frozen', False) and getattr(sys, '_MEIPASS', os.path.abspath(".")) or os.path.abspath(".")

# 创建 logs 目录（如果不存在）
log_dir_info = os.path.join(base_dir, "logs/info")
log_dir_error = os.path.join(base_dir, "logs/error")
# 创建 logs 目录（如果不存在）
os.makedirs("logs/error", exist_ok=True)  # 存放 error 日志
os.makedirs("logs/info", exist_ok=True)   # 存放 info 日志

# 日志格式，增加IP地址
LOG_FORMAT = f"%(asctime)s - {local_ip} - %(name)s - %(levelname)s - %(message)s"

# 定义日志记录器
logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)  # 设置日志记录器的全局级别为 DEBUG

# 创建处理器：INFO 级别日志按天轮转到 info.log
info_handler = TimedRotatingFileHandler(
    "logs/info/info.log", when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# 创建处理器：ERROR 级别日志按天轮转到 error.log
error_handler = TimedRotatingFileHandler(
    "logs/error/error.log", when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # 控制台输出 DEBUG 及以上的所有日志
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# 将处理器添加到记录器
logger.addHandler(info_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)
