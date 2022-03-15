from apscheduler.schedulers.blocking import BlockingScheduler

from auth import CHECK_PERIOD
from utils.service_utils import check_and_update_db

if __name__ == '__main__':

    scheduler = BlockingScheduler()
    scheduler.add_job(check_and_update_db, 'interval', seconds=CHECK_PERIOD)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        pass

scheduler.shutdown()
