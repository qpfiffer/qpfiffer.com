from collections import namedtuple
from datetime import datetime, timezone
from os import listdir
import hashlib, subprocess

BASE_CONTEXT = {
    "TIMELINE_ENTRIES": [
        {"date": "January 1 2021", "weeks": "15", "text": "Flagstaff, AZ", "containerclass": "left"},
        {"date": "April 17 2021", "weeks": "6", "text": "Boise, ID", "containerclass": "right"},
        {"date": "May 31 2021", "weeks": "4", "text": "Mazama, WA", "containerclass": "left"},
        {"date": "July 4 2021", "weeks": "4", "text": "Squamish", "containerclass": "right"},
        {"date": "August 2021", "weeks": "4", "text": "Northwest Territories (Nahanni, Cirque of the Unclimbambles)", "containerclass": "left"},
        {"date": "September 6 2021", "weeks": "5", "text": "Grant's Pass, OR", "containerclass": "right"},
        {"date": "October 16 2021", "weeks": "5", "text": "Bend, OR", "containerclass": "left"},
        {"date": "November 25 2021", "weeks": "12", "text": "Geneva, Switzerland", "containerclass": "right"},
        {"date": "March 1 2022", "weeks": "12", "text": "Norway", "containerclass": "left"},
        {"date": "June 1 2022", "weeks": "8", "text": "Faroe Islands", "containerclass": "right"},
        {"date": "August 1 2022", "weeks": "12", "text": "Vancouver Island", "containerclass": "left"},
        {"date": "November 1 2022", "weeks": "?", "text": "South America", "containerclass": "right"},
    ]
}

Tag = namedtuple("Tag", ["name", "color", "html"])

def get_html_from_markdown(filename, filepath):
    htmlname = "/tmp/{}".format(filename.replace(".markdown", ".html"))
    subprocess.run(["pandoc", "-o", htmlname, filepath])
    all_text = None
    with open(htmlname, "r") as htmlfile:
        all_text = htmlfile.read()

    return all_text

def build_blog_context(default_context, directory, output_path, var_name):
    tag_str = f"{var_name}_TAGS"
    default_context[var_name] = []
    default_context[tag_str] = []

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
        new_post['link'] = "{}{}".format(output_path, post.replace("markdown", "html"))
        new_post['filename'] = post
        split_post = post.split("-")[:3]
        new_post['date'] = "-".join(split_post)
        new_post['built_filename'] = post.replace("markdown", "html")
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
        try:
            tags = new_post['tags']
            tags = tags.strip().rstrip().split(",")
            tags_html = ""
            for tag in tags:
                single_tag_html = ""
                colors = ["#f79533", "#f37055", "#ef4e7b", "#a166ab", "#5073b8", "#1098ad", "#07b39b", "#6dba82"]
                hsh = int(hashlib.sha1(tag.encode()).hexdigest(), 16)
                hsh2 = int(hashlib.sha1(tag[::-1].encode()).hexdigest(), 16)
                bg_color = 'background: linear-gradient(90deg, {} 0%, {} 100%);'.format(
                        colors[hsh % len(colors)],
                        colors[hsh2 % len(colors)])
                single_tag_html += '<span style="{}" class="tag">{}</span>'.format(
                        bg_color, tag.strip().rstrip()
                )
                tags_html += single_tag_html
                new_post['tags'] = tags_html

                new_tag = Tag(**{"name": tag, "color": bg_color, "html": single_tag_html})
                default_context[tag_str].append(new_tag)
        except Exception as e:
            pass
        default_context[var_name].append(new_post)
        muh_file.close()
    default_context[var_name] = sorted(default_context[var_name], key=lambda x: x["date"], reverse=True)
    limited_name = '{}_LIMITED'.format(var_name)
    default_context[limited_name] = default_context[var_name][:5]
    default_context[tag_str] = sorted([x._asdict() for x in set(default_context[tag_str])], key=lambda x: x["name"])
    return default_context
