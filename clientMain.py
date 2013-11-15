from watchDir.watchDir import OneDir_Observer
from client import LocalMachine

if __name__ == "__main__":

    lm = LocalMachine('testUser', '/home/student/pycharm-community-3.0.1/OneDir/test_user/test.txt', address='localhost')
    OneDog = OneDir_Observer(lm)
    OneDog.startWatching()