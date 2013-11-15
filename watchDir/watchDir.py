import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class OneDir_Observer():

    def __init__(self, local):
        self.lm = local
#
        #self.logging.basicConfig(level=logging.INFO,
        #                    format='%(asctime)s - %(message)s',
        #                    datefmt='%Y-%m-%d %H:%M:%S')
        #path = sys.argv[1] if len(sys.argv) > 1 else '.'

    def startWatching(self):
        self.event_handler = OneDirHandler(self.lm)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.lm.oneDir, recursive=True)
        self.observer.start()
        self.observer.join()


class OneDirHandler(FileSystemEventHandler):
    #localstring = (str)
    #localstring = os.getcwd()
    #locallen = localstring.__len__()+1
    #machine = (LocalMachine)
    def __init__(self, local):
        self.machine = local

    def on_moved(self, event):
        #Only really called on name change
        #Should tell server to change name on file (src_path) to (dest_path)
        source = event.src_path
        dest = event.dest_path

        if source.find(".goutputstream") == -1 and source[len(source)-1] != '~':
            print("File moved! (" + source + " at time: " +
            time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            print("Destination: " + dest)
            self.machine.moved(source, dest)
    def on_created(self, event):
        #Called on making new file
        #Should send file over to server
        source = event.src_path
        if source.find(".goutputstream") == -1 and source[len(source)-1] != '~':
            print("File created! (" + source + " at time: " +
            time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            self.machine.created(source)
    def on_deleted(self, event):
        #Called on deletion of file/directory
        #Server should delete same file
        source = event.src_path
        if source.find(".goutputstream") == -1 and source[len(source)-1] != '~':
            print("File deleted! (" + source + " at time: " +
            time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            self.machine.deleted(source)
    def on_modified(self, event):
        source = event.src_path
        if source.find(".goutputstream") == -1 and source[len(source)-1] != '~':
            print("File modified! (" + source + " at time: " +
            time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            self.machine.modified(source)
