#!/usr/bin/env python3

import cgi
import cgitb
#cgitb.enable(display=0, logdir='/var/log/httpd/cgi_err/')
import datetime

import MySQLdb

import common
import config as conf

#print('Content-Type: text/html\n\n');

def reply():
    """Create a reply to the thread from the form recieved. A comment is
    required, as well as the thread ID. Updates 'posts', 'threads' and 'files'
    (when supplied a file) tables.
    """
    form = cgi.FieldStorage()

    # Make sure a thread ID and comment are supplied
    if 'thread_id' not in form or not form['thread_id'].value:
        common.write_error('No thread specified.')
    if 'text' not in form or not form['text'].value:
        common.write_error('Empty body.')

    thread_id = form['thread_id'].value

    conn = MySQLdb.connect(
        host    = conf.SQL_HOST,
        user    = conf.SQL_USER,
        passwd  = conf.SQL_PASS,
        db      = conf.SQL_DB
    )

    cursor = conn.cursor()

    # Make sure thread exists
    cursor.execute('SELECT ID FROM threads WHERE ID=%s', (thread_id,))
    if cursor.rowcount == 0:
        common.write_error('Thread does not exist')

    p_fields = 'TIME, TEXT, THREAD_ID'
    p_phldrs = '%s, %s, %s'
    p_values = (
        datetime.datetime.now(),
        form['text'].value,
        thread_id
    )

    if 'file' in form and form['file'].value:
        # Save image and store it in the file table
        file_id = common.store_file(form['file'], cursor)
        p_fields += ', FILE_ID'
        p_phldrs += ', %s'
        p_values += (file_id, )

    # Insert the post into 'posts' table
    cursor.execute(
        'INSERT INTO posts (%s) VALUES (%s)' % (p_fields, p_phldrs),
        p_values
    )

    # Update the time of last post for the thread
    cursor.execute(
        'UPDATE threads SET LAST_POST = %s WHERE ID = %s',
        (p_values[0], thread_id)
    )

    cursor.close()
    conn.commit()
    conn.close()


reply()
print(
    'Status: 303 See other\n'
    # TODO: Change to the appropriate thread page
    'Location: board.py\n'
)

