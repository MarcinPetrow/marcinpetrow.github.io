from __future__ import annotations

from pathlib import Path
import sys
import threading

import gi

gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Adw, Gio, GLib, GObject, Gtk, WebKit  # noqa: E402

from .document import PostDocument, create_post, discover_posts, render_markdown, slugify
from .images import ImageEdits, edit_image, import_image
from .publisher import (
    configure_git_identity,
    git_identity,
    publication_files,
    publish_post,
    update_repository,
)


APP_CSS = """
@define-color window_bg_color #242424;
@define-color window_fg_color #f5f6f7;
@define-color view_bg_color #2d2d2d;
@define-color view_fg_color #f5f6f7;
@define-color headerbar_bg_color #2b2b2b;
@define-color headerbar_fg_color #ffffff;
@define-color card_bg_color #2d2d2d;
@define-color card_fg_color #f5f6f7;
@define-color accent_color #ff9a52;
@define-color accent_bg_color #ef762f;
@define-color accent_fg_color #ffffff;

window, .background {
  background-color: #242424;
  color: #f5f6f7;
}

.topbar {
  min-height: 72px;
  background: #2b2b2b;
  color: #ffffff;
  border-bottom: 1px solid #171717;
}
.brand-panel {
  min-width: 232px;
  padding: 0 18px;
  background: #303030;
  border-right: 1px solid #171717;
}
.brand-mark {
  min-width: 24px;
  color: #ef762f;
  font-size: 30px;
  font-weight: 300;
}
.brand-title {
  color: #ffffff;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.brand-subtitle { color: #929292; font-size: 11px; }
.workspace-header { padding: 0 20px; }
.workspace-title { color: #f6f6f6; font-size: 16px; font-weight: 600; }
.workspace-subtitle { color: #8f8f8f; font-size: 11px; }
.toolbar-action {
  min-width: 42px;
  min-height: 42px;
  margin: 0 3px;
  background: transparent;
  border: 0;
}
.toolbar-action:hover { background: #393939; }
.publish-button {
  min-height: 42px;
  padding: 0 16px;
  margin: 0 6px;
}
.update-button {
  min-height: 42px;
  padding: 0 12px;
  margin: 0 3px;
  background: transparent;
}
.update-button:hover { background: #393939; }
.site-button {
  min-height: 42px;
  padding: 0 12px;
  margin: 0 3px;
  background: transparent;
}
.site-button:hover { background: #393939; }
.toolbar-separator { min-width: 1px; background: #3b3b3b; margin: 14px 8px; }

.editor-sidebar {
  background: #292929;
  border-right: 1px solid #151515;
}

.editor-pane { background: #242424; }
.preview-pane {
  background: #282828;
  border-left: 1px solid #151515;
}

entry, searchentry, textview {
  background: #252525;
  color: #f7f7f8;
  border: 1px solid #414141;
  border-radius: 3px;
  caret-color: #ff9a52;
  box-shadow: none;
}

entry:focus-within, searchentry:focus-within {
  border-color: #ef762f;
  box-shadow: 0 0 0 1px #ef762f;
}

textview text { background: #252525; color: #f7f7f8; }

button {
  color: #eef0f2;
  border-radius: 3px;
}

button:hover { background: #3a3a3a; }
.accent-button {
  background: #ef762f;
  color: #ffffff;
  font-weight: 700;
}
.accent-button:hover { background: #ff8741; }

.navigation-sidebar {
  background: transparent;
  color: #eef0f2;
}
.navigation-sidebar row {
  margin: 1px 0;
  border-radius: 0;
  border-right: 3px solid transparent;
  border-bottom: 1px solid #343434;
}
.navigation-sidebar row:hover { background: #323232; }
.navigation-sidebar row:selected {
  background: #36312e;
  border-right-color: #ef762f;
  color: #ffffff;
}
.sidebar-nav { border-bottom: 1px solid #383838; padding-bottom: 8px; }
.sidebar-nav button {
  min-height: 38px;
  padding: 0 16px;
  background: transparent;
  border: 0;
  border-radius: 0;
  color: #9e9e9e;
  font-weight: 600;
}
.sidebar-nav button box { border-spacing: 11px; }
.sidebar-nav button image { color: #8f8f8f; }
.sidebar-nav button label { color: inherit; }
.sidebar-nav button:hover { background: #323232; color: #ffffff; }
.sidebar-nav button.selected {
  background: #33302e;
  color: #ffffff;
  border-left: 3px solid #ef762f;
}

.dim-label, .caption { color: #aeb5bd; }
.section-title {
  color: #ff9a52;
  font-weight: 800;
  font-size: 11px;
  letter-spacing: 0.12em;
}
.metadata-card {
  padding: 8px;
  background: #2d2d2d;
  border: 1px solid #3a3a3a;
  border-bottom: 2px solid #ef762f;
  border-radius: 2px;
}
.field-card {
  padding: 3px 5px;
  background: transparent;
  border: 0;
}
.page-heading {
  color: #ffffff;
  font-size: 21px;
  font-weight: 600;
}
.page-subtitle {
  color: #858585;
  font-size: 11px;
}
.content-label {
  color: #a7a7a7;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
}
.content-toolbar { min-height: 34px; }
.content-insert {
  min-height: 30px;
  padding: 0 10px;
  background: #303030;
  border: 1px solid #444444;
  color: #e7e7e7;
}
.content-insert:hover { background: #393939; border-color: #ef762f; }
.panel-toggle {
  min-height: 38px;
  padding: 0 12px;
  background: #2b2b2b;
  border: 1px solid #3b3b3b;
  border-radius: 2px;
  color: #d0d0d0;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
}
.panel-toggle:hover { background: #323232; }
.panel-toggle image { color: #ef762f; }
.settings-collapse {
  padding: 0;
  background: transparent;
  border: 0;
  border-radius: 0;
}
.settings-collapse:hover { background: transparent; }
.settings-status {
  min-height: 36px;
  padding-left: 12px;
  border-left: 1px solid #414141;
}
.preview-toggle.active { background: #ef762f; color: #ffffff; }
.date-picker entry { border-radius: 3px 0 0 3px; }
.date-picker button {
  min-width: 40px;
  border-left: 0;
  border-radius: 0 3px 3px 0;
}
.tag-editor {
  min-height: 36px;
  padding: 2px 5px;
  background: #252525;
  border: 1px solid #414141;
  border-radius: 3px;
}
.tag-editor entry {
  min-width: 160px;
  min-height: 30px;
  background: transparent;
  border: 0;
  box-shadow: none;
}
.field-card entry { min-height: 34px; }
.control-row { min-height: 36px; }
.control-row > button { min-height: 36px; }
.tag-chip {
  padding: 3px 5px 3px 9px;
  background: #49362c;
  border: 1px solid #8d4e29;
  border-radius: 999px;
  color: #ffd9bf;
}
.tag-chip button {
  min-width: 20px;
  min-height: 20px;
  padding: 0;
  border-radius: 999px;
  background: transparent;
}

paned > separator {
  min-width: 1px;
  min-height: 1px;
  background: #111111;
  opacity: 1;
}

scrolledwindow.card, picture.card {
  background: #2d2d2d;
  border: 1px solid #3c3c3c;
  border-radius: 3px;
  box-shadow: none;
}

switch:checked { background: #ef762f; }
scrollbar slider { background: #69727c; min-width: 6px; min-height: 6px; }
scrollbar slider:hover { background: #8b949e; }
"""


