import datetime
import logging.config
import asyncio
from aiohttp import web
from aiohttp_sse import sse_response

from web.automatonrunner import AutomatonRunner


async def get_logs(request: web.BaseRequest):
    if 'start' in request.query.keys():
        try:
            start = datetime.datetime.fromisoformat(request.query.get('start'))
        except ValueError:
            start = datetime.datetime.now() - datetime.timedelta(days=1)
    else:
        start = datetime.datetime.now() - datetime.timedelta(days=1)

    if 'end' in request.query.keys():
        try:
            end = datetime.datetime.fromisoformat(request.query.get('end'))
        except ValueError:
            end = datetime.datetime.now()
    else:
        end = datetime.datetime.now()

    print('logs start:{0} end:{1}'.format(start, end))

    return web.json_response({'data': [
        {'id': 1, 'entry_id': '516612345677890', 'reason': '布控理由理由理由', 'req': '布控要求要求要求', 'note': '备注备注备注',
         'containers': 3, 'exam_req': '查验要求', 'exam_mode': '查验方式', 'exam_containers': 2,
         'exam_time': '2018-09-18T17:53:22Z'}
    ]})


async def post_start(request):
    if not request.app['automaton_runner']['runner'].is_running:
        request.app['automaton_runner']['runner'].run_once_no_wait()
        return web.json_response({"status": "started"})
    else:
        return web.json_response({"status": "running"})


async def get_status(request):
    if not request.app['automaton_runner']['runner'].is_running:
        return web.json_response({"status": "stopped"})
    else:
        return web.json_response({"status": "running"})


async def subscribe_status(request):
    loop = request.app.loop
    async with sse_response(request) as resp:
        while True:
            if request.app['automaton_runner']['runner'].is_running:
                await resp.send('running')
            else:
                await resp.send('stopped')
            await asyncio.sleep(10, loop=loop)


async def subscribe_status_test(request):
    d = """
    <html>
        <head>
            <script type="text/javascript"
                src="http://code.jquery.com/jquery.min.js"></script>
            <script type="text/javascript">
            var evtSource = new EventSource("/api/control/subscribe");
            evtSource.onmessage = function(e) {
              $('#response').html(e.data);
            }
            </script>
        </head>
        <body>
            <h1>Response from server:</h1>
            <pre id="response"></pre>
        </body>
    </html>
    """
    return web.Response(text=d, content_type="text/html")


async def setup_automaton(app):
    runner = AutomatonRunner(app)
    app['automaton_runner'] = {
        'runner': runner,
        'task': app.loop.create_task(runner.run_forever_in_background())
    }


async def cleanup_automaton(app):
    app['automaton_runner']['task'].cancel()
    await app['automaton_runner']['task']


def main():
    app = web.Application()
    app.add_routes([web.get("/api/logs", get_logs),
                    web.get("/api/control/status", get_status),
                    web.post("/api/control/start", post_start),
                    web.get("/api/control/subscribe", subscribe_status),
                    web.get("/test", subscribe_status_test)])

    app.on_startup.append(setup_automaton)
    app.on_cleanup.append(cleanup_automaton)

    web.run_app(app)


if __name__ == "__main__":
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'default'
            },
            'rotate_file': {
                'level': 'DEBUG',
                'formatter': 'default',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': 'automaton.log',
                'encoding': 'utf8',
                'when': 'D',
                'interval': 30
            },
            'errors': {
                'level': 'ERROR',
                'formatter': 'default',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'automaton_error.log',
                'encoding': 'utf8',
                'maxBytes': 102400000,
                'backupCount': 30
            }
        },
        'loggers': {
            'RiskExamAutomaton': {
                'level': 'DEBUG'
            },
            '': {
                'level': 'INFO',
                'handlers': ['console', 'rotate_file', 'errors']
            }
        }
    })

    main()
