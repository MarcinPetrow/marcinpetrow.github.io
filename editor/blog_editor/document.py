from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from html import escape
from pathlib import Path
import re
import unicodedata

import yaml


POST_EXTENSIONS = {'.md', '.mdx'}
FIELD_ORDER = (
    'title',
    'description',
    'slug',
    'date',
    'image',
    'categories',
    'tags',
    'draft',
)


def split_frontmatter(source: str) -> tuple[dict, str]:
    match = re.match(r'^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)', source, re.S)
    if not match:
        return {}, source
    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise ValueError('Front matter must be a YAML object.')
    return metadata, source[match.end():]


def _yaml_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [_yaml_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _yaml_value(item) for key, item in value.items()}
    return value


def compose_source(metadata: dict, body: str) -> str:
    ordered = {}
    for key in FIELD_ORDER:
        if key in metadata and metadata[key] not in (None, ''):
            ordered[key] = _yaml_value(metadata[key])
    for key, value in metadata.items():
        if key not in ordered and value not in (None, ''):
            ordered[key] = _yaml_value(value)
    frontmatter = yaml.safe_dump(
        ordered,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).rstrip()
    clean_body = '\n'.join(line.rstrip() for line in body.lstrip().splitlines())
    return f'---\n{frontmatter}\n---\n\n{clean_body.rstrip()}\n'


def slugify(value: str) -> str:
    value = value.translate(str.maketrans({'ł': 'l', 'Ł': 'L'}))
    normalized = unicodedata.normalize('NFKD', value)
    ascii_value = normalized.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', ascii_value.lower())).strip('-')


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


@dataclass
class PostDocument:
    path: Path
    metadata: dict = field(default_factory=dict)
    body: str = ''

    @classmethod
    def load(cls, path: Path) -> 'PostDocument':
        metadata, body = split_frontmatter(path.read_text(encoding='utf-8'))
        return cls(path=path, metadata=metadata, body=body)

    @property
    def title(self) -> str:
        return str(self.metadata.get('title') or self.path.stem)

    @property
    def tags(self) -> list[str]:
        return _as_list(self.metadata.get('tags'))

    def save(self) -> None:
        self.path.write_text(compose_source(self.metadata, self.body), encoding='utf-8')


def discover_posts(root: Path) -> list[PostDocument]:
    posts = root / 'content' / 'posts'
    if not posts.is_dir():
        raise FileNotFoundError(f'Posts directory does not exist: {posts}')
    documents = [
        PostDocument.load(path)
        for path in posts.rglob('*')
        if path.is_file() and path.suffix.lower() in POST_EXTENSIONS
    ]
    return sorted(
        documents,
        key=lambda post: str(post.metadata.get('date', '')),
        reverse=True,
    )


def create_post(root: Path, title: str, slug: str | None = None) -> PostDocument:
    safe_slug = slugify(slug or title)
    if not safe_slug:
        raise ValueError('Enter a title or a valid ASCII slug.')
    path = root / 'content' / 'posts' / f'{safe_slug}.md'
    if path.exists():
        raise FileExistsError(f'A post named {safe_slug}.md already exists.')
    document = PostDocument(
        path=path,
        metadata={
            'title': title.strip() or safe_slug,
            'description': '',
            'date': date.today().isoformat(),
            'tags': [],
            'draft': True,
        },
        body='',
    )
    document.save()
    return document


INLINE = re.compile(
    r'!\[([^]]*)\]\(([^)]+)\)|\[([^]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|`([^`]+)`'
)


def _inline(text: str) -> str:
    output = []
    cursor = 0
    for match in INLINE.finditer(text):
        output.append(escape(text[cursor:match.start()]))
        alt, image, label, link, strong, code = match.groups()
        if image:
            source = image[1:] if image.startswith('/') else image
            output.append(f'<img src="{escape(source, quote=True)}" alt="{escape(alt)}">')
        elif link:
            output.append(f'<a href="{escape(link, quote=True)}">{escape(label)}</a>')
        elif strong:
            output.append(f'<strong>{escape(strong)}</strong>')
        else:
            output.append(f'<code>{escape(code)}</code>')
        cursor = match.end()
    output.append(escape(text[cursor:]))
    return ''.join(output)


def render_markdown(body: str, root: Path) -> str:
    chunks = []
    paragraph = []
    in_code = False
    code_lines = []
    in_list = False

    def flush_paragraph():
        if paragraph:
            chunks.append(f'<p>{_inline(" ".join(paragraph))}</p>')
            paragraph.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            chunks.append('</ul>')
            in_list = False

    for line in body.splitlines():
        if line.startswith('```'):
            flush_paragraph()
            close_list()
            if in_code:
                chunks.append(f'<pre><code>{escape(chr(10).join(code_lines))}</code></pre>')
                code_lines.clear()
            in_code = not in_code
            continue
        if in_code:
            code_lines.append(line)
            continue
        heading = re.match(r'^(#{1,6})\s+(.+)$', line)
        item = re.match(r'^[-*]\s+(.+)$', line)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            chunks.append(f'<h{level}>{_inline(heading.group(2))}</h{level}>')
        elif item:
            flush_paragraph()
            if not in_list:
                chunks.append('<ul>')
                in_list = True
            chunks.append(f'<li>{_inline(item.group(1))}</li>')
        elif not line.strip():
            flush_paragraph()
            close_list()
        else:
            close_list()
            paragraph.append(line.strip())
    flush_paragraph()
    close_list()
    if code_lines:
        chunks.append(f'<pre><code>{escape(chr(10).join(code_lines))}</code></pre>')
    css = """
      :root {
        color-scheme: dark;
        font-family: Inter, system-ui, sans-serif;
        background: #282828;
        color: #eceff1;
      }
      body {
        max-width: 760px;
        margin: 0 auto;
        padding: 32px 36px 72px;
        line-height: 1.72;
        background: #282828;
      }
      h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
        line-height: 1.25;
        letter-spacing: -0.015em;
        margin: 1.7em 0 0.65em;
      }
      h1, h2 { border-bottom: 1px solid #454545; padding-bottom: 0.35em; }
      h2::before { content: ''; border-left: 3px solid #ef762f; margin-right: 10px; }
      p, li { color: #d6dade; }
      strong { color: #ffffff; }
      img {
        display: block;
        max-width: 100%;
        height: auto;
        margin: 26px auto;
        border: 1px solid #484848;
        border-radius: 3px;
        box-shadow: 0 12px 30px rgba(0,0,0,.24);
      }
      pre {
        overflow: auto;
        padding: 18px;
        border: 1px solid #454545;
        border-radius: 3px;
        background: #1e1e1e;
      }
      code { font-family: 'JetBrains Mono', monospace; color: #ffc092; }
      a { color: #ff9a52; text-decoration-color: #9d552b; }
      a:hover { color: #ffb078; }
    """
    base = (root / 'public').as_uri() + '/'
    return f'<!doctype html><html><head><base href="{base}"><style>{css}</style></head><body>{"".join(chunks)}</body></html>'
