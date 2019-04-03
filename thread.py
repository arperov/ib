#!/usr/bin/env python3

import MySQLdb
import cgi
import cgitb
cgitb.enable(display=0, logdir='/var/log/httpd/cgi_err/')


thread_id = 57

print('Content-Type: text/html\n\n');

print(
    '<html>'
    #'<link rel="stylesheet" type="text/css" href="style.css">'
    '<div class="container">'
        '<h2 class="title">Reply</h2>'
        '<form action="reply.py" method="post" id="reply_form" enctype="multipart/form-data">'
            '<input type="hidden" name="thread_id" value="%s">'
            '<div id="name"> <span>Name</span>'
            '    <input type="text" name="name">'
            '</div>'
            '<div id="email"> <span>Email</span>'
            '    <input type="text" name="email">'
            '</div>'
            '<span>File</span><input type="file" name="file" accept="image/*">'
            '<div id="comment"> <span>Comment</span>'
            '    <textarea name="text" form="reply_form"></textarea>'
            '</div>'
            '<input type="submit" id="submit_btn" value="post">'
        '</form>'
    '</div>'
    '<hr>'
    '</html>'
    % thread_id
)
