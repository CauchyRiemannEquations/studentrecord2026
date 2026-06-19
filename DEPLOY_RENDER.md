# Render 배포 방법

1. GitHub 저장소에 이 프로젝트를 푸시합니다.
2. [Render](https://render.com)에서 `New +` → `Blueprint`를 선택합니다.
3. GitHub 저장소를 연결합니다.
4. `render.yaml`을 읽어서 웹 서비스를 자동 생성하게 둡니다.
5. 배포가 끝나면 제공된 `onrender.com` 주소로 접속합니다.

확인 포인트:

- 메인 화면: `/`
- 헬스 체크: `/api/health`
- 질문 API: `/api/ask`

참고:

- 이 프로젝트는 GitHub Pages용 정적 사이트가 아니라 Python 서버가 필요한 웹앱입니다.
- 그래서 GitHub Pages에서는 `404` 또는 API 미동작이 나는 것이 정상입니다.
