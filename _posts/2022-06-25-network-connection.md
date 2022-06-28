---
layout: post
title:  "네트워크 통신."
summary: ""
author: tgparkk
date: '2022-06-25 19:45:23 +0530'
category: C++
keywords: C++, Server, network connection
permalink: /blog/WhatIsNetworkConnection/
usemathjax: true
---

# http 통신, socket 통신
http 통신
- 웹브라우저, 서버, 웹, 애플리케이션은 모두 HTTP(Hypertext Transfer Protocol)를 통해 통신해요.
- http는 신뢰성 있는 데이터 전송 프로토콜을 사용하기 때문에, 데이터가 손상됨을 신경쓸 필요가 없죠.(개발자는 인터넷 결함, 약점에 신경 쓸 필요 없이 클라이언트 개발에만~)
(참고 : https://kotlinworld.com/75)

웹 클라이언트와 서버
- 웹 콘텐츠는 웹 서버에 존재
- 웹 서버는 인터넷의 데이터를 저장하고,
- http 클라이언트가 요청한 데이터를 제공해요.
- http 요청 : "index.html 문서 가져와줘"
- http 응답 : ok, http 포맷이고, 길이는 3150 글자입니다.

- http client : chrome, edge
- "http://github.com/tgparkk/index.html" 를 열때, http 요청을 "http://github.com/" 서버에 보내고, 요청받은 "tgparkk/index.html" 를 찾으면, 타입, 길이 등의 정보와 함께 http 응답에 실어 클라이언트로 보내요.