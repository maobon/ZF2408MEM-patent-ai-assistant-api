# coding: utf-8


import pytz
from datetime import datetime

def getNowDateTime():
    # 获取当前 UTC 时间
    utc_now = datetime.utcnow()

    # 定义东八区时区
    timezone = pytz.timezone('Asia/Shanghai')

    # 将 UTC 时间转换为东八区时间
    utc_now = pytz.utc.localize(utc_now)
    shanghai_now = utc_now.astimezone(timezone)
    return shanghai_now
