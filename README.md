# tailgrep
* (high performance) tail + grep on window <br/>
* usage : tailgrep.exe --help <br/>
* [Download (on windows)](https://wiki.gnuxer.com/_media/playground/tailgrep.zip) <br/>

## [NAME]
tailgrep - grep에 tail 기능을 추가한 프로그램 입니다.

## [SYNOPSIS]
```
tailgrep.exe [--count] [--time="time format"] [--tsync=number] [--ic] [--regexp] "pattern" "file" [--tail=number]
```

## [DESCRIPTION]
문자열 검색 속도가 다소 느린 낮은 버전의 파워쉘 파싱문법을 보완하기 위해 제작 되었습니다.<br/>
기록되는 로그 파일의 tail - grep 속도 개선이 주 목적입니다.<br/>
속도를 위해 Bytes 형태로 데이터를 처리합니다.<br/>
출력 시에만 str 형태로 변환 합니다.<br/>

## [OPTION]
* "pattern", "file" 순서만 일치한다면, 옵션 위치는 무관합니다. long 옵션만 지원합니다.

**[--count]**
```
일치하는 라인 수를 출력합니다.
```

**[--time="time format"]**
```
"time format" 안에 아래의 기호와 문자열을 이용해서 "1분전" 시간을 포함하여 검색합니다.
    ex) --time="%Y/%m-%d %H:%M:%S"  ->  "2017/08-26 23:50:58"

    %y : 연도를 축약하여 표시
    %Y : 연도를 축약하지 않고 표시
    %b : 축약된 월 이름
    %B : 축약되지 않은 월 이름
    %m : 숫자로 표현한 월(01~12)
    %d : 일(01~31)
    %H : 24시를 기준으로 한 시(00~23)
    %I : 12시를 기준으로 한 시(01~12)
    %M : 분(00~59)
    %S : 초(00~59)
    %p : 오전(AM) / 오후(PM)을 표시
    %a : 축약된 요일 이름
    %A : 축약되지 않은 요일 이름
    %w : 요일을 숫자로 표시(예: 일요일(0))
    %j : 1월 1일부터 누적된 날짜(001~366)

파이썬의 strftime 변환법과 일치합니다. 더 자세한 내용은 아래의 링크를 참조하세요.
(링크 : https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior)
```
**[--tsync=number]**
```
"time format" 검색에 사용할 시간의 싱크를 조절 합니다. (단위: 분)
        ex) number가 0인경우, 현재시각을 검색합니다.
            number가 -10인경우, 10분 전 시각을 검색합니다.
            number가  15인경우, 15분 이후의 시각을 검색합니다.
```
**[--ic]**
```
대, 소문자를 무시합니다.
```

**[--regexp]**
```
정규표현식을 적용합니다.
```

**[--tail=number]**
```
tail 옵션을 추가합니다. 파일의 끝부터 가져올 라인수를 입력합니다.
```

