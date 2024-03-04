import schedule
from action import *

schedule.every(10).seconds.do(post_articles)
while True:
    schedule.run_pending()
    time.sleep(1)