from PyQt5.QAxContainer import *

from PyQt5.QtCore import *

import time

from config.errorCode import *

from PyQt5.QtTest import *

from numba.tests.cache_usecases import self_test

from numpy.distutils.system_info import accelerate_info

from pytest import mark

from datetime import datetime

​

from config.errorCode import *

​

'''

매매 로직

1.장초, 장마감(2시~3시)는 변동성 가장심한 종목으로 단타(3프로수익)

1)전일 대비 상승률 가장 좋은 종목중에 상승률25%이하 종목 1개 추출

2)하루 2번 매매만. 2회 매매 달성시 break

3.당일매매 원칙으로 3시~3시20분사이에 전종목 청산.

4.회당 매수는 전체예수금에 1/10씩만 매수.

​

'''

​

#강의 54강 들을 차례

class Kiwoom(QAxWidget):

def __init__(self):

super().__init__()

​

##### eventloop 모듈########

self .login_event_loop = None

#########################

​

##### eventloop 모음#######

self .detail_account_info_loop = QEventLoop()

#self .detail_account_mystock_loop = None

self .calculator_event_loop = QEventLoop()

#self.sendorder_loop = QEventLoop()

#########################

​

########변수모음########

self.stock_code = None #069500:KODEX200

self.account_num = None

self.real_time_price_rate = 0

self.real_time_price_kodex = 0 #069500:KODEX200

self.stock_code_kodex = "069500" #KODEX200

self.real_time_price = 0

self.before_sell_price = 0

self.before_buy_price = 0

self.not_concluded_rows = 0

self.stock_quantity = 0

self.buy_price = 0

self.learn_rate_mp = "+"

self.learn_rate = 0

self.before_buy_yn = "N"

self.trade_time = 0

########################

​

########스크린번호 모음########

self.screen_my_info = "2000"

self.screen_calculation_stock = "4000"

########################

​

########계좌관련변수########

self.use_money = 0

self.use_money_percent = 0.5

########################

​

########변수모음########

self.account_stock_dict = {} #계좌정보dic

self.notok_stock_dict = {} #미체결dic

########################

​

self.get_ocx_instance()

self.event_slot()

self.signal_login_commConnect()

self.get_account_info()

while 1==1:

time.sleep(30)

self.detail_account_info() #예수금 확인

self.not_concluded_account() #미체결수량 확인, 변수명 : not_concluded_rows

self.detail_account_mystock()#계좌평가내역

#self.real_time_price_kodex_check() #kodex200 price check

if self.stock_quantity == 0 and self.not_concluded_rows == 0:

self.stock_search() #신규종목찾기

if self.stock_code is not None :

self.real_time_price_rate_check() #해당종목현재수익률, 변수명 : real_time_price_rate

self.before_sell_price_check() #직전매도가, 변수명 : before_sell_price

self.before_buy_price_check() #직전매수가, 변수명 : before_buy_price

self.send_order() #주문

​

​

#self.calculator_fnc() # 종목분석 임시용으로 실행

​

​

​

def get_ocx_instance(self):

#키움 응용프로그램 제어, 레지스트리경로 : KHOPENAPI.KHOpenApiCtrl.1

self.setControl("KHOPENAPI.KHOpenApiCtrl.1")

​

#로그인 버전처리 이벤트 : OnEventConnect

def event_slot(self):

self.OnEventConnect.connect(self.login_slot)

self.OnReceiveTrData.connect(self.trdata_slot)

#self.OnReceiveMsg.connect(self.receive_msg) # 매수시도후 에러발생시

​

# 매수후메세지리턴(성공이든 실패든 호출한다)

'''def receive_msg(self, scr_no, rq_name, tr_code, msg):

print(

"receive_msg 호출됨, scr_no = " + scr_no + ", rq_name = " + rq_name + ", tr_code = " + tr_code + ", msg = " + msg)

try:

self.sendorder_loop.exit()

except AttributeError:

pass'''

​

def login_slot(self, errCode):

print(errors(errCode))

self.login_event_loop.exit() # 아래 exec 종료

​

def signal_login_commConnect(self):

self.dynamicCall("CommConnect()")

self.login_event_loop = QEventLoop() #핸들오류, 데이터 수신과 시간차 해결

