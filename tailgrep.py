#!/usr/bin/python3

from sys import argv, exit
from re import compile, search, IGNORECASE, sub
from datetime import timedelta, datetime


# 이거 배포하려면 예상 로그파일 그랩해서, 차이나는 라인 수 만큼 avg_len을 변경해서 긁어와야할듯
# 이렇게 변경한다면 1.5배 곱하는걸로 수정

#"줄바꿈 문자 옵션만 넣으면 됨"
# --count, --tail, --time "%m-%d %H:%M:"

# afgrep.exe [--count] [--time="time format"] [--tsync="number"] [--ic] [--regexp] "string" "file" [--tail="lines"]
# --time "%m-%d %H:%M:"

# --help가 있으면?
help_str = '''
    [NAME] - Made by argon(2chaes)
        tailgrep - grep에 tail 기능을 추가한 프로그램 입니다.

    [SYNOPSIS]
        tailgrep.exe [--count] [--time="time format"] [--tsync=number] [--ic] [--regexp] "pattern" "file" [--tail=number]

    [DESCRIPTION]
        문자열 검색 속도가 다소 느린 파워쉘 파싱문법을 보완하기 위해 제작 되었습니다.
        기록되는 로그 파일의 tail - grep 속도 개선이 주 목적입니다.
        속도를 위해 Bytes 형태로 데이터를 처리합니다.
        출력 시에만 str 형태로 변환 합니다.

    [OPTION] - "pattern", "file" 순서만 일치한다면, 옵션 위치는 무관합니다. long 옵션만 지원합니다.
        [--count]
            일치하는 라인 수를 출력합니다.

        [--time="time format"]
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

        [--tsync=number]
            "time format" 검색에 사용할 시간의 싱크를 조절 합니다. (단위: 분)

                ex) number가 0인경우, 현재시각을 검색합니다.
                    number가 -10인경우, 10분 전 시각을 검색합니다.
                    number가  15인경우, 15분 이후의 시각을 검색합니다.

        [--ic]
            대, 소문자를 무시합니다.

        [--regexp]
            정규표현식을 적용합니다.

        [--tail=number]
            tail 옵션을 추가합니다. 파일의 끝부터 가져올 라인수를 입력합니다.
    '''

try:
    cnt_idx = argv.index("--help")
    print(help_str)
    exit()
except ValueError:
    pass


##### 옵션 파싱 영역 #####
is_cnt = 0
is_time = 0
is_tsync = 0
is_tail = 0
is_ic = 0
is_regexp = 0

try: # count
    cnt_idx = argv.index("--count")
    is_cnt = 1
    argv.pop(cnt_idx)
except ValueError:
    #print("count 없음")
    pass


try: # time format
    time_idx = list(map(lambda x:x[:7], argv)).index("--time=")
    time_format = argv[time_idx][7:]
    is_time = 1
    argv.pop(time_idx)
    #print(time_format)

    tsync_idx = list(map(lambda x:x[:8], argv)).index("--tsync=")
    time_sync = sub(r"[\"\']", "", argv[tsync_idx][8:])
    time_sync = -1 * int(time_sync) # 형변환 실패시 에러 발생, pop 불가
    is_tsync = 1
    argv.pop(tsync_idx)
    #print(time_sync)
except ValueError:
    #print("시간 포맷 없음")
    #print("또는 sync 포맷 안맞음")
    pass


try: # ignore case
    ic_idx = argv.index("--ic")
    is_ic = 1
    argv.pop(ic_idx)
except ValueError:
    #print("ignore case 없음")
    pass


try: # reg exp
    regexp_idx = argv.index("--regexp")
    is_regexp = 1
    argv.pop(regexp_idx)
except ValueError:
    #print("regexp 없음")
    pass


try: # tail
    tail_idx = list(map(lambda x:x[:7], argv)).index("--tail=")
    tail_value = argv[tail_idx][7:]
    if tail_value.isnumeric():
        tail_value = int(tail_value)
        if tail_value > 0:
            #print("숫자임")
            pass
        else:
            raise Exception
    else:
        raise Exception
    is_tail = 1
    argv.pop(tail_idx)

except ValueError:
    #print("tail 없음")
    pass
except:
    print("tail 뒤에는 0 이상의 숫자가 필요합니다.")
    exit()

#print(argv)
if len(argv) != 3:
    print("알수 없는 옵션이 있습니다.")
    exit()


##### 옵션 설정 영역 #####

parse_str = bytes(argv[1], 'utf-8')

if is_ic == 1:
    parse_str = parse_str.lower()

timedata = b''
if is_time == 1: # 시간 옵션은 파이썬 strftime 문법을 따름
    is_regexp = 1
    timedata = bytes(datetime.strftime(datetime.now() - timedelta(time_sync/24/60), time_format), 'utf-8') + b".*"

if is_regexp == 1:
    ptn = compile(timedata + parse_str)

if is_tail == 1:
    grep_len = tail_value
    goal_grep_len = tail_value

