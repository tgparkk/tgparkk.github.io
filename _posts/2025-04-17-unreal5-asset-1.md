---
layout: post
title: "언리얼 엔진 5.4: 에셋 기본 개념과 활용법"
date: 2025-04-17
categories: gamedev
tags: [gamedev, unreal, asset, 게임개발, 언리얼, 에셋]
excerpt: "에셋 기본 개념과 활용법."
comments: true
---

## 1. 언리얼 엔진에서 에셋(Asset)이란?

에셋은 게임이나 애플리케이션을 구성하는 모든 요소를 의미합니다. 주요 에셋 종류는 다음과 같습니다:

- **스태틱 메시**: 움직이지 않는 3D 모델 (건물, 가구 등)
- **스켈레탈 메시**: 애니메이션이 적용될 수 있는 3D 모델 (캐릭터 등)
- **텍스처**: 모델 표면에 적용되는 이미지
- **머티리얼**: 표면의 시각적 특성을 정의 (색상, 반사, 거칠기 등)
- **사운드**: 음향 파일
- **블루프린트**: 비주얼 스크립팅으로 만든 게임 로직
- **입자 시스템**: 불, 연기, 먼지 등의 효과
- **레벨**: 게임의 특정 영역이나 맵

## 2. 콘텐츠 브라우저

언리얼 엔진에서는 '콘텐츠 브라우저'를 통해 에셋을 관리합니다. 주요 기능은 다음과 같습니다:

- 에셋 찾기 및 필터링
- 폴더 관리
- 에셋 가져오기(Import)
- 새 에셋 생성

## 3. 에셋 인스턴싱

하나의 에셋을 여러 번 사용할 때 적용되는 개념으로, 주요 장점은:

- **메모리 절약**: 동일한 에셋을 여러 번 사용해도 메모리에는 한 번만 로드
- **일관성 유지**: 원본 에셋 수정 시 모든 인스턴스에 변경사항 반영

## 4. 머티리얼 적용

3D 모델에 머티리얼을 적용하여 시각적 표현을 향상시킬 수 있습니다. 기본 코드 예시:

```cpp
// 기본 머티리얼 생성 C++ 코드 예시
UMaterial* CreateBasicMaterial()
{
    UMaterial* NewMaterial = NewObject<UMaterial>();
    NewMaterial->BaseColor = FColor::Red;
    NewMaterial->Metallic = 0.0f;
    NewMaterial->Roughness = 0.5f;
    return NewMaterial;
}
```

## 5. 에셋 최적화 기본 원칙

- **LOD(Level of Detail)**: 거리에 따라 모델의 디테일 조절
- **텍스처 크기 관리**: 필요 이상의 큰 텍스처 피하기
- **인스턴싱 활용**: 동일한 오브젝트는 인스턴싱으로 효율적 렌더링
- **드로우 콜 최소화**: 비슷한 머티리얼끼리 묶기

## 6. 블루프린트로 에셋 제어

블루프린트를 사용하여 게임 내에서 에셋을 동적으로 제어할 수 있습니다. C++ 코드로 에셋 동적 로드 예시:

```cpp
// 런타임에 에셋 동적 로드 예시
UStaticMesh* LoadMeshAtRuntime(FString MeshPath)
{
    return Cast<UStaticMesh>(StaticLoadObject(UStaticMesh::StaticClass(), nullptr, *MeshPath));
}

// 에셋 다이나믹 로드 및 적용
void ApplyMeshToComponent(UStaticMeshComponent* Component, FString MeshPath)
{
    UStaticMesh* NewMesh = LoadMeshAtRuntime(MeshPath);
    if (NewMesh)
    {
        Component->SetStaticMesh(NewMesh);
    }
}
```

## 7. 에셋 참조 이해하기

에셋 참조는 에셋이 다른 에셋에 의존하는 관계를 말합니다. 관리 방법으로는:

- **레퍼런스 뷰어**: 특정 에셋의 참조 관계를 시각적으로 확인
- **리디렉터**: 에셋 경로 변경 시 참조를 유지하는 도우미 객체

---