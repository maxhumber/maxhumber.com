library(tidyverse)
library(viridis)
library(gganimate)
library(ggstance)
library(animation)
library(stringr)

# http://www5.statcan.gc.ca/cansim/a26
# https://www.climate-lab-book.ac.uk/spirals/

ani.options(autobrowse = FALSE, interval = 1/24)

URL <- str_c("https://raw.githubusercontent.com/maxhumber", 
    "/maxhumber.com/master/assets/data/tourists.csv")

df <- read_csv(URL) %>% 
    select(Ref_Date, value = Value) %>% 
    separate(Ref_Date, into = c("year", "month"), sep = "/") %>% 
    mutate(year = as.numeric(year), month = as.numeric(month)) %>% 
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

ggplot(df, aes(x = month, y = value, frame = frame)) +
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

ggplot(df, aes(x = month, y = value, frame = frame)) +
    geom_line(aes(colour = year, group = year, cumulative = TRUE)) +
    coord_polar(theta = "x") +
    scale_x_continuous(breaks = seq(1, 12, 1)) +
    labs(title = "Total Visitors to Canada (1972 - 2016)") 

BACKGROUND <- "#FFFFFF"
GRID <- "#E50000"
TEXT <- "#E50000"
LOW <- "#220000"
HIGH <- "#FF3333"

p <- df %>% 
    filter(frame <= 24) %>% 
    ggplot(aes(x = month, y = value, frame = frame)) +
    # disk outline
    geom_rect(aes(
        xmin = 0, ymin = min(df$value, na.rm = TRUE) - 2e6, 
        xmax = 12, ymax = max(df$value, na.rm = TRUE) + 2e6),
        fill = BACKGROUND) + 
    # grid line #1 with label
    geom_linerangeh(aes(
        xmin = 0, xmax = 12, y = 1e6), 
        color = GRID, lty = 3, size = 0.5) + 
    annotate("label", x = 0, y = 1e6, color = TEXT, 
        fill = BACKGROUND, label = "1M", size = 3) + 
    # grid line #2 with label
    geom_linerangeh(aes(
        xmin = 0, xmax = 12, y = 7e6), 
        color = GRID, lty = 3, size = 0.5) + 
    annotate("label", x = 0, y = 7e6, color = TEXT, 
        fill = BACKGROUND, label = "7M", size = 3) + 
    # data
    geom_line(aes(colour = year, group = year, cumulative = TRUE), show.legend = FALSE) +
    geom_text(aes(
        label = year, x = 6, y = min(df$value, na.rm = TRUE) - 2e6), 
        color = TEXT) + 
    coord_polar(theta = "x") +
    scale_y_continuous(
        limits = range(df$value, na.rm = TRUE) + c(-2e6, 2e6)) +
    # hack out the zeroth months
    scale_x_continuous(
        breaks = seq(1, 12, 1),
        labels = c(
            "Jan", "Feb", "Mar", "Apr", 
            "May", "Jun", "Jul", "Aug", 
            "Sep", "Oct", "Nov", "Dec")) +
    scale_color_gradient(low = LOW, high = HIGH) + 
    labs(title = "Total Visitors to Canada (1972 - 2016)", 
         caption = "@maxhumber") + 
    # spice
    theme(
        panel.background = element_rect(fill = "#F0F0F0"),
        plot.background = element_rect(fill = "#F0F0F0"),
        plot.title = element_text(color = TEXT, hjust = 0.5, size = 16),
        plot.caption = element_text(color = TEXT, hjust = 1, size = 10),
        panel.grid = element_blank(), 
        axis.text.y = element_blank(),
        axis.text.x = element_text(
            color = TEXT, size = 12, 
            angle = seq(-30, -360, length.out = 12)),
        axis.title = element_blank(), 
        axis.ticks = element_blank())

gganimate(p, filename = "canada.html", title_frame = FALSE)

saveGIF({
    for (i in 1:nrow(df)) {
        print(
        
            df %>% 
            filter(frame <= i) %>% 
            ggplot(aes(x = month, y = value)) +
            # disk outline
            geom_rect(aes(
                xmin = 0, ymin = min(df$value, na.rm = TRUE) - 2e6, 
                xmax = 12, ymax = max(df$value, na.rm = TRUE) + 2e6),
                fill = BACKGROUND) + 
            # grid line #1 with label
            geom_linerangeh(aes(
                xmin = 0, xmax = 12, y = 1e6), 
                color = GRID, lty = 3, size = 0.5) + 
            annotate("label", x = 0, y = 1e6, color = TEXT, 
                     fill = BACKGROUND, label = "1M", size = 3) + 
            # grid line #2 with label
            geom_linerangeh(aes(
                xmin = 0, xmax = 12, y = 7e6), 
                color = GRID, lty = 3, size = 0.5) + 
            annotate("label", x = 0, y = 7e6, color = TEXT, 
                     fill = BACKGROUND, label = "7M", size = 3) + 
            # data
            geom_line(aes(colour = year, group = year), show.legend = FALSE) +
            geom_text(aes(
                label = year, x = 6, y = min(df$value, na.rm = TRUE) - 2e6), 
                color = TEXT) + 
            coord_polar(theta = "x") +
            scale_y_continuous(
                limits = range(df$value, na.rm = TRUE) + c(-2e6, 2e6)) +
            # hack out the zeroth months
            scale_x_continuous(
                breaks = seq(1, 12, 1),
                labels = c(
                    "Jan", "Feb", "Mar", "Apr", 
                    "May", "Jun", "Jul", "Aug", 
                    "Sep", "Oct", "Nov", "Dec")) +
            scale_color_gradient(low = LOW, high = HIGH) + 
            labs(title = "Total Visitors to Canada (1972 - 2016)", 
                 caption = "@maxhumber") + 
            # spice
            theme(
                panel.background = element_rect(fill = "#F0F0F0"),
                plot.background = element_rect(fill = "#F0F0F0"),
                plot.title = element_text(color = TEXT, hjust = 0.5, size = 16),
                plot.caption = element_text(color = TEXT, hjust = 1, size = 10),
                panel.grid = element_blank(), 
                axis.text.y = element_blank(),
                axis.text.x = element_text(
                    color = TEXT, size = 12, 
                    angle = seq(-30, -360, length.out = 12)),
                axis.title = element_blank(), 
                axis.ticks = element_blank())
            
            ) 
    }},
    movie.name = "canada.gif", 
    interval = 1/24, 
    ani.width = 600, 
    ani.height = 600
)


