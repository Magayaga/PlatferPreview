# Copyright 2023-2025 Cyril John Magayaga
# Platfer Preview (v2.0-preview5)
# Linux operating system
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
from gi.repository import Gtk, WebKit2, GLib

class Platfer:
    def __init__(self):
        self.linux = Gtk.Window()
        self.linux.set_title("Platfer Preview")
        self.linux.set_default_size(950, 600)
        
        # Keep track of tabs
        self.tabs = []
        self.current_tab = None
        
        self.init_ui()

    def init_ui(self):
        # Main vertical box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Setup header bar
        self.navbar = Gtk.HeaderBar()
        self.navbar.set_show_close_button(True)
        self.linux.set_titlebar(self.navbar)

        # URL entry
        self.entry = Gtk.Entry()
        self.entry.set_width_chars(40)
        self.entry.connect("activate", self.enter)
        self.navbar.set_custom_title(self.entry)

        # Navigation buttons
        self.go_back_button = Gtk.Button.new_from_icon_name("go-previous", Gtk.IconSize.SMALL_TOOLBAR)
        self.go_back_button.connect("clicked", self.go_back)
        self.navbar.pack_start(self.go_back_button)

        self.go_forward_button = Gtk.Button.new_from_icon_name("go-next", Gtk.IconSize.SMALL_TOOLBAR)
        self.go_forward_button.connect("clicked", self.go_forward)
        self.navbar.pack_start(self.go_forward_button)

        self.go_refresh_button = Gtk.Button.new_from_icon_name("view-refresh", Gtk.IconSize.SMALL_TOOLBAR)
        self.go_refresh_button.connect("clicked", self.go_refresh)
        self.navbar.pack_start(self.go_refresh_button)

        self.go_home_button = Gtk.Button.new_from_icon_name("go-home", Gtk.IconSize.SMALL_TOOLBAR)
        self.go_home_button.connect("clicked", self.go_home)
        self.navbar.pack_start(self.go_home_button)

        # About button
        self.about_btn = Gtk.Image.new_from_icon_name("help-about", Gtk.IconSize.SMALL_TOOLBAR)
        self.about_button = Gtk.Button()
        self.about_button.add(self.about_btn)
        self.about_button.connect("clicked", self.go_about)
        self.navbar.pack_end(self.about_button)

        # New tab button
        self.new_tab_btn = Gtk.Image.new_from_icon_name("list-add", Gtk.IconSize.SMALL_TOOLBAR)
        self.new_tab_button = Gtk.Button()
        self.new_tab_button.add(self.new_tab_btn)
        self.new_tab_button.connect("clicked", self.create_new_tab)
        self.navbar.pack_end(self.new_tab_button)

        # Create notebook (tabbed container)
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.connect("switch-page", self.on_tab_switch)
        
        # Add notebook to main container
        self.main_box.pack_start(self.notebook, True, True, 0)
        
        # Create first tab
        self.create_new_tab()
        
        self.linux.connect("destroy", Gtk.main_quit)
        self.linux.add(self.main_box)
        self.linux.show_all()
        Gtk.main()

    def create_tab_content(self, url="https://www.google.com"):
        # Create scrolled window
        scrolled_window = Gtk.ScrolledWindow()
        
        # Create WebView
        web_view = WebKit2.WebView()
        web_view.load_uri(url)
        web_view.connect("notify::estimated-load-progress", self.change_url)
        web_view.connect("notify::title", self.update_tab_title)
        
        # Add WebView to scrolled window
        scrolled_window.add(web_view)
        
        return scrolled_window, web_view

    def create_tab_label(self, title="New Tab"):
        # Create a box for tab label
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        # Add label
        label = Gtk.Label(title)
        box.pack_start(label, True, True, 0)
        
        # Add close button
        close_button = Gtk.Button()
        close_icon = Gtk.Image.new_from_icon_name("window-close", Gtk.IconSize.MENU)
        close_button.add(close_icon)
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.connect("clicked", self.close_tab)
        box.pack_start(close_button, False, False, 0)
        
        box.show_all()
        return box, label

    def create_new_tab(self, widget=None, url="https://www.google.com"):
        # Create tab content
        tab_content, web_view = self.create_tab_content(url)
        
        # Create tab label
        tab_box, tab_label = self.create_tab_label()
        
        # Add page to notebook
        page_index = self.notebook.append_page(tab_content, tab_box)
        
        # Store tab info
        tab_info = {
            "web_view": web_view,
            "label": tab_label,
            "scrolled_window": tab_content
        }
        self.tabs.append(tab_info)
        
        # Show all widgets
        self.notebook.show_all()
        
        # Switch to new tab
        self.notebook.set_current_page(page_index)

    def close_tab(self, button):
        # Get the tab that contains this button
        current_page = self.notebook.get_current_page()
        
        # Remove the tab
        self.notebook.remove_page(current_page)
        
        # Remove from our list
        if current_page < len(self.tabs):
            self.tabs.pop(current_page)
        
        # If no tabs left, create a new one
        if self.notebook.get_n_pages() == 0:
            self.create_new_tab()

    def on_tab_switch(self, notebook, page, page_num):
        # Update current tab
        if page_num < len(self.tabs):
            self.current_tab = self.tabs[page_num]
            
            # Update URL bar
            web_view = self.current_tab["web_view"]
            uri = web_view.get_uri()
            if uri:
                self.entry.set_text(uri)

    def update_tab_title(self, web_view, param):
        # Find which tab contains this web_view
        for i, tab in enumerate(self.tabs):
            if tab["web_view"] == web_view:
                title = web_view.get_title()
                if title:
                    tab["label"].set_text(title[:15] + "..." if len(title) > 15 else title)
                break

    def go_about(self, about_button):
        window = Gtk.Window()
        window.set_default_size(600, 275)

        # Get the current WebKit version
        webkit_version = WebKit2.get_major_version(), WebKit2.get_minor_version(), WebKit2.get_micro_version()
        webkit_version_str = f"{webkit_version[0]}.{webkit_version[1]}.{webkit_version[2]}"

        # Platfer Preview version
        platfer_preview_version = "v2.0-preview5"
        platfer_preview_stable_release = "March 23, 2025"

        label = Gtk.Label()
        window.set_title("About")
        label.set_markup(
            "<b><big>Platfer Preview</big></b>\n"
            "The Philippines' first web browser.\n"
            "It was created, designed, and developed by <b>Cyril John Magayaga</b>.\n\n"
            f"<b>Stable release</b>: ({platfer_preview_version}) / {platfer_preview_stable_release}.\n"
            f"Powered by <b>WebKit</b> browser engine ({webkit_version_str})\n\n"
            "Copyright 2022-2025 Cyril John Magayaga. All rights reserved."
        )
        label.set_justify(Gtk.Justification.LEFT)
        label.set_line_wrap(True)
        window.add(label)

        label.show()
        window.show()

    def enter(self, entry):
        url = entry.get_text()
        if self.current_tab:
            web_view = self.current_tab["web_view"]
            if url.startswith("http://") or url.startswith("https://"):
                web_view.load_uri(url)
            else:
                platferurl = "https://" + url
                web_view.load_uri(platferurl)

    def change_url(self, web_view, param):
        if self.current_tab and web_view == self.current_tab["web_view"]:
            uri = web_view.get_uri()
            if uri:
                self.entry.set_text(uri)

    def go_back(self, button):
        if self.current_tab:
            self.current_tab["web_view"].go_back()

    def go_forward(self, button):
        if self.current_tab:
            self.current_tab["web_view"].go_forward()

    def go_refresh(self, button):
        if self.current_tab:
            self.current_tab["web_view"].reload()

    def go_home(self, button):
        if self.current_tab:
            self.current_tab["web_view"].load_uri("https://www.google.com")

if __name__ == "__main__":
    app = Platfer()
