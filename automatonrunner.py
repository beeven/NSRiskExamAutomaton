import asyncio
import functools
import logging
from logging.handlers import QueueListener, QueueHandler
import queue
from concurrent.futures import ThreadPoolExecutor
from rx.subjects import ReplaySubject


import examautomaton

from rx.concurrency import AsyncIOScheduler
from rx.core import Observable
from rx.internal import extensionmethod
from rx.concurrency import ThreadPoolScheduler


future_ctor = asyncio.Future


@extensionmethod(Observable)
async def __aiter__(self):
    source = self

    class AIterator:
        def __init__(self):
            self.notifications = []
            self.future = future_ctor()
            pool_scheduler = ThreadPoolScheduler()

            source.materialize().subscribe_on(pool_scheduler).subscribe(self.on_next)

        def feeder(self):
            if not self.notifications or self.future.done():
                return

            notification = self.notifications.pop(0)
            dispatch = {
                'N': lambda: self.future.set_result(notification.value),
                'E': lambda: self.future.set_exception(notification.exception),
                'C': lambda: self.future.set_exception(StopAsyncIteration)
            }

            dispatch[notification.kind]()

        def on_next(self, notification):
            self.notifications.append(notification)
            self.feeder()

        async def __anext__(self):
            self.feeder()

            value = await self.future
            self.future = future_ctor()
            return value

    return AIterator()


class AutomatonRunner(object):

    def __init__(self, app, interval=1800, buffer_size=20):
        self.app = app
        self.is_running = False
        self.interval = interval
        self.logger = logging.getLogger("AutomatonRunner")
        self.pool = ThreadPoolExecutor()
        self.logging_queue = queue.Queue(-1)

        self.logger.addHandler(QueueHandler(self.logging_queue))

        self.log_source = ReplaySubject(buffer_size=buffer_size)
        logging_handler = LoggingRxHandler(self.log_source)
        logging_handler.setFormatter(logging.Formatter('\033[34m%(asctime)s \033[91m%(name)s\033[0m %(message)s'))
        self.logging_queue_listener = QueueListener(self.logging_queue, logging_handler)
        self.logging_queue_listener.start()

    def __del__(self):
        self.logging_queue_listener.stop()

    async def run_forever_in_background(self, delay=0):
        try:
            await asyncio.sleep(delay)
            while True:
                if not self.is_running:
                    fn = functools.partial(self.run)
                    await self.app.loop.run_in_executor(self.pool, fn)
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            self.logger.info("Runner stopping")

    def run_once_no_wait(self):
        if not self.is_running:
            fn = functools.partial(self.run)
            self.logger.info("Start running.")
            self.app.loop.run_in_executor(self.pool, fn)

    def run(self):
        self.is_running = True
        automaton = examautomaton.RiskExamAutomaton(logging_queue=self.logging_queue)
        try:
            automaton.run()
        except Exception as ex:
            self.logger.warning("Automaton encountered an error: {0}".format(ex))

        del automaton
        self.is_running = False



class LoggingRxHandler(logging.Handler):

    def __init__(self, subject):
        super().__init__()
        self.subject = subject

    def emit(self, record):
        msg = self.format(record)
        self.subject.on_next(msg)

