#!/usr/bin/env python3

import os
import sys
import wx
import bank
import helpers

class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)

        self.file_data = None
        self.init_ui()

    def create_menu_bar(self):
        file_menu = wx.Menu()
        open_item = file_menu.Append(wx.ID_OPEN, '&Open...', 'Open K5000 file')
        exit_item = file_menu.Append(wx.ID_EXIT)

        convert_menu = wx.Menu()
        self.convert_item = convert_menu.Append(wx.ID_ANY, '&Convert', 'Convert to System Exclusive')
        self.convert_item.Enable(False)  # disable this menu item until we have file data

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, '&File')
        menu_bar.Append(convert_menu, "&Convert")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.OnExit, exit_item)
        self.Bind(wx.EVT_MENU, self.OnFileOpen, open_item)
        self.Bind(wx.EVT_MENU, self.OnConvertToSysEx, self.convert_item)

    def init_ui(self):
        self.panel = wx.Panel(self, wx.ID_ANY)

        title = wx.StaticText(self.panel, wx.ID_ANY, 'Kawai K5000 File Information')

        file_kind_label = wx.StaticText(self.panel, wx.ID_ANY, 'File kind')
        self.file_kind_value = wx.StaticText(self.panel, wx.ID_ANY, '(unknown)')

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_sizer.Add(title, 0, wx.ALL, 5)

        file_kind_sizer = wx.BoxSizer(wx.HORIZONTAL)
        file_kind_sizer.Add(file_kind_label, 0, wx.ALL, 5)
        file_kind_sizer.Add(self.file_kind_value, 1, wx.ALL | wx.EXPAND, 5)

        self.patch_count_value = wx.StaticText(self.panel, wx.ID_ANY, str(0))
        patch_count_label = wx.StaticText(self.panel, wx.ID_ANY, 'Patch count')
        patch_count_sizer = wx.BoxSizer(wx.HORIZONTAL)
        patch_count_sizer.Add(patch_count_label, 0, wx.ALL, 5)
        patch_count_sizer.Add(self.patch_count_value, 1, wx.ALL | wx.EXPAND, 5)

        self.patch_list = wx.ListView(self.panel, wx.ID_ANY)
        self.patch_list.InsertColumn(0, 'name', width=100)

        top_sizer.Add(title_sizer, 0, wx.CENTER)
        top_sizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 5)
        top_sizer.Add(file_kind_sizer)
        top_sizer.Add(patch_count_sizer)
        top_sizer.Add(self.patch_list, 1, wx.EXPAND)
        self.panel.SetSizer(top_sizer)
        top_sizer.Fit(self)

        self.create_menu_bar()

        self.statusbar = self.CreateStatusBar(number=1)  # one field
        self.statusbar.SetStatusText('Select K5000 file to convert with the File | Open menu command')

        self.SetSize((640, 480))
        self.SetTitle('K5KTools')
        self.Centre()

    def OnConvertToSysEx(self, event):
        if self.file_data is None:
            print("No file data, unable to convert to SysEx")
            return

        print('Here we would convert the file to SysEx')

    def OnFileOpen(self, event):
        with wx.FileDialog(self, "Open Kawai K5000 file",
                           wildcard="Kawai K5000 files (*.kaa;*.ka1;*.kca;*.kc1)|*.kaa;*.ka1;*.kca;*.kc1",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = file_dialog.GetPath()
            file_root, file_ext = os.path.splitext(pathname)
            file_kind = file_ext[1:].lower()  # skip the dot in the extension
            print(f'Pathname = {pathname}, kind = {file_kind}')
            try:
                self.file_data = helpers.read_file_data(pathname)
                print(f'Read {len(self.file_data)} bytes of data from file')
                self.convert_item.Enable(self.file_data is not None)

                # Collect the information to use in the UI
                kind_value = 'Unknown'
                patch_count = 0
                patch_names = []
                if file_kind == 'kaa':
                    kind_value = 'Bank of single patches'
                    bank_data = bank.get_bank(self.file_data)
                    patches = sorted(bank_data['patches'], key=lambda x: x['index'])
                    for ix, patch in enumerate(patches):
                        patch_count += 1
                        patch_names.append(patch['name'])
                elif file_kind == 'ka1':
                    kind_value = 'One single patch'
                    patch_count = 1
                elif file_kind == 'kca':
                    kind_value = 'Bank of multi/combi patches'
                    patch_count = 64
                elif file_kind == 'kc1':
                    kind_value = 'One multi/combi patch'
                    patch_count = 1
                self.file_kind_value.SetLabel(kind_value)
                self.patch_count_value.SetLabel(str(patch_count))

                for ix, name in enumerate(patch_names):
                    self.patch_list.InsertItem(ix, name)
                    # Other columns would be filled in using the index

            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

def main():
    app = wx.App()
    main_frame = MainFrame(None)
    main_frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
