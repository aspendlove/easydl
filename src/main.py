# main.py
#
# Copyright 2021 Aidan Spendlove
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
import sys
import gi
import youtube_dl

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio, Gdk

from .window import EasydlGuiWindow


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.github.copperly123.easydl',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource('/com/github/copperly123/easydl/style.css')
        priority = Gtk.STYLE_PROVIDER_PRIORITY_USER
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, priority)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = EasydlGuiWindow(application=self)
        win.present()



def main(version):
    app = Application()
    return app.run(sys.argv)
