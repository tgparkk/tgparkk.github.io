---
layout: post
title:  "SQL-INNER JOIN"
author: tgparkk
categories: [ CS, SQL ]
tags: [#sql, 내부조인, INNERJOIN]
image: assets/images/Visual_SQL_JOINS_orig.jpg
description: "My review of Inception movie. Acting, plot and something else in this short description."
featured: false
hidden: false
---

sql join

#### How to use?

![walking]({{ site.baseurl }}/assets/images/8.jpg)

INNER JOIN, 

1. 와일드카드 * 를 사용하기
```sql
SELECT tmp1.*, tmp2.mobile_no
FROM addr AS tmp1, mobile AS tmp2
WHERE tmp1.cust_id = tmp2.cust_id; 
```
