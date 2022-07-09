# Generating Alerts from Database Structure Change Log Events Produced by IRI Ripcurrent

## Synopsis

Ripcurrent logs database change events related to structure in the source database being monitored.

This log can be monitored for new events in order to send alerts.

This example is a sample Python application that monitors the Ripcurrent log file and triggers Windows toast notifications when new database structure change events are written to a log file by IRI Ripcurrent.

The alerts can be a signal to re-run IRI wizards that generated scripts based on the contents of the database at that moment, such as the IRI Schema Data Class Search Wizard.

## Requirements

Python 3 must be installed.

## Execution

The dependencies for this example can be installed by running `pip install -r requirements.txt`, and the script can be run by executing the command `python main.py`.