self.login_event_loop.exec() #로그인 완료 될떄까지 다음코드 실행안되도록.

# #자동로그인시 윈도우 하단에 서버와 통신연결 창 오른쪽 버튼을 통해 비밀번호 등록후 AUTO 설정을 해주어야한다.

​

def get_account_info(self):

account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO")

self.account_num = account_list.split(';')[0] #리스트값에 ;를 빼고 리스트중에 가장처음값만 필요하므로 [0]추가

#print("나의 계좌번호리스트 %s" % account_list)

print("나의 계좌번호 %s" % self.account_num)

​

#TR요청 이벤트 : OnReceiveTrData

def detail_account_info(self):

self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)

self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")

self.dynamicCall("SetInputValue(String, String)", "입력매체구분", "00")

self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")

self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)

​

self.detail_account_info_loop.exec() #로그인 완료 될떄까지 다음코드 실행안되도록.

​

def detail_account_mystock(self, sPrevNext="0"):

self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)

self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")

self.dynamicCall("SetInputValue(String, String)", "입력매체구분", "00")

self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")

self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)

​

self.detail_account_info_loop.exec() #로그인 완료 될떄까지 다음코드 실행안되도록.

​

def not_concluded_account(self, sPrevNext="0"):

self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)

self.dynamicCall("SetInputValue(String, String)", "매매구분", "0")

self.dynamicCall("SetInputValue(String, String)", "체결구분", "1")

self.dynamicCall("CommRqData(String, String, int, String)", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

​

self.detail_account_info_loop.exec() #로그인 완료 될떄까지 다음코드 실행안되도록.

​

def real_time_price_rate_check(self):

self.dynamicCall("SetInputValue(String, String)", "종목코드", self.stock_code)

self.dynamicCall("CommRqData(String, String, int, String)", "해당종목현재수익률", "opt10003", "0", self.screen_my_info)

​

self.detail_account_info_loop.exec() #로그인 완료 될떄까지 다음코드 실행안되도록.

​

def real_time_price_kodex_check(self):

self.dynamicCall("SetInputValue(String, String)", "종목코드", self.stock_code_kodex)

self.dynamicCall("CommRqData(String, String, int, String)", "KODEX현재수익률", "opt10003", "0", self.screen_my_info)

​

self.detail_account_info_loop.exec() #로그인 완료 될떄까지 다음코드 실행안되도록.

​

def before_sell_price_check(self):

self.dynamicCall("SetInputValue(String, String)", "종목코드", self.stock_code)

self.dynamicCall("SetInputValue(String, String)", "조회구분", "1")

self.dynamicCall("SetInputValue(String, String)", "매도수구분", "1")

self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)

self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")

self.dynamicCall("SetInputValue(String, String)", "체결구분", "2")

self.dynamicCall("CommRqData(String, String, int, String)", "직전매도가확인", "opt10076", "0", self.screen_my_info)

​

self.detail_account_info_loop.exec() #로그인 완료 될떄까지 다음코드 실행안되도록.

​

def before_buy_price_check(self):

self.dynamicCall("SetInputValue(String, String)", "종목코드", self.stock_code)

self.dynamicCall("SetInputValue(String, String)", "조회구분", "1")

self.dynamicCall("SetInputValue(String, String)", "매도수구분", "2")

self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)

self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")

self.dynamicCall("SetInputValue(String, String)", "체결구분", "2")

self.dynamicCall("CommRqData(String, String, int, String)", "직전매수가확인", "opt10076", "0", self.screen_my_info)

​

self.detail_account_info_loop.exec() #로그인 완료 될떄까지 다음코드 실행안되도록.

​

def stock_search(self):

self.dynamicCall("SetInputValue(String, String)", "시장구분", "000") # 000:전체, 001:코스피, 101:코스닥, 201:코스피200

self.dynamicCall("SetInputValue(String, String)", "등락구분", "1") # 1:급등, 2:급락

self.dynamicCall("SetInputValue(String, String)", "시간구분", "2") # 1:분전, 2:일전

self.dynamicCall("SetInputValue(String, String)", "거래량구분", "01000") # 1:분전, 2:일전

