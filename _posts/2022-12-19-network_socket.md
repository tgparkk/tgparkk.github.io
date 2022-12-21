---
layout: post
title:  "c++ network_socket"
summary: ".."
author: tgparkk
date: '2022-12-19 11:00:23 +0530'
category: C++
keywords: c++, networt, socket
permalink: /blog/network_socket/
usemathjax: true
---

# 네트워크 프로그래밍과 소켓의 이해
소켓 : 네트워크를 통한 두 컴퓨터의 연결을 의미해요.

- 전화받는 소켓의 생성과정(서버)
1. 소켓 생성 : socket 함수호출
2. IP주소와 PORT번호 할당 : bind 함수호출
3. 연결요청 가능상태로 변경 : listen 함수호출
4. 연결요청에 대한 수락 : accept 함수호출

- 전화거는 소켓의 생성과정(클라이언트)
1. 소켓 생성 : socket 함수호출
3. 연결요청 : connect 함수호출

# 소켓의 타입
1. 연결지향형 소켓(SOCK_STREAM)
-컨베이어벨트로 예시 
-중간에 데이터가 소멸되지 않고 목적지로 전송 
-전송 순서대로 수신 
-전송되는 데이터의 경계가 존재하지 않음 

2. 비연결지향형 소켓(SOCK_DGRAM)
-오토바이 배달로 예시 
-전송된 순서에 상관없이 가장 빠른 전송 지향 
-전송된 데이터의 손실, 파손 우려 
-전송되는 데이터의 경계 존재 
-한번에 전송할 수 있는 데이터의 크기 제한 

# 주소체계와 
