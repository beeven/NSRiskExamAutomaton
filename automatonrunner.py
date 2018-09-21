import asyncio
import functools
import logging
from concurrent.futures import ThreadPoolExecutor
import examautomaton


class AutomatonRunner(object):

    def __init__(self, app, interval=1800):
        self.app = app
        self.is_running = False
        self.interval = interval
        self.logger = logging.getLogger("AutomatonRunner")
        self.pool = ThreadPoolExecutor()

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
            self.app.loop.run_in_executor(self.pool, fn)

    def run(self):
        self.is_running = True
        automaton = examautomaton.RiskExamAutomaton()
        try:
            automaton.run()
        except Exception as ex:
            self.logger.warning("Automaton encountered an error: {0}".format(ex))
        del automaton
        self.is_running = False