class TagEditor(Gtk.Box):
    __gsignals__ = {'changed': (GObject.SignalFlags.RUN_FIRST, None, ())}

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add_css_class('tag-editor')
        self.tags: list[str] = []
        self.chips = Gtk.FlowBox(
            selection_mode=Gtk.SelectionMode.NONE,
            column_spacing=5,
            row_spacing=5,
            max_children_per_line=8,
            homogeneous=False,
        )
        self.chips.set_hexpand(True)
        self.append(self.chips)
        self.entry = Gtk.Entry(placeholder_text='Type a tag and press Enter')
        self.entry.set_width_chars(18)
        self.entry.connect('activate', self._commit_entry)
        self.entry.connect('changed', self._split_commas)
        self.append(self.entry)

    def _split_commas(self, entry):
        value = entry.get_text()
        if ',' not in value:
            return
        parts = value.split(',')
        entry.set_text(parts.pop())
        for part in parts:
            self.add_tag(part)

    def _commit_entry(self, entry):
        self.add_tag(entry.get_text())
        entry.set_text('')

    def add_tag(self, value: str, emit=True):
        value = value.strip().lower()
        if not value or value in self.tags:
            return
        self.tags.append(value)
        chip = Gtk.Box(spacing=3)
        chip.add_css_class('tag-chip')
        chip.append(Gtk.Label(label=value))
        remove = Gtk.Button(icon_name='window-close-symbolic', tooltip_text=f'Remove {value}')
        remove.set_focusable(False)
        remove.connect('clicked', lambda *_: self.remove_tag(value, chip))
        chip.append(remove)
        self.chips.append(chip)
        if emit:
            self.emit('changed')

    def remove_tag(self, value: str, chip):
        if value in self.tags:
            self.tags.remove(value)
        parent = chip.get_parent()
        self.chips.remove(parent if isinstance(parent, Gtk.FlowBoxChild) else chip)
        self.emit('changed')

    def set_tags(self, values):
        while child := self.chips.get_first_child():
            self.chips.remove(child)
        self.tags = []
        for value in values:
            self.add_tag(str(value), emit=False)
        self.emit('changed')

    def get_tags(self) -> list[str]:
        pending = self.entry.get_text().strip()
        if pending:
            self.add_tag(pending)
            self.entry.set_text('')
        return list(self.tags)


