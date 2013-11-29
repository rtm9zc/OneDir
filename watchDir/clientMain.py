from multiprocessing import Process

from watchDir import OneDir_Observer
from sendingClient import LocalMachine

if __name__ == "__main__":

    lm = LocalMachine('testUser', '/home/student/OneDir/test_user/', address='localhost')
    OneDog = OneDir_Observer(lm)
    OneDog.startWatching()

    #p = Process(target=OneDog.startWatching)
    #p.start()

    #p.join()