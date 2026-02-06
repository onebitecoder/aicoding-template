# Design Reference Guide

이 폴더에 디자인 레퍼런스 이미지를 넣어주세요.
Claude Code가 이미지를 분석하여 UI 스타일을 적용합니다.

## 파일 구조

```
design/
├── reference.png    # 레퍼런스 이미지
└── README.md        # 이 파일
```

## 사용 방법

1. `design/reference.png`에 레퍼런스 이미지 배치
2. Claude Code에게 "프로젝트 생성해줘" 또는 "UI 만들어줘" 요청
3. Claude Code가 자동으로 이미지를 분석하여 스타일 적용

## 좋은 레퍼런스 예시

- Dribbble, Behance에서 찾은 UI 디자인
- 참고하고 싶은 웹사이트 스크린샷
- Figma/Sketch 디자인 Export
- 직접 그린 와이어프레임

## 지원 파일 형식

- PNG (권장)
- JPG / JPEG
- WebP

## 이미지가 없는 경우

이미지가 없으면 Claude Code가 다음과 같이 질문합니다:

```
"design/reference.png 레퍼런스 이미지가 없습니다.
어떤 스타일로 디자인할까요?
1. 깔끔한 미니멀 스타일
2. 모바일 앱 스타일 (인스타그램, 토스)
3. 기본 TailwindCSS 스타일
4. 직접 설명해주세요"
```
