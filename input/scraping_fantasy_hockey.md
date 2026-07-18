---
title: How to Win Fantasy Hockey
date: 2019-09-28
tags: code
slug: scraping_fantasy_hockey
---

## How to Win Fantasy Hockey

*A recipe for using python to scrape player projection data and build a value over replacement ranking model*

Jupyter notebook for this blog post available [here](https://github.com/maxhumber/maxhumber.com/blob/master/blog/2019-09-28_scraping_fantasy_hockey.ipynb)

№1 Identify a data source ([CBS Sports](https://www.cbssports.com/fantasy/hockey/stats/F/2019/season/projections/) is a good option)

№2 `get` the html data with [gazpacho](https://maxhumber.github.io/gazpacho/)

```python
from gazpacho import get

position = 'F'

base = f'https://www.cbssports.com/fantasy/hockey/stats'
url = f'{base}/{position}/2019/restofseason/projections/'

html = get(url)
```

№3 Pass the captured html to a `Soup` parser

```python
from gazpacho import Soup

soup = Soup(html)
```

№4 `find` the html tags that contain player projection data

```python
# HTML: <tr class="TableBase-bodyTr ">
rows = soup.find('tr', {'class': 'TableBase-bodyTr '})
```

№5. Capture a single row (and inspect for good measure)

```python
row = rows[0]
```

№6 Use `find` to grab those tags that map to player name, position, and projected Fantasy Points

```python
# name
row.find('span', {'class': 'CellPlayerName--long'}).find('a').text

# position
(row.find('span', {'class': 'CellPlayerName--long'})
     .find('span', {'class': 'CellPlayerName-position'}).text
)

# points
float(row.find('td', {'class': 'TableBase-bodyTd'})[1].text)
```

```
361.1
```

№7 Wrap these `find` operations into a function

```python
row = rows[0]

def parse_row(row):
    meta = row.find('span', {'class': 'CellPlayerName--long'})
    try:
        name = meta.find('a').text
    except AttributeError:
        name = meta.text
    position = meta.find('span', {'class': 'CellPlayerName-position'}).text
    points = float(row.find('td', {'class': 'TableBase-bodyTd'})[1].text)
    return name, position, points

parse_row(row)
```

```
('Nikita Kucherov', 'RW', 361.1)
```

№8 Make sure that the function works for all the captured rows

```python
players = []
for row in rows:
    try: 
        players.append(parse_row(row))
    except AttributeError:
        pass

players[-2:]
```

```
[('Brandon Pirri', 'LW', 165.4), ('Pavel Buchnevich', 'RW', 164.9)]
```

№9 Bundle up the logic so that it can be applied to multiple pages

```python
def scrape_position(position):
    base = f'https://www.cbssports.com/fantasy/hockey/stats'
    url = f'{base}/{position}/2019/restofseason/projections/'
    html = get(url)
    soup = Soup(html)
    rows = soup.find('tr', {'class': 'TableBase-bodyTr '})
    data = []
    for row in rows:
        try: 
            data.append(parse_row(row))
        except AttributeError:
            pass
    return data
```

№10 Scrape each page that contains player projection data

```python
# F for Forwards
# D for Defence
# G for goalies

import time

data = []
for position in ['F', 'D', 'G']:
    d = scrape_position(position)
    data.extend(d)
    time.sleep(1)
```

№11 Stuff the captured data into a pandas `DataFrame`

```python
import pandas as pd

df = pd.DataFrame(data, columns=['name', 'position', 'points'])
df.sample(5)
```

```
name position  points
171     Mike Matheson        D    92.0
60       David Perron       RW   196.9
86        Tomas Tatar       LW   176.1
190  Dennis Cholowski        D    83.0
257    Thatcher Demko        G    89.0
```

№12 Calculate the <a href="https://en.wikipedia.org/wiki/Value_over_replacement_player">value over player replacement</a> score for each player

```python
pool_size = 8
starters = {'C': 1, 'LW': 1, 'RW': 1, 'D': 2, 'G': 1}

for position, slots in starters.items():
    replacement = (
        df[df['position'] == position]
        .sort_values('points', ascending=False)
        .head(slots * pool_size)
        ['points']
        .mean()
    )
    df.loc[df['position'] == position, 'vorp'] = df['points'] - replacement
```

№13 Re-rank and draft players according to their VORP rank

```python
df['rank'] = df['vorp'].rank(method='average', ascending=False)
df.sort_values('rank').set_index('rank').head(20)
```

```
name position  points      vorp
rank                                               
1.0      Nikita Kucherov       RW   361.1  75.38750
2.0       Leon Draisaitl       LW   333.1  58.51250
3.0       Connor McDavid        C   337.1  45.13750
4.0   Andrei Vasilevskiy        G   433.9  41.26250
5.0          Brent Burns        D   225.1  34.09375
6.0        Brad Marchand       LW   302.1  27.51250
7.0         Patrick Kane       RW   312.7  26.98750
8.0     Dustin Byfuglien        D   216.7  25.69375
9.0        Mark Giordano        D   210.2  19.19375
10.0       Morgan Rielly        D   208.0  16.99375
11.0        John Carlson        D   207.0  15.99375
12.0         Kris Letang        D   205.2  14.19375
13.0        Tyson Barrie        D   203.6  12.59375
14.0      Mikko Rantanen       RW   297.2  11.48750
15.0    Nathan MacKinnon        C   302.8  10.83750
16.0       Alex Ovechkin       LW   283.9   9.31250
17.0   Jordan Binnington        G   393.5   0.86250
18.0          Torey Krug        D   191.8   0.79375
19.0      Steven Stamkos        C   292.3   0.33750
20.0         Tuukka Rask        G   392.7   0.06250
```

№14 Profit
