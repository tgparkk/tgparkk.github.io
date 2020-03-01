---
layout: post
title:  "SQL-INNER JOIN"
author: tgparkk
categories: [ CS, SQL ]
tags: [#sql, 내부조인, INNERJOIN]
image: assets/images/Visual_SQL_JOINS_orig.jpg
---

sql join

#### How to use?

![walking]({{ site.baseurl }}/assets/images/Visual_SQL_JOINS_orig.jpg)

INNER JOIN : 두 테이블의 교집합

1. 와일드카드 * 를 사용하기
```sql
SELECT tmp1.*, tmp2.mobile_no
FROM addr AS tmp1, mobile AS tmp2
WHERE tmp1.cust_id = tmp2.cust_id; 
```
2. AS 사용하지 않고 별칭 주기
```sql
SELECT tmp1.*, tmp2.mobile_no
FROM addr tmp1, mobile tmp2
WHERE tmp1.cust_id = tmp2.cust_id; 
```
3. INNER JOIN 사용하기
```sql
SELECT tmp1.*, tmp2.mobile_no
FROM addr AS tmp1 INNER JOIN mobile AS tmp2
WHERE tmp1.cust_id = tmp2.cust_id; 
```
4. INNER JOIN 사용 예시
```sql
SELECT tmp1.*, tmp2.mobile_no
FROM CUSTOMERS tmp1 
INNER JOIN ORDERS tmp2 ON tmp1.cust_id = tmp2.cust_id
INNER JOIN EMPLOYEE tmp3 ON tmp2.emp_id = tmp3.emp_id
```

OUTER JOIN : 두 테이블중 A 테이블의 차집합 제외
1. LEFT OUTER JOIN 예시

![walking]({{ site.baseurl }}/assets/images/left_outer_join_ex.jpg)
```sql
SELECT tmp1.cust_id AS cust_id1, tmp1.home_addr1, tmp1.home_addr2,
       tmp2.cust_id AS cust_id2, tmp2.mobile_no
FROM addr1 AS tmp1
LEFT OUTER JOIN mobile2 AS tmp2
ON tmp1.cust_id = tmp2.cust_id;
```
2. RIGHT OUTER JOIN 예시

![walking]({{ site.baseurl }}/assets/images/right_outer_join_ex.jpg)
```sql
SELECT tmp1.cust_id AS cust_id1, tmp1.home_addr1, tmp1.home_addr2,
       tmp2.cust_id AS cust_id2, tmp2.mobile_no
FROM addr1 AS tmp1
RIGHT OUTER JOIN mobile2 AS tmp2
ON tmp1.cust_id = tmp2.cust_id;
```
