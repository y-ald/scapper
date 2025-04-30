import random
import time


def wait_random_delay(base=30):
    delay = base + random.randint(0, 5)
    time.sleep(delay)
