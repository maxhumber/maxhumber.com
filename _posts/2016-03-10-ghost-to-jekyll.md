---
layout: post
title: Why I Switched from Ghost to Jekyll
---

**TL;DR** Use [Jekyll and Github Pages](https://help.github.com/articles/about-github-pages-and-jekyll/) for a cheap and maintainable blog.

I made a new blog! For the past few months I had been content with [Ghost](https://ghost.org), the publishing platform for professional bloggers. I enjoyed its simplicity and even made a couple themes for it (check them out on my [Github](https://github.com/getmicah)), but as time went on I got tired of paying for server time every month. With all the buzz about "static blogs" I decided to give it a try. Inevitably, I came across Github Pages and Jekyll. Free hosting and a static site blog? Yes, Please.

It wasn't like there was anything wrong with Ghost. I was just tired of paying to host it on a server. There are quite a few things that I didn't even realize I would appreciate before using Jekyll.

# Static Site
One of those being the idea of a static website being generated and no need for a backend. This just makes sense and everything is very fast. Jekyll also automatically generates your Sass files into css which is very handy (no need setting up gulp every project).

# Local Posts
Another thing I especially appreciate about Jekyll is how all your posts are stored locally. You just type out your post in markdown in your editor and push to Github to post. Also, its implementation of templates is extremely useful when constructing posts.

# Variables
The use of variables has to be my favorite feature. It splits variables up between site and page variables. Site variables would include the name of your blog and the description while page variables would be the name of the post or the date. You can include your own site variables inside the &#95;config.yml file, such as a Google Analytics code or something of the nature.

# Data Files
Another way to access info in your blog is through data files. Instead of just variables, data files allow you to create a YAML, JSON, or CSV file to put data into. For example on this site I have /data/websites.yml file where I store the websites I've made, the fields being the name and url, and then loop them into a list inside my html.
