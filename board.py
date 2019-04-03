#!/usr/bin/env python3

import cgi

import cgitb
cgitb.enable(display=0, logdir='/var/log/httpd/cgi_err/')

print('Content-Type: text/html\n\n');

print(
    '<html>'
    #'<link rel="stylesheet" type="text/css" href="style.css">'
    '<div class="container">'
        '<h2 class="title">Some Text</h2>'
        '<form action="post.py" method="post" id="post_form" enctype="multipart/form-data">'
            '<div id="name"> <span>Name</span>'
            '    <input type="text" name="name">'
            '</div>'
            '<div id="email"> <span>Email</span>'
            '    <input type="text" name="email">'
            '</div>'
            '<div id="subject"> <span>Subject</span>'
            '    <input type="text" name="subject">'
            '</div>'
            '<span>File</span><input type="file" name="file" accept="image/*">'
            '<div id="comment"> <span>Comment</span>'
            '    <textarea name="text" form="post_form"></textarea>'
            '</div>'
            '<input type="submit" id="submit_btn" value="post">'
        '</form>'
    '</div>'
    '<hr>'
    '</html>'
)


