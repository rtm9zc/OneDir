import logging
import StringIO

class adminLog:

    def __init__(self):
        #self.logStream= StringIO.StringIO()
        logging.basicConfig(format='[%(asctime)s %(name)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, file='log.txt')
        self.logger = logging.getLogger('logger')
        handler = logging.FileHandler('log.txt')
        self.logger.addHandler(handler)
        #handler = logging.StreamHandler()
        #self.logger.addHandler(handler)


    def add(self,line):
        self.logger.info(line)

    def __add__(self, line):
        self.logger.info(line)

    def end(self):
        self.logStream.close()

    def getString(self):
        self.adminString = "blank"
            #self.logStream.getvalue()
        #print 'MMMMMMMMMMMMMMMMMMMMMMMMM'
        return self.adminString