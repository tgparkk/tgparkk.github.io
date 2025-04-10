---
layout: post
title: "C++14와 MFC에서 std::thread를 활용한 파일 다운로드 구현하기"
date: 2025-04-10
categories: windows
tags: [windows, win32, http, thread, async]
excerpt: "윈도우 app에서 비동기 다운로드 기능을 구현하는 시간을 가져 보려고 합니다."
---


# C++14와 MFC에서 std::thread를 활용한 파일 다운로드 구현하기

윈도우 app에서 비동기 다운로드 기능을 구현하는 시간을 가져 보려고 합니다.

## 비동기 다운로드를 위한 준비물

비동기 다운로드 구현을 위해 몇 가지 준비물이 필요합니다.

### 1. 필요한 헤더 파일

```cpp
#include <afxinet.h>  // MFC 인터넷 기능
#include <thread>     // std::thread
#include <functional> // std::function
#include <memory>     // std::shared_ptr
```

### 2. std::thread와 콜백 함수

다운로드 같은 시간이 오래 걸리는 작업은 별도의 스레드에서 실행해야 UI가 멈추지 않습니다. 여기서 `std::thread`가 필요한 이유죠. 작업이 완료된 후 결과를 알려주기 위해서는 콜백 함수도 필요합니다.

```cpp
// 다운로드 결과를 전달하기 위한 콜백 함수 타입 정의
typedef std::function<void(bool success, const CString& errorMsg)> DownloadCallback;
```

### 3. 인터넷 접근 클래스

MFC에서는 `CInternetSession`, `CHttpConnection`, `CHttpFile` 등의 클래스를 통해 HTTP 통신을 할 수 있습니다. 이 클래스들을 사용하면 URL 파싱, HTTP 연결 설정, 데이터 송수신 등의 작업을 쉽게 처리할 수 있죠.

## 핵심 구현

이제 위 세 가지 요소를 조합해서 비동기 다운로드 기능을 구현해봅시다.

### 다운로드 스레드 함수

```cpp
void DownloadThreadFunction(CString strURL, CString strLocalPath, DownloadCallback callback)
{
    BOOL bResult = FALSE;
    CString errorMessage;
    CInternetSession session;
    CHttpConnection* pConnection = NULL;
    CHttpFile* pFile = NULL;
    
    try
    {
        // URL 분석
        DWORD dwServiceType;
        CString strServer, strObject;
        INTERNET_PORT nPort;
        
        if(!AfxParseURL(strURL, dwServiceType, strServer, strObject, nPort))
            throw "잘못된 URL 형식입니다.";
        
        // HTTP 연결 생성
        pConnection = session.GetHttpConnection(strServer, nPort);
        if(!pConnection)
            throw "서버 연결 실패";
        
        // HTTP 요청 생성
        pFile = pConnection->OpenRequest(CHttpConnection::HTTP_VERB_GET, 
            strObject, NULL, 1, NULL, NULL, 
            INTERNET_FLAG_RELOAD | INTERNET_FLAG_DONT_CACHE);
        
        if(!pFile)
            throw "파일 열기 요청 실패";
        
        // 요청 전송
        if(!pFile->SendRequest())
            throw "요청 전송 실패";
        
        // 응답 확인
        DWORD dwStatusCode = 0;
        pFile->QueryInfoStatusCode(dwStatusCode);
        
        if(dwStatusCode != HTTP_STATUS_OK)
            throw "HTTP 오류";
        
        // 로컬 파일 생성
        CFile localFile;
        if(!localFile.Open(strLocalPath, CFile::modeCreate | CFile::modeWrite | CFile::shareDenyWrite))
            throw "로컬 파일을 생성할 수 없습니다.";
        
        // 데이터 다운로드
        BYTE buffer[4096];
        UINT bytesRead = 0;
        
        while((bytesRead = pFile->Read(buffer, sizeof(buffer))) > 0)
        {
            localFile.Write(buffer, bytesRead);
        }
        
        localFile.Close();
        bResult = TRUE;
    }
    catch(LPCTSTR lpszError)
    {
        errorMessage = lpszError;
    }
    catch(CInternetException* pEx)
    {
        pEx->Delete();
    }
    
    // 리소스 정리
    if(pFile) {
        pFile->Close();
        delete pFile;
    }
    
    if(pConnection) {
        pConnection->Close();
        delete pConnection;
    }
    
    session.Close();
    
    // 콜백 함수를 통해 결과 전달
    if (callback) {
        callback(bResult == TRUE, errorMessage);
    }
}
```

