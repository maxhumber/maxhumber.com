---
title: 'Starry Night Plots'
date: 2017-02-05
tags: [r]
---

I think good data science reads like a good story. In that it flows. Has an arc. And is compelling.

But data science has a dirty secret. For every piece that works, there are about nine others that didn't. Nine other stories that look like they were typed up by a monkey with a typewriter (and in a [finite amount of time!](https://en.wikipedia.org/wiki/Infinite_monkey_theorem))

The problem with this problem is that unless you did the work you never get to see the monkey scripts. The stuff that never worked. The stuff that got thrown out.

This creates, I think, unrealistic expectations about how data science gets done. Because every tutorial, textbook, lesson, workshop, talk, and blog post about data science just works. And we forget that this stuff has been designed and vetted to work. Most real world stuff doesn't just work...

I initially wanted this post to be about the Super Bowl. To build some simple toy model on "Points For/Against" and push it through a new plot that I've been working on. But nothing was working. The data and my toy model told a story that literally made zero sense.

But then it struck me. This is perfect. I was able to catch and diagnose a garbage model exactly because of the plot I wanted to talk about!

So. Here's my monkey script and the "Starry Night Plot" that helped me throw it out:

SETUP
-----

``` r
library(tidyverse)
library(viridis)
```
<br>

DATA
----

``` r
df <- read_csv(paste0(
    "https://raw.githubusercontent.com/maxhumber/",
    "maxhumber.com/master/assets/data/superbowl_data.csv"))
```
<br>

These data are scraped from [pro-football-reference.com](http://www.pro-football-reference.com/) with `purrr` and `rvest`. If you want to learn more about webscraping within the *tidverse* I have a quick post on the process [here](http://maxhumber.com/2017/01/08/vorp-hockey.html).

MODEL
-----

I was trying to build a toy model to predict who might win Super Bowl LI. I don't know much about the NFL, but I thought that I might be able to do something with "Season Average Points For" and "Season Average Points Against". Basically, I wanted to tease out the relative importance of Defense and Offense for past Super Bowl contenders:

``` r
mod1 <- glm(
    win ~ pf + pa,
    family = "binomial",
    data = df)

# summary(mod1)
```
<br>

If you run `summary(mod1)` you can see that the p-values aren't traditionally "significant", however, `pf` hits 0.1 which gets you a little `.` if you're "star-gazing" the printout.

Pumping the model through a prediction grid of all likely/possible points combinations:

``` r
pred_grid <- expand.grid(
    pf = 0:40, 
    pa = 0:40)

pred_grid$prob <- predict(
    mod1, newdata = pred_grid, type = "response")
```
<br>

And the putting that grid through a Tile Plot gets you:

``` r
pred_grid %>% 
    ggplot(aes(x = pf, y = pa)) + 
    geom_tile(aes(fill = prob))
```

![center]({{ site.url }}/assets/img/starry_1.png)

Sweet. Looks alright. But what does it mean? It's kind of hard to tell...

To improve the interpretability of `geom_tile` I added a contour layer and made the breaks hit the same sequence.

``` r
br <- 0.2

pred_grid %>% 
    ggplot(aes(x = pf, y = pa)) + 
    geom_tile(aes(fill = prob)) + 
    geom_contour(aes(z = prob), color = "white", 
        lty = 2, binwidth = br) + 
    scale_fill_continuous(
        breaks = seq(0, 1, br),
        labels = scales::percent_format())
```

![center]({{ site.url }}/assets/img/starry_2.png)

Now I can see that my dumb toy model thinks that "Points For" is more predictive than "Points Against". And that "Season Average Points For" is a bad thing when it comes to winning the Super Bowl.

Basically, if I put Atlanta and New England through this model the better team on paper would be expected to lose the Super Bowl (lol).

I wanted to figure out my toy model was behaving so strangely, so I added in the underlying data through some `geom_point` layers (Os for actual wins, Xs for actual losses) and a bit of polish:

``` r
br <- 0.2

pred_grid %>% 
    ggplot(aes(x = pf, y = pa)) + 
    geom_tile(aes(fill = prob)) + 
    geom_contour(aes(z = prob), 
        color = "white", lty = 2, binwidth = br) +
    geom_point(
        data = (df %>% filter(win == 1)),
        color = "white", shape = 16, size = 2) +
    geom_point(
        data = (df %>% filter(win == 0)),
        color = "white", shape = 4, size = 2) +
    scale_fill_viridis(
        direction = 1, end = 0.85, option = "D", 
        breaks = seq(0, 1, br),
        labels = scales::percent_format()) + 
    coord_cartesian(xlim = c(10, 40), ylim = c(10, 40)) + 
    labs(title = "Super Dumb Super Bowl Model", 
        x = "Points For", y = "Points Against", fill = "Prob") + 
    theme(panel.background = element_rect(fill = "white"))
```

![center]({{ site.url }}/assets/img/starry_3.png)

Now I can see that the behaviour of this model makes some sense (small data, and big upsets).

There's nothing really new about this type of plot. It's just a bunch of `tile`, `contour` and `point` layers and the viridis colourmap but I've been calling it the Starry Night Plot because it kind of looks like the painting. And I wanted to write about it because it has been super helpful in diagnosing and explaining model behaviour to other people.

I guess I hope you might be able to use it.

~

P.S. I also tried building models on point differntials for the exact matchups and conditioning the points for/against on Strength of Schedule... but then I just realized that I was p-hacking...

P.S.S. Go Falcons.
