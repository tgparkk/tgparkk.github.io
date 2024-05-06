---
title: "sql"
layout: archive
permalink: categories/sql
author_profile: true
sidebar_main: true
---

<!--assign posts에만 변수 변경 -->
{% assign posts = site.categories.sql %}
{% for post in posts %} {% include archive-single2.html type=page.entries_layout %} {% endfor %}