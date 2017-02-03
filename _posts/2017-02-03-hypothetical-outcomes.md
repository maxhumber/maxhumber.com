---
title: 'Hypothetical Outcome Plots'
date: 2017-02-03
tags: [r]
---

``` r
suppressPackageStartupMessages(library(tidyverse))
# devtools::install_github("dgrtwo/gganimate")
# install.packages("cowplot")
library(gganimate)
# install image magick in terminal >> "brew install image magick"
```
<br>

If the Weatherman says that there is 30% chance of rain tomorrow. And it rains. Was he wrong? It's an important question. Because it rained on November 8th. And a lot of people think that it wasn't supposed to.

Communicating uncertainty is hard. It's hard because uncertainty can be convoluted and opaque. And it's hard because a lot of people can't get down with boxplots or measures of spread.

Take this toy data for example:

``` r
set.seed(2016)

df <- tibble(
    `Blue Team` = round(rnorm(50, mean = 48, sd = 5)), 
    `Red Team` = round(rnorm(50, mean = 45, sd = 3))
    ) %>% 
    mutate(simulation = row_number()) %>% 
    gather(team, probability, -simulation) %>% 
    mutate(probability = ifelse(probability >= 100, 100, probability) / 100)
```
<br>

Imagine that this data was generated from some model. How might we represent the uncertainty in our model and around our predictions?

Perhaps we might push the data through a boxplot:

``` r
df %>% 
    ggplot(aes(x = team, y = probability)) +
    geom_boxplot()
```

![center]({{ site.url }}/assets/img/hop_1.png)

Or a density chart:

``` r
df %>% 
    ggplot(aes(x = probability, fill = team)) + 
    geom_density(alpha = 1/2) + 
    scale_fill_manual(values = c("blue", "red"))
```

![center]({{ site.url }}/assets/img/hop_2.png)

Or use some errorbars:

``` r
df %>% 
    group_by(team) %>% 
    summarise(
        mean = mean(probability), 
        low = quantile(probability, 0.025),
        high = quantile(probability, 0.975)) %>% 
    ggplot(aes(x = team, y = mean)) +
    geom_errorbar(aes(ymin = low, ymax = high))
```

![center]({{ site.url }}/assets/img/hop_3.png)

These options all kind of suck, though. They're not super intuitive. And they aren't all that convincing, because they can intimidate a lot of people!

Instead of boxplots or density charts or regular errorbars we can hack errorbars to generate a proto-Hypothetical Outcome Plot:

``` r
df %>% 
    ggplot(aes(x = team, y = probability)) +
    geom_errorbar(aes(ymin = probability, ymax = probability))
```

![center]({{ site.url }}/assets/img/hop_4.png)

Hypothetical Outcome Plots (HOPs) are a way to build and visualize uncertainty in the same way that we experience it (in and by countable events). The depth and theory behind HOPs is beyond the scope of this quick post, but if you're interested in learning more check out [this awesome Medium story](https://medium.com/hci-design-at-uw/hypothetical-outcomes-plots-experiencing-the-uncertain-b9ea60d7c740#.taennvi6g) by the *UW Interactive Data Lab*.

Extending our hacked errorbars with `gganimate` we can implement an actual HOP in just a few lines of R:

``` r
p <- df %>% 
    ggplot(aes(x = team, y = probability, frame = simulation)) +
    geom_errorbar(aes(ymin = probability, ymax = probability))

gganimate(p, title_frame = FALSE)
```

![center]({{ site.url }}/assets/img/hop_5.gif)

In this way we can directly experience the uncertainty of our model and the predictions that it happens to make.

In looking at the HOP it seems as though the Blue Team is supposed to win our imaginary game. Importantly, however, the Red Team comes up on top in certain simulations. So, don't say that the model is wrong if they happen to actually win our imaginary game!

If you want to add a little polish to your HOP, I might suggest extending it with some ghost bars:

``` r
p <- df %>%
    ggplot(aes(x = team, y = probability)) +
    geom_errorbar(aes(
        ymin = probability, ymax = probability, 
        frame = simulation, cumulative = TRUE), 
        color = "grey80", alpha = 1/8) +
    geom_errorbar(aes(
        ymin = probability, ymax = probability, frame = simulation), 
        color = "#00a9e0") +
    scale_y_continuous(
        limits = c(0, 1), 
        labels = scales::percent_format()) +
    theme(panel.background = element_rect(fill = "#FFFFFF")) +
    labs(title = "", y = "Probability of winning", x = "")

gganimate(p, title_frame = FALSE)
```

![center]({{ site.url }}/assets/img/hop_6.gif)

But that's it. Thanks for reading!

I have two more posts in the queue about visualizing models and model performance. Look for them in the near future!
