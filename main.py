from src.elastic.setup import setup_elastic
from src.elastic.sync import sync_elastic
from flask import Flask
from src.config.config import sync_interval
from src.app import start_flask
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from src.elastic.sync import es_sync_scheduler, close_scheduler, EndEventError, es_job_id
import multiprocessing
import signal
import sys


app = Flask(__name__)


def start_server(flask_debug=False):
    '''
    Starts docfex
    '''
    start_elastic()
    with app.app_context():
        start_flask(debug=flask_debug)


def start_elastic():
    '''
    Connects to elastic and creates a background job to kepp elastic and os in sync
    '''
    client = setup_elastic()
    # omitting a trigger removes the job from the job pool, but interval trigger first waits for the interval to finish before execution
    # => using cron first, then reschedule to interval to start job immediately  
    es_sync_scheduler.add_job(sync_elastic, id=es_job_id,
                              trigger='cron', second='*/10', kwargs={'es_client': client, 'app': app})
    es_sync_scheduler.add_listener(job_end_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    if not(es_sync_scheduler.running):
        es_sync_scheduler.start()


def job_end_listener(job_event):
    '''
    Gets called when a background job finished
    '''
    if job_event.exception:
        if type(job_event.exception) == EndEventError:
            sys.exit()
        print('scheduled job crashed')
        raise job_event.exception
    else:
        es_job = es_sync_scheduler.get_job(job_event.job_id)
        if (es_job == None) or (es_job_id != job_event.job_id):
            return
        
        print('scheduled job closed successfully')
        if es_sync_scheduler.running:
            es_job.reschedule(trigger='interval', minutes=sync_interval)
            print('rescheduled job')

        
if __name__ == '__main__':
    start_server(flask_debug=True)
