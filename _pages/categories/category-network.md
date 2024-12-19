---
title: "network"
layout: archive
permalink: categories/network
author_profile: true
sidebar_main: true
---

<!--assign posts에만 변수 변경 -->
{% assign posts = site.categories.network %}
{% for post in posts %} {% include archive-single2.html type=page.entries_layout %} {% endfor %}
