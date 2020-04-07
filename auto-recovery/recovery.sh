#!/bin/bash

: <<'END'
----------------------------- README----------------------------- 

#사용 전 쉘 실행 권한 변경
[baseball@localhost baseball]$ ./recovery.sh 2019
-bash: ./recovery.sh: Permission denied
[baseball@localhost baseball]$ chmod +x ./recovery.sh

#실행
[baseball@localhost baseball]$ ./recovery.sh 2019

#1. 결과
vi recovery*.txt
명령어 실행 시간, 해당 명령어, insert/update 데이터가 기록됨 

#2. 결과
램프 로그에 동기화 수행 결과 출력

---------------------------------------------------------------- 
END
#kboschedule 리커버리 월별로 12회 수행
#기준일 12월 1일로 잡아서 1월 1일까지 수행

day=$1'1201'

for i in `seq 0 11`; 
do
    gday=`date +%Y%m%d -d "$day -$i months"`; 
    gyear=`date +%Y -d "$day -$i months"`; 
    echo "python3.6 /data/baseball/tester/kboschedule.py $gyear $gday" >> /data/baseball/log/recoveryresult$(date '+%Y%m%d').txt
    sleep 1
    python3.6 /data/baseball/tester/kboschedule.py $gyear $gday >> /data/baseball/log/recoveryresult$(date '+%Y%m%d').txt
done

#기준일 12월 31일로 잡고 1월 1일까지 수행
day=$1'1231'

#작업 시작 시간 입력
echo "---------------------teamrank 백업 시작 -------------------" >> /data/baseball/log/recoveryresult$(date '+%Y%m%d').txt
echo date > /data/baseball/backupresult$(date '+%Y%m%d').txt

#score 리커버리 일별 365회 수행
for i in `seq 0 364`; 
do
    gday=`date +%Y%m%d -d "$day -$i days"`; 
    gyear=`date +%Y -d "$day -$i days"`; 
    echo "python3.6 /data/baseball/tester/score.py $gyear $gday" >> /data/baseball/log/recoveryresult$(date '+%Y%m%d').txt
    sleep 0.3
    python3.6 /data/baseball/tester/score.py $gyear $gday >> /data/baseball/log/recoveryresult$(date '+%Y%m%d').txt
done

#iescoreinning 리커버리 일별 365회 수행
for i in `seq 0 364`; 
do
    gday=`date +%Y%m%d -d "$day -$i days"`; 
    gyear=`date +%Y -d "$day -$i days"`; 
    echo "python3.6 /data/baseball/tester/iescoreinning.py $gyear $gday" >> /data/baseball/log/recoveryresult$(date '+%Y%m%d').txt
    sleep 0.3
    python3.6 /data/baseball/tester/iescoreinning.py $gyear $gday >> /data/baseball/log/recoveryresult$(date '+%Y%m%d').txt
done

#iescorerheb 리커버리 일별 365회 수행
for i in `seq 0 364`; 
do
    gday=`date +%Y%m%d -d "$day -$i days"`; 
    gyear=`date +%Y -d "$day -$i days"`; 
    echo "python3.6 /data/baseball/tester/iescorerheb.py $gyear $gday" >> /data/baseball/log/recoveryresult$(date '+%Y%m%d').txt
    sleep 0.3
    python3.6 /data/baseball/tester/iescorerheb.py $gyear $gday >> /data/baseball/log/recoveryresult$(date '+%Y%m%d').txt
done

#iegamestate 리커버리 일별 365회 수행
for i in `seq 0 364`; 
do
    gday=`date +%Y%m%d -d "$day -$i days"`; 
    gyear=`date +%Y -d "$day -$i days"`; 
    echo "python3.6 /data/baseball/tester/iegamestate.py $gyear $gday" >> /data/baseball/log/recoveryresult$(date '+%Y%m%d').txt
    sleep 0.3
    python3.6 /data/baseball/tester/iegamestate.py $gyear $gday >> /data/baseball/log/recoveryresult$(date '+%Y%m%d').txt
done


