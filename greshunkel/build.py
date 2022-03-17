#!/usr/bin/env python3
from greshunkel.utils import parse_variable, interpolate
from os import listdir, makedirs, path
import hashlib, re

POSTS_DIR = "posts/"
WIKI_DIR = "wiki/"
TEMPLATE_DIR = "templates/"
BLOGPOST_FILE = "blog_post.html"
BLOGPOST_TEMPLATE = TEMPLATE_DIR + BLOGPOST_FILE
TAGGED_POSTS_FILE = "tagged_posts.html"
TAGGED_POSTS_TEMPLATE = TEMPLATE_DIR + TAGGED_POSTS_FILE
BUILD_DIR = "built/"

DOCUMENTATION_FILE = "documentation.html"
DOCUMENTATION_TEMPLATE = TEMPLATE_DIR + DOCUMENTATION_FILE

RSS_FILE = "rss.xml"

def _render_file(file_yo, context, output_filename=None):
    if file_yo.get("children"):
        # We DoNt ReNdEr FiLeS wItH cHiLdReN
        for base_file in file_yo["children"]:
            _render_file(base_file, context)
    else:
        desired_fname = file_yo['filename'] if output_filename is None else output_filename
        output = open(BUILD_DIR + desired_fname, "w+")
        parent_file = None

        if file_yo['vars'].get("PARENT"):
            parent_file = open(file_yo['vars']['PARENT'], "r")

        in_file = open(file_yo['file'], "r")

        if parent_file:
            for line in parent_file:
                to_write = line
                if 'xXx' in line:
                    if '@' in line:
                        to_write = interpolate(line.replace("@", ""), {}, context)
                    elif '=' in line:
                        to_write = interpolate(line, file_yo, context)
                    else:
                        # ChIlD BloCk oR SoMeThIng, Yo
                        beginning = line.split("xXx")[0]
                        end = line.split("xXx")[2]
                        block_name = line.split("xXx")[1].strip()
                        block_data = file_yo['blocks'].get(block_name, "")
                        to_write = beginning + block_data + end

                output.write(to_write if "core" not in to_write else to_write)
        else:
            for line in in_file:
                to_write = line
                if 'xXx' in line:
                    to_write = interpolate(line, file_yo, context)

                output.write(to_write)

        if parent_file:
            parent_file.close()
        in_file.close()
        output.close()

def _loop_context_interpolate(variable, loop_variable, current_item, i, context):
    if variable[1] == 'i':
        # i is special, it is an itervar
        muh_list =  context.get(variable[0], None)
        return muh_list[i] if muh_list else ""
    elif variable[1].isdigit():
        # They are trying to index a list
        return context.get(variable[0], None)[int(variable[1])]
    elif variable[0] == loop_variable:
        try:
            return current_item[variable[1]]
        except TypeError:
            import ipdb; ipdb.set_trace()
        except KeyError as e:
            try:
                hsh = str(int(hashlib.sha1(current_item['title'].encode()).hexdigest(), 16))
                hsh2 = str(int(hashlib.sha1(current_item['filename'].encode()).hexdigest(), 16))
                rgba1 = [0, 1, 2]
                rgba1[0] = (int(hsh) & 0xFF0000) >> 16
                rgba1[1] = (int(hsh) & 0x00FF00) >> 8
                rgba1[2] = (int(hsh) & 0x0000FF)
                rgba2 = [0, 0, 0]
                rgba2[0] = (int(hsh2) & 0xFF0000) >> 16
                rgba2[1] = (int(hsh2) & 0x00FF00) >> 8
                rgba2[2] = (int(hsh2) & 0x0000FF)
            except KeyError as e:
                rgba1 = (243, 68, 17)
                rgba2 = (51, 37, 255)
            extra_variables_map = {
                'bg-image': "/static/img/bg.jpg",
                'bg-img-src': "http://www.flickr.com/photos/104820964@N07/11595685883/",
                'title': 'NO TITLE',
                'author': 'NO AUTHOR',
                'tags': '',
                'css-rgb-colors': 'rgba({}, {}, {})'.format(rgba1[0], rgba1[1], rgba1[2]),
                'css-rgba-colors1': 'rgba({}, {}, {}, 1)'.format(rgba1[0], rgba1[1], rgba1[2]),
                'css-rgba-colors2': 'rgba({}, {}, {}, 2)'.format(rgba2[0], rgba2[1], rgba2[2]),
            }
            var = extra_variables_map.get(variable[1], None)
            if var == None:
                import ipdb; ipdb.set_trace()
                raise e
            return var
    # All else fails try to use the dict variable
    return current_item[variable[1]]

