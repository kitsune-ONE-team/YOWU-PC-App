#!/usr/bin/env python3

# Copyright (c) 2025 kitsune.ONE team.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import gi
import platform

from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from gi.events import GLibEventLoopPolicy

PERIPHERALS = (
    'YOWU-SELKIRK-4',
    'YOWU-SELKIRK-4GS',
)

MODES = (
    (1, 'Default'),
    (2, 'Flash'),
    (3, 'Breath'),
    (4, 'Rhythm'),
    (5, 'YOWU'),
    (6, 'Off'),
)


if platform.system() == 'Windows':
    try:
        from bleak.backends.winrt.util import allow_sta
        allow_sta()
    except ImportError:
        pass


def add_checksum(data: bytearray) -> None:
    # Calculate checksum (sum of all bytes with wrapping subtraction)
    checksum = 0
    for byte in data:
        checksum = (checksum - byte) & 0xFF  # & 0xFF for byte wrapping
    data[-1] = checksum


def set_mode(
        mode: int = 0,
        rgb: tuple[int, int, int] = (0, 0, 0),
        settings: tuple[int, int] = (0, 0)) -> bytes:
    # 0xFC, 0x04, 0x01, 0x06 = header / command
    # settings: brightness + speed / bpm + duration
    cmd = bytearray([
        0xFC, 0x04, 0x01, 0x06, 
        mode, rgb[0], rgb[1], rgb[2], settings[0], settings[1], 
        0x00,
    ])
    add_checksum(cmd)
    return bytes(cmd)


class Win(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_border_width(8)
        self.set_default_size(480, 360)

        self.header = Gtk.HeaderBar(title='YOWU')
        self.header.set_show_close_button(True)

        self.apply = Gtk.Button(label='Apply')
        self.apply.connect('clicked', self.on_apply)
        self.header.pack_start(self.apply)

        self.set_titlebar(self.header)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        container = Gtk.FlowBox()
        container.set_valign(Gtk.Align.START)
        container.set_max_children_per_line(1)
        container.set_selection_mode(Gtk.SelectionMode.NONE)
        container.set_row_spacing(8)
        container.set_column_spacing(8)

        self.color = Gtk.ColorButton.new_with_rgba(Gdk.RGBA(1, 0, 0, 1))
        container.add(self.color)

        modes = Gtk.ListStore(int, str)
        for item in MODES:
            modes.append(list(item))
        mode_text = Gtk.CellRendererText()
        self.mode = Gtk.ComboBox.new_with_model(modes)
        self.mode.pack_start(mode_text, True)
        self.mode.add_attribute(mode_text, 'text', 1)
        self.mode.set_active(0)
        container.add(self.mode)

        self.value_label = Gtk.Label('Speed:')
        container.add(self.value_label)

        self.value = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.value.set_value(1)
        container.add(self.value)

        self.duration_label = Gtk.Label('Duration:')
        container.add(self.duration_label)

        self.duration = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.duration.set_value(1)
        container.add(self.duration)

        self.spinner = Gtk.Spinner()
        container.add(self.spinner)

        scroll.add(container)

        self.add(scroll)

        self.show_all()

        self.headset = None
        self.client = None
        self.header.set_subtitle('Connecting...')
        self.spinner.start()
        self.color.hide()
        self.mode.hide()
        self.value_label.hide()
        self.value.hide()
        self.duration_label.hide()
        self.duration.hide()
        self.apply.set_sensitive(False)
 
        self.connect('destroy', self.on_exit)
        self.discover_task = asyncio.create_task(self.do_discover())

    def on_exit(self, *args):
        self.exit_task = asyncio.create_task(self.do_exit(self.headset, self.client))

    async def do_exit(self, headset, client):
        if client:
            await client.disconnect()
        Gtk.main_quit()

    async def do_discover(self):
        headset = None
        try:
            peripherals = await BleakScanner.discover()
            for peripheral in peripherals:
                print(peripheral.details)
                if peripheral.name in PERIPHERALS:
                    headset = peripheral
                    break
        except BleakError:
            pass

        client = None
        if headset:
            client = BleakClient(headset)
            await client.connect()

        self.on_discover(headset, client)

    def on_discover(self, headset, client):
        self.headset = headset
        self.client = client

        self.spinner.stop()
        self.spinner.hide()

        if self.headset:
            self.header.set_subtitle(self.headset.name)
            self.color.show()
            self.mode.show()
            self.value_label.show()
            self.value.show()
            self.duration_label.show()
            self.duration.show()
            self.apply.set_sensitive(True)
        else:
            self.header.set_subtitle('Headset not found')

    def on_apply(self, *args):
        color = self.color.get_rgba().to_color()
        rgb = [round(x * 255) for x in color.to_floats()]

        mode_iter = self.mode.get_active_iter() or 0
        mode = self.mode.get_model()[mode_iter][0]

        value = round(self.value.get_value() / 100 * 255)
        duration = round(self.duration.get_value() / 100 * 255)

        self.apply.set_sensitive(False)
        self.apply_task = asyncio.create_task(self.do_apply(
            self.headset, self.client, mode=mode, rgb=rgb, settings=[value, duration]))

    async def do_apply(self, headset, client, **kwargs):
        cmd = set_mode(rgb=kwargs['rgb'])
        await client.write_gatt_char('2A06', cmd, response=False)

        cmd = set_mode(mode=kwargs['mode'], settings=kwargs['settings'])
        await client.write_gatt_char('2A06', cmd, response=False)

        self.apply.set_sensitive(True)


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='one.kitsune.YOWU')
        self.win = None

    def do_activate(self):
        if not self.win:
            self.win = Win(application=self)
        self.win.present()


def main():
    asyncio.set_event_loop_policy(GLibEventLoopPolicy())
    app = App()
    app.run()


if __name__ == '__main__':
    main()
