from futures import ThreadPoolExecutor, ProcessPoolExecutor
import time, threading
from abc import ABCMeta, abstractmethod






class Pool(object):
    __metaclass__ = ABCMeta
    class debugger(threading.Thread):
        def __init__(self, pool, interval = 5):
            self.pool = pool
            self.interval = interval
            threading.Thread.__init__(self)

        def start(self):
            self._running = True
            self.startTime = time.time()
            self.lastTime = time.time()
            self.lastNumber = 0
            self.numberAtStart = self.pool.processed
            threading.Thread.start(self)

        def stop(self):
            self._running = False

        def debug(self):
            meanSpeed = (self.pool.processed - self.numberAtStart) / (time.time() - self.startTime)
            instantSpeed = (self.pool.processed - self.lastNumber) / (time.time() - self.lastTime)
            print "%s Threads: %s Remaining: %s Speed: %s / %s Done: %s" % (
                ("["+self.pool.name+"]").ljust(15),
                str(self.pool.maxWorkers).ljust(4),
                str(self.pool.getQueueSize()).ljust(3),
                ("%.2f" % instantSpeed).ljust(9),
                ("%.2f" % meanSpeed).ljust(9),
                str(self.pool.processed)
            )
            self.lastTime = time.time()
            self.lastNumber = self.pool.processed

        def run(self):
            while(self._running):
                self.debug()
                time.sleep(self.interval)

    def __init__(self, maxWorkers, queueSize):
        self.maxWorkers = maxWorkers
        self._pool = ThreadPoolExecutor(max_workers=maxWorkers)
        self._pool._work_queue.maxsize = queueSize
        #self._pool = ProcessPoolExecutor(max_workers=20)
        #self._pool._work_ids.maxsize = 2

        self.processed = 0
        self.debugger = self.__class__.debugger(self)
        self.debugger.start()

    def getQueueSize(self):
        return self._pool._work_queue.qsize()
        #return self._pool._work_ids.qsize()*self.maxWorkers


    @property
    def name(self):
        return self.__class__.__name__

    def submit(self, task, *args, **kwargs):
        def handleSubmit():
            try:
                result = task(*args, **kwargs)
            except Exception as e:
                self.handleError(task, e)
            else:
                self.agregate(task, result)
            self.processed += 1

        self._pool.submit(handleSubmit)

    def waitAndShutdown(self):
        self._pool.shutdown(wait = True)
        self.debugger.stop()

    @abstractmethod
    def handleError(self, task, e):
        pass

    @abstractmethod
    def agregate(self, task, result):
        pass

def test(arg):
    pass



p = Pool(maxWorkers=4, queueSize=20)

for i in xrange(500000000):
    p.submit(test, str(i))

print "Envoi fini"

p.waitAndShutdown()

print "Programme fini"