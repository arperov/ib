import sys
import MySQLdb
from wand.image import Image
import cgitb
cgitb.enable(display=0, logdir='/var/log/httpd/cgi_err/')

# The value to which THREAD_ID is set when the post is the OP
SQL_CONST_OP = 0
MAX_FILE_SIZE = 1 << 24 # 16 MB
MAX_OP_IMG_WIDTH = 250
MAX_IMG_WIDTH = 150

MAX_THREADS = 2
MAX_REPLIES = 3


def write_OP(t_dic, p_dic, f_dic, r_count, i_count, p_count=0, in_thread=False):
    f_name = f'{f_dic["NAME"]}.{f_dic["EXT"]}'
    f_path = f'files/{f_dic["ID"]}.{f_dic["EXT"]}'
    t_path = f'files/{f_dic["ID"]}s.{f_dic["EXT"]}'
    name = 'Anonymous' if not p_dic['USERNAME'] else p_dic['USERNAME']
    subj = '' if not t_dic['SUBJECT'] else t_dic['SUBJECT']

    in_thread_summ = \
        '<span class="summary">'\
            f'{r_count} replies and {i_count} images by {p_count} '\
                'posters total. '\
            f'<a href="thread.py?thread_id={t_dic["ID"]}" '\
                'class=replylink"> Click here'\
            '</a> to view.'\
        '</span>'

    outside_summ = \
            '<div class="nav_bar">'\
                '[<a href="board.py">Return</a>]'\
                '<span class="t_stats">'\
                    f'<span class="t_replies" title="Replies">{r_count}</span>'\
                    ' / '\
                    f'<span class="t_images" title="Images">{i_count}</span>'\
                    ' / '\
                    f'<span class="t_posters" title="Posters">{p_count}</span>'\
            '</div>'\
            '<hr>'

    if in_thread:
        in_thread_summ = ''
    else:
        outside_summ = ''

    print(
        f'{outside_summ}'
        f'<div class="op_container" id="pc{t_dic["ID"]}">'
            f'<div class="op" id="p{t_dic["ID"]}">'
                f'<div class="file" id="f{t_dic["ID"]}">'
                    f'<div class="file_info" id="fi{t_dic["ID"]}">'
                        'File: '
                        f'<a href="{f_path}" target="_blank">{f_name}</a>'
                        f' ({f_dic["SIZE"] // 1024}KB, {f_dic["RES"]})'
                    '</div>'
                    f'<a class="file_thumb" href="{f_path}" target="_blank">'
                        #<!-- style height width-->
                        f'<img src="{t_path}" alt="what is this" >'
                    '</a>'
                '</div>'
                f'<div class="post_info" id="pi{t_dic["ID"]}">'
                    f'<span class="subject"> {subj} </span>'
                    f'<span class="name"> {name} </span>'
                    f'<span class="time"> {p_dic["TIME"]} </span>'
                    '<span class="post_num">'
                        'No.'
                        # TODO: enter the post ID into the textarea
                        f'<a href="thread.py?thread_id={t_dic["ID"]}" '
                            f'title="Reply to this post">{t_dic["ID"]}</a>'
                    '</span>'
                    '<span>'
                        f' [<a href="thread.py?thread_id={t_dic["ID"]}"'
                            'class="replylink">Reply</a>]'
                    '</span>'
                '</div>'
                f'<blockquote class="post_text" id="t{t_dic["ID"]}">'
                    f'{p_dic["TEXT"]}'
                '</blockquote>'
                f'{in_thread_summ}'
            '</div>'
        '</div>'
    )

