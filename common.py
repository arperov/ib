import sys

# The value to which THREAD_ID is set when the post is the OP
SQL_CONST_OP = 0

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
