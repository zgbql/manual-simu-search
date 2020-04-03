# -*- coding: utf-8 -*-
import sys,os
from core import index
__author__ = "xiaxia"

def start():
        index.main()

#从根目录启动，确保相对路径调用正常
if __name__ == '__main__':
    os.popen("adb start-server")
    start()

