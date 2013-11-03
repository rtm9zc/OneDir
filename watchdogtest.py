import sys
import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class OneDirHandler(FileSystemEventHandler):
    localstring = (str)
    localstring = os.getcwd()
    locallen = localstring.__len__()+1
    def on_moved(self, event):
        #Only really called on name change
        #Should tell server to change name on file (src_path) to (dest_path)
        source = event.src_path[self.locallen:]
        dest = event.dest_path[self.locallen:]
        if (source.find(".git") == -1 and source.find(".idea") == -1):
            print("File moved! (" + source + " at time: " +
              time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            print("Destination: " + dest)
    def on_created(self, event):
        #Called on making new file
        #Should send file over to server
        source = event.src_path[self.locallen:]
        if (source.find(".git") == -1 and source.find(".idea") == -1):
            print("File created! (" + source + " at time: " +
              time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
    def on_deleted(self, event):
        #Called on deletion of file/directory
        #Server should delete same file
        source = event.src_path[self.locallen:]
        if (source.find(".git") == -1 and source.find(".idea") == -1):
            print("File deleted! (" + source + " at time: " +
              time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
    def on_modified(self, event):
        source = event.src_path[self.locallen:]
        if (source.find(".git") == -1 and source.find(".idea") == -1):
            print("File modified! (" + source + " at time: " +
              time.strftime("%Y-%m-%d %H:%M:%S")+ ")")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = OneDirHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()