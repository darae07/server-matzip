## 프로젝트 소개

> 직장인들의 점심 메뉴 선정 시 간편하게 커뮤니케이션 할 수 있도록 돕는 서비스 **'오늘 뭐 먹지?'** 의 백엔드 레포지토리 입니다.

회사 동료들과 쉽게 점심 메뉴를 선정할 수 있도록 오늘의 메뉴를 등록하고 동료를 초대할 수 있으며, 고정적인 점심 멤버가 있는 경우 크루를 구성하고 투표를 통해서 메뉴를 선정할 수 있습니다.

맛집 검색엔 카카오 맵 api를 이용합니다.

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

