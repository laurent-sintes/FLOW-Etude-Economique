"""Durations and machine-readable outcomes, including failed runs."""
from datetime import datetime, timezone
import json
import sys
from threading import Event, Lock, Thread
from pathlib import Path
import time
import unittest
import uuid
import xml.etree.ElementTree as ET


def run_directory(root):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    path = root / 'tmp' / 'validation' / (stamp + '-' + uuid.uuid4().hex[:8])
    path.mkdir(parents=True)
    return path


def test_ids(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from test_ids(item)
        else:
            yield item.id()


class Progress:
    """Live phase/test state, flushed output and a heartbeat during slow checks."""
    def __init__(self, directory, last, stream=None, interval=15):
        self.directory, self.last = Path(directory), Path(last)
        self.stream = stream if stream is not None else sys.stdout
        self.started = time.perf_counter()
        self.lock, self.stop = Lock(), Event()
        self.state = dict(status='running', phase='initialization', completed=0, total=0,
                          failures=0, current_test=None, directory=str(directory))
        self.phases = []
        self.issues = set()
        self.interval = interval
        self.thread = Thread(target=self.heartbeat, daemon=True)
        self.emit()
        self.thread.start()

    def emit(self, console=True):
        self.state['elapsed_seconds'] = round(time.perf_counter() - self.started, 1)
        text = json.dumps(self.state, ensure_ascii=False)
        for path in (self.directory / 'progress.json', self.last):
            pending = path.with_suffix('.pending-' + self.directory.name)
            pending.write_text(text, encoding='utf-8')
            pending.replace(path)
        if console:
            state = self.state
            print(f"[validation {state['elapsed_seconds']:.1f}s] {state['status']} | "
                  f"{state['phase']} | tests {state['completed']}/{state['total']} | "
                  f"failures {state['failures']}" +
                  (f" | {state['current_test']}" if state['current_test'] else ''),
                  file=self.stream, flush=True)

    def heartbeat(self):
        while not self.stop.wait(self.interval):
            with self.lock:
                self.emit()

    def phase(self, name):
        with self.lock:
            self.phases.append(name)
            self.state.update(phase=name, current_test=None)
            self.emit()

    def end_phase(self):
        with self.lock:
            if self.phases:
                self.phases.pop()
            self.state.update(phase=self.phases[-1] if self.phases else 'between_phases', current_test=None)
            self.emit()

    def schedule(self, total):
        with self.lock:
            self.state['total'] = total
            self.emit()

    def test_started(self, name):
        with self.lock:
            self.state['current_test'] = name
            self.emit(console=False)

    def issue(self, name):
        with self.lock:
            self.issues.add(name)
            self.state['failures'] = len(self.issues)
            self.emit()

    def test_finished(self):
        with self.lock:
            self.state['completed'] += 1
            self.state['current_test'] = None
            self.emit(console=self.state['completed'] % 10 == 0 or self.state['completed'] == self.state['total'])

    def close(self, status):
        self.stop.set()
        self.thread.join()
        with self.lock:
            self.state.update(status=status, current_test=None)
            self.emit()


class TimedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        self.progress = kwargs.pop('progress', None)
        super().__init__(*args, **kwargs)
        self.records = []
        self.running = {}

    def startTest(self, test):
        if self.progress:
            self.progress.test_started(test.id())
        self.running[test.id()] = dict(id=test.id(), status='passed', started=time.perf_counter())
        super().startTest(test)

    def outcome(self, test, status, message=''):
        record = self.running.setdefault(test.id(), dict(id=test.id(), started=time.perf_counter()))
        record.update(status=status, message=message)
        if status in ('failure', 'error'):
            if self.progress:
                self.progress.issue(test.id())
            self.stream.writeln('\n' + test.id() + '\n' + message)

    def addFailure(self, test, err):
        self.outcome(test, 'failure', self._exc_info_to_string(err, test))
        super().addFailure(test, err)

    def addError(self, test, err):
        self.outcome(test, 'error', self._exc_info_to_string(err, test))
        super().addError(test, err)

    def addSkip(self, test, reason):
        self.outcome(test, 'skipped', reason)
        super().addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self.outcome(test, 'expected_failure', self._exc_info_to_string(err, test))
        super().addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self.outcome(test, 'failure', 'Unexpected success')
        super().addUnexpectedSuccess(test)

    def addSubTest(self, test, subtest, err):
        if err is not None:
            self.outcome(test, 'failure', str(subtest) + '\n' + self._exc_info_to_string(err, test))
        super().addSubTest(test, subtest, err)

    def stopTest(self, test):
        record = self.running.pop(test.id())
        record['seconds'] = round(time.perf_counter() - record.pop('started'), 6)
        self.records.append(record)
        if self.progress:
            self.progress.test_finished()
        super().stopTest(test)

    def stopTestRun(self):
        # setUpClass / tearDownClass errors do not call startTest / stopTest.
        for record in self.running.values():
            record['seconds'] = round(time.perf_counter() - record.pop('started'), 6)
            self.records.append(record)
        self.running.clear()
        super().stopTestRun()


def save_report(report, directory, last):
    text = json.dumps(report, ensure_ascii=False, indent=2)
    (directory / 'report.json').write_text(text, encoding='utf-8')
    # Atomic stable pointer avoids leaving a truncated report after interruption.
    pending = last.with_suffix('.pending-' + directory.name + '.json')
    pending.write_text(text, encoding='utf-8')
    pending.replace(last)
    records = report.get('test_results', [])
    suite = ET.Element('testsuite', name='FLOW', tests=str(len(records)),
                       failures=str(sum(r['status'] == 'failure' for r in records)),
                       errors=str(sum(r['status'] == 'error' for r in records)))
    for record in records:
        node = ET.SubElement(suite, 'testcase', name=record['id'], time=str(record['seconds']))
        status = record['status']
        if status in ('failure', 'error', 'skipped', 'expected_failure'):
            tag = 'skipped' if status == 'expected_failure' else status
            ET.SubElement(node, tag).text = record.get('message', '')
    if report.get('error'):
        ET.SubElement(ET.SubElement(suite, 'testcase', name='validation_pipeline'), 'error').text = report['error']
        suite.set('tests', str(len(records) + 1))
        suite.set('errors', str(int(suite.get('errors')) + 1))
    ET.ElementTree(suite).write(directory / 'junit.xml', encoding='utf-8', xml_declaration=True)
