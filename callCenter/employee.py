import logging
import queue
from abc import ABC, abstractmethod
from random import random
from threading import Thread
from time import sleep

from config.config import QUEUE_TIME_OUT, HANDLING_TIME, HANDLING_PROBABILITY


class Employee(ABC, Thread):
    def __init__(self, name, shut_down_event, resp_task_q, escalated_task_q):
        super().__init__(name=name)
        self.escalated_task_q = escalated_task_q
        self.resp_task_q = resp_task_q
        self.shut_down_event = shut_down_event

    def run(self):
        self.take_call()

    @abstractmethod
    def take_call(self):
        pass

    @abstractmethod
    def handle_call(self, call):
        pass


class Manager(Employee):
    def handle_call(self, call):
        logging.info(str(call.details) + "handled")
        return True

    def __init__(self, name, event, q, q1):
        super().__init__(name, event, q, q1)

    def take_call(self):
        while not self.shut_down_event.is_set():
            try:
                call = self.escalated_task_q.get(timeout=QUEUE_TIME_OUT)
                self.handle_call(call)
                self.escalated_task_q.task_done()
            except queue.Empty:
                try:
                    call = self.resp_task_q.get(timeout=QUEUE_TIME_OUT)
                    logging.info(call.details + "picked up without escalation")
                    self.handle_call(call)
                    self.resp_task_q.task_done()
                except queue.Empty:
                    pass


class Respondent(Employee):
    def __init__(self, name, event, q, q1):
        super().__init__(name, event, q, q1)

    def handle_call(self, call):
        handled = random() < HANDLING_PROBABILITY
        sleep(HANDLING_TIME)
        if handled:
            logging.info(str(call.details) + " handled")
        else:
            logging.info(str(call.details) + " could not be handled")
        return handled

    def take_call(self):
        while not self.shut_down_event.is_set():
            try:
                call = self.resp_task_q.get(timeout=QUEUE_TIME_OUT)
                if not self.handle_call(call):
                    logging.info(str(call.details) + "escalated")
                    self.escalated_task_q.put_nowait(call)
                self.resp_task_q.task_done()
            except queue.Empty:
                pass
