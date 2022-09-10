---
layout: post
title:  "Effective c++ item44 - 매개변수에 독립적인 코드는 템플릿으로부터 분리시키자."
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
                                        // template for n x n matrices of
template<typename T, std::size_t n>     // objects of type T; see below for info
class SquareMatrix {                    // on the size_t parameter
public:
    ...
    void invert();                      // invert the matrix in place
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
- 행렬의 크기를 매개변수로 받도록 바뀐 invert 함수가 기본 클래스인 SquareMatrixBase에 들어 있죠.  
- SquareMatrixBase, SquareMatrix 모두 같은 템플릿 이지만 SquareMatrix는 행렬의 크기를 매개변수로 받죠.
- 따라서 같은 타입의 객체를 원소로 갖는 모든 정방행렬은 오직 한 가지의 SquareMatrixBase 클래스를 공유하게 되죠.
- 다시 말해, 같은 원소 타입의 정방행렬이 사용하는 기본 클래스 버전의 invert 함수도 오직 한 개의 사본이죠.  
---
- SquareMatrix::invert 함수는 파생 클래스에서 코드 복제를 피할 목적으로만 마련한 장치이기 때문에,  
public 멤버가 아닌 protected 멤버로 되어 있죠.
- 참고로, 이 함수의 호출에 드는 추가 비용은 하나도 없어야 합니다. 기본 클래스의 invert함수를 호출하도록 구현된 파생 클래스의 invert 함수가 바로 인라인 함수이니까요.(암시적 인라인)
---
- 아직 해결하지 못한 부분은 SquareMatrixBase::invert 함수는 자신이 상대할 데이터가 어떤 것인지 알려야 하는데(크기는 매개변수로 받지만 진짜 행렬을 저장한 데이터가 어디에 있는지), 알려야해요.
- 정방행렬의 메모리 위치를 파생 클래스가 기본 클래스로 넘겨주면 되겠죠.
1. 첫번째 방법으로는 SquareMatrixBase::invert 함수가 매개변수를 하나 더 받도록 하는것이죠