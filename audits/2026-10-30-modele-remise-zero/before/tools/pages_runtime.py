"""Browser adapter for the existing frozen Python model; no economic formulas."""
import json
from pathlib import PurePosixPath
from urllib.parse import parse_qs, urlsplit

from document_excerpt import document_excerpt
from study_app import ScenarioError, Study
from study_snapshot import encode


class PagesRuntime:
    def __init__(self, bundle, expected_version, expected_contract):
        self.study = Study.from_release(bundle)
        if self.study.version != expected_version or self.study.simulation_contract() != expected_contract:
            raise ValueError('Incompatible static model')
        # Deployment is an immutable delivery of the current study, not another UI mode.
        self.study.edition = dict(mode='current', date=self.study.data['scenario']['date'])

    def request(self, path, body_json=''):
        """Return the same JSON payloads and scenario errors as the local adapter."""
        url = urlsplit(path)
        if url.scheme or url.netloc:
            return self._reply(dict(error='missing_document'), 404)
        if url.path == '/api/simulate':
            try:
                if not isinstance(body_json, str) or not 0 < len(body_json.encode('utf-8')) < 100_000:
                    raise ScenarioError('invalid')
                body = json.loads(body_json)
                if not isinstance(body, dict) or set(body) != {'parameters', 'model_version'}:
                    raise ScenarioError('invalid')
                return self._reply(self.study.simulate(body['parameters'], body['model_version']))
            except ScenarioError as error:
                return self._reply(dict(error=error.code, field=error.field), 422)
            except (ValueError, TypeError, KeyError):
                return self._reply(dict(error='invalid'), 400)
            except AssertionError:
                return self._reply(dict(error='internal'), 500)
        if url.path == '/api/document' and not body_json:
            try:
                reference = parse_qs(url.query).get('path', [''])[0]
                source = reference.partition('#')[0]
                suffix = PurePosixPath(source).suffix
                if suffix not in ('.md', '.yaml', '.py'):
                    raise ScenarioError('missing_document')
                raw = self.study.document_bytes(reference)
                excerpt = document_excerpt(raw.decode('utf-8-sig'), suffix, reference.partition('#')[2])
                return self._reply(dict(path=source, format=suffix, **excerpt))
            except ScenarioError as error:
                return self._reply(dict(error=error.code), 404)
            except (ValueError, OSError):
                return self._reply(dict(error='internal'), 500)
        return self._reply(dict(error='missing_document'), 404)

    @staticmethod
    def _reply(data, status=200):
        return encode(dict(status=status, data=data)).decode('utf-8')


def load_runtime(bundle_json, expected_version, expected_contract):
    return PagesRuntime(json.loads(bundle_json), expected_version, expected_contract)