res_list = []
with open(argv[2], 'rb') as f:
    f.seek(0, 2)
    #print(f.tell())
    is_short = 0 # 예상 idx보다 전체 파일 길이가 작은지 확인
    is_all = 0 # 검색하다가 파일 시작점 이전으로 접근했는가?
    is_lb = 0 # idx 앞부분이 줄바꿈 문자인가?

    ##### is_tail 분기 영역 #####
    if is_tail == 0:
        f.seek(0, 0)
        is_all = 1
        grep_len = 0
        goal_grep_len = 0
    else:
        f.seek(0,2)
        f_length = f.tell()

        ##### idx 추측을 위해 평균 라인 수를 계산하는 영역 #####
        try:
            f.seek(-102400, 2) # 예외발생 라인, bytes 길이가 10240보다 작아서 발생

            # 한줄의 평균 길이 구함. (줄바꿈 문자 포함, avg_len)
            avg_data = sub(br'^.*?\n|\n.*$', b'', f.read()) + b'\n' # 앞뒤 짜름
            avg_len = len(avg_data) / avg_data.count(b'\n')
            avg_len += 3 # 평균길이 보정(정확한 인덱스 검색을 위함)
            #print(avg_len)

            # 평균 길이가 너무 작을때 조절 하려면 아래 값 수정
            # if avg_len < 100: avg_len = 100

            # 평균값 이용해서 가져올 index 지정
            idx = int(avg_len * grep_len * -1)

            try: # idx 이전 문자열 확인
                f.seek(idx - 1, 2)
                if f.read(1) == b'\n': # 줄바꿈 문자일 경우 일치하는 라인
                    is_lb = 1
            except OSError: # 에러 발생시 idx 벗어남
                is_all = 1

            f.seek(idx, 2) # 예외발생 라인

        except OSError: # 파일 시작점 이전에 접근 -> 모두 가져온다.
            is_short = 1
            is_all = 1
            f.seek(0, 0)


    # idx부터 읽어들임
    index_list = f.read()

    # cut_str 앞부분 짤린거, 추후 idx 지정할때 사용
    # index_list는 가져온 데이터
    if is_ic == 1:
        index_list = index_list.lower()

    if is_short == 1 or is_all == 1 or is_lb == 1:
        cut_str = ""
        index_list = index_list.split(b'\n')
        # raise exception
    else:
        cut_str, *index_list = index_list.split(b'\n')

    #print(len(index_list))


    ##### 원하는 라인만큼 가지고 오는 영역, res #####
    while True:
        # 결과 리스트에다가 index_list 넣음
        res_list = index_list + res_list
        #print(len(res_list))

        # 파싱한 라인 수가 모자라지 않으면 데이터 그랩 성공
        if len(res_list) >= goal_grep_len or is_all == 1 or is_short == 1:
            if is_tail == 0:
                res = res_list
            else:
                res = res_list[-1 * goal_grep_len:] # 수 일치 체크 해야함.
            break
        # 파싱한 라인 수가 모자라다면 남아있는 라인수보다 "넉넉하게(x2)" 가져온다.
        else:
            #print("실패")
            # 부족한 라인 수 = 가져와야할 라인수 - 가져온 라인수
            # 부족한 만큼 grep 할 라인 수의 비율에 맞게 avg_len을 조절하여 변경한다.
            remain_lines = int(grep_len) - len(index_list)
            grep_len = remain_lines
            #print(1 + (remain_lines / goal_grep_len))
            avg_len *= 1 + (remain_lines / goal_grep_len)

            # 부족한 라인수를 넘어서서 더 가지고올 수 있는 idx를 찾는다. (x1.5)
            new_idx = int(-1 * remain_lines * avg_len * 1.5)

            # 부족한 라인의 예상 idx만큼 더 앞으로 가서 파일을 "필요한만큼만" 가져온다.
            try: # 정상적인 경우
                is_lb = 0
                f.seek(idx + new_idx, 2) # 예외처리 해야함
                idx = idx + new_idx
                index_list = f.read((new_idx * -1) + len(cut_str) + 1).rstrip()

                try: # idx 이전 문자열 확인
                    f.seek(idx + new_idx - 1, 2) # 여기서 예외 나면 is_all임
                    if f.read(1) == b'\n':
                        is_lb = 1
                except OSError:
                    f.seek(0, 0)
                    # new_idx를 빼주는 이유은 idx = idx + new_idx 식이 실행 되었기 때문임
                    index_list = f.read(f_length + idx - new_idx + len(cut_str) + 1).rstrip() # 이부분은 앞에서 예외 처리드됨
                    is_all = 1
                    is_lb = 1

            except OSError: # 두번째 예상 idx 검색 시, 파일 시작점 이전에 접근하는 경우
                f.seek(0, 0)
                index_list = f.read(f_length + idx + len(cut_str) + 1).rstrip() # 이부분은 앞에서 예외 처리드됨
                is_all = 1

            # 이전에 찾은, 짤린 앞부분것도 포함해서 가지고 온다. len(cut_str) + \n 까지
            # ***** 조금이라도 더 빠르게 하려면 split 하지말고 \n 개수만 세고 str 더하고, 마지막에 split. ***** (필요시 수정)
            if is_ic == 1:
                index_list = index_list.lower()

            if is_all == 1 or is_lb == 1:
                cut_str = ""
                index_list = index_list.split(b'\n')
            else:
                cut_str, *index_list = index_list.split(b'\n')
            #print(len(index_list))
        pass


    ##### 데이터 검색, 결과 반환 영역 #####
    # "re의 search" 보다 "ptn in str" 가 검색속도가 빠름

    #print(len(res))
    if is_regexp == 1:
        #print(ptn)
        data = tuple(filter(lambda x: ptn.search(x), res))
    else:
        data = tuple(filter(lambda x: parse_str in x, res))

    if is_cnt == 0:
        for i in data:
            print(str(i, "utf-8"))
    else:
        print(len(data))
