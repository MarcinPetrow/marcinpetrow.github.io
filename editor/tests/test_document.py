from pathlib import Path
import subprocess
import tempfile
import unittest

from PIL import Image

from blog_editor.document import (
    PostDocument,
    compose_source,
    create_post,
    render_markdown,
    slugify,
    split_frontmatter,
)
from blog_editor.images import ImageEdits, edit_image, import_image
from blog_editor.publisher import (
    configure_git_identity,
    git_identity,
    post_sync_status,
    publication_files,
)


class DocumentTests(unittest.TestCase):
    def test_frontmatter_round_trip(self):
        source = "---\ntitle: Test\ntags: [one, two]\ndraft: true\n---\n\nHello"
        metadata, body = split_frontmatter(source)
        rebuilt = compose_source(metadata, body)
        again, again_body = split_frontmatter(rebuilt)
        self.assertEqual(metadata, again)
        self.assertEqual('Hello\n', again_body)

    def test_compose_source_removes_trailing_whitespace_and_adds_final_newline(self):
        source = compose_source({'title': 'Test'}, 'First line  \nSecond line\t')
        self.assertTrue(source.endswith('First line\nSecond line\n'))

    def test_slugify(self):
        self.assertEqual('nowy-wpis-zolw', slugify('Nowy wpis: Żółw!'))

    def test_create_post_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'content' / 'posts').mkdir(parents=True)
            post = create_post(root, 'Hello World')
            self.assertTrue(post.path.exists())
            with self.assertRaises(FileExistsError):
                create_post(root, 'Hello World')

    def test_preview_resolves_public_image(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'public').mkdir()
            html = render_markdown('![Example](/images/example.png)', root)
            self.assertIn('src="images/example.png"', html)


class ImageTests(unittest.TestCase):
    def test_import_and_edit(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'Source Image.png'
            Image.new('RGB', (100, 50), 'red').save(source)
            destination, public_path = import_image(root, source, 'post')
            self.assertEqual('/images/post-source-image.png', public_path)
            output = edit_image(
                destination,
                ImageEdits(width=40, rotate=90, output_format='webp'),
            )
            self.assertEqual('.webp', output.suffix)
            with Image.open(output) as image:
                self.assertEqual(40, image.width)


class PublisherTests(unittest.TestCase):
    def test_repository_local_git_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            self.assertFalse(git_identity(root).configured)
            configure_git_identity(root, 'Blog Author', 'author@example.com')
            identity = git_identity(root)
            self.assertTrue(identity.configured)
            self.assertEqual('Blog Author', identity.name)
            self.assertEqual('author@example.com', identity.email)

    def test_post_sync_status(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            configure_git_identity(root, 'Blog Author', 'author@example.com')
            post_path = root / 'content' / 'posts' / 'example.md'
            post_path.parent.mkdir(parents=True)
            post_path.write_text(
                '---\ntitle: Example\ndate: 2026-01-01\n---\n\nBody', encoding='utf-8'
            )
            post = PostDocument.load(post_path)
            self.assertEqual('unpublished', post_sync_status(root, post).key)
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            subprocess.run(['git', 'commit', '-qm', 'Initial'], cwd=root, check=True)
            subprocess.run(
                ['git', 'update-ref', 'refs/remotes/origin/master', 'HEAD'],
                cwd=root,
                check=True,
            )
            self.assertEqual('synced', post_sync_status(root, post).key)
            post_path.write_text(post_path.read_text() + '\nChanged', encoding='utf-8')
            self.assertEqual('local', post_sync_status(root, post).key)
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            subprocess.run(['git', 'commit', '-qm', 'Change post'], cwd=root, check=True)
            self.assertEqual('different', post_sync_status(root, post).key)

    def test_post_sync_status_is_unknown_without_remote(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            post_path = root / 'content' / 'posts' / 'example.md'
            post_path.parent.mkdir(parents=True)
            post_path.write_text(
                '---\ntitle: Example\ndate: 2026-01-01\n---\n\nBody', encoding='utf-8'
            )
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            configure_git_identity(root, 'Blog Author', 'author@example.com')
            subprocess.run(['git', 'commit', '-qm', 'Initial'], cwd=root, check=True)
            post = PostDocument.load(post_path)
            self.assertEqual('unknown', post_sync_status(root, post).key)

    def test_publication_contains_post_and_referenced_local_images(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            post_path = root / 'content' / 'posts' / 'example.md'
            post_path.parent.mkdir(parents=True)
            image = root / 'public' / 'images' / 'example.png'
            image.parent.mkdir(parents=True)
            image.write_bytes(b'image')
            post_path.write_text(
                '---\ntitle: Example\ndate: 2026-01-01\nimage: /images/example.png\n---\n\n'
                '![local](/images/example.png) ![remote](https://example.com/image.png)',
                encoding='utf-8',
            )
            post = PostDocument.load(post_path)
            self.assertEqual(
                ('content/posts/example.md', 'public/images/example.png'),
                publication_files(root, post),
            )


if __name__ == '__main__':
    unittest.main()
