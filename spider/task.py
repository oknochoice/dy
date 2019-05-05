import logging
import threading

class ThreadTask_imp:
    def __init__(self):
        logging.debug('%s begin', __class__)
        self.con = threading.Condition(threading.Lock())
        self.source = []
    def addTasks(self, tasks:list, isBegin = False):
        logging.debug('%s begin', __class__)
        self.con.acquire()
        if isBegin == True:
            self.source[0:0] = tasks
        else:
            self.source += tasks
        logging.debug('task %d', len(tasks))
        logging.debug('source %d', len(self.source))
        self.con.notify()
        self.con.release()
    def run(self):
        logging.debug('%s begin', __class__)
        while True:
            logging.debug('loop begin')
            self.con.acquire()
            if len(self.source) != 0:
                logging.info('working current tasks num is %d', len(self.source))
                self.current_task = self.source[0]
                self.source.pop(0)
                self.con.release()
            else:
                logging.info('waiting current tasks num is %d', len(self.source))
                self.con.wait()
                self.con.release()
                continue
            logging.info(self.current_task.desc())
            self.current_task.run()

class ThreadSource:
    def run(self):
        logging.debug('%s begin', __class__)
    def desc(self):
        return 'no desc'

class ThreadTask:
    def __init__(self):
        self.imp = ThreadTask_imp()
        self.threading = threading.Thread(target=self.imp.run, daemon=True)
        self.threading.start()
    def addTasks(self, tasks:list, isBegin = False):
        self.imp.addTasks(tasks, isBegin)
