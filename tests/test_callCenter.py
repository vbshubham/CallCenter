import unittest
from random import random
from time import sleep
from unittest import TestCase

from callCenter.callCenter import CallCenter
from config.config import RESPONDENT_COUNT


class TestCallCenter(TestCase):
    def setUp(self) -> None:
        self.call_center = CallCenter(respondent_count=RESPONDENT_COUNT)

    def test_request_call(self):
        for i in range(5):
            sleep(random())
            self.call_center.request_call("call-"+str(i))
        self.call_center.shut_down()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main(failfast=True)
