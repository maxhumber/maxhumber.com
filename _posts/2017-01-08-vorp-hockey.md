---
title: "Fantasy Hockey with rvest and purrr"
date: 2017-01-08
tags: [r]
---

`rvest` and `purrr` are wonderful bedfellows. The packages share the underlying `tidyverse` API. And it feels simple and almost natural to combine them when scraping the web.

Here is a slimmed down and worked recipe of how to leverage `rvest` and `purrr` in Fantasy Hockey.

***

**Step 0. Load packages.**

``` r
library(tidyverse)
library(rvest)
library(purrr)
library(stringr)
```

**Step 1. Find a data source.**

I'm going to use [Fantasy Sports Portal](https://www.fantasysp.com/projections/hockey/weekly/) for this example.

**Step 2. Figure out the CSS selectors for the data.**

[SelectorGadget](http://selectorgadget.com/) makes this dead simple, like so:

![](/assets/img/vorp_hockey.png)

**Step 3. Fetch the data elements.**

I like to put everything in tibble as soon as possible and use `stringr` to adjust the url for the different position pages. You'll notice that I'm only grabbing name and goals. Feel free to grab whatever!

``` r
p_fetch <- function(position = "C") {
    
    url <- str_c(sep = "", 
        "https://www.fantasysp.com/projections/hockey/weekly/",
        position)
    
    page <- read_html(url)
    
    names <- page %>%
        html_nodes("td:nth-child(2)") %>% 
        html_text()
    
    goals <- page %>% 
        html_nodes("td:nth-child(4)") %>% 
        html_text()
    
    df <- tibble(name = names, goals)
    
    return(df)
}
```  

**Step 4. Iterate through each page.**

Instead of writing a for loop, I like to use `pmap` from `purrr` to iterate through the Centre, Left-Wing, Right-Wing and Defense position projection pages (I left out the Goalies for obvious reasons).

``` r
p_pull <- function() {
    
    params <- tibble(position = c("C", "LW", "RW", "D"))
    
    df <- params %>% 
        pmap(p_fetch) %>% 
        bind_rows()

    return(df)
}
```  

**Step 5. Clean and format projection data.**

This is a pretty janky use `separate` but it works to get everything into a format that I like.

``` r
p_clean <- function() {
    
    df <- p_pull() %>% 
        separate(name, 
            into = c("junk", "first", "last", "meta"), 
            sep = "(?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z])",
            fill = "right", 
            extra = "merge") %>% 
        separate(meta, into = c("team", "position"), sep = "\\s") %>% 
        mutate(name = str_c(first, last, sep = "")) %>% 
        mutate(goals = as.numeric(goals)) %>% 
        drop_na() %>% 
        mutate(length = str_length(team)) %>% 
        filter(length <= 3) %>% 
        select(name, team, position, goals)
    
    return(df)
}

df <- p_clean()
```  

At this point you should have a nice clean tibble/dataframe with every player, their position, team, and their projected goals for this week. I could stop here, but I wanted to go a little further with a *value over replacement player* (VORP) calculation.

**Step 6. Calculate replacement player for each scoring position.**

I'm using `pmap` again to pump through each position to get the mean value for the top X players. It's a little overkill, but really flexible.

``` r
p_replacement <- function(pos, slots) {
    
    rp <- df %>% 
        filter(position == pos) %>% 
        arrange(desc(goals)) %>% 
        filter(row_number() <= slots) %>% 
        group_by(position) %>% 
        summarise(goals = mean(goals))
    
    return(rp)
}

p_vorp <- function() {
    
    # slots depend on how many position players start for each team
    # if there are 10 teams and 2 LW per team then slots -> 10 * 2 = 20
    
    params <- tribble(
        ~pos, ~slots,
        "C", 20,
        "LW", 20, 
        "RW", 20, 
        "D", 20)
    
    rp <- params %>% 
        pmap(p_replacement) %>% 
        bind_rows()
    
    return(rp)
}
```  

**Step 7. Calculate the vorp for each player.**

Simple join at this point...

``` r
replacement <- p_vorp()

# calculate value over replacement player

vorp <- df %>% 
    left_join(replacement, by = "position") %>% 
    mutate(goals_vorp = goals.x - goals.y) %>% 
    rename(goals = goals.x, goals_rp = goals.y) %>% 
    select(-goals_rp) %>% 
    arrange(desc(goals_vorp))
```
