import flow_2_regressions
from threading import Thread

t_tag = Thread(target=flow_2_regressions.run_tag)
t_tag.start()