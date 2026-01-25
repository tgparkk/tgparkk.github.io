---
layout: post
title: "C++ 메모리에서 비밀번호가 유출되는 과정과 방어법 - WinDbg 실습"
date: 2026-01-24
categories: security
tags: [C++, security, WinDbg, memory, password, 보안, 메모리덤프]
excerpt: "메모리 덤프에서 평문 비밀번호가 노출되는 취약점을 직접 확인하고, 이를 방어하는 C++ 코드를 구현합니다."
comments: true
---

# C++ 메모리에서 비밀번호가 유출되는 과정과 방어법

프로그램이 실행 중일 때, 메모리에는 우리가 다루는 모든 데이터가 저장됩니다. 문제는 **비밀번호도 예외가 아니라는 것**입니다. 이 글에서는 실제로 메모리 덤프를 통해 비밀번호가 어떻게 노출되는지 확인하고, 이를 방어하는 방법을 알아봅니다.

---

## 1. 왜 메모리 덤프가 위험한가?

메모리 덤프는 프로세스의 메모리 상태를 파일로 저장한 것입니다. 주로 디버깅 목적으로 사용되지만, 악의적인 공격자가 이를 악용할 수 있습니다:

- **악성코드**: 실행 중인 프로세스의 메모리를 읽어감
- **크래시 덤프 유출**: 오류 보고 시스템을 통해 덤프 파일이 외부로 전송
- **물리적 접근**: 공유 PC나 서버에서 덤프 파일 생성 가능

---

## 2. 취약한 코드 예시

먼저 일반적으로 작성하는 **취약한 코드**를 살펴봅니다.

```cpp
// vulnerable_login.cpp
#include <iostream>
#include <string>
#include <Windows.h>

class LoginManager {
private:
    std::string m_username;
    std::string m_password;  // 취약점: 평문 비밀번호 저장

public:
    void setCredentials(const std::string& username, const std::string& password) {
        m_username = username;
        m_password = password;
    }

    bool authenticate() {
        // 실제로는 서버 인증 등을 수행
        // 여기서는 간단히 하드코딩된 값과 비교
        return (m_username == "admin" && m_password == "MySecretP@ss123");
    }

    void clearCredentials() {
        m_username.clear();
        m_password.clear();
        // 문제: clear()는 메모리를 실제로 지우지 않음!
    }
};

int main() {
    LoginManager login;
    
    std::string username, password;
    
    std::cout << "=== 로그인 시스템 (취약한 버전) ===" << std::endl;
    std::cout << "Username: ";
    std::cin >> username;
    std::cout << "Password: ";
    std::cin >> password;
    
    login.setCredentials(username, password);
    
    if (login.authenticate()) {
        std::cout << "로그인 성공!" << std::endl;
    } else {
        std::cout << "로그인 실패!" << std::endl;
    }
    
    login.clearCredentials();
    
    std::cout << "\n[덤프 분석을 위해 대기 중... 작업 관리자에서 덤프를 생성하세요]" << std::endl;
    std::cout << "아무 키나 누르면 종료합니다." << std::endl;
    std::cin.get();
    std::cin.get();
    
    return 0;
}
```

이 코드의 문제점:
- `std::string`은 내부적으로 힙 메모리를 사용하며, `clear()` 호출 시 메모리를 0으로 덮어쓰지 않음
- 비밀번호가 메모리에 평문으로 남아있음

---

## 3. 메모리 덤프에서 비밀번호 찾기

### 3.1 덤프 파일 생성

1. 위 프로그램을 컴파일하고 실행
2. 비밀번호 입력 (예: `MySecretP@ss123`)
3. **작업 관리자** 열기 (Ctrl + Shift + Esc)
4. **세부 정보** 탭에서 해당 프로세스 찾기
5. 우클릭 → **덤프 파일 만들기**

![작업 관리자 덤프 생성](/assets/images/task-manager-dump.png)

덤프 파일은 `C:\Users\{사용자}\AppData\Local\Temp` 폴더에 저장됩니다.

### 3.2 WinDbg로 분석

