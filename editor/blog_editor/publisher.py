from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess

from .document import PostDocument


IMAGE_LINK = re.compile(r'!\[[^]]*\]\(([^)\s]+)(?:\s+["\'][^"\']*["\'])?\)')


class PublishError(RuntimeError):
    pass


@dataclass(frozen=True)
class PublishResult:
    commit: str
    files: tuple[str, ...]
    validation: str


@dataclass(frozen=True)
class UpdateResult:
    output: str
    commit: str


@dataclass(frozen=True)
class GitIdentity:
    name: str
    email: str
    configured: bool


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def publication_files(root: Path, post: PostDocument) -> tuple[str, ...]:
    candidates = [post.path]
    references = [match.group(1) for match in IMAGE_LINK.finditer(post.body)]
    cover = post.metadata.get('image')
    if cover:
        references.append(str(cover))
    for reference in references:
        if re.match(r'^[a-z][a-z\d+.-]*:', reference, re.I) or reference.startswith('//'):
            continue
        path = (
            root / 'public' / reference.lstrip('/')
            if reference.startswith('/')
            else post.path.parent / reference
        )
        if path.is_file() and _inside(root, path):
            candidates.append(path)
    relative = {path.resolve().relative_to(root.resolve()).as_posix() for path in candidates}
    return tuple(sorted(relative))


def _run(root: Path, command: list[str], timeout=180) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise PublishError(str(error)) from error
    output = result.stdout.strip()
    if result.returncode:
        raise PublishError(output or f'Command failed: {" ".join(command)}')
    return output


def _optional(root: Path, command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ''


def git_identity(root: Path) -> GitIdentity:
    name = _optional(root, ['git', 'config', '--local', '--get', 'user.name'])
    email = _optional(root, ['git', 'config', '--local', '--get', 'user.email'])
    configured = bool(name and email)
    if not name:
        name = _optional(root, ['git', 'log', '-1', '--format=%an'])
    if not email:
        email = _optional(root, ['git', 'log', '-1', '--format=%ae'])
    return GitIdentity(name=name, email=email, configured=configured)


def configure_git_identity(root: Path, name: str, email: str) -> GitIdentity:
    name = name.strip()
    email = email.strip()
    if not name:
        raise PublishError('Author name is required.')
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
        raise PublishError('Enter a valid author email address.')
    _run(root, ['git', 'config', '--local', 'user.name', name])
    _run(root, ['git', 'config', '--local', 'user.email', email])
    return GitIdentity(name=name, email=email, configured=True)


def publish_post(root: Path, post: PostDocument) -> PublishResult:
    branch = _run(root, ['git', 'branch', '--show-current'])
    if branch != 'master':
        raise PublishError(f'Publishing requires the master branch; current branch is {branch!r}.')
    _run(root, ['git', 'remote', 'get-url', 'origin'])
    files = publication_files(root, post)

    validation = 'Git checks passed. pnpm was not available, so Astro diagnostics were skipped.'
    if shutil.which('pnpm'):
        validation_output = _run(root, ['pnpm', 'check'], timeout=300)
        validation = validation_output or 'Astro diagnostics passed.'

    _run(root, ['git', 'add', '--', *files])
    _run(root, ['git', 'diff', '--cached', '--check', '--', *files])
    changed = subprocess.run(
        ['git', 'diff', '--cached', '--quiet', '--', *files],
        cwd=root,
        check=False,
    )
    if changed.returncode == 0:
        ahead = int(_run(root, ['git', 'rev-list', '--count', 'origin/master..HEAD']) or '0')
        if ahead:
            commit = _run(root, ['git', 'rev-parse', '--short', 'HEAD'])
            _run(root, ['git', 'push', 'origin', 'master'], timeout=300)
            return PublishResult(commit=commit, files=files, validation=validation)
        raise PublishError('There are no new changes to publish for this post.')
    if changed.returncode != 1:
        raise PublishError('Git could not inspect the staged publication.')

    slug = post.path.stem if post.path.stem != 'index' else post.path.parent.name
    _run(root, ['git', 'commit', '-m', f'Publish {slug}', '--', *files])
    commit = _run(root, ['git', 'rev-parse', '--short', 'HEAD'])
    _run(root, ['git', 'push', 'origin', 'master'], timeout=300)
    return PublishResult(commit=commit, files=files, validation=validation)


def update_repository(root: Path) -> UpdateResult:
    branch = _run(root, ['git', 'branch', '--show-current'])
    if branch != 'master':
        raise PublishError(f'Updating requires the master branch; current branch is {branch!r}.')
    output = _run(root, ['git', 'pull', '--ff-only', 'origin', 'master'], timeout=300)
    commit = _run(root, ['git', 'rev-parse', '--short', 'HEAD'])
    return UpdateResult(output=output or 'Already up to date.', commit=commit)
