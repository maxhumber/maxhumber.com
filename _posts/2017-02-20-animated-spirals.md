---
title: 'Animated Spirals 🌀'
date: 2017-02-20
tags: [r]
---

Ed Hawkins' [Global Temperature Spiral](https://www.climate-lab-book.ac.uk/spirals/) is my new favourite visualization.

It's powerful, compelling, and super tangible.

I wanted to apply the spiral to my own data, so I got janky with `ggplot2` and figured out how to do it.

Here's my own spiral with [StatsCan data](http://www5.statcan.gc.ca/cansim/a26) on tourists visits to Canada 🍁:

![center]({{ site.url }}/assets/img/canada.gif)

(Side Note: Y U no come to Canada N E more? It's our [Sesquicentennial](http://canada.pch.gc.ca/eng/1468262573081) this year, the CAD is dirt cheap, and we have good beer!)

Spirals look super cool, but really, there's not much to them. You can effectively spin up your own in 4 lines of `R`:

``` r
ggplot(df, aes(x = month, y = value)) +
    geom_line(aes(colour = year, group = year)) +
    coord_polar(theta = "x") +
    scale_x_continuous(breaks = seq(1, 12, 1))
```
<br>

The hard part is getting the data to squish into those four lines.

This is how I made the StatsCan data all squishy:

``` r
library(tidyverse)
library(stringr)

URL <- str_c("https://raw.githubusercontent.com/maxhumber",
    "/maxhumber.com/master/assets/data/tourists.csv")

df <- read_csv(URL) %>%
    select(Ref_Date, value = Value) %>%
    separate(Ref_Date, into = c("year", "month"), sep = "/") %>%
    mutate(year = as.numeric(year), month = as.numeric(month)) %>%
    filter(year >= 2000) %>% 
    group_by(year) %>%
    # add zeroth month with fill to make spiral actually spiral
    complete(month = seq(0, 12, 1)) %>%
    ungroup() %>%
    fill(value, .direction = "down") %>%
    arrange(year, month) %>%
    drop_na() %>%
    # 2 data points in first frame for geom_line to work
    mutate(frame = lag(row_number())) %>%
    fill(frame, .direction = "up")
```
<br>

The trick, I figured out, is to split out and separate the months from the years and create a dummy linking month so that the spiral can actually spiral. If you're playing along at home, I'd recommend running things one line at a time to see the intermediate wrangling steps.

After the data is wrangled, you can spice up the original 4 lines and wrap it in a function to pass to `animation::saveGIF`.

``` r
library(viridis)
library(animation)

draw_spiral <- function(i=1) {

    # plot sequence
    p <- df %>% 
        filter(frame <= i) %>% 
        ggplot(aes(x = month, y = value))
    
    # add outline and gridlines with labels
    p <- p +
        geom_rect(aes(
            xmin = 0, ymin = min(df$value, na.rm = TRUE) - 2e6, 
            xmax = 12, ymax = max(df$value, na.rm = TRUE) + 2e6),
            fill = "#000000") + 
        # 1M
        geom_hline(yintercept = 1e6, color = "red") + 
        annotate("label", x = 0, y = 1e6, color = "red", 
            fill = "#000000", label = "1M", size = 3) + 
        # 7M
        geom_hline(yintercept = 7e6, color = "red") + 
        annotate("label", x = 0, y = 7e6, color = "red", 
            fill = "#000000", label = "7M", size = 3)
    
    # plot actual data
    p <- p +
        geom_line(aes(colour = year, group = year))
    
    # year label
    p <- p +
        geom_text(
            data = ( df %>% filter(frame == i) ), aes(
            label = year, x = 6, y = min(df$value, na.rm = TRUE) - 2e6),
            color = "#FFFFFF")

    # coordinate and scale systems
    p <- p +
        coord_polar(theta = "x") +
        scale_y_continuous(
            limits = range(df$value, na.rm = TRUE) + c(-2e6, 2e6)) +
        scale_x_continuous(
            # hack out the zeroth month
            breaks = seq(1, 12, 1),
            labels = c(
                "Jan", "Feb", "Mar", "Apr", 
                "May", "Jun", "Jul", "Aug", 
                "Sep", "Oct", "Nov", "Dec"))
    
    # theme and formats
    p <- p +
        scale_color_viridis(limits = range(df$year), begin = 0, end = 1) + 
        labs(title = "Total Visitors to Canada (2000 - 2016)", 
             caption = "@maxhumber") + 
        theme(
            legend.position = "none",
            panel.background = element_rect(fill = "#313131"),
            plot.background = element_rect(fill = "#313131"),
            plot.title = element_text(color = "#FFFFFF", hjust = 0.5, size = 16),
            plot.caption = element_text(color = "#FFFFFF", hjust = 1, size = 10),
            panel.grid = element_blank(), 
            axis.text.y = element_blank(),
            axis.text.x = element_text(
                color = "#FFFFFF", size = 12, 
                angle = seq(-30, -360, length.out = 12)),
            axis.title = element_blank(), 
            axis.ticks = element_blank())
    
    print(p)
}

# draw_spiral(i=219)
```
<br>

And, finally, you can wrap the function with an `animation` snippet to make the spiral actually spiral. (I initially tried to use `gganimate` but things started to get weird (@drob), so I fell back on vanilla `animation`):

``` r
saveGIF({
    for (i in 1:(nrow(df)-1)) {
        draw_spiral(i)
    }},
    movie.name = "canada.gif", 
    interval = 1/12, 
    ani.width = 600, 
    ani.height = 600
)
```
<br>

Hope to see your spirals soon 🌀. And I hope to see you in July 🍁!

If you've enjoyed this post you might also like what I've done on:

-   [gganimate](http://maxhumber.com/2017/02/03/hypothetical-outcomes.html)
-   [Spirals](http://maxhumber.com/2016/12/31/sleep-circle.html)
-   [Pie charts](http://maxhumber.com/2017/01/21/THE-BEST.html)
-   [Canada](http://maxhumber.com/2017/02/15/tile_canada.html)
