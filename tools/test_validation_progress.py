"""Live progress must reflect tests, failures and long-running phases."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from validation_reporting import Progress, TimedResult


class ValidationProgressTests(unittest.TestCase):
    def test_counts_failures_and_current_test_are_written_before_completion(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            out = io.StringIO()
            progress = Progress(root, root / 'last.json', stream=out)
            try:
                progress.phase('python_tests')
                progress.schedule(2)
                progress.test_started('test.slow')
                live = json.loads((root / 'last.json').read_text())
                self.assertEqual(live['current_test'], 'test.slow')
                self.assertEqual(live['completed'], 0)
                progress.issue('test.slow')
                progress.issue('test.slow')
                progress.test_finished()
                self.assertEqual(json.loads((root / 'progress.json').read_text())['failures'], 1)
                progress.end_phase()
            finally:
                progress.close('failed')
            live = json.loads((root / 'last.json').read_text())
            self.assertEqual((live['status'], live['completed'], live['total']), ('failed', 1, 2))
            self.assertIn('tests 1/2', out.getvalue())
            self.assertFalse(progress.thread.is_alive())

    def test_real_runner_reports_success_failure_skip_and_class_error(self):
        class Fixture(unittest.TestCase):
            def test_ok(self): pass
            def test_failure(self): self.fail('fixture')
            @unittest.skip('fixture')
            def test_skip(self): pass
        class Broken(unittest.TestCase):
            @classmethod
            def setUpClass(cls): raise ValueError('class fixture')
            def test_never(self): pass
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            progress = Progress(root, root / 'last.json', stream=io.StringIO())
            try:
                suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(Fixture), unittest.defaultTestLoader.loadTestsFromTestCase(Broken)])
                progress.schedule(suite.countTestCases())
                result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=lambda *a, **k: TimedResult(*a, progress=progress, **k)).run(suite)
                self.assertFalse(result.wasSuccessful())
            finally:
                progress.close('failed')
            live = json.loads((root / 'last.json').read_text())
            self.assertEqual(live['completed'], result.testsRun)
            self.assertEqual(live['failures'], 2)
            self.assertEqual(len(result.records), 4)

    def test_heartbeat_updates_while_phase_is_blocked(self):
        from threading import Event
        class SignalStream(io.StringIO):
            def __init__(self):
                super().__init__()
                self.signal = Event()
            def write(self, value):
                if 'long_phase' in value: self.signal.set()
                return super().write(value)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            stream = SignalStream()
            progress = Progress(root, root / 'last.json', stream=stream, interval=0.02)
            try:
                progress.phase('long_phase')
                stream.signal.clear()
                self.assertTrue(stream.signal.wait(2))
                self.assertEqual(json.loads((root / 'last.json').read_text())['phase'], 'long_phase')
            finally:
                progress.close('passed')
