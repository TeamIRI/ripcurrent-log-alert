import argparse
import logging
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from win10toast import ToastNotifier

# Sample application to trigger Windows toast notifications when new database structure change events are written to
# a log file by IRI Ripcurrent.

directory = ''  # The directory of the specified Ripcurrent log file.
file = ''  # The location to the Ripcurrent log file as specified.


def read(filename):
    toaster = ToastNotifier()
    last_line = ''
    with open(filename) as f:
        data = f.read().split('\n')[:-1]
        for line in data:
            last_line = line
    toaster.show_toast("Ripcurrent Database Structure Change Alert",
                       f'Database structure change event detected: "{last_line}".')


class DirectoryWatch:

    def __init__(self):
        self.observer = Observer()

    def run(self, directory):
        event_handler = Handler()
        self.observer.schedule(event_handler, directory)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            logging.info("Observer Stopped")
            exit(1)

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == 'created' or event.event_type == 'modified':
            if event.src_path == file:
                # Event is created, you can process it now
                logging.info("Watchdog received {} event - {}.".format(event.event_type, event.src_path))
                time.sleep(1)
                read(event.src_path)


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(description='File watcher for Ripcurrent schema change event log.')
    parser.add_argument('file', type=str,
                        help="The location of the log file.")
    args = parser.parse_args()
    if args.file:
        file = args.file
    directory = str(Path(file).resolve().parent)
    watch = DirectoryWatch()
    watch.run(directory)
