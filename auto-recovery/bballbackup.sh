#!/bin/bash

: <<'END'
----------------------------- README----------------------------- 

#사용 전 쉘 실행 권한 변경
[baseball@localhost baseball]$ ./bballbackup.sh
-bash: ./bballbackup.sh: Permission denied
[baseball@localhost baseball]$ chmod +x ./bballbackup.sh

#실행
[baseball@localhost baseball]$ ./bballbackup.sh

#1. 실행 진단 -> 아래 sql 결과가 없으면 실패
SELECT * FROM KBO_SCHEDULE WHERE GYEAR='2017'
SELECT * FROM KBO_SCORE WHERE GYEAR='1982'

#2. 실행 진단 -> 실행 결과 파일에 로그
vi backupresult*.txt
명령어 실행 시간, 해당 명령어, 해당 백업 데이터가 기록됨 
---------------------------------------------------------------- 
END

#작업 시작 시간 입력
echo "---------------------teamrank 백업 시작 -------------------" >> /data/baseball/backupresult$(date '+%Y%m%d').txt
echo date >> /data/baseball/backupresult$(date '+%Y%m%d').txt

#teamrank 백업
for gyear in {1982..2018}
do
    echo "python3.6 /data/baseball/tester/teamrank.py $gyear 20180325" >> /data/baseball/backupresult$(date '+%Y%m%d').txt
    python3.6 /data/baseball/tester/teamrank.py $gyear 20180325 >> /data/baseball/backupresult$(date '+%Y%m%d').txt
    sleep 3
done

#kboschedule 백업
echo "---------------------kboschedule 백업 시작 -------------------" >> /data/baseball/backupresult$(date '+%Y%m%d').txt
echo date >> /data/baseball/backupresult$(date '+%Y%m%d').txt

for gyear in {1982..2018}
do
    echo "python3.6 /data/baseball/tester/kboschedule.py $gyear 20180325" >> /data/baseball/backupresult$(date '+%Y%m%d').txt
    python3.6 /data/baseball/tester/kboschedule.py $gyear 20180325 >> /data/baseball/backupresult$(date '+%Y%m%d').txt
    sleep 5
done

echo "---------------------score 백업 시작 -------------------" >> /data/baseball/backupresult$(date '+%Y%m%d').txt
echo date >> /data/baseball/backupresult$(date '+%Y%m%d').txt

: <<'END'
#가비지 값 넘어와서 수행안함
#score 백업 2018~2016년도
for i in `seq 0 1095`; 
do
    gday=`date +%Y%m%d -d "20181231 -$i days"`; 
    echo $gday
    gyear=`date +%Y -d "20181231 -$i days"`; 
    #echo $gyear
    sleep 0.8
    echo "python3.6 /data/baseball/tester/score.py $gyear $gday" >> /data/baseball/backupresult$(date '+%Y%m%d').txt
    python3.6 /data/baseball/tester/score.py $gyear $gday >> /data/baseball/backupresult$(date '+%Y%m%d').txt
done
END
