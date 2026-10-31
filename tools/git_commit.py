"""Prepare a reviewable local commit, then commit exactly that unchanged scope."""
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from threading import Thread
import time
import importlib.metadata
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
REPOSITORY = 'laurent-sintes/FLOW-Etude-Economique'
WHITESPACE = 'blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol'


class CommitError(RuntimeError):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


class Git:
    def __init__(self, root):
        self.root = Path(root).resolve()
        bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
        self.binary = str(bundled) if bundled.is_file() else shutil.which('git')
        if not self.binary:
            raise CommitError('Git est introuvable')

    def raw(self, *args, allowed=(0,)):
        options = [] if args[0] == 'check-ignore' else ['--literal-pathspecs']
        result = subprocess.run([self.binary, *options, *args], cwd=self.root, capture_output=True)
        if result.returncode not in allowed:
            raise CommitError('Git ' + args[0] + ' : ' + result.stderr.decode('utf-8', errors='replace').strip())
        return result.stdout

    def text(self, *args, **kwargs):
        return self.raw(*args, **kwargs).decode('utf-8', errors='replace').strip()

    def names(self, *args):
        return [name.decode('utf-8') for name in self.raw(*args).split(b'\0') if name]

    def entries(self):
        entries = {}
        for row in self.raw('ls-files', '--stage', '-z').split(b'\0'):
            if row:
                state, name = row.split(b'\t', 1)
                if state.split()[-1] != b'0':
                    raise CommitError('Résoudre les conflits de l’index avant de préparer le commit')
                entries[name.decode('utf-8')] = state.decode('ascii')
        return entries

    def repository(self):
        if Path(self.text('rev-parse', '--show-toplevel')).resolve() != self.root:
            raise CommitError('Le dossier ne correspond pas à la racine Git')
        branch = self.text('branch', '--show-current')
        if branch != 'main':
            raise CommitError('Le workflow courant attend la branche main')
        for direction in ((), ('--push',)):
            urls = self.text('remote', 'get-url', *direction, '--all', 'origin').splitlines()
            if not urls or any(not re.fullmatch(r'(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)' + re.escape(REPOSITORY) + r'(?:\.git)?/?', url) for url in urls):
                raise CommitError('Origin doit cibler exclusivement le dépôt FLOW-Etude-Economique autorisé')
        return dict(root=str(self.root), branch=branch, head=self.text('rev-parse', 'HEAD'),
                    upstream=self.text('rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{upstream}', allowed=(0, 128)),
                    author=self.text('var', 'GIT_AUTHOR_IDENT').rsplit(' ', 2)[0])


def source_hashes(root):
    from validation_changes import snapshot
    return {name: item['sha256'] for name, item in snapshot(root)['files'].items()}


def normalize_paths(root, names):
    paths = []
    for name in names:
        path = (root / name).resolve()
        if not path.is_relative_to(root) or path == root or path.is_dir():
            raise CommitError('Choisir des fichiers précis dans le dépôt : ' + name)
        relative = path.relative_to(root).as_posix()
        if any(part in ('.git', 'node_modules', '__pycache__', '.venv') for part in Path(relative).parts) or relative.startswith(('tmp/', 'app/dist/', 'app/dist-pages/')):
            raise CommitError('Un cache ou un artefact local ne peut pas être inclus : ' + relative)
        if (root / name).is_symlink():
            raise CommitError('Examiner les liens symboliques séparément')
        paths.append(relative)
    if not paths:
        raise CommitError('Indiquer au moins un fichier')
    return sorted(set(paths))


def inspect_scope(git, names, inputs):
    paths = normalize_paths(git.root, names)
    entries = git.entries()
    for name in paths:
        exists = (git.root / name).is_file()
        tracked = bool(git.raw('ls-files', '-z', '--', name))
        if not exists and not tracked:
            raise CommitError('Fichier absent et non suivi : ' + name)
        if exists and not tracked and git.raw('check-ignore', '--', name, allowed=(0, 1)):
            raise CommitError('Fichier ignoré par Git : ' + name)
    staged = set(git.names('diff', '--cached', '--name-only', '-z'))
    unstaged = set(git.names('diff', '--name-only', '-z'))
    partial = set(paths) & staged & unstaged
    if partial:
        raise CommitError('Index partiel à préserver. Examiner ces fichiers avant de continuer : ' + ', '.join(sorted(partial)))
    dirty = set(git.names('diff', 'HEAD', '--name-only', '-z'))
    untracked = set(git.names('ls-files', '--others', '--exclude-standard', '-z'))
    outside = ((dirty | untracked) & set(inputs)) - set(paths)
    if outside:
        raise CommitError('Des entrées de validation modifiées sont hors périmètre : ' + ', '.join(sorted(outside)))
    if not ((dirty | untracked) & set(paths)):
        raise CommitError('Aucun changement dans les fichiers sélectionnés')
    return paths, entries


