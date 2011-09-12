# vim:set et sts=4 sw=4:
#
# ibus - The Input Bus
#
# Copyright (c) 2007-2010 Peng Huang <shawn.p.huang@gmail.com>
# Copyright (c) 2007-2010 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import IBus
import locale
from icon import load_icon
from i18n import _, N_

class EngineComboBox(Gtk.ComboBox):
    __gtype_name__ = 'EngineComboBox'
    __gproperties__ = {
        'active-engine' : (
            object,
            'selected engine',
            'selected engine',
            GObject.PARAM_READABLE)
    }

    def __init__(self):
        super(EngineComboBox, self).__init__()
        self.connect("notify::active", self.__notify_active_cb)

        self.__model = None

        renderer = Gtk.CellRendererPixbuf()
        renderer.set_property("xalign", 0)
        renderer.set_property("xpad", 2)
        self.pack_start(renderer, False)
        self.set_cell_data_func(renderer, self.__icon_cell_data_cb, None)

        renderer = Gtk.CellRendererText()
        renderer.set_property("xalign", 0)
        renderer.set_property("xpad", 2)
        self.pack_start(renderer, True)
        self.set_cell_data_func(renderer, self.__name_cell_data_cb, None)

    def set_engines(self, engines):
        self.__model = Gtk.TreeStore(object)

        iter1 = self.__model.append(None)
        self.__model.set(iter1, 0, 0)
        lang = {}
        for e in engines:
            l = IBus.get_language_name(e.get_language())
            if not l:
                l = "Other"
            if l not in lang:
                lang[l] = []
            lang[l].append(e)

        keys = lang.keys()
        keys.sort(locale.strcoll)
        #add "Others" to the end of the combo box
        if "Other" in keys:
            keys.remove("Other")
            keys += ["Other"]
        for l in keys:
            iter1 = self.__model.append(None)
            self.__model.set(iter1, 0, l)
            def cmp_engine(a, b):
                if a.get_rank() == b.get_rank():
                    return locale.strcoll(a.get_longname(), b.get_longname())
                return int(b.get_rank() - a.get_rank())
            lang[l].sort(cmp_engine)
            for e in lang[l]:
                iter2 = self.__model.append(iter1)
                self.__model.set(iter2, 0, e)

        self.set_model(self.__model)
        self.set_active(0)

    def __icon_cell_data_cb(self, celllayout, renderer, model, iter, data):
        engine = self.__model.get_value(iter, 0)

        if isinstance(engine, str) or isinstance (engine, unicode):
            renderer.set_property("visible", False)
            renderer.set_property("sensitive", False)
        elif isinstance(engine, int):
            renderer.set_property("visible", False)
            renderer.set_property("sensitive", False)
        else:
            renderer.set_property("visible", True)
            renderer.set_property("sensitive", True)
            pixbuf = load_icon(engine.get_icon(), Gtk.IconSize.LARGE_TOOLBAR)
            if pixbuf == None:
                pixbuf = load_icon("ibus-engine", Gtk.IconSize.LARGE_TOOLBAR)
            if pixbuf == None:
                pixbuf = load_icon(Gtk.STOCK_MISSING_IMAGE, Gtk.IconSize.LARGE_TOOLBAR)
            renderer.set_property("pixbuf", pixbuf)

    def __name_cell_data_cb(self, celllayout, renderer, model, iter, data):
        engine = self.__model.get_value(iter, 0)

        if isinstance (engine, str) or isinstance (engine, unicode):
            renderer.set_property("sensitive", False)
            renderer.set_property("text", engine)
            renderer.set_property("weight", Pango.Weight.NORMAL)
        elif isinstance(engine, int):
            renderer.set_property("sensitive", True)
            renderer.set_property("text", _("Select an input method"))
            renderer.set_property("weight", Pango.Weight.NORMAL)
        else:
            renderer.set_property("sensitive", True)
            renderer.set_property("text", engine.get_longname())
            renderer.set_property("weight", Pango.Weight.BOLD if engine.get_rank() > 0 else Pango.Weight.NORMAL)

    def __notify_active_cb(self, combobox, property):
        self.notify("active-engine")

    def do_get_property(self, property):
        if property.name == "active-engine":
            i = self.get_active()
            if i == 0 or i == -1:
                return None
            iter = self.get_active_iter()
            return self.get_model()[iter][0]
        else:
            raise AttributeError, 'unknown property %s' % property.name

    def get_active_engine(self):
        return self.get_property("active-engine")



if __name__ == "__main__":
    ec = EngineComboBox()
    ec.set_engines(IBus.Bus().list_engines())
    w = Gtk.Window()
    w.add(ec)
    w.resize(400, 400)
    w.connect("delete-event", Gtk.main_quit)
    w.show_all()
    Gtk.main()
