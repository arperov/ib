#!/usr/bin/env python3

import cgi
import cgitb
#cgitb.enable(display=0, logdir='/var/log/httpd/cgi_err/')
#cgitb.enable()

import MySQLdb
import datetime

import common
import config as conf

import io
import os

#print('Content-Type: text/html\n\n')

def purge_thread(thread, cursor):
    # Fetch info on files to be deleted
    cursor.execute(
        'SELECT posts.FILE_ID, files.EXT FROM posts '
        'INNER JOIN files ON posts.FILE_ID=files.ID '
        'WHERE posts.THREAD_ID = %s OR posts.ID = %s',
        (thread, thread)
    )

    # Delete the files
    for f in cursor.fetchall():
        os.remove(f'files/{f[0]}.{f[1]}')
        os.remove(f'files/{f[0]}s.{f[1]}')

    # Purge files from the table
    cursor.execute(f'DELETE FROM files WHERE ID={f[0]}')

    # Delete all posts in the thread
    cursor.execute(
        'DELETE FROM posts WHERE THREAD_ID = %s OR ID = %s',
        (thread, thread)
    )

    # Delete the thread
    cursor.execute(f'DELETE FROM threads WHERE ID = {thread}')



def create_thread():
    """Create a thread from the form recieved. A file and comment are required,
    the rest of the fields are optional. Updates 'posts', 'threads' and 'files'
    (by calling store_file) tables.
    """
    form = cgi.FieldStorage()

    # Make sure the mandatory file and text fields are not empty
    #TODO: cgi is not supposed to include fields with empty values, but it does.
    #Figure out how to fix it.
    if 'file' not in form or not form['file'].value:
        common.write_error('No file selected.')
    if 'text' not in form or not form['text'].value:
        common.write_error('Empty body.')

    conn = MySQLdb.connect(
        host    = conf.SQL_HOST,
        user    = conf.SQL_USER,
        passwd  = conf.SQL_PASS,
        db      = conf.SQL_DB
    )

    cursor = conn.cursor()

    # Purge the thread with the oldest last reply if already at MAX_THREADS
    active_threads = cursor.execute('SELECT ID FROM threads')
    if active_threads >= common.MAX_THREADS:
        cursor.execute('SELECT ID FROM threads ORDER BY LAST_POST ASC LIMIT 1')
        least_active = cursor.fetchone()
        purge_thread(least_active[0], cursor)


    # Save image and store it in the file table
    file_id = common.store_file(form['file'], cursor, OP=True)

    # Set mandatory fields
    p_fields = 'TIME, TEXT, THREAD_ID, FILE_ID, IP'
    p_phldrs = '%s, %s, %s, %s, %s'
    p_values = (
        datetime.datetime.now(),
        form['text'].value.replace('\n', '<br />'),
        common.SQL_CONST_OP,
        file_id,
        cgi.escape(os.environ['REMOTE_ADDR'])
    )

    # Set optional fields
    if 'name' in form and form['name'].value:
        p_fields += ', USERNAME'
        p_phldrs += ', %s'
        p_values += (form['name'].value, )

    # Store the post in the post table
    cursor.execute(
        'INSERT INTO posts (%s) VALUES (%s)' % (p_fields, p_phldrs),
        p_values
    )

    OP = cursor.lastrowid

    if 'subject' in form and form['subject'].value:
        cursor.execute(
            'INSERT INTO threads (ID, SUBJECT, LAST_POST) VALUES (%s, %s, %s)',
            (OP, form['subject'].value, p_values[0])
        )
    else:
        cursor.execute(
            'INSERT INTO threads (ID, LAST_POST) VALUES (%s, %s)',
            (OP, p_values[0])
        )

    cursor.close()
    conn.commit()
    conn.close()

    return OP


print(
    'Status: 303 See other\n'
    'Location: thread.py?thread_id=%s\n' 
    % create_thread()
)

