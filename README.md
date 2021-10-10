* icon - 응용프로그램에서 사용될 image source 모음
* main.py - 응용프로그램 진입점
* tkinter.py - 응용프로그램 UI관련 클래스
* WebScraping.py - 웹 크롤링관련 클래스
* DataSave.py - 오라클과 연동하여 테이블 Create & Delete, 초기Data Initialize Insert하는 클래스
* DataRefine.py - DataSave에서 테이블 생성 및 Insert한 데이터를 Select하여 볼 수 있고 (콤보박스 및 검색기능 有), Modify & Delete할 수 있는 클래스

기존 playdata_first_project가 웹 크롤링에 중점을 두어서 만들어진 프로젝트라면 
이번 프로젝트는 웹크롤링에 오라클 DB에 저장 및 data조작이 추가 되었습니다.  
매 번 크롤링할때마다 여러 정보들이 많이 쌓여서 관리하기가 힘들 것 같아서 이름이라는 시스템을 만들어서 관리하였습니다.  
입력받은 이름으로 폴더 및 파일관리를 하고, 중복된 이름을 입력 시 경고창으로 처리여부를 물어봅니다.
