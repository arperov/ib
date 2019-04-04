#!/usr/bin/env python3

import cgi
import cgitb
#cgitb.enable(display=0, logdir='/var/log/httpd/cgi_err/')
cgitb.enable()
import datetime
import os
import re

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
        common.write_error(f'Thread ({thread_id}) does not exist')

    # Handle link quotes
    # TODO: handle cross thread links
    # TODO: filter out broken links
    text = form['text'].value
    quotes = re.findall(r'>>(\d+)', text, flags=re.MULTILINE)
    if quotes:
        text = re.sub(
            r'(>>(\d+))',
            r'<a href="#p\2">\1</a>',
            text,
            flags=re.MULTILINE
        )

    # Handle greentext
    text = re.sub(
        r'(^[^>]*)(>[^>]*$)',
        r'\1<span class="greentext">\2</span>',
        text,
        flags=re.MULTILINE
    )
    text = text.replace('\n', '<br />')

    p_fields = 'TIME, TEXT, THREAD_ID, IP'
    p_phldrs = '%s, %s, %s, %s'
    p_values = (
        datetime.datetime.now(),
        text,
        thread_id,
        cgi.escape(os.environ['REMOTE_ADDR'])
    )

    if 'file' in form and form['file'].value:
        # Save image and store it in the file table
        file_id = common.store_file(form['file'], cursor)
        p_fields += ', FILE_ID'
        p_phldrs += ', %s'
        p_values += (file_id, )
    if 'name' in form and form['name'].value:
        p_fields += ', USERNAME'
        p_phldrs += ', %s'
        p_values += (form['name'].value, )

    # Insert the post into 'posts' table
    cursor.execute(
        'INSERT INTO posts (%s) VALUES (%s)' % (p_fields, p_phldrs),
        p_values
    )

    # Update posts that have been referenced 
    post_id = ' ' + str(cursor.lastrowid)
    for quote in quotes:
        cursor.execute(
            'UPDATE posts SET REFS = CONCAT(REFS, %s) WHERE ID = %s',
            (post_id, quote)
        )

    # Update the time of last post for the thread unless we reached the bump
    # limit
    bumps = cursor.execute(f'SELECT ID FROM posts WHERE THREAD_ID={thread_id}')
    if bumps <= common.MAX_REPLIES:
        cursor.execute(
            'UPDATE threads SET LAST_POST = %s WHERE ID = %s',
            (p_values[0], thread_id)
        )

    cursor.close()
    conn.commit()
    conn.close()

    return thread_id


print(
    'Status: 303 See other\n'
    'Location: thread.py?thread_id=%s\n'
    % reply()
)

