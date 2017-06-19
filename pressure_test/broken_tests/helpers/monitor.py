import sched, time
from threading import Thread


camera_id_2_monitor = {}


class Monitor(object):
    def __init__(self):
        self.schedule = sched.scheduler(time.time, time.sleep)
        self.events = []
    
    def add_periodic_jobs(self, abs_time, action, actionargs=()):
        piror = 1
        print( "PERIOD JOB: ", abs_time, action, actionargs)
        evt = self.schedule.enterabs(abs_time, piror, action, actionargs)
        self.events.append(evt)

    def start(self):
        # create threading to run
        t = Thread(
            target=self.schedule.run,
        )

        t.start()
    
    def stop(self):
        if self.schedule:
            for event in self.schedule.queue:
                self.schedule.cancel(event)
        self.events = []

