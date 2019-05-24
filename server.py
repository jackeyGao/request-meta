import os
import json
import responder
import logging
from uvicorn.config import get_logger
from datetime import datetime
from db import Entry, db


api = responder.API()
env = os.environ.get('PYENV', 'DEBUG')

__version__ = 'v0.0.1'
__author__ = "JG (之及)"


def __initalize_runserver__():
    if env == 'DEBUG':
        log_level = 'debug'
    else:
        log_level = 'info'

    logger = get_logger(log_level)
    db.connect()
    db.create_tables([Entry, ])

    logger.debug('Running on debug')
    logger.info('Database is ready')

    api.run(address="0.0.0.0", debug=env=='DEBUG', logger=logger)


@api.route('/')
async def index(req, resp):
    resp.html = api.template('index.html')


@api.route('/{location}/inspect')
async def inspect(req, resp, *, location):
    if len(location) != 32:
        resp.text = "location must be UUID."
        resp.status_code = api.status_codes.bad
        return

    entrys = Entry.select().where(
        Entry.location==location
    ).order_by(Entry.time.desc())
    
    resp.html = api.template('inspect.html', **locals())


@api.route('/{location}')
async def meta(req, resp, *, location):
    if len(location) != 32:
        resp.text = "location must be UUID."
        resp.status_code = api.status_codes.bad
        return

    data = {
        "path": req.full_url,
        "method": req.method,
        "params": req.params,
        "headers": dict(req.headers),
        "body": await req.text,
        "cookies": req.cookies
    }

    Entry.create(location=location, time=datetime.now(), data=data)

    resp.media = {"status": "ok"}


@api.route('/ping')
async def ping(req, resp):
    resp.media = {
        "_": "pong",
        "version": __version__,
        "author": __author__,
    }


if __name__ == '__main__':
    __initalize_runserver__()
