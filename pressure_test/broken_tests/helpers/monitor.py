import sched, time
from threading import Thread
from datetime import datetime


camera_id_2_monitor = {}


class Monitor(object):
    def __init__(self):
        self.schedule = sched.scheduler(time.time, time.sleep)
        self.events = []
        self.total_events_counts = len(self.events)
    
    def add_periodic_jobs(self, abs_time, action, actionargs=()):
        piror = 1
        print( "PERIOD JOB: ", abs_time, action, actionargs)
        evt = self.schedule.enterabs(abs_time, piror, action, actionargs)
        self.events.append(evt)
        self.total_events_counts = len(self.events)
    
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
    
    def get_schedule_status(self):
        INTERNAL_ERR = 'internal error'
        WAITING, TESTING, FINISHED = 'waiting', 'processing', 'finished'
        print("schedule list: ", self.schedule.queue)
        if self.schedule.empty():
            print("IN EMPTY SCHEDULE")
            return FINISHED, len(self.schedule.queue), [ datetime.fromtimestamp(q.time) for q in self.schedule.queue ]
        elif len(self.schedule.queue) < self.total_events_counts:
            print("IN TESTING SCHEDULE")
            return TESTING, len(self.schedule.queue), [ datetime.fromtimestamp(q.time) for q in self.schedule.queue ]
        elif len(self.schedule.queue) == self.total_events_counts:
            print("IN WAITING SCHEDULE")
            return WAITING, len(self.schedule.queue), [ datetime.fromtimestamp(q.time) for q in self.schedule.queue ]
        else:
            return INTERNAL_ERR
