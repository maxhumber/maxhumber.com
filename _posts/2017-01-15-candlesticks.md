---
title: "Repurposing the Candlestick Chart"
date: 2017-01-15
tags: [r]
---

My cousin Eli is way cooler than me. Well, to be fair, I don't exactly set a high bar! Eli is a skydiving enthusiast with over 200 jumps to his name. And I read books and write nonsense like this...

Eli is meticulous about collecting metadata from each of his jumps. Just a glance at his logbook and you can tell there's something interesting hiding in there. So. I asked him if I could play with his data and try to come up with something.

I don't know the technical terms, but basically, when you think about it, there are, hopefully, three stages in every skydive. The jump, the pull, and the landing. I thought that I could do something interesting with those three events across each jump. But the histograms and line graphs and bar charts that I've come to rely on just weren't working. Interesting data deserves an interesting visualization.

After some time messing around with graphical primitives in `ggplot2` I hit on a candlestick-esque chart built from `geom_segment`s that I thought could work.

This was my first attempt with simulated data:

![]({{ site.url }}/assets/img/candle1.png)

After getting Eli's logbook to conform to and look like the simulated data I threw it all back into the `geom_segment`s and got this:

![]({{ site.url }}/assets/img/candle2.png)

A little busy for my tastes. So, I decided to break every rule in data visualization and strip away all the fuss. I got rid of the labels and axes and text and titles and the legends because it was all noise and getting in the way of Eli's fearlessness (stupidity?) and the data. I wanted the raw stuff to shine.

This is what I finally arrived at:

![]({{ site.url }}/assets/img/candle3.png)

I love this slimmed down version because it's kind of like putting notches in a wall. And despite the lack of labels and text annotations you can still see a lot. For instance, you can see Eli's training exercises (two short bursts on the second and third row as well as the string of short jumps near the end of the third row). You can tease out some semblance of consistency in his free falls. And you can see where it almost all came to an end...that data point near the end of the second row where he had to pull his reserve chute.

Anyways. Thanks for letting my play with your data, Eli! For anyone interested, this is the `ggplot2` code that I used to create the final graph. And if you want to see all of the data for this post, it's available on [GitHub](https://github.com/maxhumber/maxhumber.com/tree/master/_R):

``` r
df %>% 
    ggplot(aes(x = id)) + 
    geom_segment(size = 1, color = "grey20", aes(
        xend = id,
        y = jump, 
        yend = chute)) +
    geom_segment(lty = 1, size = 0.25, color = "grey40", aes(
        xend = id,
        y = chute, 
        yend = 0)) +
    facet_wrap(~section, scales = "free_x", ncol = 1) + 
    labs(title = "", x = "", y = "", color = "") + 
    scale_x_continuous(breaks = seq(0, 500, 25)) + 
    theme(
        panel.background = element_rect(fill = "#FFFFFF"), 
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        strip.text = element_blank(),
        axis.ticks = element_blank(),
        legend.position = "none",
        axis.text = element_blank())
```