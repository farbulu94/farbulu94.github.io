#!/usr/bin/env python
# -*- coding: utf8 -*-

#*****************************************************************************
#       Copyright (C) 2015 Vincent Delecroix <vincent.delecroix@labri.fr>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

import codecs
import datetime
import markdown
import json
import os
import shutil
import re

from webpage.process_article import process_article
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('webpage', 'templates'))

DATA_DIR = 'webpage/data/'
ARTICLES_DIR = 'webpage/articles/'
STATIC_DIR = 'webpage/static/'
OUTPUT_DIR = ''

#TODO: implement timestamps for everything using a dependency mechanism !!

re_sage_code = re.compile('    :::pycon')

# Update

date_today = datetime.datetime.now().strftime("%y/%m/%d")

# copy files from the static dir that are not already in the output one
for name in os.listdir(STATIC_DIR):
    static_filename = os.path.join(STATIC_DIR, name)

    output_filename = os.path.join(OUTPUT_DIR, name)
    static_mtime = os.path.getmtime(static_filename)
    try:
        output_mtime = os.path.getmtime(output_filename)
    except OSError:
        output_mtime = 0.0

    if static_mtime > output_mtime:
        print("Copy static file {}".format(name))
        shutil.copy(static_filename, output_filename)

mtime_data = 0.0
data = {}

for kind in ["journals",
             "publications",
             "prepublications",
             "conference_papers",
             "talks",
             "teaching_assistant"]:
    print("Loading json data: {}".format(kind))
    filename = os.path.join(DATA_DIR, kind + '.json')
    data[kind] = json.load(open(filename))
    mtime_data = min(mtime_data, os.path.getmtime(filename))

for content in ["general_presentation",
                "research_description"]:
    filename = os.path.join(DATA_DIR, content + '.md')
    print("Loading {}".format(filename))
    with codecs.open(filename, encoding='utf-8') as f:
        data[content] = markdown.markdown(f.read(),
                extensions=['markdown.extensions.tables'])
    mtime_data = max(mtime_data, os.path.getmtime(filename))

pages = [
   {'link': 'index.html', 'name': u'Presentation', 'template': 'index.html'},
   {'link': 'research.html', 'name': u'Research', 'template': 'research.html'},
   {'link': 'teaching.html', 'name': u'Teaching', 'template': 'teaching.html'},
   {'link': 'CV.html', 'name': u'CV', 'template': 'CV.html'},
   {'link': 'contact.html', 'name': u'Contact', 'template': 'contact.html'},
   ]

# add last update

for page in pages:
    page['last_update'] = date_today

# computing time stamps
# for page in pages:
#     page['status'] = 'unselected'
#     filename = os.path.join(OUTPUT_DIR, page['link'])
#     template = os.path.join('webpage', 'templates', page['link'])
#     page['mtime_template'] = os.path.getmtime(template)
#     try:
#         page['mtime_output'] = os.path.getmtime(filename)
#     except OSError:
#         page['mtime_output'] = 0.0

for page in pages:
    # if page['mtime_output'] < max(page['mtime_template'], mtime_data):
    #     print(u"Generate {}".format(page['name']))
    #     template = env.get_template(page['template'])
    #     filename = os.path.join('output', page['template'])
    #     page['status'] = 'selected'
    #     with codecs.open(filename, "w", encoding='utf-8') as output:
    #         output.write(template.render(pages=pages, **data))
    #     page['status'] = 'unselected'
    # else:
    #     print(u"Skip {} because already up to date".format(page['name']))
    print(u"Generate {}".format(page['name']))
    template = env.get_template(page['template'])
    filename = os.path.join('', page['template'])
    page['status'] = 'selected'
    with codecs.open(filename, "w", encoding='utf-8') as output:
        output.write(template.render(pages=pages, **data))
    page['status'] = 'unselected'

page['status'] = 'selected'  # reselect the blog !!
