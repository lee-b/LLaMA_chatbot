import string
import threading


def random_hash():
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(9))


class RunThread(threading.Thread):
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        super().__init__()

    def run(self):
        self.result = asyncio.run(self.func(*self.args, **self.kwargs))
