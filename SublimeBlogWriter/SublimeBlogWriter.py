# coding=utf-8
import sys
import os
import sublime
import sublime_plugin
import codecs
import re
import json
import threading

package_file = os.path.normpath(os.path.abspath(__file__))
package_path = os.path.dirname(package_file)
lib_path = os.path.join(package_path, "lib")

if lib_path not in sys.path:
    sys.path.append(lib_path)

import markdown
from sinastorage.bucket import SCSBucket, ACL
import sinastorage
import urllib

SETTINGS_FILE = "SublimeBlogWriter.sublime-settings"
settings = sublime.load_settings(SETTINGS_FILE)


sinastorage.setDefaultAppInfo(settings.get("scs_accesskey"), settings.get("scs_secretkey"))
s = SCSBucket('binsite', secure=False)


# 使用线程避免主界面阻塞
class ImageProcessor(threading.Thread):
    def __init__(self, input_file, callback):
        self.current_image = 0
        self.done_image = 0
        self.image_queue = []
        self.rg = re.compile('!\\[(.*?)\\]\\((.*)\\)', re.IGNORECASE | re.DOTALL)
        self.input_file = input_file
        self.callback = callback
        self.text = ""
        threading.Thread.__init__(self)

    def run(self):
        # text = input_file.read()
        lines = self.input_file.readlines()
        for line in lines:
            m = self.rg.search(line)
            if m:
                alt = m.group(1)
                img_path = m.group(2)
                self.image_queue.append(img_path)
                url = settings.get("image_profix_url") + settings.get("image_folder") + os.path.basename(img_path).replace(' ', '_')
                self.text += "![" + alt + "](" + url + ")\n"
            else:
                self.text += line

        self.image_num = len(self.image_queue)
        self.uploadFile()


    def uploadFile(self):
        def uploadFileCallback(progress, size):
            if progress == size:
                if self.current_image > self.done_image:
                    sublime.status_message("Image(" + str(self.current_image) + "/" + str(self.image_num) + "): upload successfully!")
                    self.done_image += 1
                    self.uploadFile()
            else:
                sublime.status_message("Uploading image(" + str(self.current_image) + "/" + str(self.image_num) + "): %d%%" % (progress * 100.0 / size))

        if len(self.image_queue) > 0:
            self.current_image += 1
            sublime.status_message("Start to upload image: " + str(self.current_image) + "/" + str(self.image_num))
            local_file_path = self.image_queue.pop(0)
            upload_file_path = settings.get("image_folder") + os.path.basename(local_file_path).replace(' ', '_')
            acl = "public-read"
            s.putFile(upload_file_path, local_file_path, uploadFileCallback, acl)

        else:
            sublime.status_message("Image upload successfully")
            self.callback(self.text)


class PostArticleCommand(sublime_plugin.WindowCommand):
    def on_cancel(self):
        sublime.status_message("Post aborted")

    def on_get_caption(self, caption=None):
        self.caption = caption
        self.window.show_input_panel("Keywords:", "", self.on_get_keywords, None, self.on_cancel)

    def on_get_keywords(self, keywords=None):
        self.keywords = keywords
        self.process()

    def process(self):
        def processText(text):
            html = markdown.markdown(text)
            self.content = html
            self.post()
        input_file = codecs.open(self.file_path, mode="r", encoding="utf-8")
        processor = ImageProcessor(input_file=input_file, callback=processText)
        processor.start()

    def run(self, *args, **kwargs):
        self.file_path = self.window.active_view().file_name()
        if os.path.splitext(self.file_path)[1] == ".md":
            self.window.show_input_panel("Caption:", "", self.on_get_caption, None, self.on_cancel)
        else:
            sublime.message_dialog("The format of posted article should be md!")

    def post(self):
        data = {"username": settings.get("blog_username"), "password": settings.get("blog_password"),
                "operation": settings.get("operation"), "caption": self.caption,
                "classification": settings.get("article_classification"),
                "keywords": self.keywords, "content": self.content}
        post_data = urllib.parse.urlencode(data).encode(encoding="UTF8")
        try:
            response = urllib.request.urlopen(settings.get("blog_post_api"), post_data)
            result = json.loads(response.read().decode("UTF8"))
            if result["code"] == "success":
                sublime.message_dialog("Post article successfully, article_id = " + str(result["article_id"]))
            else:
                sublime.message_dialog("Fail to post the article, reason: " + result["reason"])
        except:
            sublime.message_dialog("Fail to post the article, please check the server is running!")
