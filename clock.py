import time

def timed_job():
    print '\n\n\tThis job is run every 10 minutes.\n\n'


def main():
    timed_job()
    # time.sleep(5*60)
    # timed_job()

if __name__ == '__main__':
    main()