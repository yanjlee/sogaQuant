 # -*- coding: UTF-8 -*-
'''
'''
import logging
class LogUtils(object):
    def __init__(self,fileName):
        logging.basicConfig(filename=fileName,level=logging.DEBUG,format='%(asctime)s %(name)-12s %(levelname)-6s %(message)s',datefmt='%y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger("recommend_sys")
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
    def logFile(self,content,level="INFO"):
        if level == "INFO":
            self.logger.info(content)
        else:
            self.logger.error(content)
if __name__ == "__main__":
    logger = LogUtils("/htdocs/python/logs.txt")
    logger.logFile("abc")
