---
layout: post
title:  "c++ classMemoryManagement"
summary: ".."
author: tgparkk
date: '2023-01-20 11:00:23 +0530'
category: C++
keywords: c++, smart_ptr, move
permalink: /blog/classMemoryManagement/
usemathjax: true
---

# 클래스 메모리 관리
컴파일러가 만들어준 복사 생성자, 대입 연산자는 int, double, 포인터와 같은 기본 타입에 대해서는 단위복제(bitwise copy), 얕은 복제(shallow copy)또는 대입이 적용되요.  
그러나 메모리를 동적으로 할당한 객체는 위 방법으로는 문제가 생겨요.

```c++
// 그래서 copy constructor, copy assignment operator
// 를 직접 구현해야 해요.
Spreadsheet& Spreadsheet::operator=(const Spreadsheet& rhs)
{
    if(this == &rhs) return *this;

    // 기존 메모리 해제
    for(size_t i=0; i<mWidth;i++)
    {
        delete[] mCells[i];
    }
    delete[] mCells;
    mCells = nullptr;

    // 메모리 새로 할당
    mWidth = rhs.mWidth;
    ~
    
    // 데이터 복제
    for (size_t i = 0; i < mWidth; i++) {
		for (size_t j = 0; j < mHeight; j++) {
			mCells[i][j] = src.mCells[i][j];
		}
	}

    return *this;
}
```

위는 문제없어보이지만, 중간에 익셉션이 발생할수도 있어 문제가 있어보이죠.  
copy-and-swap 기법을 이용해야하는데요.
```c++
// 안전하게 std::swap를 이용해보죠.
// swap 을 비멤버로 구현해야 표준라이브러리 알고리즘에서 활용할 수 있다고하네요..?

// 우선 정의
Spreadsheet& operator=(const Spreadsheet& rhs);
friend void swap(Spreadsheet& first, Spreadsheet& second) noexcept;

// 다음 구현
void swap(Spreadsheet& first, Spreadsheet& second) noexcept
{
	using std::swap;

	swap(first.mWidth, second.mWidth);
	swap(first.mHeight, second.mHeight);
	swap(first.mCells, second.mCells);
}

Spreadsheet& Spreadsheet::operator=(const Spreadsheet& rhs)
{
	// 자신을 대입하는지 확인한다.
	if (this == &rhs) {
		return *this;
	}

	// 복제 후 맞바꾸기(copy-and-swap) 패턴 적용
	Spreadsheet temp(rhs); // 모든 작업을 임시 인스턴스에서 처리한다.
	swap(*this, temp); // 예외를 발생하지 않는 연산으로만 처리한다.
	return *this;
}
```

## 대입, 값 전달 방식 금지 방법
```c++
Spreadsheet(size_t width, size_t height);
Spreadsheet(const Spreadsheet& src) = delete;
~Spreadsheet();

Spreadsheet& operator=(const Spreadsheet& rhs) = delete;
```

## 이동 생성자, 이동 대입 연산자 구현
```c++
#include <iostream>
#include <string>

using namespace std;

void helper(std::string&& message)
{
}

// 좌측값 레퍼런스 매개변수
void handleMessage(std::string& message)
{
	cout << "handleMessage with lvalue reference: " << message << endl;
}

// 우측값 레퍼런스 매개변수
void handleMessage(std::string&& message)
{
	cout << "handleMessage with rvalue reference: " << message << endl;
	helper(std::move(message));
}

int main()
{
	std::string a = "Hello ";
	std::string b = "World";

	// 이름 있는 변수를 처리한다.
	handleMessage(a);             // handleMessage(string& value)를 호출한다.

	// 표현식을 처리한다.
	handleMessage(a + b);         // handleMessage(string&& value)를 호출한다.

	// 리터럴을 처리한다.
	handleMessage("Hello World"); // handleMessage(string&& value)을 호출한다.

	// 이름 있는 변수를 처리하고 우측값 레퍼런스 메서드를 사용하도록 설정한다.
	handleMessage(std::move(b));  // handleMessage(string&& value)를 호출한다.

	return 0;
}
```


이동생성자, 이동대입연산자를 구현 해보면 (by std::swap, std::move)
```c++
// 이동 생성자
Spreadsheet::Spreadsheet(Spreadsheet&& src) noexcept
{
	std::cout << "Move constructor" << std::endl;

	swap(*this, src);
}

// 이동 대입 연산자
Spreadsheet& Spreadsheet::operator=(Spreadsheet&& rhs) noexcept
{
	std::cout << "Move assignment operator" << std::endl;

	Spreadsheet temp(std::move(rhs));
	swap(*this, temp);
	return *this;
}
```



```c++
// 이동 생성자, 이동 대입 연산자가 필요한 이유
Spreadsheet createObject()
{
	return Spreadsheet(3, 2);
}

int main()
{
	std::vector<Spreadsheet> vec;
	for (int i = 0; i < 2; ++i) {
		std::cout << "Iteration " << i << std::endl;
		vec.push_back(Spreadsheet(100, 100));
		std::cout << std::endl;
	}

	Spreadsheet s(2, 3);
	s = createObject();

	Spreadsheet s2(5, 6);
	s2 = s;

	return 0;
}
```

<img src="/assets/img/posts/whyWeUseMove.PNG" width="200" height="400" title='whyWeUse std::move'>