self.dynamicCall("SetInputValue(String, String)", "신용조건", "9") # 0:전체조회, 1:신용융자A군, 2:신용융자B군, 3:신용융자C군, 4:신용융자D군, 9:신용융자전체

self.dynamicCall("SetInputValue(String, String)", "가격조건", "4") #0:전체조회, 1:1천원미만, 2:1천원~2천원, 3:2천원~3천원, 4:5천원~1만원, 5:1만원이상, 8:1천원이상

self.dynamicCall("SetInputValue(String, String)", "상하한가포함", "0") # 0:미포함, 1:포함

self.dynamicCall("CommRqData(String, String, int, String)", "종목찾기", "opt10019", "0", self.screen_my_info)

​

self.detail_account_info_loop.exec() #로그인 완료 될떄까지 다음코드 실행안되도록.

​

def send_order(self):

print("실시간주문요청")

'''

<매매 logic>

1.장시작뒤 30분뒤 부터, 현재가빨간불 && stock_quantity 0 &&미체결수량 0 일경우 시장가매수 1주 start

2.수익중일때 : stock_quantity>0 && 전체계좌 0.15%수익시 매도

3.손실중일때 : 1)직전매수가보다 0.15%하락시 && 미체결내역 0일 경우 추매

3.30분동안 stock_quantity가 0 && 미체결내역 0일 경우 신규 매수 1주 >> 위로직 반복.

3시에 전량매도(당일매매)

'''

​

# LONG nOrderType, // 주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정

# BSTR sCode, // 종목코드 (6자리) 069500:KODEX200

# LONG nQty, // 주문수량

# LONG nPrice, // 주문가격 시장가주문시 주문가격은 0으로 입력합니다.

# BSTR sHogaGb, // 거래구분(혹은 호가구분)은 00 : 지정가 03 : 시장가

# BSTR sOrgOrderNo // 원주문번호. 신규주문에는 공백 입력, 정정/취소시 입력합니다.

now = datetime.now()

time = now.hour

time = str(time)

if len(time) == 1:

time = "0" + time

minute = now.minute

minute = str(minute)

if len(minute) == 1:

minute = "0" + minute

​

time_minute = str(time) + str(minute)

time_minute = int(time_minute)

​

#before_buy_gap 현재 가격과 이전 매수 가격과의 차이 >> 추매용도로 사용

self.before_buy_gap_rate = 0

if not self.before_buy_price :

self.before_buy_yn = "N"

else:

self.before_buy_yn = "Y"

​

before_buy_gap = self.real_time_price - self.before_buy_price

if before_buy_gap <= 0:

self.before_buy_gap_rate = float(((self.before_buy_price-self.real_time_price) / self.real_time_price)*100)

​

# before_sell_gap 현재 가격과 이전 매도 가격과의 차이 >> 수익실현후 신규매수 용도로 사용

if not self.before_sell_price :

before_sell_yn = "N"

else:

before_sell_yn = "Y"

before_sell_gap = self.real_time_price - self.before_sell_price

before_sell_gap_rate = 0

if before_sell_gap < 0:

before_sell_gap_rate = float((self.before_sell_price- self.real_time_price) / self.real_time_price)

​

#print("self.not_concluded_rows %s" %self.not_concluded_rows)

​

returnCode=0

print("현재종목코드 %s" %self.stock_code, "보유수량 %s"%self.stock_quantity, "미체결수량 %s"%self.not_concluded_rows,"보유수익률 %s"%self.learn_rate,

"현재가 %s"%self.real_time_price, "현재수익률 %s"%self.real_time_price_rate, "before_buy_gap_rate %s" % self.before_buy_gap_rate)

print("trade_time %s" %self.trade_time)

#오전 9~10시에만 매매 && 동일종목 매수 안되도록

#그 이후엔 etf 매매 (+인경우 만)

if 910 < time_minute < 1515 :

if self.stock_quantity == 0 and self.not_concluded_rows == 0:

print("신규 매수입니다.")

self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",

["실시간주문요청", self.screen_my_info, self.account_num, 1, self.stock_code, 10, 0, "03", ""])

elif self.stock_quantity > 0 and abs(self.learn_rate) > 3 and self.learn_rate_mp == "+" and self.not_concluded_rows == 0:

print("수익실현 매도입니다.")

self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",

