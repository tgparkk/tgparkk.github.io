---
layout: post
title:  "Effective c++ item44 - "매개변수에 독립적인 코드는 템플릿으로부터 분리시키자."
summary: "Factor parameter-independent code out of 
templates."
author: tgparkk
date: '2022-06-19 20:45:23 +0530'
category: C++
keywords: c++
permalink: /blog/effective-cpp-item44/
usemathjax: true
---

# 항목 44: 매개변수에 독립적인 코드는 템플릿으로부터 분리시키자
템플릿의 단점은 ***코드 비대화(code bloat)*** 가 초래되는 것이죠.  
똑같은(거의 똑같은) 내용의 코드와 데이터가 여러 벌로 중복되어 이진 파일로 생성되는 점 입니다.  
소스코드의 중복은 명시적이지만, 템플릿은 암시적이므로 판별하기 힘들죠.
```c++
template<typename T,    // template for n x n matrices of
std::size_t n>          // objects of type T; see below for info
class SquareMatrix {    // on the size_t parameter
public:
    ...
    void invert();      // invert the matrix in place
};
```
This template takes a type parameter, T, but it also takes a parameter of type size_t — a non-type parameter.  
Non-type parameters are less common than type parameters,  
but they’re completely legal, and, as in this example, they can be quite natural.
```c++
SquareMatrix<double, 5> sm1;
...
sm1.invert(); // call SquareMatrix<double, 5>::invert
SquareMatrix<double, 10> sm2;
...
sm2.invert(); // call SquareMatrix<double, 10>::invert
```
이때 ***invert***의 사본이 인스턴스화되는데, 만들어지는 사본의 개수가 두 개 입니다.  
그렇지만 행과 열의 크기를 나타내는 상수만 빼면 두 함수는 완전히 똑같습니다.  
이런 현상이 바로 템플릿을 포함한 프로그램이 코드 비대화를 일으키는 일반적인 형태죠.

```c++
template<typename T>                        // size-independent base class for
class SquareMatrixBase {                    // square matrices
protected:
    ...
    void invert(std::size_t matrixSize);    // invert matrix of the given size
    ...
};

template<typename T, std::size_t n>
class SquareMatrix: private SquareMatrixBase<T> {
private:
    using SquareMatrixBase<T>::invert;      // make base class version of invert
                                            // visible in this class; see Items 33
                                            // and 43
public:
    ...
    void invert() { invert(n); }            // make inline call to base class
};                                          // version of invert
```