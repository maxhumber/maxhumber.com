---
layout: post
title: "Kindle clippings.txt with Python"
date: 2017-12-23
tags: python
---

Exactly a year ago I posted [Kindle clippings.txt with R](http://maxhumber.com/kindle-clippings-r). Since then things have changed... I'm a Pythonista now! Consequently, I thought it would be fun to update that post and parse highlights with *3.6+* and *pandas*. Janky, but it works:

``` python
import pandas as pd

txt = """Sourdough (Robin Sloan)
- Your Highlight on page 187 | Location 2853-2855 | Added on Tuesday, October 2, 2017 8:47:09 PM

The world is going to change, I think—slowly at first, then faster than anyone expects.
==========
Sapiens (Yuval Noah Harari)
- Your Highlight on page 196 | Location 2996-2997 | Added on Tuesday, October 3, 2017 8:51:09 PM

Evolution has made Homo sapiens, like other social mammals, a xenophobic creature.
==========
Life 3.0 (Max Tegmark)
- Your Highlight on page 75 | Location 1136-1137 | Added on Wednesday, October 11, 2017 6:00:15 PM

In short, computation is a pattern in the spacetime arrangement of particles
==========
"""

with open('clippings.txt', 'w', encoding='utf-8-sig') as f:
    f.write(txt)

with open('clippings.txt', 'r', encoding='utf-8-sig') as f:
    contents = f.read().replace(u'\ufeff', '')
    lines = contents.rsplit('==========')
    store = {'author': [], 'title': [], 'quote': []}
    for line in lines:
        try:
            meta, quote = line.split(')\n- ', 1)
            title, author = meta.split(' (', 1)
            _, quote = quote.split('\n\n')
            store['author'].append(author.strip())
            store['title'].append(title.strip())
            store['quote'].append(quote.strip())
        except ValueError:
            pass

df = pd.DataFrame(store)
print(df.to_csv(index=False, encoding='utf-8-sig'))
# author,quote,title
# Robin Sloan,"The world is going to change, I think—slowly at first, then faster than anyone expects.",Sourdough
# Yuval Noah Harari,"Evolution has made Homo sapiens, like other social mammals, a xenophobic creature.",Sapiens
# Max Tegmark,"In short, computation is a pattern in the spacetime arrangement of particles",Life 3.0
```

Right now I'm 49 books deep. It's crunch time, but I can see the end! Look for my annual *52 Quotes* post in a couple of days!