1. **WinDbg** 실행 (Windows SDK에 포함, 또는 Microsoft Store에서 "WinDbg Preview" 설치)
2. File → Open Crash Dump → 덤프 파일 선택

![WinDbg 덤프 파일 열기](/assets/images/windbg-open-dump.png)
*WinDbg에서 File → Open Crash Dump로 덤프 파일을 엽니다*

3. 심볼 경로 설정 (선택사항, 더 자세한 분석을 위해):

```
.sympath srv*c:\symbols*https://msdl.microsoft.com/download/symbols
.reload
```

#### WinDbg 기본 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `lm` | 로드된 모듈 목록 | `lm` |
| `db` | 메모리를 바이트로 표시 | `db 0x00401000 L100` |
| `dc` | 메모리를 DWORD + ASCII로 표시 | `dc 0x00401000 L40` |
| `da` | ASCII 문자열로 표시 | `da 0x00401000` |
| `du` | 유니코드 문자열로 표시 | `du 0x00401000` |
| `s` | 메모리 검색 | `s -a 0 L?80000000 "password"` |

#### 문자열 검색 명령어 상세

```
// 기본 문법
s -[타입] [시작주소] L?[길이] "[검색어]"

// ASCII 문자열 검색 (전체 메모리)
s -a 0 L?80000000 "MySecretP@ss123"

// 유니코드 문자열 검색
s -u 0 L?80000000 "MySecretP@ss123"

// 바이트 패턴 검색 (16진수)
s -b 0 L?80000000 4d 79 53 65 63 72 65 74

// 대소문자 무시 검색 (ASCII)
s -[1]a 0 L?80000000 "mysecretp@ss123"
```

#### 메모리 상세 분석 명령어

```
// 특정 주소의 메모리 내용 보기 (128바이트)
db 00000201`a3c45a20 L80

// 해당 주소 주변 컨텍스트 보기 (앞뒤로 확장)
db 00000201`a3c45a00 L100

// DWORD 단위로 보기 (구조체 분석에 유용)
dd 00000201`a3c45a20 L20

// 포인터 크기 단위로 보기 (64비트)
dq 00000201`a3c45a20 L10
```

#### 힙 메모리 분석 (std::string이 사용하는 영역)

```
// 힙 요약 정보
!heap -s

// 특정 힙의 상세 정보
!heap -h 0

// 힙에서 할당된 블록 검색
!heap -srch "MySecret"

// 메모리 할당 정보 (주소가 어느 힙에 속하는지)
!address 00000201`a3c45a20
```

#### 스택 분석 (함수 호출 흐름 확인)

```
// 현재 스레드의 콜스택
k

// 모든 스레드의 콜스택
~*k

// 스택 프레임의 로컬 변수 (심볼 필요)
dv

// 특정 스레드로 전환
~0s
```

#### 실용적인 검색 시나리오

```
// 1. 먼저 어떤 문자열이든 검색
s -a 0 L?80000000 "password"
s -a 0 L?80000000 "secret"
s -a 0 L?80000000 "key"
s -a 0 L?80000000 "token"

// 2. 발견된 주소 주변 메모리 확인
db [발견된주소] L100

// 3. 해당 메모리가 어디에 속하는지 확인
!address [발견된주소]

