---
layout: post
title: "Kindle Clippings"
date: 2016-12-23
tags: [r]
---

I highlight a lot of shit on my Kindle. Well, it's not all shit! 💩 There's usually some good stuff buried in the `clippings.txt` file. But it's hard to manually parse through the file (and the shit).

In the past I've relied on online tools to organize my clippings. But this year, I thought I'd try and build my script to manage and clean it all.

Here's what I ended up with:

``` r
library(tidyverse)
library(stringr)
txt <- read_lines("clippings_archive_2016.txt")

parse_clippings <- function(txt) {
    
    h1_tibble <- txt %>% as_tibble()
    
    h2_prepend <- bind_rows(tibble(value = "=========="), h1_tibble) 
    
    h3_index <- h2_prepend %>% 
        mutate(index = ifelse(
            str_detect(pattern = "==========", value), 0, NA)) %>% 
        mutate(row = row_number()) %>% 
        mutate(row = ifelse(index == 0, row, NA)) %>% 
        fill(row, .direction = "down") %>% 
        mutate(entry = row %/% 5 + 1) %>% 
        group_by(entry) %>% 
        mutate(meta = row_number())
    
    meta <- tribble(
        ~meta, ~type,
            1, "start",
            2, "book",
            3, "location",
            4, "blank", 
            5, "highlight"
    )
    
    h4_meta <- h3_index %>% 
        left_join(meta, "meta") %>% 
        select(entry, value, type) %>% 
        spread(type, value) %>% 
        ungroup()
    
    h5_separate <- h4_meta %>% 
        select(book, location, highlight) %>% 
        separate(location, 
            into = c("page", "location", "date"), 
            sep = "\\s\\|\\s", fill = "right") %>% 
        separate(book, 
            into = c("book", "author"), 
            sep = "\\s\\(", extra = "merge", fill = "right")
    
    h6_replace <- h5_separate %>% 
        mutate(author = str_replace_all(
            author, pattern = "\\)", "")) %>% 
        mutate(page = str_replace_all(
            page, "\\-\\sYour\\sHighlight\\son\\spage\\s", "")) %>% 
        mutate(location = str_replace_all(
            location, "Location\\s", "")) %>% 
        mutate(date = str_replace_all(
            date, "Added\\son\\s", ""))
    
    h7_format <- h6_replace %>% 
        drop_na() %>% 
        mutate(date = as.Date(date, 
            format = "%A, %B %d, %Y %I:%M:%S %p")) %>% 
        mutate(page = as.integer(page))
    
    return(h7_format)
}

clippings <- parse_clippings(txt)
```

<br />

I've just pumped my clippings from 2016 through the script and everything seems to be working! I'm sifting through each highlight right now, trying to curate them down my to annual "Favourite Quotes of YYYY" post. Should have it up tomorrow!
