I hate pie charts. They're incredibly misleading and way overused. Walter Hickey has a great post on [why you should never use them](http://www.businessinsider.com/pie-charts-are-the-worst-2013-6?op=1), but the entire argument can basically be summed up in an image:

![](/assets/img/sleep_pies.png)

Last night while browsing [/r/dataisbeautiful](https://www.reddit.com/r/dataisbeautiful/), however, I spyed a pie chart that I actually kind of liked. I'm talking about this thing:

![](/assets/img/sleep_inspiration.png)

[My daughters sleeping patterns for the first 4 months of her life. One continuous spiral starting on the inside when she was born, each revolution representing a single day.](https://www.reddit.com/r/dataisbeautiful/comments/5l39mu/my_daughters_sleeping_patterns_for_the_first_4/?sort=new) is sitting at 52.4k upvotes and is right now the most liked post on /r/dataisbeautiful. Ever.

The pie chart format is well suited for sleep data because time spirals like a clock. It doesn't abruptly stop and start again on the other side of a bar or column. The graph is powerful, this once, because it helps to show an infant finding her circadian rhythm.

I thought it would be fun to recreate [/u/andrew_elliott](https://www.reddit.com/user/andrew_elliott)'s graph, but the process he detailed in the comments was fairly opaque and unhelpful:

"Visualisation pattern was created using the CAD package Rhinoceros with Grasshopper plugin, using my own script. Then Adobe Illustrator was used for appearance. Source data was manually logged using Baby Connect iPhone app by my wife and myself."

After futzing around in R for a couple of hours with data that I simulated, I think I've come close to a viable recreation.

Here's my version of /u/andrew_elliott's Sleep Circle / Time Spiral Graph:

![](/assets/img/sleep_recreated2.png)

If you're interested in creating time spiral graphs for yourself, the script that underpins this post is available on [GitHub](https://github.com/maxhumber/sleep_circle/blob/master/sleep_circle.R)