이 함수가 별도의 스레드에서 실행될 메인 다운로드 함수입니다. MFC의 인터넷 클래스를 사용해 HTTP 요청을 보내고 응답을 받아 파일로 저장하는 작업을 수행합니다. 작업이 완료되면 콜백 함수를 통해 결과를 알려줍니다.

### 스레드 생성 함수

```cpp
std::shared_ptr<std::thread> DownLoadMlas(CString strURL, CString strLocalPath, DownloadCallback callback = nullptr)
{
    return std::make_shared<std::thread>(
        DownloadThreadFunction, strURL, strLocalPath, callback);
}
```

이 함수는 `std::thread`를 생성하고 스마트 포인터로 관리합니다. 이렇게 하면 메모리 누수 걱정 없이 스레드 객체를 안전하게 관리할 수 있죠.

## MFC 대화상자에서 활용하기

이제 위에서 만든 함수들을 MFC 대화상자에서 어떻게 활용하는지 살펴봅시다.

### 멤버 변수와 메시지 맵

```cpp
// 헤더 파일
private:
    std::shared_ptr<std::thread> m_pDownloadThread;
    afx_msg LRESULT OnDownloadComplete(WPARAM wParam, LPARAM lParam);
    
// 메시지 맵
BEGIN_MESSAGE_MAP(CYourDlg, CDialogEx)
    ON_MESSAGE(WM_USER + 100, OnDownloadComplete)
END_MESSAGE_MAP()
```

### 다운로드 시작 함수

```cpp
void CYourDlg::OnBnClickedButtonDownload(const CString& strURL, const CString& strLocalPath)
{
    // 다운로드 시작 - 람다 함수를 콜백으로 사용
    m_pDownloadThread = DownLoadMlas(strURL, strLocalPath, 
        [this](bool success, const CString& errorMsg) {
            // 스레드 간 안전한 통신을 위해 PostMessage 사용
            this->PostMessage(WM_USER + 100, success ? 1 : 0, (LPARAM)new CString(errorMsg));
        });
    
    // UI 업데이트
    SetDlgItemText(IDC_STATIC_STATUS, _T("다운로드가 시작되었습니다..."));
    GetDlgItem(IDC_PROGRESS_DOWNLOAD)->ShowWindow(SW_SHOW);
}
```

여기서는 람다 함수를 콜백으로 전달해 다운로드 결과를 받아옵니다. 다운로드 스레드에서 UI 스레드로 안전하게 메시지를 전달하기 위해 `PostMessage`를 사용했습니다.

### 다운로드 완료 처리

```cpp
LRESULT CYourDlg::OnDownloadComplete(WPARAM wParam, LPARAM lParam)
{
    BOOL bSuccess = (BOOL)wParam;
    CString* pErrorMsg = (CString*)lParam;
    
    if(bSuccess) {
        AfxMessageBox(_T("다운로드 성공!"));
    } else {
        AfxMessageBox(_T("다운로드 실패: ") + *pErrorMsg);
    }
    
    // CString 객체 정리
    delete pErrorMsg;
    
    // 스레드 종료 대기
    if(m_pDownloadThread && m_pDownloadThread->joinable()) {
        m_pDownloadThread->join();
        m_pDownloadThread.reset();
    }
    
    // UI 업데이트
    SetDlgItemText(IDC_STATIC_STATUS, _T("다운로드 완료"));
    GetDlgItem(IDC_PROGRESS_DOWNLOAD)->ShowWindow(SW_HIDE);
    
    return 0;
}
```

### 리소스 정리

```cpp
void CYourDlg::OnDestroy()
{
    CDialogEx::OnDestroy();
    
    // 다운로드 스레드 정리
    if(m_pDownloadThread && m_pDownloadThread->joinable()) {
        m_pDownloadThread->join();
    }
}
```

## 마무리

이렇게 std::thread와 MFC의 인터넷 클래스, 그리고 콜백 함수를 조합해서 윈도우 앱에서 비동기 다운로드 기능을 구현해봤습니다. 핵심은 다음과 같이 요약할 수 있겠네요:

1. std::thread로 별도 스레드에서 다운로드 작업 실행
2. CInternetSession, CHttpConnection, CHttpFile로 HTTP 통신 처리
3. 콜백 함수와 PostMessage로 스레드 간 안전한 통신
4. std::shared_ptr로 스레드 객체의 수명 관리

이 구현을 기반으로 필요에 따라 진행 상황 표시, 다운로드 취소 기능 등을 추가해볼 수 있을 것 같습니다.