import sublime
import sublime_plugin
import os


class BuildWithArgsCommand(sublime_plugin.WindowCommand):

    def on_cancel(self):
        sublime.status_message("Compile aborted")

    def on_get_args(self, args=None):
        self.command += args
        # sublime.message_dialog(self.command)
        self.window.run_command("exec", {"cmd": ["bash", "-c", self.command]})

    def run(self, *args, **kwargs):
        file_path = self.window.active_view().file_name()
        split = os.path.splitext(file_path)
        target_file_path = split[0]
        file_type = split[1]
        if file_type == ".c":
            # 如果为unp的例子，加上链接库-lunp
            if self.window.active_view().find("unp.h", 0, sublime.IGNORECASE):
                self.command = "gcc '" + file_path + "'  -lunp -o  '" + target_file_path + "' && '" + target_file_path + "' "
            else:
                self.command = "gcc '" + file_path + "' -o  '" + target_file_path + "' && '" + target_file_path + "' "
        elif file_type == ".py":
            self.command = "python " + file_path + " "
        self.window.show_input_panel("Input args(split by SPACE):", "", self.on_get_args, None, self.on_cancel)

        # extend for .note
        elif file_type == ".note":
            note_file = open(file_path, 'r')
            sublime.message_dialog("aaa")