["실시간주문요청", self.screen_my_info, self.account_num, 2, self.stock_code,

self.stock_quantity, 0, "03", ""])

self.trade_time += 1

elif self.stock_quantity > 0 and self.learn_rate_mp == "-" \

and (self.before_buy_yn == "Y" and self.before_buy_gap_rate != 0 and self.before_buy_gap_rate > 3) and self.not_concluded_rows == 0:

print("추매입니다.")

self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",

["실시간주문요청", self.screen_my_info, self.account_num, 1, self.stock_code, 10, 0, "03", ""])

# 정정매매 추가

elif self.not_concluded_rows > 0:

print("정정매매입니다.")

self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",

["실시간주문요청", self.screen_my_info, self.account_num, 5, self.stock_code, self.not_concluded_rows, 0, "03", ""])

​

elif 1515 < time_minute < 1520 and self.stock_quantity > 0 and self.not_concluded_rows == 0:

print("마감 매매입니다.")

self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",

["실시간주문요청", self.screen_my_info, self.account_num, 2, self.stock_code, self.stock_quantity,

0, "03", ""])

elif time_minute >= 1520:

print("프로그램 종료합니다.")

exit()

​

​

#아래는 etf 로직

'''if 920 < time_minute < 930 :

if self.stock_quantity == 0 and self.real_time_price_rate_mp =="+" and self.not_concluded_rows == 0:

print("시초가 매수입니다.")

self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",

["실시간주문요청", self.screen_my_info, self.account_num, 1, self.stock_code, 1, 0, "03", ""])

elif 930 < time_minute < 1500 :

if self.stock_quantity > 0 and abs(self.learn_rate) > 0.15 and self.learn_rate_mp == "+" and self.not_concluded_rows == 0 :

print("수익실현 매도입니다.")

self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",

["실시간주문요청", self.screen_my_info, self.account_num, 2, self.stock_code, self.stock_quantity, 0, "03", ""])

elif self.stock_quantity == 0 and before_sell_yn=="N" and self.real_time_price_rate_mp == "+" and self.not_concluded_rows == 0:

print("신규 매수입니다.")

self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",

["실시간주문요청", self.screen_my_info, self.account_num, 1, self.stock_code, 1, 0, "03", ""])

#수익실현후 재매수를 못하고, 시간이 흘러갔을때 로직 추가.

elif self.stock_quantity == 0 and (before_sell_yn=="Y" and before_sell_gap_rate !=0 and before_sell_gap_rate>0.015) \

and self.not_concluded_rows == 0 :

print("수익실현후 재매수입니다.")

self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",

["실시간주문요청", self.screen_my_info, self.account_num, 1, self.stock_code, 1, 0, "03", ""])

elif self.stock_quantity > 0 and self.learn_rate_mp == "-" \

and (before_buy_yn =="Y" and before_buy_gap_rate !=0 and before_buy_gap_rate >0.015) and self.not_concluded_rows == 0 :

print("추매입니다.")

self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",

["실시간주문요청", self.screen_my_info, self.account_num, 1, self.stock_code, 1, 0, "03", ""])

​

elif 1500 < time_minute < 1520 and self.stock_quantity>0 and self.not_concluded_rows == 0 :

print("마감 매매입니다.")

self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",

["실시간주문요청", self.screen_my_info, self.account_num, 2, self.stock_code, self.stock_quantity, 0, "03", ""])

#정정매매 추가

elif time_minute >= 1520 :

print("프로그램 종료합니다.")

exit()'''

​

​

​

​

​

​

def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):

'''

tr요청을 받는 구역이다, 슬롯

:param sScrNo: 스크린번호

:param sRQName: 내가요청했을 때 지은 이름

:param sTrCode: 요청id, tr코드

:param sRecordName: 사용x

:param sPrevNext: 다음 페이지가 있는 지 여부

:return:

'''

​

if sRQName == "예수금상세현황요청":

string_deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")

deposit = int(string_deposit) #형변환을 통해 0000050000 의 값을 50000으로 바꿔줌

​

#print("예수금 %s" % deposit)

​

self.use_money = deposit * self.use_money_percent

self.use_money = self.use_money / 4

​

ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")

