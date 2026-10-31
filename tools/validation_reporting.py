"""Durations and machine-readable outcomes, including failed runs."""
from datetime import datetime, timezone
import json
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


class TimedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.running = {}

    def startTest(self, test):
        self.running[test.id()] = dict(id=test.id(), status='passed', started=time.perf_counter())
        super().startTest(test)

    def outcome(self, test, status, message=''):
        record = self.running.setdefault(test.id(), dict(id=test.id(), started=time.perf_counter()))
        record.update(status=status, message=message)
        if status in ('failure', 'error'):
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
