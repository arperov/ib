#!/usr/bin/env python3

import MySQLdb
import cgi
import cgitb
cgitb.enable(display=0, logdir='/var/log/httpd/cgi_err/')


form = cgi.FieldStorage()
# Make sure a thread ID is specified
if 'thread_id' not in form or not form['thread_id'].value:
    common.write_error('No thread specified.')

print('Content-Type: text/html\n\n');

print(
    '<html>'
    '<link rel="stylesheet" type="text/css" href="style.css">'
    '<div class="container">'
        '<h2 class="title">Reply</h2>'
        '<form action="reply.py" method="post" id="reply_form" enctype="multipart/form-data">'
            f'<input type="hidden" name="thread_id" value="{form["thread_id"].value}">'
            '<div id="name"> <span>Name</span>'
            '    <input type="text" name="name">'
            '</div>'
            '<span>File</span>'
                '<label for="file_btn" class="cstm_btn">'
                '<span>Select File</span>'
                '</label>'
                '<input type="file" name="file" id="file_btn" accept="image/*">'
            '<div id="comment"> <span>Comment</span>'
            '    <textarea name="text" form="reply_form"></textarea>'
            '</div>'
            '<input type="submit" id="submit_btn" value="post">'
        '</form>'
    '</div>'
    '<hr>'
    '</html>'
)