// 4. 힙 블록이면 할당 크기 확인
!heap -p -a [발견된주소]
```

#### WinDbg 팁

- **`L?`**: 검색 범위를 크게 지정할 때 사용 (`L80000000`은 에러, `L?80000000`은 OK)
- **주소 형식**: 64비트에서는 백틱(`) 사용 (예: `00000201`a3c45a20`)
- **Ctrl+Break**: 오래 걸리는 검색 중단
- **`.cls`**: 화면 지우기

### 3.3 결과 확인

문자열 검색 명령어를 실행하면 비밀번호가 메모리에서 발견됩니다:

```
0:000> s -a 0 L?80000000 "MySecretP@ss123"
00000201`a3c45a20  4d 79 53 65 63 72 65 74-50 40 73 73 31 32 33 00  MySecretP@ss123.
00000201`a3c48b40  4d 79 53 65 63 72 65 74-50 40 73 73 31 32 33 00  MySecretP@ss123.
```

![WinDbg 비밀번호 검색 결과](/assets/images/windbg-search-found.png)
*s -a 명령어로 메모리에서 비밀번호가 발견된 화면*

발견된 주소의 메모리를 상세히 확인해봅니다:

```
0:000> db 00000201`a3c45a20 L80
00000201`a3c45a20  4d 79 53 65 63 72 65 74-50 40 73 73 31 32 33 00  MySecretP@ss123.
00000201`a3c45a30  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
...
```

![WinDbg 메모리 상세 보기](/assets/images/windbg-memory-view.png)
*db 명령어로 해당 주소의 메모리 내용을 확인*

**비밀번호가 메모리에 평문으로 남아있습니다!** `clear()`를 호출했음에도 불구하고 말이죠.

---

## 4. 해결책 구현

### 4.1 SecureZeroMemory를 사용한 메모리 제로화

Windows API의 `SecureZeroMemory`는 컴파일러 최적화에 의해 제거되지 않고 확실하게 메모리를 0으로 덮어씁니다.

```cpp
// secure_string.h
#pragma once
#include <Windows.h>
#include <string>
#include <vector>

class SecureString {
private:
    std::vector<char> m_data;

public:
    SecureString() = default;
    
    explicit SecureString(const std::string& str) {
        m_data.assign(str.begin(), str.end());
        m_data.push_back('\0');
    }
    
    ~SecureString() {
        clear();
    }
    
    // 복사 방지
    SecureString(const SecureString&) = delete;
    SecureString& operator=(const SecureString&) = delete;
    
    // 이동은 허용
    SecureString(SecureString&& other) noexcept {
        m_data = std::move(other.m_data);
    }
    
    SecureString& operator=(SecureString&& other) noexcept {
        if (this != &other) {
            clear();
            m_data = std::move(other.m_data);
        }
        return *this;
    }
    
    void assign(const std::string& str) {
        clear();
        m_data.assign(str.begin(), str.end());
        m_data.push_back('\0');
    }
    
    void clear() {
        if (!m_data.empty()) {
            // 핵심: SecureZeroMemory로 확실하게 메모리 제로화
            SecureZeroMemory(m_data.data(), m_data.size());
            m_data.clear();
            m_data.shrink_to_fit();  // 메모리 해제
        }
    }
    
    const char* c_str() const {
        return m_data.empty() ? "" : m_data.data();
    }
    
    size_t size() const {
        return m_data.empty() ? 0 : m_data.size() - 1;
    }
    
    bool empty() const {
        return m_data.empty() || m_data.size() <= 1;
    }
    
    bool operator==(const std::string& other) const {
        if (empty() && other.empty()) return true;
        if (size() != other.size()) return false;
        
        // 타이밍 공격 방지를 위한 상수 시간 비교
        volatile int result = 0;
        for (size_t i = 0; i < size(); ++i) {
            result |= m_data[i] ^ other[i];
        }
        return result == 0;
    }
};
```

### 4.2 Windows DPAPI를 사용한 암호화

더 강력한 보호가 필요하다면 **DPAPI(Data Protection API)**를 사용하여 메모리에 암호화된 상태로 저장할 수 있습니다.

```cpp
// encrypted_string.h
#pragma once
#include <Windows.h>
#include <wincrypt.h>
#include <vector>
#include <string>
#include <stdexcept>

#pragma comment(lib, "crypt32.lib")

class EncryptedString {
private:
    std::vector<BYTE> m_encryptedData;
    
public:
    EncryptedString() = default;
    
    explicit EncryptedString(const std::string& plainText) {
        encrypt(plainText);
    }
    
    ~EncryptedString() {
        clear();
    }
    
    void encrypt(const std::string& plainText) {
        clear();
        
        DATA_BLOB inputBlob;
        DATA_BLOB outputBlob;
        
        inputBlob.pbData = reinterpret_cast<BYTE*>(const_cast<char*>(plainText.data()));
        inputBlob.cbData = static_cast<DWORD>(plainText.size() + 1);
        
        // DPAPI로 암호화 (현재 사용자 컨텍스트)
        if (!CryptProtectData(
                &inputBlob,
                L"Password",      // 설명 (선택)
                nullptr,          // 추가 엔트로피 (선택)
                nullptr,          // 예약됨
                nullptr,          // 프롬프트 구조체
                CRYPTPROTECT_LOCAL_MACHINE,  // 플래그
                &outputBlob)) {
            throw std::runtime_error("암호화 실패");
        }
        
        m_encryptedData.assign(outputBlob.pbData, 
                               outputBlob.pbData + outputBlob.cbData);
        
        // 할당된 메모리 해제
        LocalFree(outputBlob.pbData);
    }
    
    std::string decrypt() const {
        if (m_encryptedData.empty()) {
            return "";
        }
        
        DATA_BLOB inputBlob;
        DATA_BLOB outputBlob;
        
        inputBlob.pbData = const_cast<BYTE*>(m_encryptedData.data());
        inputBlob.cbData = static_cast<DWORD>(m_encryptedData.size());
        
        if (!CryptUnprotectData(
                &inputBlob,
                nullptr,          // 설명
                nullptr,          // 추가 엔트로피
                nullptr,          // 예약됨
                nullptr,          // 프롬프트 구조체
                0,                // 플래그
                &outputBlob)) {
            throw std::runtime_error("복호화 실패");
        }
        
        std::string result(reinterpret_cast<char*>(outputBlob.pbData));
        
        // 복호화된 데이터 즉시 제로화 후 해제
        SecureZeroMemory(outputBlob.pbData, outputBlob.cbData);
        LocalFree(outputBlob.pbData);
        
        return result;
    }
    
    void clear() {
        if (!m_encryptedData.empty()) {
            SecureZeroMemory(m_encryptedData.data(), m_encryptedData.size());
            m_encryptedData.clear();
            m_encryptedData.shrink_to_fit();
        }
    }
    
    bool empty() const {
        return m_encryptedData.empty();
    }
};
```

### 4.3 개선된 로그인 시스템

```cpp
// secure_login.cpp
#include <iostream>
#include <string>
#include <Windows.h>
#include "secure_string.h"
#include "encrypted_string.h"

class SecureLoginManager {
private:
    SecureString m_username;
    EncryptedString m_password;  // 암호화된 상태로 저장

public:
    void setCredentials(const std::string& username, const std::string& password) {
        m_username.assign(username);
        m_password.encrypt(password);
        
        // 원본 문자열은 호출자가 정리해야 함
    }
    
    bool authenticate() {
        // 복호화는 비교 직전에만 수행
        std::string decryptedPassword = m_password.decrypt();
        
        bool result = (m_username == "admin" && decryptedPassword == "MySecretP@ss123");
        
        // 사용 후 즉시 제로화
        SecureZeroMemory(decryptedPassword.data(), decryptedPassword.size());
        
        return result;
    }
    
    void clearCredentials() {
        m_username.clear();
        m_password.clear();
    }
};

// 안전한 입력 함수
SecureString secureGetPassword() {
    std::string input;
    
    // 콘솔에서 에코 없이 입력받기
    HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
    DWORD mode;
    GetConsoleMode(hStdin, &mode);
    SetConsoleMode(hStdin, mode & ~ENABLE_ECHO_INPUT);
    
    std::getline(std::cin, input);
    
    SetConsoleMode(hStdin, mode);
    std::cout << std::endl;
    
    SecureString result(input);
    
    // 입력 버퍼 제로화
    SecureZeroMemory(input.data(), input.size());
    
    return result;
}

int main() {
    SecureLoginManager login;
    
    std::cout << "=== 로그인 시스템 (보안 버전) ===" << std::endl;
    
    std::string username;
    std::cout << "Username: ";
    std::cin >> username;
    std::cin.ignore();
    
    std::cout << "Password: ";
    SecureString password = secureGetPassword();
    
    // 임시 std::string 생성 후 즉시 제로화
    std::string tempPassword(password.c_str());
    login.setCredentials(username, tempPassword);
    SecureZeroMemory(tempPassword.data(), tempPassword.size());
    
    // username도 제로화
    SecureZeroMemory(username.data(), username.size());
    
    if (login.authenticate()) {
        std::cout << "로그인 성공!" << std::endl;
    } else {
        std::cout << "로그인 실패!" << std::endl;
    }
    
    login.clearCredentials();
    
    std::cout << "\n[덤프 분석을 위해 대기 중...]" << std::endl;
    std::cout << "아무 키나 누르면 종료합니다." << std::endl;
    std::cin.get();
    
    return 0;
}
```

### 4.4 수동 메모리 제로화 (SecureZeroMemory 대안)

`SecureZeroMemory`가 예상대로 동작하지 않거나, 크로스 플랫폼 환경에서 사용할 수 없는 경우를 대비한 수동 제로화 방법입니다.

#### 왜 일반 memset은 안 되는가?

```cpp
// 위험! 컴파일러가 최적화로 제거할 수 있음
memset(password, 0, length);
```

컴파일러는 "이 메모리는 이후에 사용되지 않으니 굳이 0으로 채울 필요 없다"고 판단하여 이 코드를 제거할 수 있습니다.

#### 방법 1: volatile 포인터 사용

`volatile` 키워드는 컴파일러에게 "이 메모리 접근을 최적화하지 마라"고 지시합니다.

```cpp
void secureZeroManual(void* ptr, size_t size) {
    volatile unsigned char* p = static_cast<volatile unsigned char*>(ptr);
    while (size--) {
        *p++ = 0;
    }
}
```

#### 방법 2: 다중 패턴 덮어쓰기

더 확실한 제거를 위해 여러 패턴으로 덮어씁니다. 일부 포렌식 도구는 단순 제로화 후에도 이전 값을 복구할 수 있다는 이론이 있습니다.

```cpp
void secureZeroMultiPass(void* ptr, size_t size) {
    volatile unsigned char* p = static_cast<volatile unsigned char*>(ptr);
    
    // 1단계: 0xFF로 덮어쓰기
    for (size_t i = 0; i < size; ++i) {
        p[i] = 0xFF;
    }
    
    // 2단계: 0x00으로 덮어쓰기
    for (size_t i = 0; i < size; ++i) {
        p[i] = 0x00;
    }
    
    // 3단계: 랜덤 값으로 덮어쓰기
    for (size_t i = 0; i < size; ++i) {
        p[i] = static_cast<unsigned char>(rand() % 256);
    }
    
    // 4단계: 최종 0x00으로 덮어쓰기
    for (size_t i = 0; i < size; ++i) {
        p[i] = 0x00;
    }
}
```

#### 방법 3: C11 memset_s (권장)

C11 표준에서 추가된 `memset_s`는 컴파일러 최적화에 의해 제거되지 않도록 보장됩니다.

```cpp
#define __STDC_WANT_LIB_EXT1__ 1
#include <string.h>

void secureZeroC11(void* ptr, size_t size) {
    // memset_s는 절대 최적화로 제거되지 않음
    memset_s(ptr, size, 0, size);
}
```

> **주의**: MSVC에서는 `memset_s` 지원이 제한적일 수 있습니다. Windows에서는 `SecureZeroMemory`가 더 안정적입니다.

#### 방법 4: 통합 유틸리티 클래스

위 방법들을 통합한 크로스 플랫폼 유틸리티:

```cpp
// secure_memory.h
#pragma once
#include <cstddef>
#include <cstdlib>

#ifdef _WIN32
    #include <Windows.h>
    #define SECURE_ZERO(ptr, size) SecureZeroMemory(ptr, size)
#else
    // Linux/macOS: explicit_bzero 사용 (glibc 2.25+)
    #include <string.h>
    #ifdef __GLIBC__
        #define SECURE_ZERO(ptr, size) explicit_bzero(ptr, size)
    #else
        // fallback: volatile 수동 제로화
        inline void manual_secure_zero(void* ptr, size_t size) {
            volatile unsigned char* p = static_cast<volatile unsigned char*>(ptr);
            while (size--) *p++ = 0;
        }
        #define SECURE_ZERO(ptr, size) manual_secure_zero(ptr, size)
    #endif
#endif

// 다중 패턴 덮어쓰기 (paranoid 모드)
inline void secureZeroParanoid(void* ptr, size_t size) {
    volatile unsigned char* p = static_cast<volatile unsigned char*>(ptr);
    
    // Pass 1: 0xFF
    for (size_t i = 0; i < size; ++i) p[i] = 0xFF;
    
    // Pass 2: 0xAA
    for (size_t i = 0; i < size; ++i) p[i] = 0xAA;
    
    // Pass 3: 0x55
    for (size_t i = 0; i < size; ++i) p[i] = 0x55;
    
    // Pass 4: 0x00
    for (size_t i = 0; i < size; ++i) p[i] = 0x00;
    
    // 최종: 플랫폼별 보안 제로화
    SECURE_ZERO(const_cast<unsigned char*>(p), size);
}
```

#### 사용 예시

```cpp
#include "secure_memory.h"
#include <string>

int main() {
    std::string password = "MySecretP@ss123";
    
    // ... 비밀번호 사용 ...
    
    // 일반 제로화
    SECURE_ZERO(password.data(), password.size());
    
    // 또는 더 확실한 다중 패턴 제로화
    // secureZeroParanoid(password.data(), password.size());
    
    password.clear();
    
    return 0;
}
```

#### 검증: 어셈블리 확인

컴파일러가 제로화 코드를 제거하지 않았는지 확인하려면:

```bash
# MSVC
cl /FA secure_test.cpp
# 생성된 .asm 파일에서 제로화 루프 확인

# GCC/Clang
g++ -S -O2 secure_test.cpp
# 생성된 .s 파일에서 제로화 루프 확인
```

---

## 5. 개선된 코드 검증

보안 버전(SecureString, EncryptedString 사용)으로 다시 덤프를 생성하고 WinDbg에서 검색해봅니다:

```
0:000> s -a 0 L?80000000 "MySecretP@ss123"
0:000> 
```

![WinDbg 검색 결과 없음](/assets/images/windbg-search-empty.png)
*보안 버전에서는 동일한 검색 명령어에 결과가 나오지 않습니다*

**결과: 검색 결과 없음!**

비밀번호가 메모리에서 제대로 제거되었습니다. 이것이 바로 `SecureZeroMemory`와 DPAPI 암호화의 효과입니다.

---

## 6. 정리하면서

### 뭘 바꾸면 되나요?

| 이렇게 하면 위험 | 이렇게 바꾸세요 |
|-----------------|----------------|
| `std::string password` | `SecureString` 또는 `EncryptedString` |
| `password.clear()` | `SecureZeroMemory()` |

### 실수하기 쉬운 부분

- **"나중에 지우면 되지"** → 비밀번호는 쓰자마자 바로 지워야 합니다. 나중은 없어요.
- **복사 남발** → `std::string`을 여기저기 넘기면 메모리 곳곳에 흔적이 남습니다.
- **디버그 빌드** → Release에서만 테스트하고 끝내면 안 됩니다. 디버그 빌드는 최적화가 안 되어서 더 많이 노출돼요.
- **스왑 파일** → 메모리가 부족하면 OS가 RAM 내용을 디스크에 씁니다. `VirtualLock()`으로 막을 수 있어요.

---

## 마무리

사실 이 글은 보안팀에서 요청이 들어오면서 시작됐습니다.

"프로그램 메모리에서 민감정보가 평문으로 노출되는지 점검해달라"는 요청이었는데, 막상 덤프를 떠서 WinDbg로 열어보니까 진짜 보이더라고요. `clear()` 호출했는데도요.

그때부터 수정 작업이 시작됐고, 이왕 삽질한 거 정리해서 글로 남겨두면 좋겠다 싶었습니다.

혹시 비슷한 요청을 받으셨다면, 이 글이 조금이나마 도움이 됐으면 합니다.
