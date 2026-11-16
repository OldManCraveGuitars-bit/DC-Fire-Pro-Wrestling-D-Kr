# 패처 소스 실행·빌드

Windows x64, Python 3.13, PyInstaller 6.22.3으로 배포 EXE를 만들었습니다.
릴리스의 `FireProD-Kr-v0.901-Source-and-Payload.zip`을 새 폴더에 풀면 아래 파일이 함께 있습니다.

- `src/patcher.py`: GUI/CLI 패처 전체 소스
- `tools/build_patcher.py`, `packaging/version-info.txt`: EXE 빌드 설정
- `payload/`: 검증 매니페스트, 트랙 03·50의 차이 패치, 추출/적용 도구와 라이선스

Git 저장소만 복제했다면 같은 ZIP의 `payload` 폴더를 저장소 루트에 놓으세요.

```powershell
python -m pip install PyInstaller==6.22.3
python tools/build_patcher.py
```

결과는 `dist/FireProD-Kr-v0.901-Patcher.exe`입니다. 빌드 환경과 시간에 따라 EXE 자체 해시는 달라질 수 있습니다.
배포된 EXE의 해시는 릴리스의 `SHA256SUMS.txt`로 대조하세요. 같은 페이로드를 적용한 GDI/트랙은 고정 해시로 검사합니다.

소스로 실행할 때는 `python src/patcher.py`를 사용합니다. 자체 검사는 `python src/patcher.py --self-test`입니다.
CLI는 `--source 원본.chd --output 새폴더 --report 새보고서.json`을 지원하며 기존 출력/보고서 파일을 덮어쓰지 않습니다.

동봉 chdman 0.264에 대응하는 MAME 전체 소스는 같은 릴리스의 `MAME-0.264-source.tar.gz`입니다.
외부 도구 고지와 라이선스 전문은 `THIRD_PARTY_NOTICES.md`, `docs/licenses` 및 `payload/licenses`에서 확인하세요.