def github_metadata(root):
    cache = root / 'tmp/git-commit/repository.json'
    try:
        record = json.loads(cache.read_text(encoding='utf-8'))
        if time.time() - record['checked_at'] < 600:
            return record['repository']
    except (OSError, ValueError, KeyError):
        pass
    request = Request('https://api.github.com/repos/' + REPOSITORY, headers={'User-Agent': 'FLOW-local-commit', 'Accept': 'application/vnd.github+json'})
    try:
        with urlopen(request, timeout=15) as response:
            data = json.load(response)
    except OSError as error:
        raise CommitError('Vérification du dépôt GitHub indisponible : ' + str(error)) from error
    result = dict(full_name=data['full_name'], visibility=data.get('visibility'), private=data['private'])
    write_json(cache, dict(checked_at=time.time(), repository=result))
    return result


def public_repository(metadata):
    if metadata.get('full_name') != REPOSITORY or metadata.get('private') is not False or metadata.get('visibility') != 'public':
        raise CommitError('Le dépôt GitHub attendu doit être public, sans changement automatique de visibilité')


def check_report(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    if value.get('status') != 'passed':
        raise CommitError('Un rapport de contrôle n’est pas réussi : ' + str(path))
    return value


def file_proofs(paths):
    return {str(Path(path).resolve()): digest(Path(path).read_bytes()) for path in paths}


def environment():
    env = dict(os.environ)
    bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin'
    if not shutil.which('node') and (bundled / 'node.exe').is_file():
        env['PATH'] = str(bundled) + os.pathsep + env.get('PATH', '')
    if os.name == 'nt' and 'PLAYWRIGHT_CHROMIUM_EXECUTABLE' not in env:
        for path in ('C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'):
            if Path(path).is_file():
                env['PLAYWRIGHT_CHROMIUM_EXECUTABLE'] = path
                break
    return env


def runtime_signature():
    node = subprocess.run(['node', '--version'], env=environment(), capture_output=True, text=True)
    if node.returncode:
        raise CommitError('Node.js est requis pour valider l’application')
    return dict(python=sys.version, executable=sys.executable, node=node.stdout.strip(),
                packages={name: importlib.metadata.version(name) for name in ('PyYAML', 'jsonschema')})


def verify_proofs(proofs):
    if not proofs:
        raise CommitError('Aucune preuve de validation')
    for path, expected in proofs.items():
        if not Path(path).is_file() or digest(Path(path).read_bytes()) != expected:
            raise CommitError('Une preuve de validation a changé. Refaire la préparation')
        check_report(path)


def command(root, args):
    result = subprocess.run(args, cwd=root, env=environment())
    if result.returncode:
        raise CommitError('Un contrôle a échoué. Aucun commit créé')


def validate(root, inputs):
    receipt = root / 'tmp/git-commit/validation.json'
    try:
        cached = json.loads(receipt.read_text(encoding='utf-8'))
        if cached['inputs'] == inputs and cached['runtime'] == runtime_signature():
            verify_proofs(cached['reports'])
            return dict(cached, reused=True)
    except (OSError, ValueError, KeyError, CommitError):
        pass
    model_report = None
    try:
        manifest = json.loads((root / 'tmp/validation-full-manifest.json').read_text(encoding='utf-8'))
        if {n: item['sha256'] for n, item in manifest['files'].items()} == inputs:
            previous = check_report(manifest['report'])
            if previous['mode'] == 'full':
                model_report = Path(manifest['report'])
    except (OSError, ValueError, KeyError, CommitError):
        pass
    if model_report is None:
        command(root, [sys.executable, '-m', 'tools.check_model', '--auto', '--browser'])
        last = check_report(root / 'tmp/check-model-last.json')
        model_report = Path(last['directory']) / 'report.json'
    # Verify the real Pages prefix too, using the existing build and browser scripts.
    command(root, [sys.executable, '-m', 'tools.prepare_static_app', '--output', 'app/dist-pages', '--base', '/FLOW-Etude-Economique/'])
    oracle = root / 'tmp/git-commit/pages-cases.json'
    command(root, [sys.executable, '-m', 'tools.pages_validation', '--output', str(oracle)])
    browser_report = root / 'tmp/git-commit/pages-browser.json'
    from browser_checks import QuietHandler
    class Handler(QuietHandler):
        def translate_path(self, path):
            path = path[len('/FLOW-Etude-Economique'):] if path.startswith('/FLOW-Etude-Economique/') else '/__not_found__'
            return super().translate_path(path)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(root / 'app/dist-pages')))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        command(root, ['node', 'app/scripts/verify-pages.mjs', '--url', f'http://127.0.0.1:{server.server_port}/FLOW-Etude-Economique/', '--cases', str(oracle), '--output', str(browser_report)])
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    browser = check_report(browser_report)
    if browser.get('httpApiRequests') != []:
        raise CommitError('Une API HTTP a été appelée dans le navigateur')
    if source_hashes(root) != inputs:
        raise CommitError('Les sources ont changé pendant les contrôles')
    result = dict(inputs=inputs, runtime=runtime_signature(), reports=file_proofs([model_report, browser_report]), reused=False)
    write_json(receipt, result)
    return result


