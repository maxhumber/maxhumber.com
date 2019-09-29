import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter

with open('blog/2019-09-23_mummify.md', 'r') as f:
    md = f.read()

##### meta metadata

def extract_metadata(md):
    dash_splits = md.split('---', maxsplit=2)
    meta = dash_splits[1]
    meta = meta.split('\n')[1:-1]
    meta = [m.split(': ', 1) for m in meta]
    meta = {k.strip(): v.strip() for k, v in meta}
    body = fence_splits[2]
    return meta, body

extract_metadata(md)



####


class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return f'\n<pre><code>{mistune.escape(code)}</code></pre>\n'
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(code, lexer, formatter)

renderer = HighlightRenderer()
markdown = mistune.Markdown(renderer=renderer)
html = markdown(md)

with open('output/test.html', 'w') as f:
    f.write(html)




table(header, body)

    Rendering table element. Wrap header and body in it.
    Parameters:

        header – header part of the table.
        body – body part of the table.

table_cell(content, **flags)

    Rendering a table cell. Like <th> <td>.
    Parameters:

        content – content of current table cell.
        header – whether this is header or not.
        align – align of current table cell.

table_row(content)

    Rendering a table row. Like <tr>.
    Parameters:	content – content of current table row.


##
