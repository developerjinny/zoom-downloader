# ⬇ Zoom Downloader

> Zoom 녹화 영상을 터미널 없이 더블클릭 한 번으로 다운로드하는 macOS 앱

![macOS](https://img.shields.io/badge/macOS-10.13+-black?style=flat-square&logo=apple)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

<br>

## 📸 미리보기

브라우저 기반 GUI — 앱을 실행하면 브라우저가 자동으로 열립니다.

```
URL 입력  →  Cookie 입력  →  다운로드 버튼  →  완료!
```

<br>

## ✨ 주요 기능

- 🔗 Zoom 녹화 영상 URL 입력
- 🍪 Cookie 붙여넣기
- 💾 저장 폴더 / 파일명 설정
- 📋 실시간 다운로드 로그
- 🖥 macOS `.app` 더블클릭 실행

<br>

## 🛠 설치 방법

### 1. yt-dlp 설치 (최초 1회)

```bash
brew install yt-dlp
```

### 2. 앱 다운로드

[Releases](https://github.com/developerjinny/zoom-downloader/releases) 페이지에서 `ZoomDownloader_app.zip` 다운로드 후 압축 해제

### 3. 처음 실행 시 보안 허용

macOS 보안 정책으로 인해 처음 한 번은 아래 방법으로 실행하세요:

```
ZoomDownloader.app 우클릭 → 열기 → 열기 버튼 클릭
```

이후부터는 **더블클릭**으로 바로 실행됩니다. ✅

<br>

## 🍪 URL과 Cookie 구하는 방법

1. Zoom 포털에서 녹화 영상 **재생 페이지** 접속
2. `F12` (또는 `Cmd + Option + I`) → **Network** 탭 열기
3. 영상 재생 → `.mp4` 요청 클릭
4. **Request URL** → 앱의 URL 칸에 붙여넣기
5. **Request Headers → cookie** → 앱의 Cookie 칸에 붙여넣기

> ⚠️ 다운로드 URL은 만료 시간이 있으므로 복사 후 빠르게 다운로드하세요.

<br>

## 💻 직접 실행 (터미널)

앱 없이 Python 스크립트로 바로 실행할 수도 있습니다.

```bash
python3 zoom_downloader.py
```

<br>

## 🏗 동작 원리

tkinter 같은 GUI 라이브러리 없이, Python 내장 `http.server`로 로컬 서버를 띄우고 브라우저를 GUI로 활용합니다. 별도 패키지 설치가 필요 없습니다.

```python
# 로컬 서버 시작 + 브라우저 자동 오픈
server = http.server.HTTPServer(('127.0.0.1', 18765), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
webbrowser.open('http://127.0.0.1:18765')
```

<br>

## 📁 파일 구조

```
zoom-downloader/
├── zoom_downloader.py       # 메인 스크립트
├── ZoomDownloader.app/      # macOS 앱 번들
│   └── Contents/
│       ├── Info.plist
│       └── MacOS/
│           ├── ZoomDownloader      # 실행 쉘 스크립트
│           └── zoom_downloader.py
└── README.md
```

<br>

## ⚙️ 요구사항

- macOS 10.13 이상
- Python 3.8 이상
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (`brew install yt-dlp`)

<br>

## 📄 License

MIT © [developerjinny](https://github.com/developerjinny)