def _render_loop(loop_obj, context):
    loop_list = loop_obj["loop_list"]
    loop_str = loop_obj["loop_str"]
    loop_variable = loop_obj["loop_variable"]
    #outer_loop_variable = loop_obj["outer_loop_variable"]

    temp_loop_str = ""
    regex = re.compile("xXx (?P<variable>[a-zA-Z_0-9\-\$]+) xXx")
    wombat = re.compile("xXx LOOP (?P<variable>[a-zA-S_\-]+) (?P<fancy_list>[a-zA-S_\-\$]+) xXx(?P<subloop>.*)xXx BBL xXx")
    shattered_loops = wombat.split(loop_str)
    if len(shattered_loops) != 1:
        print("BEEP BEEP BEEP SUBLOOP DETECTED")

    i = 0
    for thing in context[loop_list]:
        # Lookit these higher order functions, godDAMN
        def loop_func(x):
            if x == 'i':
                return str(i)
            elif x == "BBL":
                return ""
            elif x == loop_variable:
                return str(thing)
            elif "$" in x and x in regex.findall(loop_str):
                #fUcK
                y = x.split("$")
                if y[0] == loop_variable and y[1].isdigit():
                    return thing[int(y[1])]
                return _loop_context_interpolate(y, loop_variable, thing, i, context)
            return x
        broken_man = regex.split(shattered_loops[0])
        for chunk in broken_man:
            bro = loop_func(chunk)
            temp_loop_str = temp_loop_str + "".join(bro)
        if len(shattered_loops) != 1:
            # HACKIEST SHIT THAT EVER HACKED
            # TODO: If it ain't broke, don't fix it
            context[shattered_loops[2]] = thing["params"]
            temp_loop_str = temp_loop_str + _render_loop(loop_obj["loop_subloop"], context)
            if shattered_loops[4] != "":
                broken_man = regex.split(shattered_loops[4])
                for chunk in broken_man:
                    bro = loop_func(chunk)
                    temp_loop_str = temp_loop_str + "".join(bro)
        i = i + 1

    return temp_loop_str

