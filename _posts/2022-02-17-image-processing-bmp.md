---
published: true
layout: post
title:  "영상처리의 개요"
summary: "영상처리 C++"
author: tgparkk
date: '2022-02-17 19:27:23 +0530'
category: image processing
thumbnail: /assets/img/posts/code.jpg
keywords: image processing, CV, C++, Algorithm, bmp
permalink: /blog/image-processing_2_bmp/
usemathjax: true
---

# 3.1 비트맵 개요

## 3.1.1 비트맵 정의와 종류
컴퓨터에서 영상을 표현하는 대표적인 방법이 비트맵**bitmap**이다.

비트맵은 말 그대로 비트**bit**들의 집합**map**이다.

여러 개의 비트가 모여 한 점(픽셀)의 색상을 표현하고, 색상을 가진 점들이 모여 영상을 구성한다.

비트맵 방식은 영상의 전체 크기(가로* 세로)에 해당하는 픽셀 정보를 모두 저장하기 때문에 메모리 용량을 많이 차지하는 단점이 있지만, 압축 기법을 사용하지 않고 표현이 직관적이어서 분석이 용이하다.

또한 비트맵 방식은 복잡한 계산 없이 단순히 그림을 복사하여 화면에 보여주기 때문에 벡터 방식보다 화면 출력 속도가 빠르다. 참고로 비트맵 방식과 상반되는 개념으로 벡터 그래픽**vector graphics** 방식이 있다.

Windows에서 지원하는 비트맵에는 두 가지 종류가 있다. 하나는 장치 의존 비트맵**Device Dependent Bitmap**이고 다른 하나는 장치 독립 비트맵**Device Independent Bitmap**이다.
각각 DDB, DIB 라고 쓴다.

DIB는 출력 장치(모니터)가 달라도 자신의 색상을 표현하는 색상 테이블**color table**이 있다.


# 3.2 BMP 파일의 이해

## 3.2.1 BMP 파일의 전체 구조

|비트맵 파일 헤더(BITMAPFILEHEADER)|
|--|
|비트맵 정보 헤더(BITMAPINFOHEADER)|
|색상 테이블/팔레트(RGBQUAD 배열)|
|픽셀 데이터(RGB 배열 또는 팔레트 인덱스 배열)|

BMP 파일 구조 **4개 정보**

DIB 구조 **하위 3개 정보**

그레이스케일 영상의 BMP 파일에는 256단계의 무채색을 표현하는 RGBQUAD 배열이 저장되어 있다. RGBQUAD 구조체 하나의 크기가 4바이트 이므로 그레이스케일 비트맵의 색상 테이블 영역의 크기가 256*4=1024 바이트이다.

그리고 픽셀 데이터 부분에는 각 픽셀의 그레이스케일을 표현하는 RGBQUAD 배열의 인덱스가 저장되어 있다.

트루컬러 영상을 표현하는 BMP 파일은 색상 테이블이 존재하지 않으며, 픽셀 데이터 부분에는 각 픽셀의 색상이 파란색, 녹색, 빨간색 순서의 3바이트 단위로 저장되어 있다.
