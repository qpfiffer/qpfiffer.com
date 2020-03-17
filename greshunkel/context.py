from datetime import datetime, timezone
from os import listdir
import subprocess

BASE_CONTEXT = {}

def get_html_from_markdown(filename, filepath):
    htmlname = "/tmp/{}".format(filename.replace(".markdown", ".html"))
    subprocess.run(["pandoc", "-o", htmlname, filepath])
    all_text = None
    with open(htmlname, "r") as htmlfile:
        all_text = htmlfile.read()

    return all_text

def build_blog_context(default_context, directory, output_path, var_name):
    default_context[var_name] = []

    for post in listdir(directory):
        if not post.endswith(".markdown"):
            continue

        new_post = {}
        dashes_seen = 0
        reading_meta = True
        filepath = directory + post
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
        new_post['link'] = "{}/{}".format(output_path, post.replace("markdown", "html"))
        new_post['filename'] = post
        split_post = post.split("-")[:3]
        new_post['date'] = "-".join(split_post)
        try:
            dtime = datetime.now(timezone.utc).replace(
                    year=int(split_post[0]),
                    month=int(split_post[1]),
                    day=int(split_post[2]),
                    hour=16,
                    minute=0,
                    second=0,
                    microsecond=0)
            new_post['rss_date'] = dtime.strftime("%a, %d %b %Y %H:%M:%S %z")
        except Exception as e:
            pass
        new_post['built_filename'] = post.replace("markdown", "html")
        default_context[var_name].append(new_post)
        muh_file.close()
    default_context[var_name] = sorted(default_context[var_name], key=lambda x: x["date"], reverse=True)
    limited_name = '{}_LIMITED'.format(var_name)
    default_context[limited_name] = default_context[var_name][:5]
    return default_context
