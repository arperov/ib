#!/usr/bin/env python3

import cgi
import cgitb
#cgitb.enable(display=0, logdir='/var/log/httpd/cgi_err/')

import MySQLdb
import datetime
from wand.image import Image

import common
import config as conf

import io

MAX_FILE_SIZE = 1 << 24
MAX_IMG_WIDTH = 250

#print('Content-Type: text/html\n\n')

def store_file(f, cursor):
    """Store image located in MiniFieldStorage 'f', alongside its thumbnail of
    width 250, and add it to the files table accessed through 'cursor'. If the
    size of file exceedes MAX_FILE_SIZE an error is shown and the process is
    aborted.
    """
    # TODO: Make sure the height does not get out of hand

    f_size = f.file.seek(0,2)
    f.file.seek(0,0)

    # Make sure the file is not too large
    if f_size > MAX_FILE_SIZE:
        common.write_error(
            'Filesize exceeds maximum (%dMB).'
            %
            (MAX_FILE_SIZE // pow(1024, 2))
        )

    img = Image(blob=f.file.read())

    # Add the image to the file table
    fp = f.filename.find('.')
    name    = f.filename[0:fp]
    ext     = f.filename[fp + 1:len(f.filename)] 
    cursor.execute(
        'INSERT INTO files (NAME, EXT, SIZE, RES) VALUES (%s, %s, %s, %s)',
        (name, ext, f_size, '%dx%d' % (img.size[0], img.size[1]))
    )

    # Save image
    img.save(filename='files/%s.%s' % (cursor.lastrowid, ext))

    # Create a thmbnail
    img.transform(resize='250x')
    img.save(filename='files/%ss.%s' % (cursor.lastrowid, ext))

    ## Create thumbnail
    #img = Image(filename='files/1.png')
    #img.transform(resize='250x')
    #img.save(filename='asdf2.png')
    return cursor.lastrowid


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

    # Save image and store it in the file table
    file_id = store_file(form['file'], cursor)

    # Set mandatory fields
    p_fields = 'TIME, TEXT, THREAD_ID, FILE_ID'
    p_phldrs = '%s, %s, %s, %s'
    p_values = (
        datetime.datetime.now(),
        form['text'].value,
        common.SQL_CONST_OP,
        file_id
    )

    # Set optional fields
    if 'name' in form and form['name'].value:
        p_fields += ', USERNAME'
        p_phldrs += ', %s'
        p_values += (form['name'].value, )
    if 'email' in form and form['email'].value:
        p_fields += ', EMAIL'
        p_phldrs += ', %s'
        p_values += (form['email'].value, )

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



create_thread()
print(
    'Status: 303 See other\n'
    'Location: board.py\n'
)