def write_post(t_dic, p_dic, f_dic):
    file_str = ''
    if f_dic:
        f_name = f'{f_dic["NAME"]}.{f_dic["EXT"]}'
        f_path = f'files/{f_dic["ID"]}.{f_dic["EXT"]}'
        t_path = f'files/{f_dic["ID"]}s.{f_dic["EXT"]}'
        file_str = \
            f'<div class="file" id="f{p_dic["ID"]}">' \
                f'<div class="file_info" id="fi{p_dic["ID"]}">' \
                    'File: ' \
                    f'<a href="{f_path}" target="_blank">{f_name}</a>' \
                    f' ({f_dic["SIZE"] // 1024}KB, {f_dic["RES"]})' \
                '</div>' \
                f'<a class="file_thumb" href="{f_path}" target="_blank">' \
                    f'<img src="{t_path}" alt="what is this" >' \
                '</a>' \
            '</div>'

    name = 'Anonymous' if not p_dic['USERNAME'] else p_dic['USERNAME']
    print(
        f'<div class="reply_container" id="pc{p_dic["ID"]}">'
            f'<div class="side_arrows" id="sa{p_dic["ID"]}">>></div>'
            f'<div class="post" id="p{p_dic["ID"]}">'
                f'<div class="post_info" id="pi{p_dic["ID"]}">'
                    f'<span class="name"> {name} </span>'
                    f'<span class="time"> {p_dic["TIME"]} </span>'
                    '<span class="post_num">'
                        'No.'
                        # TODO: enter the post ID into the textarea
                        f'<a href="thread.py?thread_id={t_dic["ID"]}"'
                            f'title="Reply to this post">{p_dic["ID"]}</a>'
                    '</span>'
                    f'{file_str}'
                '</div>'
                f'<blockquote class="post_text" id="t{t_dic["ID"]}">'
                    f'{p_dic["TEXT"]}'
                '</blockquote>'
            '</div>'
        '</div>'
    )

def write_thread(thread, cursor, in_thread=False):
    if not thread:
        return
    print(f'<div class="thread" id="t{thread["ID"]}">')
    cursor.execute(
        'SELECT ID, TIME, USERNAME, TEXT, FILE_ID FROM posts WHERE ID = %s',
        (thread['ID'], )
    )
    p_dic = cursor.fetchone()
    
    cursor.execute('SELECT * FROM files WHERE ID = %s', (p_dic['FILE_ID'],))
    f_dic = cursor.fetchone()

    # TODO: Use COUNT
    img_cnt = cursor.execute(
        'SELECT ID FROM posts WHERE FILE_ID IS NOT NULL AND THREAD_ID = %s',
        (thread['ID'], )
    ) + 1
    reply_cnt = cursor.execute(
        'SELECT ID FROM posts WHERE THREAD_ID = %s',
        (thread['ID'], )
    )

    p_count = cursor.execute(
        'SELECT DISTINCT IP FROM posts WHERE THREAD_ID=%s',
        (thread['ID'], )
    )

    write_OP(thread, p_dic, f_dic, reply_cnt, img_cnt, p_count, in_thread)

    # Write replies
    if in_thread:
        cursor.execute(
            'SELECT ID, TIME, USERNAME, TEXT, FILE_ID '
            'FROM posts WHERE THREAD_ID = %s',
            (thread['ID'], )
        )
    else:
        cursor.execute(
            'SELECT * FROM ( '
                'SELECT ID, TIME, USERNAME, TEXT, FILE_ID '
                'FROM posts WHERE THREAD_ID = %s '
                'ORDER BY TIME DESC LIMIT 5 '
            ') x ORDER BY TIME ASC',
            (thread['ID'], )
        )
    for post in cursor.fetchall():
        cursor.execute('SELECT * FROM files WHERE ID = %s', (post['FILE_ID'],))
        write_post(thread, post, cursor.fetchone())
            
    print('</div>')
    print('<hr>')

def store_file(f, cursor, OP=False):
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
        write_error(
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
    img.transform(
        resize=str(MAX_IMG_WIDTH if not OP else MAX_OP_IMG_WIDTH) + 'x')
    img.save(filename='files/%ss.%s' % (cursor.lastrowid, ext))

    return cursor.lastrowid

def write_error(msg):
    print(
            'Content-Type: text/html\n\n'
            '<html>'
            '<center>'
            '<font color="red"><h2>ERROR: %s</h2></font>'
            '<h3>[<a href="board.py" title="return">return</a>]</h3>'
            '</center>'
            '</html>'
            %
            (msg)
    )
    sys.exit(0)
