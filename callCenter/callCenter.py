import logging
import queue
from threading import Event

from callCenter.call import Call
from callCenter.employee import Manager, Respondent

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(threadName)s %(message)s')


class CallCenter:
    def __init__(self, respondent_count):
        self.calls_q = queue.Queue()
        self.escalated_calls_q = queue.Queue()
        self.shut_down_event = Event()
        self.respondents = []
        for i in range(respondent_count):
            resp = Respondent("Respondent-" + str(i), self.shut_down_event, self.calls_q, self.escalated_calls_q)
            resp.start()
        self.manager = Manager("Manager ", self.shut_down_event, self.calls_q, self.escalated_calls_q)
        self.manager.start()

    def request_call(self, call_details):
        call = Call(call_details)
        self.calls_q.put_nowait(call)
        logging.info(str(call_details) + " added to the queue")

    def shut_down(self):
        self.calls_q.join()
        self.escalated_calls_q.join()
        self.shut_down_event.set()
        for resp in self.respondents:
            resp.join()
        self.manager.join()
        logging.info("all tasks done")
