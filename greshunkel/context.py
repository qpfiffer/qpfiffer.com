from greshunkel.build import POSTS_DIR
from greshunkel.utils import parse_variable

from os import listdir, walk
import subprocess, re

BASE_CONTEXT = {}

def get_html_from_markdown(filename, filepath):
    htmlname = "/tmp/{}".format(filename.replace(".markdown", ".html"))
    proc = subprocess.run(["pandoc", "-o", htmlname, filepath])
    all_text = None
    with open(htmlname, "r") as htmlfile:
        all_text = htmlfile.read()

    return all_text

def build_blog_context(default_context):
    default_context['POSTS'] = []

    for post in listdir(POSTS_DIR):
        if not post.endswith(".markdown"):
            continue

        new_post = {}
        dashes_seen = 0
        reading_meta = True
        filepath = POSTS_DIR + post
        filename = post
        muh_file = open(filepath)
        all_text = ""
        for line in muh_file:
            stripped = line.strip()
            if stripped == '---':
                dashes_seen += 1
                if reading_meta and dashes_seen < 2:
                    continue
            elif reading_meta and dashes_seen >= 2:
                reading_meta = False
                continue

            if reading_meta and ':' in line:
                split_line = stripped.split(":")
                new_post[split_line[0]] = "".join(split_line[1:]).replace('"', '')

            if not reading_meta:
                all_text += line

        new_post['content'] = get_html_from_markdown(filename, filepath)
        new_post['preview'] = new_post['content'][:300] + "&hellip;"
        new_post['link'] = "posts/{}".format(post.replace("markdown", "html"))
        new_post['filename'] = post
        new_post['date'] = "-".join(post.split("-")[:3])
        new_post['built_filename'] = post.replace("markdown", "html")
        default_context['POSTS'].append(new_post)
        muh_file.close()
    default_context['POSTS'] = sorted(default_context['POSTS'], key=lambda x: x["date"], reverse=True)
    default_context['POSTS_LIMITED'] = default_context['POSTS'][:5]
    return default_context
