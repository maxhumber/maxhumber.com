---
title: 'The Tile Grid Map for Canada'
date: 2017-02-15
tags: [r]
---

I love the tile grid map:

![center]({{ site.url }}/assets/img/tile_america.png)

[Source](http://blog.apps.npr.org/2015/05/11/hex-tile-maps.html)

I think they're elegant, easy to read, and great for data that are population agnostic.

I live in Canada, though. And it sucks (well, no it doesn't!) because I've only ever seen tile grids for America.

I decided that Canada deserved one.

So, here is the tile grid map template for all you Canadian useRs:

![center]({{ site.url }}/assets/img/tile_canada.png)

``` r
library(tidyverse)
library(viridis)

# LOCATION DATAFRAME

canada <- tribble(
    ~province, ~code, ~x, ~y,
    "Yukon", "YK", 1, 3,
    "British Columbia", "BC", 1, 2, 
    "Northwest Territories", "NW", 2, 3, 
    "Alberta", "AB", 2, 2, 
    "Nunavut", "NU", 3, 3, 
    "Saskatchewan", "SK", 3, 2,
    "Manitoba", "MB", 4, 2, 
    "Ontario", "ON", 5, 1,
    "Quebec", "QC", 6, 2, 
    "Prince Edward Island", "PE", 7, 3, 
    "New Brunswick", "NB", 7, 2,
    "Newfoundland and Labrador", "NL", 8, 3, 
    "Nova Scotia", "NS", 8, 1
)

# YOUR DATA HERE
# just make sure province = province
 
df <- tibble(
    province = c("Ontario", "British Columbia", "Alberta", "Manitoba", "Nova Scotia"), 
    `Fake Data` = c(10, 4, 3, 6, 0)
)

# TILE GRID MAP

canada %>% 
    left_join(df, by = "province") %>% 
    ggplot(aes(x, y)) + 
    geom_tile(aes(fill = `Fake Data`)) + 
    geom_text(aes(label = code), color = "white") + 
    coord_fixed(ratio = 1) + 
    theme(
        panel.background = element_blank(),
        panel.grid = element_blank(), 
        axis.title = element_blank(), 
        axis.text = element_blank(), 
        axis.ticks = element_blank()) + 
    scale_fill_viridis(na.value = "#E1E1E1", option = "D", begin = 0.2, end = 0.8)
```

