import threading
from time import sleep, perf_counter

counter = 0


def task():
    global counter
    print('start task')
    sleep(1)
    counter += 1
    print('end task')


def task2():
    print('start task2')
    sleep(10)
    print('end task2')


t2 = threading.Thread(target=task2, name='task2')

t2.start()
for i in range(10):
    t1 = threading.Thread(target=task, name='task')
    t1.start()
    t1.join()
t2.join()

print(counter)



