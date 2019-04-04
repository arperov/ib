#!/usr/bin/env python3

import MySQLdb
import cgi
import cgitb
cgitb.enable(display=0, logdir='/var/log/httpd/cgi_err/')
import common
import config as conf
#print('Content-Type: text/html\n\n');

def write_post_form():
    print(
        '<div class="container">'
            '<center><h2 class="title">Start a New Thread</h2></center>'
            '<form action="/cgi-bin/post.py" method="post" id="post_form" enctype="multipart/form-data">'
                '<div id="name"> <span>Name</span>'
                    '<input type="text" name="name">'
                '</div>'
                '<div id="subject"> <span>Subject</span>'
                    '<input type="text" name="subject">'
                '</div>'
                    '<label for="file_btn" class="cstm_btn">'
                    '<span>Select File</span>'
                    '</label>'
                    '<input type="file" name="file" id="file_btn" accept="image/*">'
                '<div id="comment"> <span>Comment</span>'
                    '<textarea name="text" form="post_form"></textarea>'
                '</div>'
                '<input type="submit" id="submit_btn" value="post">'
            '</form>'
        '</div>'
        '<hr>'
    )

def write_board():
    print(
        'Content-Type: text/html\n\n'
        '<html>'
        '<link rel="stylesheet" type="text/css" href="/cgi-bin/style.css">'
    );
    common.write_banner()
    write_post_form()


    conn = MySQLdb.connect(
        host    = conf.SQL_HOST,
        user    = conf.SQL_USER,
        passwd  = conf.SQL_PASS,
        db      = conf.SQL_DB
    )
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('SELECT ID, SUBJECT FROM threads ORDER BY LAST_POST DESC')
    for thread in cursor.fetchall():
        common.write_thread(thread, cursor)

    print('</html>')

    cursor.close()
    conn.commit()
    conn.close()


write_board()
