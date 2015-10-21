# !/usr/bin/env python
# coding=utf-8
#
# FileName:      AddHeader.py
# Author:        binss
# Create:        2015-10-21 13:38:47
# Description:   No Description
#

import sublime
import sublime_plugin
import os
import datetime


class AddHeaderCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_path = self.view.file_name()
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_path)[1]
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # sublime.message_dialog(time)
        author = "binss"

        if file_type == ".py":
            header = "# !/usr/bin/env python\n"
            header += "# coding=utf-8\n"
            header += "# \n"
            header += "# FileName:      %s\n" % file_name
            header += "# Author:        %s\n" % author
            header += "# Create:        %s\n" % time
            header += "# Description:   No Description\n"
            header += "# \n"


        elif file_type in [".c", ".cpp", ".h", ".hpp"]:
            header = "/***********************************************************\n"
            header += "* FileName:      %s\n" % file_name
            header += "* Author:        %s\n" % author
            header += "* Create:        %s\n" % time
            header += "* Description:   No Description\n"
            header += "***********************************************************/\n"
            header += "\n"

        else:
            return
        self.view.insert(edit, 0, header)
        region = self.view.find("No Description", 0)
        self.view.show(region)
        pos = self.view.sel()
        self.view.sel().clear()
        self.view.sel().add(region)
