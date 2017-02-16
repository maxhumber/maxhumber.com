library(tidyverse)
library(viridis)
library(gganimate)
library(ggstance)
library(animation)
library(stringr)

# http://www5.statcan.gc.ca/cansim/a26
# https://www.climate-lab-book.ac.uk/spirals/

ani.options(autobrowse = FALSE, interval = 0.1)

URL <- str_c("https://raw.githubusercontent.com/maxhumber", 
    "/maxhumber.com/master/assets/data/tourists.csv")

df <- read_csv(URL) %>% 
    select(Ref_Date, value = Value) %>% 
    separate(Ref_Date, into = c("year", "month"), sep = "/") %>% 
    mutate(year = as.numeric(year), month = as.numeric(month)) %>% 
    group_by(year) %>% 
    # add in zero month with fill to make spiral work
    complete(month = seq(0, 12, 1)) %>% 
    ungroup() %>% 
    fill(value, .direction = "down") %>%
    arrange(year, month) %>% 
    # need 2 data points in first frame for geom_line to work
    mutate(frm = lag(row_number())) %>% 
    fill(frm, .direction = "up")

ggplot(df, aes(x = month, y = value, frame = frm)) +
    # black outline
    geom_rect(aes(
        xmin = 0, ymin = min(df$value, na.rm = TRUE) - 2e6, 
        xmax = 12, ymax = max(df$value, na.rm = TRUE) + 2e6),
        fill = "#000000") + 
    # 1M grid line with label
    geom_linerangeh(aes(
        xmin = 0, xmax = 12, y = 1e6), 
        color = "red") + 
    annotate("label", x = 0, y = 1e6, color = "red", 
        fill = "#000000", label = "1M", size = 3) + 
    # 7M grid line label
    geom_linerangeh(aes(
        xmin = 0, xmax = 12, y = 7e6), 
        color = "red") + 
    annotate("label", x = 0, y = 7e6, color = "red", 
        fill = "#000000", label = "7M", size = 3) + 
    # actual data
    geom_line(aes(colour = year, group = year, cumulative = TRUE)) +
    geom_text(aes(
        label = year, x = 6, y = min(df$value, na.rm = TRUE) - 2e6), 
        color = "#FFFFFF") + 
    coord_polar(theta = "x") +
    scale_y_continuous(
        limits = range(df$value, na.rm = TRUE) + c(-2e6, 2e6)) +
    # hack: getting rid of the "0 months"
    scale_x_continuous(
        breaks = seq(1, 12, 1),
        labels = c(
            "Jan", "Feb", "Mar", "Apr", 
            "May", "Jun", "Jul", "Aug", 
            "Sep", "Oct", "Nov", "Dec")) +
    scale_color_viridis() + 
    labs(title = "Total Visitors to Canada (1972 - 2016)", 
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
            # make axis text hug circle
            angle = seq(-30, -360, length.out = 12)),
        axis.title = element_blank(), 
        axis.ticks = element_blank())

# alternate colours

BACKGROUND <- "#FFFFFF"
GRID <- "#E50000"
TEXT <- "#E50000"
LOW <- "#990000"
HIGH <- "#ff3333"

ggplot(df, aes(x = month, y = value, frame = frm)) +
    # white disk
    geom_rect(aes(
        xmin = 0, ymin = min(df$value, na.rm = TRUE) - 2e6, 
        xmax = 12, ymax = max(df$value, na.rm = TRUE) + 2e6),
        fill = BACKGROUND) + 
    # 1M grid line with label
    geom_linerangeh(aes(
        xmin = 0, xmax = 12, y = 1e6), 
        color = GRID, lty = 3, size = 0.5) + 
    annotate("label", x = 0, y = 1e6, color = TEXT, 
        fill = BACKGROUND, label = "1M", size = 3) + 
    # 7M grid line label
    geom_linerangeh(aes(
        xmin = 0, xmax = 12, y = 7e6), 
        color = GRID, lty = 3, size = 0.5) + 
    annotate("label", x = 0, y = 7e6, color = TEXT, 
        fill = BACKGROUND, label = "7M", size = 3) + 
    # actual data
    geom_line(aes(colour = year, group = year, cumulative = TRUE)) +
    geom_text(aes(
        label = year, x = 6, y = min(df$value, na.rm = TRUE) - 2e6), 
        color = TEXT) + 
    coord_polar(theta = "x") +
    scale_y_continuous(
        limits = range(df$value, na.rm = TRUE) + c(-2e6, 2e6)) +
    # hack: getting rid of the "0 months"
    scale_x_continuous(
        breaks = seq(1, 12, 1),
        labels = c(
            "Jan", "Feb", "Mar", "Apr", 
            "May", "Jun", "Jul", "Aug", 
            "Sep", "Oct", "Nov", "Dec")) +
    scale_color_gradient(low = LOW, high = HIGH) + 
    labs(title = "Total Visitors to Canada (1972 - 2016)", 
         caption = "@maxhumber") + 
    theme(
        legend.position = "none",
        panel.background = element_rect(fill = "#F0F0F0"),
        plot.background = element_rect(fill = "#F0F0F0"),
        plot.title = element_text(color = TEXT, hjust = 0.5, size = 16),
        plot.caption = element_text(color = TEXT, hjust = 1, size = 10),
        panel.grid = element_blank(), 
        axis.text.y = element_blank(),
        axis.text.x = element_text(
            color = TEXT, size = 12, 
            # make axis text hug circle
            angle = seq(-30, -360, length.out = 12)),
        axis.title = element_blank(), 
        axis.ticks = element_blank())



# proto type
    
df <- expand.grid(
    year = 1:5, 
    month = 1:12
    ) %>% 
    mutate(temp = year + month/12 + rnorm(nrow(.), mean = 0, sd = 1)) %>% 
    arrange(year, month) %>% 
    mutate(frm = row_number())

ggplot(df, aes(x = month, y = temp, color = year, group = year)) + 
    geom_line()

p <- ggplot(df, aes(x = month, y = temp, color = year, group = year)) + 
    geom_line(aes(frame = frm, cumulative = TRUE)) + 
    coord_polar(theta = "x")

gganimate(p)

# manual:
# https://stackoverflow.com/questions/41453746/how-to-get-complete-rather-than-partial-pie-charts-using-gganimate

for (i in unique(df$frm)) {
    p <- ggplot(df[df$frm <= i + 1,], aes(x = qtr, y = temp, color = year, group = year)) + 
        geom_path() + 
        coord_polar(theta = "x")
    print(p)
}

df <- expand.grid(
    day = 1:365,
    year = 1990:2017
    ) %>% 
    mutate(temp = day/365 + year) %>% 
    mutate(temp = temp - 1990 + rnorm(nrow(.), mean = 0, sd = 1)) %>% 
    arrange(year, day) %>% 
    mutate(movave = zoo::rollmean(temp, 15, align="right", na.pad=TRUE)) %>% 
    filter(day %% 30 == 0) %>% 
    mutate(frm = row_number()) %>% 
    mutate(frm = lag(frm)) %>% 
    fill(frm, .direction = "up")
    
p <- ggplot(df, aes(x = day, y = movave, frame = frm)) + 
    geom_line(aes(colour = year, group = year, cumulative = TRUE)) + 
    coord_polar(theta = "x") +
    scale_color_viridis()

gganimate(p)