def prepare(root, names, message, plan_only=False, validator=None, metadata=None):
    root = Path(root).resolve()
    git = Git(root)
    repository = git.repository()
    inputs = source_hashes(root)
    paths, entries = inspect_scope(git, names, inputs)
    if not message.strip() or '\0' in message:
        raise CommitError('Le message de commit est vide ou invalide')
    files = {name: digest((root / name).read_bytes()) if (root / name).is_file() else None for name in paths}
    runtime = runtime_signature()
    remote = (metadata or github_metadata)(root)
    public_repository(remote)
    validation = None if plan_only else (validator or validate)(root, inputs)
    if validation is not None:
        verify_proofs(validation['reports'])
    if source_hashes(root) != inputs or git.entries() != entries or git.repository() != repository:
        raise CommitError('Le candidat ou l’index a changé pendant la préparation')
    if any((digest((root / name).read_bytes()) if (root / name).is_file() else None) != expected for name, expected in files.items()):
        raise CommitError('Un fichier sélectionné a changé pendant les contrôles')
    result = dict(format=1, repository=repository, github=remote, paths=paths, files=files, inputs=inputs, runtime=runtime,
                  index=entries, message=message, ready=not plan_only, validation=validation,
                  diff=git.text('diff', 'HEAD', '--stat', '--', *paths))
    result['sha256'] = digest(json.dumps(result, ensure_ascii=False, sort_keys=True).encode())
    path = root / 'tmp/git-commit/plan.json'
    write_json(path, result)
    return path, result


def commit(root, plan):
    root = Path(root).resolve()
    git = Git(root)
    data = json.loads(Path(plan).read_text(encoding='utf-8'))
    checksum = data.pop('sha256')
    if digest(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()) != checksum:
        raise CommitError('Le plan a été modifié. Refaire la préparation')
    if data.get('format') != 1:
        raise CommitError('Format de préparation inconnu')
    if not data['ready'] or not data.get('validation'):
        raise CommitError('Le plan est une prévisualisation non validée')
    if git.repository() != data['repository'] or source_hashes(root) != data['inputs'] or git.entries() != data['index'] or runtime_signature() != data['runtime']:
        raise CommitError('HEAD, l’index ou les sources ont changé. Refaire la préparation')
    paths, entries = inspect_scope(git, data['paths'], data['inputs'])
    for name, expected in data['files'].items():
        actual = digest((root / name).read_bytes()) if (root / name).is_file() else None
        if actual != expected:
            raise CommitError('Un fichier sélectionné a changé : ' + name)
    public_repository(data['github'])
    verify_proofs(data['validation']['reports'])
    message = root / 'tmp/git-commit/message.txt'
    message.write_text(data['message'], encoding='utf-8')
    git.raw('add', '-A', '--', *paths)
    outside = {n: v for n, v in entries.items() if n not in paths}
    if {n: v for n, v in git.entries().items() if n not in paths} != outside:
        raise CommitError('L’index hors périmètre a changé. Aucun commit créé')
    git.raw('-c', 'core.whitespace=' + WHITESPACE, 'diff', '--cached', '--check', '--', *paths)
    # --only keeps unrelated staged work out of this commit and in the real index.
    git.raw('commit', '--only', '-F', str(message), '--', *paths)
    sha = git.text('rev-parse', 'HEAD')
    if {n: v for n, v in git.entries().items() if n not in paths} != outside:
        raise CommitError('Commit créé (' + sha + ') mais l’index hors périmètre a changé. Examiner le statut')
    result = dict(commit=sha, subject=data['message'].splitlines()[0], paths=paths,
                  remaining=git.text('status', '--short'), pushed=False)
    write_json(root / 'tmp/git-commit/result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='action', required=True)
    preparation = modes.add_parser('prepare', help='Préparer un périmètre vérifié sans modifier l’index')
    preparation.add_argument('--paths', nargs='+', required=True)
    message = preparation.add_mutually_exclusive_group(required=True)
    message.add_argument('--message')
    message.add_argument('--message-file', type=Path)
    preparation.add_argument('--plan-only', action='store_true', help='Prévisualiser sans tests, plan inutilisable pour committer')
    execution = modes.add_parser('commit', help='Créer uniquement le commit local préparé')
    execution.add_argument('--plan', type=Path, default=ROOT / 'tmp/git-commit/plan.json')
    args = parser.parse_args()
    try:
        if args.action == 'prepare':
            text = args.message if args.message is not None else args.message_file.read_text(encoding='utf-8-sig')
            path, result = prepare(ROOT, args.paths, text, args.plan_only)
            print(json.dumps(dict(plan=str(path), ready=result['ready'], paths=result['paths'], diff=result['diff'], validation=result['validation']), ensure_ascii=False, indent=2))
        else:
            print(json.dumps(commit(ROOT, args.plan), ensure_ascii=False, indent=2))
    except (CommitError, OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
