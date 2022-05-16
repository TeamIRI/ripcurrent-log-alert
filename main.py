import argparse
import json
import linecache
import logging
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from win10toast import ToastNotifier

# Sample application to trigger Windows toast notifications when new database structure change events are written to
# a log file by IRI Ripcurrent.

lines = []  # The lines that make up the current event.
directory = ''  # The directory of the specified Ripcurrent log file.
file = ''  # The location to the Ripcurrent log file as specified.
current_line = 1  # Current line being processed from Ripcurrent log.
line_number_tracker_file = None  # File to log current line number.
line_json = None  # Python dictionary with key of line_number.


def read(filename):
    toaster = ToastNotifier()
    global current_line
    line = linecache.getline(filename, current_line)
    if line != '':
        current_line += 1
        line_json['line_number'] = current_line
        with open('line_number.json', 'w') as f:
            f.write(json.dumps(line_json))
    while line != '':
        lines.append(line)
        if 'detected for table' in line:  # 'detected for table signals the end of an event.
            text_of_lines = ''.join([str(item) for item in lines])
            toaster.show_toast("Ripcurrent Database Structure Change Alert",
                               f'Database structure change event detected: "{text_of_lines}".')
            lines.clear()
        line_json['line_number'] = current_line
        with open('line_number.json', 'w') as f:
            f.write(json.dumps(line_json))
        current_line += 1
        line = linecache.getline(filename, current_line)


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
    try:
        line_number_tracker_file = open('line_number.json')
        text = line_number_tracker_file.read()
        if text != '':
            line_json = json.loads(text)
            current_line = int(line_json['line_number'])
        else:
            line_json = {"line_number": current_line}
        line_number_tracker_file.close()
    except OSError as e:
        line_json = {"line_number": current_line}
    watch = DirectoryWatch()
    watch.run(directory)
