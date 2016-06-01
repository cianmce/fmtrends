import time

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=3)
def timed_job():
    print 'Doing stuff every 3 mins'
    time.sleep(30)
    print 'Done'


sched.start()



# def timed_job():
#     print '\n\n\tThis job is run every 5 minutes.\n\n'


# def main():
#     timed_job()
#     time.sleep(5*60)
#     timed_job()

# if __name__ == '__main__':
#     main()