ok_deposit = int(ok_deposit) # 형변환을 통해 0000050000 의 값을 50000으로 바꿔줌

​

#print("출금가능금액 %s" % ok_deposit)

​

self.detail_account_info_loop.exit() # 아래 exec 종료

​

elif sRQName == "해당종목현재수익률":

​

real_time_price_rate = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "대비율")

real_time_price_rate = real_time_price_rate.strip()

self.real_time_price_rate_mp = real_time_price_rate[0]

real_time_price_rate = float(real_time_price_rate.strip())

self.real_time_price_rate = real_time_price_rate

#print("해당종목현재수익률 %s" % self.real_time_price_rate)

real_time_price = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "현재가")

real_time_price = real_time_price.strip()

if real_time_price[0] == "-":

real_time_price = real_time_price[1:]

self.real_time_price = int(real_time_price)

#print("현재가 %s" % self.real_time_price)

self.detail_account_info_loop.exit() # 아래 exec 종료

​

elif sRQName == "KODEX현재수익률":

real_time_price_kodex = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "현재가")

real_time_price_kodex = real_time_price_kodex.strip()

if real_time_price_kodex[0] == "-":

real_time_price_kodex = real_time_price_kodex[1:]

self.real_time_price_kodex = int(real_time_price_kodex)

self.detail_account_info_loop.exit() # 아래 exec 종료

​

elif sRQName == "직전매도가확인":

​

before_sell_price = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "체결가")

if not before_sell_price :

print("직전매도 내역이 없습니다.")

else:

self.before_sell_price = int(before_sell_price) #형변환을 통해 0000050000 의 값을 50000으로 바꿔줌

print("직전매도가 %s" % self.before_sell_price)

self.detail_account_info_loop.exit() # 아래 exec 종료

​

elif sRQName == "직전매수가확인":

​

before_buy_price = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "체결가")

if not before_buy_price:

print("직전매수 내역이 없습니다.")

else:

self.before_buy_price = int(before_buy_price) #형변환을 통해 0000050000 의 값을 50000으로 바꿔줌

print("직전매수가 %s" % self.before_buy_price)

self.detail_account_info_loop.exit() # 아래 exec 종료

​

​

elif sRQName == "종목찾기":

​

print("종목찾기 START")

#25%이하 상승 종목만 추출.

self.stock_code = None

rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

for i in range(rows): #0부터 rows 미만까지.

up_and_down = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "등락률")

up_and_down = up_and_down.strip()[1:]

up_and_down = float(up_and_down)

if up_and_down < 25:

self.stock_code = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, i, "종목코드")

self.stock_code = self.stock_code.strip()

break

print("종목찾기 %s" %self.stock_code)

self.detail_account_info_loop.exit() # 아래 exec 종료

​

​

elif sRQName == "계좌평가잔고내역요청":

​

total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")

total_buy_money = int(total_buy_money) # 형변환을 통해 0000050000 의 값을 50000으로 바꿔줌

​

total_profit_rate = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")

total_profit_rate = float(total_profit_rate) # 형변환을 통해 0000050000 의 값을 50000으로 바꿔줌

​

print("총매입금액 %s" % total_buy_money, "내계좌수익률 %s" % total_profit_rate)

rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

if rows != 0 :

#for i in range(rows): #0부터 rows 미만까지.

# i는 몇번쨰 row인지만을 의미하고, 해당로우에서 값은 "XXX"로 찾는다

code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목번호")

code = code.strip()[1:] #stirp은 양쪽 공배 지워주기, [1:]의 의미는 두번쨰 문자부터 출력

self.stock_code = code

code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목명")

code_nm = code_nm.strip()

stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "보유수량")

self.stock_quantity = int(stock_quantity.strip())

buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매입가")

self.buy_price = int(buy_price.strip())

learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "수익률(%)")

learn_rate = learn_rate.strip()

self.learn_rate_mp = learn_rate[0]

if self.learn_rate_mp != "-":

self.learn_rate_mp = "+"

self.learn_rate = float(learn_rate)

currrent_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "현재가")

currrent_price = int(currrent_price.strip())

total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매입금액")

total_chegual_price = int(total_chegual_price.strip())

possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "매매가능수량")

possible_quantity = int(possible_quantity.strip())

else:

print("보유종목이 없습니다.")

self.stock_quantity = 0

self.learn_rate_mp = "+"

self.learn_rate = 0

self.detail_account_info_loop.exit() # 아래 exec 종료

​

​

#딕셔너리 만들기

'''if code in self.account_stock_dict:

pass

else:

self.account_stock_dict.update({code:{}})

self.account_stock_dict[code].update({"종목명": code_nm})

self.account_stock_dict[code].update({"보유수량": stock_quantity})

self.account_stock_dict[code].update({"매입가": buy_price})

self.account_stock_dict[code].update({"수익률(%)": learn_rate})

self.account_stock_dict[code].update({"현재가": currrent_price})

self.account_stock_dict[code].update({"매입금액": total_chegual_price})

self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

print("계좌평가잔고내역요청Multi %s" % self.account_stock_dict)'''

​

'''#다음페이지가 있을경우 sPrevNext를 2로 던져줌. 오류시 eventloop쪽을 다시 봐야함.

if sPrevNext == "2":

self.detail_account_mystock(sPrevNext="2")

else:

self.detail_account_info_loop.exit() # 아래 exec 종료'''

elif sRQName == "실시간미체결요청":

​

not_concluded_rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

not_concluded_rows = int(not_concluded_rows)

self.not_concluded_rows = not_concluded_rows

​

self.detail_account_info_loop.exit() # 아래 exec 종료

​

'''for i in range(rows): # 0부터 rows 미만까지.

# i는 몇번쨰 row인지만을 의미하고, 해당로우에서 값은 "XXX"로 찾는다

code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")

code = code.strip()[1:] # stirp은 양쪽 공배 지워주기, [1:]의 의미는 두번쨰 문자부터 출력

code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")

code_nm = code_nm.strip()

order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")

order_no = int(order_no.strip())

order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태")

order_status = order_status.strip()

order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")

order_quantity = int(order_quantity.strip())

order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")

order_price = int(order_price.strip())

order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분")

order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")

not_quantity = int(not_quantity.strip())

ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

ok_quantity = int(ok_quantity.strip())

​

# 딕셔너리 만들기

if order_no in self.notok_stock_dict:

pass

else:

self.notok_stock_dict.update({order_no: {}})

ddd = self.notok_stock_dict[order_no]

ddd.update({"종목번호": code})

ddd.update({"종목명": code_nm})

ddd.update({"주문상태": order_status})

ddd.update({"주문수량": order_quantity})

ddd.update({"주문가격": order_price})

ddd.update({"주문구분": order_gubun})

ddd.update({"미체결수량": not_quantity})

ddd.update({"체결량": ok_quantity})

​

'''

​

​

​

elif "주식일봉차트조회" == sRQName:

code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")

code = code.strip()

print("일봉데이터 요청 %s" % code)

​

rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

print(rows)

#한번 조회하면 600일치까지 일봉데이터를 조회할수 있다.

​

​

# 다음페이지가 있을경우 sPrevNext를 2로 던져줌. 오류시 eventloop쪽을 다시 봐야함.

if sPrevNext == "2":

self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)

else:

self.calculator_event_loop.exit()

​

​

def get_code_list_by_market(self, market_code):

'''

종목 코드들 반환

:param market_code:

:return:

'''

code_list = self.dynamicCall("GetCodeListByMarket(Qstring)", market_code)

#109012;239423;

code_list = code_list.split(";")[:-1]

return code_list

​

def calculator_fnc(self):

'''

종목분석 실행용 함수

:return: 

'''

​

code_list = self.get_code_list_by_market("0")

print("코스닥 갯수 %s" % len(code_list))

​

for idx, code in enumerate(code_list):

​

self.dynamicCall("DisconnectRealData(Qstring)", self.screen_calculation_stock) #DisconnectRealData 스크린번호 끊어주는 함수

​

print("%s / %s : KODAQ stock code : %s is updating.." % (idx+1, len(code_list), code))

self.day_kiwoom_db(code = code)

​

def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):

print("주식일봉차트조회 부분")

QTest.qWait(3600)

​

self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)

self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", 1)

if date != None:

self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

​

self.dynamicCall("CommRqData(String, String, int, String)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)

self.calculator_event_loop.exec()