def parse_file(context, radical_file):
    tfile = open(TEMPLATE_DIR + radical_file, "r")
    file_meta = {}
    file_meta['file'] = TEMPLATE_DIR + radical_file
    file_meta['filename'] = radical_file
    file_meta['vars'] = {}
    file_meta['blocks'] = {}
    file_meta['loops'] = []

    reading_block = False
    block_str = ""
    end_str = ""
    block_name = ""

    loop_stack = None
    active_loops = 0
    for line in tfile:
        stripped = line.strip()
        if "xXx" in stripped and "=" in stripped.split("xXx")[1]:
            var = parse_variable(line)
            file_meta['vars'][var[0]] = var[1]
        elif "xXx TTYL xXx" == stripped:
            file_meta['blocks'][block_name] = block_str + end_str
            reading_block = False
            block_str = ""
            block_name = ""
            end_str = ""
        # We LoOpIn BaBy
        elif "xXx LOOP " in stripped:
            variables = stripped.split("xXx")[1].strip().replace("LOOP ", "").split(" ")
            active_loops = active_loops + 1
            print("We've entered timeskip {}!".format(variables[1]))
            if loop_stack is None:
                loop_stack = {
                    "loop_depth": active_loops,
                    "loop_variable": variables[0],
                    "loop_str": "",
                    "loop_list": variables[1],
                    "loop_subloop": None
                }
            else:
                #ThIs WoRkS FoR MoRe ThAn TwO LoOpS
                def recurse_bro(item):
                    if item is None:
                        loop_stack["loop_subloop"] = {
                            "loop_depth": active_loops,
                            "loop_variable": variables[0],
                            "loop_str": "",
                            "loop_list": variables[1],
                            "loop_subloop": None
                        }
                    else:
                        recurse_bro(item["loop_subloop"])
                recurse_bro(loop_stack)

        elif "xXx BBL xXx" == stripped:
            active_loops = active_loops - 1
            if active_loops == 0:
                temp_loop_str = _render_loop(loop_stack, context)
                # AsSuMe WeRe In A bLoCk
                block_str = block_str + temp_loop_str
                # wE DoNe LoOpIn NoW
                loop_stack = None
        elif "xXx" in stripped and reading_block is True:
            if '@' in stripped:
                line = stripped = interpolate(stripped.replace("@", ""), {}, context)
        elif "xXx" in stripped and reading_block is False:
            reading_block = True
            lstripped = line.split("xXx")
            block_name = lstripped[1].strip()
            block_str = lstripped[0]
            end_str = lstripped[2]
        if active_loops == 0 and reading_block is True and "xXx" not in stripped:
            block_str = block_str + line
        if active_loops > 0:
            def recurse_bro(item):
                if item is not None:
                    if item["loop_depth"] <= active_loops:
                        if "xXx LOOP" in stripped and item["loop_depth"] != active_loops:
                            item["loop_str"] = item["loop_str"] + stripped
                        elif "xXx LOOP" not in stripped:
                            item["loop_str"] = item["loop_str"] + stripped
                        recurse_bro(item["loop_subloop"])
            recurse_bro(loop_stack)

    return file_meta

def main(context):
    all_templates = []
    required_dirs = ['./built', './built/posts', './built/wiki', './built/tags']

    for dirn in required_dirs:
        if not path.exists(dirn):
            makedirs(dirn)

    for radical_file in listdir(TEMPLATE_DIR):
        # We don't want to render the blog_post template by itself, or the documentation.
        if TEMPLATE_DIR + radical_file in [BLOGPOST_TEMPLATE, DOCUMENTATION_TEMPLATE, TAGGED_POSTS_TEMPLATE]:
            continue
        if not radical_file.endswith(".html"):
            continue
        file_meta = parse_file(context, radical_file)
        all_templates.append(file_meta)

    # BuIlD a SiCk TrEe oF TeMpLaTeS yO
    tree = {}
    for tfile in all_templates:
        if tfile['vars'].get('PARENT'):
            parent = tfile['vars']['PARENT']
            if tree.get(parent):
                tree[parent]['children'].append(tfile)
            else:
                tree[parent] = {
                        'children': [tfile]
                    }

    for base_file in tree:
        _render_file(tree[base_file], context)

    for post in context['POSTS']:
        context['dumb_meta'] = [post]
        post_meta = parse_file(context, BLOGPOST_FILE)
        _render_file(post_meta, context, output_filename="posts/" + post['built_filename'])

    for tag in context['POSTS_TAGS']:
        context['tag'] = [tag]
        context['POSTS_WITH_TAG'] = [x for x in context['POSTS'] if tag['name'] in x.get('tag_names', [])]
        post_meta = parse_file(context, TAGGED_POSTS_FILE)
        _render_file(post_meta, context, output_filename=f'tags/{tag["name"]}.html')

    for post in context['WIKI_POSTS']:
        context['dumb_meta'] = [post]
        post_meta = parse_file(context, BLOGPOST_FILE)
        _render_file(post_meta, context, output_filename="wiki/" + post['built_filename'])

    post_meta = parse_file(context, RSS_FILE)
    _render_file(post_meta, context, output_filename="feed.xml")

    # BeCaUsE WhY NoT
    return 0

