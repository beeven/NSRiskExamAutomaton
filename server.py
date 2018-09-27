import datetime
import logging.config
import sqlite3
import os
import json
import asyncio
from aiohttp import web
from aiohttp_sse import sse_response

from automatonrunner import AutomatonRunner

async def get_index(request):
    return web.FileResponse("./client/dist/index.html")


async def get_logs(request):
    if 'sort' in request.query.keys():
        sort = request.query.get('sort').lower()
        if sort not in ('id', 'entry_id', 'reason', 'req', 'note',
                        'container_num', 'exam_req', 'exam_method', 'exam_container_num', 'exam_time'):
            sort = 'exam_time'
    else:
        sort = 'exam_time'

    if 'order' in request.query.keys():
        order = request.query.get('order').lower()
        if order not in ('asc', 'desc'):
            order = 'desc'
    else:
        order = 'desc'

    if 'page' in request.query.keys():
        try:
            page = int(request.query.get('page'))
        except ValueError:
            page = 0
    else:
        page = 0

    if 'size' in request.query.keys():
        try:
            size = int(request.query.get('size'))
            if not 0 < size <= 30:
                size = 15
        except ValueError:
            size = 15
    else:
        size = 15

    if 'filter' in request.query.keys():
        keyword = request.query.get('filter')
        if not keyword.isdigit():
            keyword = '%'
        else:
            keyword = '%' + keyword + '%'
    else:
        keyword = '%'

    cursor = request.app['dbconn'].cursor()
    cursor.execute("""select count(*) 'count' from logs
        where entry_id like ?
        """, (keyword,))
    row = cursor.fetchone()
    row_count = row["count"]
    cursor.execute("""
        select id, entry_id, reason, req, note, 
        container_num, exam_req, exam_method, exam_container_num, strftime('%Y-%m-%dT%H:%M:%S', exam_time) as 'exam_time'
        from logs
        where entry_id like ?
        order by {0} {1}
        limit ? offset ?""".format(sort, order), (keyword, size, size * page))

    rows = cursor.fetchall()
    cursor.close()

    return web.json_response({'data': rows, 'total': row_count})


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
    async with sse_response(request) as resp:
        async for line in request.app['automaton_runner']['runner'].log_source:
            await resp.send(json.dumps({'message': line,
                                        'running': request.app['automaton_runner']['runner'].is_running}))


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
        # 'task': app.loop.create_task(runner.run_forever_in_background(1800))
    }


async def cleanup_automaton(app):
    # app['automaton_runner']['task'].cancel()
    # await app['automaton_runner']['task']
    pass


async def init_db(app):
    app['dbconn'] = sqlite3.connect("logs.db")

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    app['dbconn'].row_factory = dict_factory


async def cleanup_db(app):
    app['dbconn'].close()


def main():

    app = web.Application(debug=True)

    os.makedirs('./client/dist', exist_ok=True)
    app.add_routes([web.get("/api/logs", get_logs),
                    web.get("/api/control/status", get_status),
                    web.post("/api/control/start", post_start),
                    web.get("/api/control/subscribe", subscribe_status),
                    web.get("/test", subscribe_status_test),
                    web.get("/", get_index),
                    web.static("/", "./client/dist")])

    app.on_startup.append(setup_automaton)
    app.on_cleanup.append(cleanup_automaton)

    app.on_startup.append(init_db)
    app.on_cleanup.append(cleanup_db)

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
