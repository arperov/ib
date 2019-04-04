#!/usr/bin/env python3

import MySQLdb
import cgi
import cgitb
import common
import config as conf
#cgitb.enable(display=0, logdir='/var/log/httpd/cgi_err/')
cgitb.enable()

#print('Content-Type: text/html\n\n');

def write_reply_form(thread_id, prefill_text=''):
    print(
        '<link rel="stylesheet" type="text/css" href="style.css">'
        '<div class="container">'
            '<center><h2 class="title">Reply</h2></center>'
            '<form action="reply.py" method="post" id="reply_form" enctype="multipart/form-data">'
                f'<input type="hidden" name="thread_id" value="{thread_id}">'
                '<div id="reply_name"> <span>Name</span>'
                    '<input type="text">'
                '</div>'
                    '<label for="file_btn" class="cstm_btn">'
                    '<span>Select File</span>'
                    '</label>'
                    '<input type="file" name="file" id="file_btn" accept="image/*">'
                '<div id="comment"> <span>Comment</span>'
                    '<textarea name="text" form="reply_form">'
                        f'{prefill_text}'
                    '</textarea>'
                '</div>'
                '<input type="submit" id="submit_btn" value="post">'
            '</form>'
        '</div>'
        '<hr>'
    )

def write_thread():
    form = cgi.FieldStorage()
    # Make sure a thread ID is specified
    if 'thread_id' not in form or not form['thread_id'].value:
        common.write_error('No thread specified.')

    print('Content-Type: text/html\n\n');
    print('<html>')
    write_reply_form(
        form['thread_id'].value,
        form['prefill_text'].value if 'prefill_text' in form and form['prefill_text'].value is not None else ''
    )

    conn = MySQLdb.connect(
        host    = conf.SQL_HOST,
        user    = conf.SQL_USER,
        passwd  = conf.SQL_PASS,
        db      = conf.SQL_DB
    )
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)


    cursor.execute(
        'SELECT ID, SUBJECT FROM threads WHERE ID=%s',
        (form['thread_id'].value, )
    )

    thread = cursor.fetchone()

    common.write_thread(thread, cursor, in_thread=True)


    cursor.close()
    conn.commit()
    conn.close()

    print('</html>')

write_thread()
