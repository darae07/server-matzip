# 오늘 뭐 먹지?
## 프로젝트 소개

> 직장인들의 점심 메뉴 선정 시 간편하게 커뮤니케이션 할 수 있도록 돕는 서비스 **'오늘 뭐 먹지?'** 의 서버 레포지토리 입니다.

- 유저는 맛집 이름으로 메뉴를 제안할 수 있습니다. 메뉴 제안은 매일 12시에 초기화 됩니다.
- 오늘의 메뉴 기능은 모든 팀 구성원에게 맛집을 제안할 수 있도록 합니다.
- 크루 기능은 소규모 그룹을 이룰수 있도록 하며, 여기에 맛집을 제안하면 크루원들이 투표할 수 있습니다.
- 맛집은 팀의 리뷰 정보를 가집니다. 옵션을 선택하면 카카오맵 연결 링크를 제공합니다.
- 팀을 만들고 가입할 수 있습니다. 팀 생성시 발급되는 입장 코드를 통해 팀에 가입할 수 있습니다.
- 초대가 발생하면 유저는 프로필메뉴에서 알림을 받습니다.
  
![instruction](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbyHpXZ%2FbtrMDXW84ap%2FAlAoBRBCge6DUFQLiZb4kk%2Fimg.jpg)

## 서비스 링크

https://eatwhat.kr

## 프로젝트 상세 소개

https://dahna.tistory.com/7

## 프로젝트 실행

서버 구동:

```bash
(m1 mac) arch -x86_64 zsh (터미널 설정 변경)
python manage.py runserver
```

[http://localhost:8000](http://localhost:8000) 에서 구동 결과 확인  
어드민: [http://localhost:8000/admin](http://localhost:8000/admin)  
-- env 파일 필요

**GDAL 설치 필요할수 있음. (requirements에 포함되지 않도록 주의)**

## 기술 스택

<img width="481" alt="스크린샷 2022-06-27 오후 2 40 40" src="https://user-images.githubusercontent.com/61297852/175867585-d79e9e03-0273-4b29-82b9-0f0e3545d99f.png">

## DB 스키마
![스키마](https://user-images.githubusercontent.com/61297852/175874968-8fc8baff-046e-4698-93a5-dd55cdfe5eab.jpeg)


## 배포 환경

server& DB - Heroku 배포  
image - Cloudinary  

## 개발자 계정 설정
카카오, 구글 개발자 계정 설정 필요

