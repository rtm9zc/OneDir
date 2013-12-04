import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def getExtension(filename):
    return os.path.splitext(filename)[-1].lower()

class OneDir_Observer():

    def __init__(self, local):
        self.lm = local


    def startWatching(self):
        self.event_handler = OneDirHandler(self.lm)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.lm.oneDir, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()


class OneDirHandler(FileSystemEventHandler):

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
            if not event.is_directory:
                if getExtension(source) != '.DS_Store' and os.path.basename(source)[0] != '.':
                    self.machine.moved(source, dest)
            if event.is_directory and source != self.machine.oneDir:
                # if not os.listdir(dest):
                #     createMessage = 'isDirCreated' + dest
                #     self.machine.sendMessage(createMessage)
                #     deleteMessage = 'isDirDeleted' + source
                #     self.machine.sendMessage(deleteMessage)
                # else:
                #     deleteMessage = 'isDirDeleted' + source
                #     self.machine.sendMessage(deleteMessage)
                self.machine.moved(source, dest)


    def on_created(self, event):
        #Called on making new file
        #Should send file over to server
        source = event.src_path
        if source.find(".goutputstream") == -1 and source[len(source)-1] != '~':
            print("File created! (" + source + " at time: " +
            time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            if not event.is_directory:
                if getExtension(source) != '.DS_Store' and getExtension(source) != '.tmp' and os.path.basename(source)[0] != '.':
                    self.machine.created(source)
            if event.is_directory and source != self.machine.oneDir:
                message = 'isDirCreated' + source
                self.machine.sendMessage(message)

    def on_deleted(self, event):
        #Called on deletion of file/directory
        #Server should delete same file
        source = event.src_path
        if source.find(".goutputstream") == -1 and source[len(source)-1] != '~':
            print("File deleted! (" + source + " at time: " +
            time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            if not event.is_directory:
                if getExtension(source) != '.DS_Store' and getExtension(source) != '.tmp' and os.path.basename(source)[0] != '.':
                    self.machine.deleted(source)
            if event.is_directory:
                message = 'isDirDeleted' + source
                self.machine.sendMessage(message)

    def on_modified(self, event):
        source = event.src_path
        if source.find(".goutputstream") == -1 and source[len(source)-1] != '~':
            print("File modified! (" + source + " at time: " +
            time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            if not event.is_directory:
                if getExtension(source) != '.DS_Store' and getExtension(source) != '.tmp' and os.path.basename(source)[0] != '.':
                    self.machine.modified(source)
