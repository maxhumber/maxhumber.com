import re

with open('output/yass.html', 'r') as f:
    html = f.read()

html = re.sub('\n</table>\n</div>', '\n</table>\n</div>\n<br/>\n', html)

def fix_notebook_html(html):
    # add break line after code
    html = re.sub('\n</pre></div>','\n</pre></div>\n<br/>\n', html)
    # fix code outputs
    html = re.sub('\n\n\n</code></pre>','</code></pre>\n<br/>', html)
    # remove table style
    html = re.sub(r'\n<style scoped>.*?</style>', '', html, 0, flags=re.DOTALL)
    # remove table border
    html = re.sub('<table border="1"', '<table', html)
    # add break line after table
    html = re.sub('\n</table>\n</div>', '\n</table>\n</div>\n<br/>\n', html)
    # make plots and graphs responsive
    html = re.sub('(?<=\")(.*)(?=alt)', ' class="img-fluid mx-auto d-block" ', html)
    return html


with open('output/test.html', 'w') as f:
    f.write(html)