class BlogEditorWindow(Adw.ApplicationWindow):
    def __init__(self, application: Adw.Application, root: Path):
        super().__init__(application=application, title='Blog Editor')
        self.root = root
        self.posts: list[PostDocument] = []
        self.current: PostDocument | None = None
        self.dirty = False
        self.status_filter = 'all'
        self.preview_timer = 0
        self.set_default_size(1440, 900)
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        css = Gtk.CssProvider()
        css.load_from_string(APP_CSS)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        toolbar = Adw.ToolbarView()
        topbar = Gtk.Box()
        topbar.add_css_class('topbar')
        brand = Gtk.Box(spacing=10)
        brand.add_css_class('brand-panel')
        mark = Gtk.Label(label='◇')
        mark.add_css_class('brand-mark')
        mark.set_valign(Gtk.Align.CENTER)
        brand.append(mark)
        brand_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        brand_text.set_valign(Gtk.Align.CENTER)
        brand_title = Gtk.Label(label='BLOG EDITOR', xalign=0)
        brand_title.add_css_class('brand-title')
        brand_subtitle = Gtk.Label(label=root.name, xalign=0)
        brand_subtitle.add_css_class('brand-subtitle')
        brand_text.append(brand_title)
        brand_text.append(brand_subtitle)
        brand.append(brand_text)
        topbar.append(brand)

        workspace = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1, hexpand=True)
        workspace.add_css_class('workspace-header')
        workspace.set_valign(Gtk.Align.CENTER)
        workspace_title = Gtk.Label(label='WRITING WORKSPACE', xalign=0)
        workspace_title.add_css_class('workspace-title')
        workspace_subtitle = Gtk.Label(label='Markdown publishing studio', xalign=0)
        workspace_subtitle.add_css_class('workspace-subtitle')
        workspace.append(workspace_title)
        workspace.append(workspace_subtitle)
        topbar.append(workspace)

        site_button = Gtk.Button(tooltip_text='Open the public blog in a browser')
        site_content = Gtk.Box(spacing=7)
        site_content.append(Gtk.Image.new_from_icon_name('web-browser-symbolic'))
        site_content.append(Gtk.Label(label='Open blog'))
        site_button.set_child(site_content)
        site_button.add_css_class('site-button')
        site_button.connect('clicked', self._open_blog)
        topbar.append(site_button)

        self.update_button = Gtk.Button(tooltip_text='Download updates from origin/master')
        update_content = Gtk.Box(spacing=7)
        update_content.append(Gtk.Image.new_from_icon_name('view-refresh-symbolic'))
        update_content.append(Gtk.Label(label='Update'))
        self.update_button.set_child(update_content)
        self.update_button.add_css_class('update-button')
        self.update_button.connect('clicked', self._confirm_update)
        topbar.append(self.update_button)

        new_button = Gtk.Button(icon_name='document-new-symbolic', tooltip_text='New post')
        new_button.add_css_class('toolbar-action')
        new_button.connect('clicked', self._show_new_post)
        topbar.append(new_button)
        save_button = Gtk.Button(icon_name='document-save-symbolic', tooltip_text='Save')
        save_button.add_css_class('toolbar-action')
        save_button.connect('clicked', self._save)
        topbar.append(save_button)
        self.publish_button = Gtk.Button(tooltip_text='Commit and publish this post')
        publish_content = Gtk.Box(spacing=7)
        publish_content.append(Gtk.Image.new_from_icon_name('send-to-symbolic'))
        publish_content.append(Gtk.Label(label='Publish'))
        self.publish_button.set_child(publish_content)
        self.publish_button.add_css_class('accent-button')
        self.publish_button.add_css_class('publish-button')
        self.publish_button.connect('clicked', self._confirm_publish)
        topbar.append(self.publish_button)

        image_button = Gtk.Button(icon_name='insert-image-symbolic', tooltip_text='Insert image')
        image_button.add_css_class('toolbar-action')
        image_button.connect('clicked', lambda *_: self._choose_image('insert'))
        topbar.append(image_button)
        edit_image_button = Gtk.Button(icon_name='image-crop-symbolic', tooltip_text='Edit image')
        edit_image_button.add_css_class('toolbar-action')
        edit_image_button.connect('clicked', lambda *_: self._choose_image('edit'))
        topbar.append(edit_image_button)
        self.preview_button = Gtk.Button(
            icon_name='view-dual-symbolic', tooltip_text='Show or hide preview'
        )
        self.preview_button.add_css_class('toolbar-action')
        self.preview_button.add_css_class('preview-toggle')
        self.preview_button.add_css_class('active')
        self.preview_button.connect('clicked', self._toggle_preview)
        topbar.append(self.preview_button)
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        separator.add_css_class('toolbar-separator')
        topbar.append(separator)
        topbar.append(Gtk.WindowControls(side=Gtk.PackType.END))
        handle = Gtk.WindowHandle()
        handle.set_child(topbar)
        toolbar.add_top_bar(handle)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL, wide_handle=True)
        paned.set_position(268)
        paned.set_start_child(self._build_sidebar())
        self.editor_preview = Gtk.Paned(
            orientation=Gtk.Orientation.HORIZONTAL, wide_handle=True
        )
        self.editor_preview.set_position(690)
        self.editor_preview.set_start_child(self._build_editor())
        self.preview_panel = self._build_preview()
        self.editor_preview.set_end_child(self.preview_panel)
        paned.set_end_child(self.editor_preview)
        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(paned)
        toolbar.set_content(self.toast_overlay)
        self.set_content(toolbar)
        self._load_posts()

    def _build_sidebar(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_size_request(230, -1)
        box.add_css_class('editor-sidebar')
        title = Gtk.Label(label='POSTS', xalign=0)
        title.add_css_class('section-title')
        title.set_margin_start(16)
        title.set_margin_top(18)
        title.set_margin_bottom(10)
        box.append(title)
        nav = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        nav.add_css_class('sidebar-nav')
        self.filter_buttons = {}
        for key, label, icon in (
            ('all', 'All posts', 'view-list-symbolic'),
            ('draft', 'Drafts', 'document-edit-symbolic'),
            ('published', 'Published', 'emblem-ok-symbolic'),
        ):
            button = Gtk.Button()
            button_content = Gtk.Box(spacing=11)
            button_content.append(Gtk.Image.new_from_icon_name(icon))
            button_content.append(Gtk.Label(label=label, xalign=0, hexpand=True))
            button.set_child(button_content)
            button.set_halign(Gtk.Align.FILL)
            button.connect('clicked', lambda _button, value=key: self._set_status_filter(value))
            if key == 'all':
                button.add_css_class('selected')
            self.filter_buttons[key] = button
            nav.append(button)
        box.append(nav)
        library = Gtk.Label(label='LIBRARY', xalign=0)
        library.add_css_class('section-title')
        library.set_margin_start(16)
        library.set_margin_top(14)
        library.set_margin_bottom(8)
        box.append(library)
        self.search = Gtk.SearchEntry(placeholder_text='Search posts')
        self.search.set_margin_start(12)
        self.search.set_margin_end(12)
        self.search.set_margin_bottom(12)
        self.search.connect('search-changed', self._filter_posts)
        box.append(self.search)
        self.post_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self.post_list.add_css_class('navigation-sidebar')
        self.post_list.connect('row-selected', self._select_post)
        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(self.post_list)
        box.append(scroll)
        return box

    def _field(self, label: str, widget):
        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        row.add_css_class('field-card')
        caption = Gtk.Label(label=label, xalign=0)
        caption.add_css_class('caption')
        row.append(caption)
        row.append(widget)
        return row

    def _build_editor(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        outer.set_margin_start(14)
        outer.set_margin_end(14)
        outer.set_margin_top(12)
        outer.set_margin_bottom(12)
        outer.add_css_class('editor-pane')
        page_header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.page_title = Gtk.Label(label='Post editor', xalign=0)
        self.page_title.add_css_class('page-heading')
        self.page_subtitle = Gtk.Label(
            label='Compose content, manage publication data and assets', xalign=0
        )
        self.page_subtitle.add_css_class('page-subtitle')
        page_header.append(self.page_title)
        page_header.append(self.page_subtitle)
        outer.append(page_header)

        settings_header = Gtk.Box(spacing=10)
        settings_header.add_css_class('panel-toggle')
        settings_button = Gtk.Button(hexpand=True)
        settings_button.add_css_class('settings-collapse')
        settings_content = Gtk.Box(spacing=8)
        settings_content.append(Gtk.Label(label='POST SETTINGS', xalign=0, hexpand=True))
        self.settings_chevron = Gtk.Image.new_from_icon_name('pan-down-symbolic')
        settings_content.append(self.settings_chevron)
        settings_button.set_child(settings_content)
        settings_button.connect('clicked', self._toggle_settings)
        settings_header.append(settings_button)
        draft_header = Gtk.Box(spacing=8)
        draft_header.add_css_class('settings-status')
        self.draft_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        draft_header.append(self.draft_switch)
        draft_header.append(Gtk.Label(label='Draft'))
        settings_header.append(draft_header)
        outer.append(settings_header)
        self.title_entry = Gtk.Entry(placeholder_text='Post title')
        self.description_entry = Gtk.Entry(placeholder_text='Short description')
        self.date_entry = Gtk.Entry(placeholder_text='YYYY-MM-DD', editable=False)
        self.calendar = Gtk.Calendar()
        self.calendar.connect('day-selected', self._calendar_selected)
        self.date_popover = Gtk.Popover()
        self.date_popover.set_child(self.calendar)
        date_button = Gtk.MenuButton(
            icon_name='x-office-calendar-symbolic',
            tooltip_text='Choose publication date',
            popover=self.date_popover,
        )
        date_box = Gtk.Box()
        date_box.add_css_class('date-picker')
        date_box.add_css_class('control-row')
        date_box.set_hexpand(True)
        date_box.set_valign(Gtk.Align.CENTER)
        self.date_entry.set_hexpand(True)
        date_box.append(self.date_entry)
        date_box.append(date_button)
        self.tags_editor = TagEditor()
        self.tags_editor.set_valign(Gtk.Align.CENTER)
        self.cover_entry = Gtk.Entry(placeholder_text='/images/cover.webp', hexpand=True)
        cover_button = Gtk.Button(label='Choose…')
        cover_button.connect('clicked', lambda *_: self._choose_image('cover'))
        cover_box = Gtk.Box(spacing=6)
        cover_box.add_css_class('control-row')
        cover_box.set_valign(Gtk.Align.CENTER)
        cover_box.append(self.cover_entry)
        cover_box.append(cover_button)
        self.cover_preview = Gtk.Picture(
            can_shrink=True,
            content_fit=Gtk.ContentFit.COVER,
            alternative_text='Cover image preview',
        )
        self.cover_preview.set_size_request(48, 34)
        self.cover_preview.set_hexpand(False)
        self.cover_preview.set_vexpand(False)
        self.cover_preview.add_css_class('card')
        self.cover_preview.set_visible(False)
        cover_box.append(self.cover_preview)

        grid = Gtk.Grid(column_spacing=6, row_spacing=5)
        grid.add_css_class('metadata-card')
        grid.set_column_homogeneous(True)
        grid.attach(self._field('TITLE', self.title_entry), 0, 0, 2, 1)
        grid.attach(self._field('DESCRIPTION', self.description_entry), 2, 0, 2, 1)
        grid.attach(self._field('PUBLICATION DATE', date_box), 0, 1, 1, 1)
        grid.attach(self._field('TAGS', self.tags_editor), 1, 1, 3, 1)
        grid.attach(self._field('COVER IMAGE', cover_box), 0, 2, 4, 1)
        self.settings_revealer = Gtk.Revealer(
            transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN,
            transition_duration=180,
            reveal_child=True,
        )
        settings_scroll = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
            propagate_natural_height=True,
            max_content_height=270,
        )
        settings_scroll.set_child(grid)
        self.settings_revealer.set_child(settings_scroll)
        outer.append(self.settings_revealer)

        content_header = Gtk.Box(spacing=8)
        content_header.add_css_class('content-toolbar')
        content_label = Gtk.Label(label='CONTENT', xalign=0, hexpand=True)
        content_label.add_css_class('content-label')
        content_header.append(content_label)
        insert_image = Gtk.Button(tooltip_text='Copy an image to the repository and insert it')
        insert_content = Gtk.Box(spacing=6)
        insert_content.append(Gtk.Image.new_from_icon_name('insert-image-symbolic'))
        insert_content.append(Gtk.Label(label='Insert image'))
        insert_image.set_child(insert_content)
        insert_image.add_css_class('content-insert')
        insert_image.connect('clicked', lambda *_: self._choose_image('insert'))
        content_header.append(insert_image)
        outer.append(content_header)
        self.text_view = Gtk.TextView(
            monospace=True,
            wrap_mode=Gtk.WrapMode.WORD_CHAR,
            top_margin=12,
            bottom_margin=12,
            left_margin=12,
            right_margin=12,
        )
        self.text_view.get_buffer().connect('changed', self._content_changed)
        text_scroll = Gtk.ScrolledWindow(vexpand=True)
        text_scroll.set_min_content_height(220)
        text_scroll.set_child(self.text_view)
        text_scroll.add_css_class('card')
        outer.append(text_scroll)
        for widget in (
            self.title_entry,
            self.description_entry,
            self.date_entry,
            self.cover_entry,
        ):
            widget.connect('changed', self._metadata_changed)
        self.tags_editor.connect('changed', self._metadata_changed)
        self.cover_entry.connect('changed', self._update_cover_preview)
        self.draft_switch.connect('notify::active', self._metadata_changed)
        return outer

    def _toggle_settings(self, *_):
        expanded = not self.settings_revealer.get_reveal_child()
        self.settings_revealer.set_reveal_child(expanded)
        self.settings_chevron.set_from_icon_name(
            'pan-down-symbolic' if expanded else 'pan-end-symbolic'
        )

    def _calendar_selected(self, calendar):
        self.date_entry.set_text(calendar.get_date().format('%Y-%m-%d'))

    def _toggle_preview(self, *_):
        visible = not self.preview_panel.get_visible()
        self.preview_panel.set_visible(visible)
        if visible:
            self.preview_button.add_css_class('active')
        else:
            self.preview_button.remove_css_class('active')

    def _open_blog(self, *_):
        try:
            cname = (self.root / 'public' / 'CNAME').read_text(encoding='utf-8').strip()
            if not cname or any(character.isspace() for character in cname):
                raise ValueError('public/CNAME does not contain a valid domain.')
            Gio.AppInfo.launch_default_for_uri(f'https://{cname}', None)
        except Exception as error:
            self._error(f'Could not open the blog:\n\n{error}')

    def _build_preview(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.add_css_class('preview-pane')
        label = Gtk.Label(label='Preview', xalign=0)
        label.add_css_class('section-title')
        label.set_margin_start(14)
        label.set_margin_top(14)
        label.set_margin_bottom(6)
        box.append(label)
        self.webview = WebKit.WebView(vexpand=True, hexpand=True)
        box.append(self.webview)
        return box

    def _load_posts(self, select: Path | None = None):
        self.posts = discover_posts(self.root)
        while child := self.post_list.get_first_child():
            self.post_list.remove(child)
        selected_row = None
        for post in self.posts:
            row = Gtk.ListBoxRow()
            row.post = post
            content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            content.set_margin_top(8)
            content.set_margin_bottom(8)
            content.set_margin_start(8)
            content.set_margin_end(8)
            title = Gtk.Label(label=post.title, xalign=0, ellipsize=3)
            title.add_css_class('heading')
            content.append(title)
            details = f'{post.metadata.get("date", "")}  ·  {post.path.name}'
            subtitle = Gtk.Label(label=details, xalign=0, ellipsize=3)
            subtitle.add_css_class('dim-label')
            subtitle.add_css_class('caption')
            content.append(subtitle)
            row.set_child(content)
            self.post_list.append(row)
            if select and post.path == select:
                selected_row = row
        if selected_row:
            self.post_list.select_row(selected_row)
        elif self.posts and self.current is None:
            self.post_list.select_row(self.post_list.get_row_at_index(0))

    def _filter_posts(self, *_):
        query = self.search.get_text().casefold().strip()
        row = self.post_list.get_first_child()
        while row:
            post = row.post
            haystack = f'{post.title} {post.path.name} {" ".join(post.tags)}'.casefold()
            is_draft = bool(post.metadata.get('draft', False))
            status_matches = (
                self.status_filter == 'all'
                or (self.status_filter == 'draft' and is_draft)
                or (self.status_filter == 'published' and not is_draft)
            )
            row.set_visible(status_matches and (not query or query in haystack))
            row = row.get_next_sibling()

    def _set_status_filter(self, value: str):
        self.status_filter = value
        for key, button in self.filter_buttons.items():
            if key == value:
                button.add_css_class('selected')
            else:
                button.remove_css_class('selected')
        self._filter_posts()

    def _select_post(self, _list, row):
        if row is None or row.post is self.current:
            return
        if self.dirty:
            self._save(show_message=False)
        self.current = row.post
        self.dirty = False
        data = self.current.metadata
        self.page_title.set_label(self.current.title)
        state = 'Draft' if data.get('draft', False) else 'Published'
        self.page_subtitle.set_label(f'{state}  ·  {data.get("date", "No publication date")}')
        self.title_entry.set_text(str(data.get('title', '')))
        self.description_entry.set_text(str(data.get('description', '')))
        value = data.get('date', '')
        date_value = value.isoformat() if hasattr(value, 'isoformat') else str(value)
        self.date_entry.set_text(date_value)
        try:
            year, month, day = (int(part) for part in date_value[:10].split('-'))
            self.calendar.select_day(GLib.DateTime.new_local(year, month, day, 12, 0, 0))
        except (TypeError, ValueError):
            pass
        tags = data.get('tags', [])
        self.tags_editor.set_tags(tags if isinstance(tags, list) else [str(tags)])
        self.cover_entry.set_text(str(data.get('image', '')))
        self.draft_switch.set_active(bool(data.get('draft', False)))
        self.text_view.get_buffer().set_text(self.current.body)
        self.dirty = False
        self._update_preview()

    def _metadata_changed(self, *_):
        if self.current:
            self.dirty = True

    def _update_cover_preview(self, *_):
        value = self.cover_entry.get_text().strip()
        if not value or '://' in value:
            self.cover_preview.set_visible(False)
            self.cover_preview.set_paintable(None)
            return
        if value.startswith('/'):
            path = self.root / 'public' / value.lstrip('/')
        elif self.current:
            path = self.current.path.parent / value
        else:
            path = self.root / value
        if path.is_file():
            self.cover_preview.set_filename(str(path))
            self.cover_preview.set_visible(True)
        else:
            self.cover_preview.set_visible(False)
            self.cover_preview.set_paintable(None)

    def _content_changed(self, *_):
        if not self.current:
            return
        self.dirty = True
        if self.preview_timer:
            GLib.source_remove(self.preview_timer)
        self.preview_timer = GLib.timeout_add(250, self._update_preview)

    def _body_text(self):
        buffer = self.text_view.get_buffer()
        return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)

    def _update_preview(self):
        self.preview_timer = 0
        html = render_markdown(self._body_text(), self.root)
        self.webview.load_html(html, (self.root / 'public').as_uri() + '/')
        return GLib.SOURCE_REMOVE

    def _apply_form(self):
        if not self.current:
            return
        metadata = self.current.metadata
        metadata['title'] = self.title_entry.get_text().strip()
        metadata['description'] = self.description_entry.get_text().strip()
        metadata['date'] = self.date_entry.get_text().strip()
        metadata['tags'] = self.tags_editor.get_tags()
        metadata['draft'] = self.draft_switch.get_active()
        cover = self.cover_entry.get_text().strip()
        if cover:
            metadata['image'] = cover
        else:
            metadata.pop('image', None)
        self.current.body = self._body_text()

    def _save(self, *_args, show_message=True):
        if not self.current:
            return
        try:
            self._apply_form()
            self.current.save()
            self.dirty = False
            if show_message:
                self._toast('Post saved')
        except Exception as error:
            self._error(str(error))

    def _confirm_publish(self, *_):
        if not self.current:
            return
        identity = git_identity(self.root)
        if not identity.configured:
            self._show_git_identity(identity)
            return
        try:
            self._apply_form()
            files = publication_files(self.root, self.current)
        except Exception as error:
            self._error(str(error))
            return
        state = 'Draft remains enabled.' if self.draft_switch.get_active() else 'Draft is disabled.'
        listed = '\n'.join(f'• {path}' for path in files)
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=f'Publish “{self.current.title}”?',
            body=(
                f'{state}\n\nThe following files will be committed and pushed to origin/master:\n{listed}'
            ),
        )
        dialog.add_response('cancel', 'Cancel')
        dialog.add_response('publish', 'Publish')
        dialog.set_response_appearance('publish', Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response('publish')
        dialog.connect('response', self._start_publish)
        dialog.present()

    def _show_git_identity(self, identity):
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading='Commit author',
            body=(
                'Git needs an author name and email. These values will be stored only '
                'in this blog repository.'
            ),
        )
        dialog.add_response('cancel', 'Cancel')
        dialog.add_response('save', 'Save and continue')
        dialog.set_response_appearance('save', Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response('save')
        fields = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        name = Gtk.Entry(placeholder_text='Author name', text=identity.name)
        email = Gtk.Entry(placeholder_text='Author email', text=identity.email)
        fields.append(name)
        fields.append(email)
        dialog.set_extra_child(fields)

        def respond(_dialog, response):
            if response != 'save':
                return
            try:
                configure_git_identity(self.root, name.get_text(), email.get_text())
            except Exception as error:
                self._error(str(error))
                return
            self._confirm_publish()

        dialog.connect('response', respond)
        dialog.present()

    def _start_publish(self, _dialog, response):
        if response != 'publish' or not self.current:
            return
        try:
            self._apply_form()
            self.current.save()
            self.dirty = False
        except Exception as error:
            self._error(str(error))
            return
        post = self.current
        self.publish_button.set_sensitive(False)
        self._toast('Publishing…')

        def worker():
            try:
                result = publish_post(self.root, post)
                GLib.idle_add(self._publish_finished, result, None)
            except Exception as error:
                GLib.idle_add(self._publish_finished, None, error)

        threading.Thread(target=worker, daemon=True).start()

    def _publish_finished(self, result, error):
        self.publish_button.set_sensitive(True)
        if error:
            self._error(f'Publishing failed:\n\n{error}')
            return GLib.SOURCE_REMOVE
        files = '\n'.join(f'• {path}' for path in result.files)
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading='Published successfully',
            body=f'Commit {result.commit} was pushed to origin/master.\n\n{files}',
        )
        dialog.add_response('ok', 'OK')
        dialog.present()
        return GLib.SOURCE_REMOVE

    def _confirm_update(self, *_):
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading='Update local repository?',
            body=(
                'The editor will save the current post and download changes from '
                'origin/master using fast-forward-only mode. Local changes will not be '
                'overwritten; Git will stop if an update conflicts with them.'
            ),
        )
        dialog.add_response('cancel', 'Cancel')
        dialog.add_response('update', 'Update')
        dialog.set_response_appearance('update', Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response('update')
        dialog.connect('response', self._start_update)
        dialog.present()

    def _start_update(self, _dialog, response):
        if response != 'update':
            return
        try:
            if self.current:
                self._apply_form()
                self.current.save()
                self.dirty = False
            selected = self.current.path if self.current else None
        except Exception as error:
            self._error(str(error))
            return
        self.update_button.set_sensitive(False)
        self.publish_button.set_sensitive(False)
        self._toast('Updating repository…')

        def worker():
            try:
                result = update_repository(self.root)
                GLib.idle_add(self._update_finished, result, None, selected)
            except Exception as error:
                GLib.idle_add(self._update_finished, None, error, selected)

        threading.Thread(target=worker, daemon=True).start()

    def _update_finished(self, result, error, selected):
        self.update_button.set_sensitive(True)
        self.publish_button.set_sensitive(True)
        if error:
            self._error(f'Update failed:\n\n{error}')
            return GLib.SOURCE_REMOVE
        self.current = None
        self._load_posts(selected)
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading='Repository updated',
            body=f'Local master is now at {result.commit}.\n\n{result.output}',
        )
        dialog.add_response('ok', 'OK')
        dialog.present()
        return GLib.SOURCE_REMOVE

    def _show_new_post(self, *_):
        dialog = Adw.MessageDialog(transient_for=self, heading='New post')
        dialog.add_response('cancel', 'Cancel')
        dialog.add_response('create', 'Create')
        dialog.set_response_appearance('create', Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response('create')
        fields = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        title = Gtk.Entry(placeholder_text='Title')
        slug = Gtk.Entry(placeholder_text='slug-generated-from-title')
        title.connect('changed', lambda entry: slug.set_placeholder_text(slugify(entry.get_text())))
        fields.append(title)
        fields.append(slug)
        dialog.set_extra_child(fields)

        def respond(_dialog, response):
            if response != 'create':
                return
            try:
                post = create_post(self.root, title.get_text(), slug.get_text() or None)
                self.current = None
                self._load_posts(post.path)
                self._toast('New draft created')
            except Exception as error:
                self._error(str(error))

        dialog.connect('response', respond)
        dialog.present()

    def _choose_image(self, mode: str):
        chooser = Gtk.FileChooserNative.new(
            'Choose image', self, Gtk.FileChooserAction.OPEN, 'Open', 'Cancel'
        )
        image_filter = Gtk.FileFilter(name='Images')
        for mime in ('image/png', 'image/jpeg', 'image/webp', 'image/gif', 'image/svg+xml'):
            image_filter.add_mime_type(mime)
        chooser.add_filter(image_filter)
        if mode == 'edit':
            chooser.set_current_folder(Gio.File.new_for_path(str(self.root / 'public')))

        def response(_chooser, result):
            if result != Gtk.ResponseType.ACCEPT:
                return
            source = Path(chooser.get_file().get_path())
            try:
                if mode == 'edit':
                    self._show_image_editor(source)
                    return
                prefix = slugify(self.current.title) if self.current else ''
                _destination, public_path = import_image(self.root, source, prefix)
                if mode == 'cover':
                    self.cover_entry.set_text(public_path)
                else:
                    buffer = self.text_view.get_buffer()
                    cursor = buffer.get_iter_at_mark(buffer.get_insert())
                    before = buffer.get_text(buffer.get_start_iter(), cursor, True)
                    after = buffer.get_text(cursor, buffer.get_end_iter(), True)
                    before_breaks = len(before) - len(before.rstrip('\n'))
                    after_breaks = len(after) - len(after.lstrip('\n'))
                    leading = '\n' * max(0, 2 - before_breaks) if before else ''
                    trailing = '\n' * max(0, 2 - after_breaks) if after else ''
                    alt = source.stem.replace('-', ' ').replace('_', ' ')
                    buffer.insert_at_cursor(f'{leading}![{alt}]({public_path}){trailing}')
                self._toast(f'Copied to public/images/{Path(public_path).name}')
            except Exception as error:
                self._error(str(error))

        chooser.connect('response', response)
        chooser.show()

    def _show_image_editor(self, path: Path):
        dialog = Adw.MessageDialog(transient_for=self, heading=f'Edit {path.name}')
        try:
            from PIL import Image

            with Image.open(path) as image:
                dimensions = f'{image.width} × {image.height} px'
        except Exception:
            dimensions = 'Image preview'
        dialog.set_body(
            f'{dimensions}. Values are applied to the image file. '
            'Leave width or height empty to keep proportions.'
        )
        dialog.add_response('cancel', 'Cancel')
        dialog.add_response('apply', 'Apply')
        dialog.set_response_appearance('apply', Adw.ResponseAppearance.SUGGESTED)
        grid = Gtk.Grid(column_spacing=8, row_spacing=8)
        preview = Gtk.Picture.new_for_filename(str(path))
        preview.set_can_shrink(True)
        preview.set_content_fit(Gtk.ContentFit.CONTAIN)
        preview.set_size_request(520, 280)
        preview.add_css_class('card')
        grid.attach(preview, 0, 0, 2, 1)
        inputs = {}
        fields = (
            ('width', 'Width'), ('height', 'Height'), ('crop_left', 'Crop left'),
            ('crop_top', 'Crop top'), ('crop_right', 'Crop right'), ('crop_bottom', 'Crop bottom'),
        )
        for index, (key, label) in enumerate(fields):
            entry = Gtk.Entry(input_purpose=Gtk.InputPurpose.DIGITS, placeholder_text='0')
            inputs[key] = entry
            grid.attach(Gtk.Label(label=label, xalign=0), 0, index + 1, 1, 1)
            grid.attach(entry, 1, index + 1, 1, 1)
        rotation = Gtk.DropDown.new_from_strings(['0°', '90°', '180°', '270°'])
        format_box = Gtk.DropDown.new_from_strings(['Keep format', 'WebP', 'JPEG', 'PNG'])
        grid.attach(Gtk.Label(label='Rotate', xalign=0), 0, 7, 1, 1)
        grid.attach(rotation, 1, 7, 1, 1)
        grid.attach(Gtk.Label(label='Format', xalign=0), 0, 8, 1, 1)
        grid.attach(format_box, 1, 8, 1, 1)
        dialog.set_extra_child(grid)

        def apply(_dialog, response):
            if response != 'apply':
                return
            try:
                number = lambda key: int(inputs[key].get_text() or '0')
                formats = [None, 'webp', 'jpeg', 'png']
                edits = ImageEdits(
                    width=number('width') or None,
                    height=number('height') or None,
                    rotate=[0, 90, 180, 270][rotation.get_selected()],
                    crop_left=number('crop_left'),
                    crop_top=number('crop_top'),
                    crop_right=number('crop_right'),
                    crop_bottom=number('crop_bottom'),
                    output_format=formats[format_box.get_selected()],
                )
                output = edit_image(path, edits)
                if output != path and self.current:
                    try:
                        old_url = '/' + path.relative_to(self.root / 'public').as_posix()
                        new_url = '/' + output.relative_to(self.root / 'public').as_posix()
                        buffer = self.text_view.get_buffer()
                        body = self._body_text().replace(old_url, new_url)
                        buffer.set_text(body)
                        if self.cover_entry.get_text() == old_url:
                            self.cover_entry.set_text(new_url)
                    except ValueError:
                        pass
                self._toast(f'Saved {output.name}')
            except Exception as error:
                self._error(str(error))

        dialog.connect('response', apply)
        dialog.present()

    def _toast(self, message: str):
        self.toast_overlay.add_toast(Adw.Toast.new(message))

    def _error(self, message: str):
        dialog = Adw.MessageDialog(transient_for=self, heading='Cannot complete the action', body=message)
        dialog.add_response('ok', 'OK')
        dialog.present()


class BlogEditorApplication(Adw.Application):
    def __init__(self, root: Path):
        super().__init__(application_id='io.boldmerge.BlogEditor', flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.root = root

    def do_activate(self):
        window = self.props.active_window
        if window is None:
            window = BlogEditorWindow(self, self.root)
        window.present()


def main(argv=None):
    argv = argv or sys.argv
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not (root / 'content' / 'posts').is_dir():
        print(f'Not an Astro blog directory: {root}', file=sys.stderr)
        return 2
    app = BlogEditorApplication(root)
    return app.run([argv[0]])
