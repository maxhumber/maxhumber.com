TL;DR: I wrote a webscraper to help me make fake money.

I've been playing around with an online marketplace called the ["Hollywood Stock Exchange"](http://www.hsx.com/) for a couple of months now. The website is basically "fantasy" for actors, directors and upcoming movies but it functions pretty much exactly like a stock market.

In simple terms here's how it works:

Rogue One [(SW16)](http://www.hsx.com/security/view/SW16) is currently trading at ~$440 on the HSX. This means that the market thinks that Rogue One will do $440 Million during the first four weeks at the Box Office. For context, the last Star Wars movie [(STAR7)](http://www.hsx.com/security/view/STAR7) did $936 Million in four weeks. If you think that Rogue One is going to do something in between $440 - $936 Million than you ought to buy the "security" because it will converge and delist on the actual Box Office total.

There's definitely money (well, fake money...) to be made on a Rogue One position right now. But, I think there's an arbitrage opportunity in buying the actors and actresses attached to Rogue One instead.

See, actors and actresses (StarBonds) are priced slightly differently on the HSX. StarBonds are calculated on the average total box-office performance over the last five credited films by release date. This means that each time a movie featuring a particular star cashes out and delists, the box-office gross is calculated into the star's Trailing Average Gross (TAG), and the bond price is adjusted to match.

Mads Mikkelsen [(MMIKK)](http://www.hsx.com/security/view/MMIKK) a Rogue One cast member, for instance, is currently priced at $47.10. His actual TAG value is only $43.54. This spread is because of Rogue One. In a couple weeks Rogue One will be added to Mads' TAG value while at the same time some random indie art film called "A Royal Affair" [(ROYAF)](http://www.hsx.com/security/view/ROYAF) will fall off and out of his TAG.

I mean, I could manually do the math for the Mads example and figure out what his TAG will be when Rogue One gets added. But there's no fun in that! And besides, Mads is already a big deal. The thing about the new Star Wars movies is that a bunch of nobodies get cast and turned it into Super Stars overnight. It means that a lot of random indie art films (think sub ~$5) are about to fall off to make room for Rogue One (~$440). Basically, Rogue One is going to make the TAGs for a lot of people pop.

The punch line:

I'm lazy. And, I didn't want to manually do the math! So, I built a webscraper to calculate the arbitrage opportunities for me. 

(If you don't care about the code just skip to the bottom of the page...)

Step 1: Setup
=============

``` r
# load packages
library(tidyverse)
library(rvest)
library(purrr)
library(stringr)
library(knitr)

# knitr options
opts_chunk$set(cache = TRUE, warning = FALSE, message = FALSE)

# set base URL for HSX.com
URL <- "http://www.hsx.com/security/view/"
```

Step 2A: Build a scraper to get the tickers for each cast member of Rogue One
=============================================================================

``` r
get_cast <- function(movie) {
    
    page <- read_html(str_c(URL, movie))
    
    name <- page %>% 
        html_nodes(".credit p") %>% 
        html_text()
    
    df <- tibble(name) %>% 
        separate(name, into = c("name", "symbol"), sep = "\\s\\(") %>%
        mutate(symbol = str_replace_all(symbol, "\\)", ""))
        
    return(df)
}

cast <- get_cast("SW16")
```

Step 2B: Save the tickers
=========================

``` r
kable(cast)
```

| name            | symbol |
|:----------------|:-------|
| Alan Tudyk      | ATUDY  |
| Ben Mendelsohn  | BMEND  |
| Diego Luna      | DLUNA  |
| Donnie Yen      | DYEN   |
| Felicity Jones  | FJONE  |
| Forest Whitaker | FWHIT  |
| Mads Mikkelsen  | MMIKK  |
| Riz Ahmed       | RAHME  |

Step 3A: Build a scraper to get the movie credits for each cast member
======================================================================

``` r
get_credits <- function(actor) {
    
    page <- read_html(str_c(URL, actor))
    
    movie <- page %>% 
        html_nodes(".credit span") %>% 
        html_text()
    
    date <- page %>% 
        html_nodes("strong") %>% 
        html_text()
    
    l <- length(movie)
    date <- date[1:l]
    
    df <- tibble(date, movie) %>% 
        mutate(symbol = actor)
    
    return(df)
}
```

Step 3B: Test the scraper on Mads
=================================

``` r
MMIKK <- get_credits("MMIKK")
MMIKK %>% head(5) %>% kable()
```

| date         | movie                        | symbol |
|:-------------|:-----------------------------|:-------|
| Dec 16, 2016 | Rogue One: A Star Wars Story | MMIKK  |
| Nov 4, 2016  | Doctor Strange               | MMIKK  |
| Apr 22, 2016 | Men & Chicken                | MMIKK  |
| Nov 15, 2013 | Charlie Countryman           | MMIKK  |
| Jul 12, 2013 | The Hunt                     | MMIKK  |

Step 3C: Get the credits for everyone
=====================================

``` r
credits <- map(cast$symbol, get_credits) %>% bind_rows() 
```

Step 4: Clean the credits and keep the last five movies for each cast member
============================================================================

``` r
clean_credits <- function(credits) {
    
    clean <- credits %>% 
        mutate(date = as.Date(date, format = "%b %d, %Y")) %>% 
        mutate(date = ifelse(!is.na(date), as.character(date), as.character("3000-01-01"))) %>% 
        mutate(date = as.Date(date)) %>% 
        group_by(movie, symbol) %>% 
        mutate(future = ifelse(date >= Sys.Date() | is.na(date), TRUE, FALSE))
    
    five <- clean %>% 
        filter(future != TRUE) %>% 
        arrange(symbol, desc(date)) %>% 
        group_by(symbol) %>% 
        mutate(movie_idx = row_number()) %>% 
        filter(movie_idx <= 5) %>% 
        select(-future) %>% 
        ungroup()
    
    return(five)
}

tag_credits <- clean_credits(credits)
glimpse(tag_credits)
```

    ## Observations: 40
    ## Variables: 4
    ## $ date      <date> 2016-11-23, 2016-03-04, 2015-12-04, 2015-05-01, 201...
    ## $ movie     <chr> "Moana", "Zootopia", "Trumbo", "Welcome to Me", "Big...
    ## $ symbol    <chr> "ATUDY", "ATUDY", "ATUDY", "ATUDY", "ATUDY", "BMEND"...
    ## $ movie_idx <int> 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3...

Poop. The movie ticker values are missing. I guess I'll have to brute force a search for them instead...

Step 5A: Generate terms for brute force search
==============================================

``` r
movies <- tag_credits %>% 
    distinct(movie, .keep_all = FALSE) %>% 
    mutate(search_term = str_replace_all(movie, "\\s", "\\+"))

movies %>% tail(5) %>% kable()
```

| movie                        | search\_term                 |
|:-----------------------------|:-----------------------------|
| Jason Bourne                 | Jason+Bourne                 |
| Nightcrawler                 | Nightcrawler                 |
| Closed Circuit               | Closed+Circuit               |
| The Reluctant Fundamentalist | The+Reluctant+Fundamentalist |
| Trishna                      | Trishna                      |

Step 5B: Brute force search for the missing movie tickers
=========================================================

``` r
get_meta_m <- function(movie) {

    page <- read_html(str_c(
        "http://www.hsx.com/search/?keyword=", 
        movie, 
        "&status=ALL&action=submit_advanced"))
    
    movie <- page %>% 
        html_nodes("td:nth-child(1)") %>% 
        html_text()
    
    symbol <- page %>% 
        html_nodes("td:nth-child(2)") %>% 
        html_text()
    
    price <- page %>% 
        html_nodes("td:nth-child(5)") %>% 
        html_text()
    
    l <- length(price)
    movie <- movie[1:l]
    symbol <- symbol[1:l]
    
    df <- tibble(movie, symbol, price)
    
    return(df)
}

meta_m <- map(movies$search_term, safely(get_meta_m))
```

Step 5C: Clean the results
==========================

``` r
clean_meta_m <- function(meta_m) {
    
    meta_t <- meta_m %>% transpose()
    is_ok <- meta_t$error %>% map_lgl(is_null)
    meta_k <- meta_t$result[is_ok]
    
    df <- meta_k %>% 
        bind_rows() %>% 
        distinct(.keep_all = TRUE) %>% 
        filter(!str_detect(movie, "H\\$")) %>% 
        filter(!str_detect(symbol,"\\."))
    
    return(df)
}

meta_m <- clean_meta_m(meta_m)
```

Step 6: Join the tickers and prices to the TAG eligible credits
===============================================================

``` r
tag_prices <- tag_credits %>% 
    left_join(meta_m, by = "movie") %>% 
    mutate(date = as.Date(date)) %>% 
    mutate(price = as.numeric(str_replace(price, "H\\$", ""))) %>% 
    group_by(movie, symbol.x) %>% 
    slice(which.max(price)) %>% 
    select(date, symbol = symbol.x, movie, price, movie_idx) %>% 
    # correct minor mistakes for DYEN
    bind_rows(tribble(
        ~date, ~symbol, ~movie, ~price, ~movie_idx, 
        NA, "DYEN", "Legend of the Fist", 0.05, 4,
        NA, "DYEN", "Ip Man 2", 0.20, 5))
```

Step 7: Build a scraper to get the meta data for each cast member
=================================================================

``` r
get_meta_a <- function(actor) {

    page <- read_html(str_c(URL, actor))
    
    meta <- page %>%
        html_nodes(".data_column td") %>%
        html_text()
    
    meta_split <- split(meta, ceiling(seq_along(meta)/2))
    
    meta_df <- tibble(meta = meta_split) %>% 
        mutate(meta = as.character(meta)) %>% 
        mutate(meta = str_replace_all(meta, '\\"|\\,|c\\(|\\)', "")) %>% 
        separate(meta, into = c("meta", "data"), sep = "\\:")
    
    value <- page %>% 
        html_nodes(".value") %>% 
        html_text()
    
    df <- meta_df %>% 
        spread(meta, data) %>%
        mutate(trading_tag = value) %>% 
        mutate(TAG = as.numeric(str_replace(TAG, "\\$", ""))) %>% 
        separate(trading_tag, into = c("junk", "trading_tag"), sep = "H\\$", extra = "drop") %>% 
        mutate(trading_tag = as.numeric(trading_tag)) %>% 
        mutate(actual_tag = round(as.numeric(TAG)/1e6,2)) %>% 
        select(symbol = Symbol, trading_tag, actual_tag) %>% 
        mutate(symbol = str_replace_all(symbol, "\\s", ""))
    
    return(df)
}

meta_a <- map(cast$symbol, get_meta_a) %>% bind_rows()
```

Step 8: Calculate the forecasted TAG values for Rogue One at $440
=================================================================

``` r
tag_new <- tag_prices %>% 
    filter(!(movie_idx == 5)) %>% 
    group_by(symbol) %>% 
    summarise(total = sum(price) + 440) %>% 
    mutate(tag_forecast = total / 5) %>% 
    select(-total)
```

Step 9: Calculate the arbitrage opportunities
=============================================

``` r
arbitrage <- meta_a %>% 
    left_join(tag_new, by = "symbol") %>% 
    mutate(investment = 20000 * trading_tag) %>% 
    mutate(return = ifelse(tag_forecast >= trading_tag, (20000 * tag_forecast), (20000 * tag_forecast * -1))) %>% 
    mutate(roi = return / investment)

arbitrage %>% kable()
```

| symbol |  trading\_tag|  actual\_tag| forecast\_tag|         roi|
|:-------|-------------:|------------:|-------------:|-----------:|
| ATUDY  |        131.96|       146.15|        169.47|         1.2|
| BMEND  |         48.60|        13.32|         88.31|         1.8|
| DLUNA  |         71.61|        30.96|        114.24|         1.6|
| DYEN   |         16.20|         0.50|         88.46|         5.5|
| FJONE  |         64.81|        55.50|        136.98|         2.1|
| FWHIT  |         48.99|        46.67|        131.12|         2.7|
| MMIKK  |         47.22|        43.54|        129.28|         2.7|
| RAHME  |         58.24|        40.20|        122.87|         2.1|

Punch Line
==========

Ha! I knew it. Arbitrage Galore. Just look at Mads. He's trading at 43.54 right now. But when Rogue One gets added he's going to pop all the way up to 129.28. But it's not just Mads. The entire top billed cast of Rogue One is chronincally undervalued right now, with Donnie Yen [(DYEN)](http://www.hsx.com/security/view/DYEN) at the extreme end. Basically an investment in DYEN could yield a return of ~5.5X. Fuck I really wish this wasn't just fake money...
