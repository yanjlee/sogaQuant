#! -*- coding:utf-8 -*-
from quant.core.Selecter import *
import pandas


class DmaSelecter(Selecter):
    '''
    dma 白线在黄线之上,长期趋势
    量度决定速度
    _OFFSET:=IF(DIF<0,DIF>REF(DIF,1),DIF<REF(DIF,1)); {DIFÎª¸ºÊý}
_UP_OFFSET:=IF(DIF<0, REF(DIF,2) < REF(DIF,1), REF(DIF,2) > REF(DIF,1));
_H:=_UP_OFFSET AND DIF>REF(DIF,1) AND DIF<DIFMA;

_M1:=DIF>=REF(DIF,1) AND REF(DIF,1)>=REF(DIF,2);
R7:=(_H OR _M1) AND REF(CLOSE,1)>REF(OPEN,1) AND LOW >MA(CLOSE,60);



DIFMA:=MA(DIF,36); {黄线}
LB:=VOL/REF(VOL,1); {1.5倍放量}
LB2:=VOL > REF(VOL,1);
KP:=DYNAINFO(4)>0; {非停牌在白线在黄线上关注下降 否则关注上涨}
{量度决定速度用于白线上穿黄线 以当天的放量坐标参考}

_C:=RANGE(REF(DIF,1),DIF,REF(DIF,2));

{齐心集团 20150123}
_OFFSET:=IF(DIF<0,DIF>REF(DIF,1),DIF<REF(DIF,1)); {DIF为负数}
_UP_OFFSET:=IF(DIF<0, REF(DIF,2) < REF(DIF,1), REF(DIF,2) > REF(DIF,1));


{波段回踩起跳002440 20150316,当天进3天内出}
_CNT:=ABS(ABS(DIF)-ABS(DIFMA)) <0.08;
_I:=_OFFSET AND REF(DIF,2) > REF(DIF,1) AND DIF>DIFMA; {下跌}
_J:=0;{白线下穿黄线，但三天内又拉起002440 20150312}
_K:=REF(C,2) < REF(O,2);{前天不能是阳线,昨天和前天不能连阳}
R8:=_I AND _K;

{隔天短线  AND LB>1.5 }


{N横盘天数，N1横盘的上下幅度}


XG: KP AND LB>1.2 AND CLOSE >10 AND CLOSE<80 AND R8  AND OPEN <CLOSE AND REF(C,1)>REF(O,1)




DIF:=MA(CLOSE,5)-MA(CLOSE,89);
DIFMA:=MA(DIF,36); {黄线}

KP:=DYNAINFO(4)>0;
_A:=COUNT(C/REF(C,1)*100-100>=9.8,10)>=1;{5天内出现过涨停}

_Y_ZF:=(C-REF(C,1))/REF(C,1);
_FP_1:=_Y_ZF <0.097;{过滤当天涨停}

_MAX_H:=HHV(HIGH,5);
{测试模式}
_B0:=((REF(HIGH,1)-REF(LOW,1))/REF(C,2))*100 >10 AND REF(OPEN,1)>REF(CLOSE,2);{昨天的震幅超过10,同时是阴线}
_B1:=(MIN(REF(CLOSE,1),REF(OPEN,1))-REF(LOW,1))/(REF(HIGH,1)-REF(LOW,1))>0.4;{昨天是上影线}
_B:=_B0;
_C:=REF(OPEN,2)<REF(CLOSE,2);{前一天为阳线}
{实盘}
B:=((HIGH-LOW)/REF(C,1))*100 > 10 AND OPEN>CLOSE AND REF(OPEN,1)<REF(CLOSE,1);
_D_P:=(REF(HIGH,1)-LOW)/REF(HIGH,1)>0.1;{最近两日跌幅超过10}
_D_S:=REF(HIGH,1)>LOW AND REF(HIGH,1)>HIGH;
_H:=HHV(HIGH,M);
_L:=LLV(LOW,M);
_D_M:=((_H-_L)/_L) > 0.20;{最近三天振幅在28%以上}
_D_O:=C*0.9 < _H*0.87;{以今日收盘价预计明天跌停是否大于以最高点下跌13%}

XG:KP AND _A AND DIF > DIFMA   AND _D_M AND _D_O AND _FP_1;



{603077 000529 002452 0407失败}


_SHADOW_UP:=(HIGH-MAX(CLOSE,OPEN))/(HIGH-LOW)>0.3667;{长上影线}
_SHADOW_DW:=(MIN(CLOSE,OPEN)-LOW)/(HIGH-LOW)>0.367;{长下影线}

_FILTER_0:=_SHADOW_UP AND _SHADOW_DW;

_Y_ZF:=(REF(C,1)-REF(C,2))/REF(C,2);
_W_3:=C> REF(HIGH,1)*0.75 AND HIGH>REF(C,1) AND LOW>REF(OPEN,1);{离高点1/3的收盘价}
_W_4:=(HIGH-REF(C,1))/REF(C,1);
_FILTER_1:=_Y_ZF>0.098 AND C<REF(HIGH,1);{昨天涨停的定准十字星}
_FILTER_2:=_Y_ZF >0.05 AND _W_3;
_FILTER_3:=VOL<REF(VOL,1)*0.9;
_FILTER_4:=_W_4<0.045 AND C>8;{上下振幅不超过4}
_FILTER_5:=((REF(HIGH,1)-REF(LOW,4))/REF(LOW,4))<0.2 AND REF(L,1)<REF(HIGH,2);{前4天累涨幅不超20%，多了必调整,大阳不能是跳开}

XG: _FILTER_0 AND _FILTER_3 AND (_FILTER_1 OR _FILTER_2) AND _FILTER_4 AND _FILTER_5;

    '''
    def __init__(self, setting):
        Selecter.__init__(self, setting)
        self.setting = setting

    def makeMa(self):
        self.df.sort_values(by=('dateline'), ascending=False)
        #print self.df
        #sys.exit()
        ma_list = [5, 89]
        for ma in ma_list:
            self.df['MA_' + str(ma)] = pandas.rolling_mean(self.df['close'], ma)

        #self.df = self.df[self.df['MA_89'].notnull()]
        #print self.df
        #sys.exit()
        #白线 code[13]
        self.df['dif'] = self.df['MA_5'] - self.df['MA_89']
        #黄线code[14]
        self.df['difma'] = pandas.rolling_mean(self.df['dif'], 36)

    def run(self):
        #pandas.set_option('display.width', 200)
        #s_code,code,dateline,chg_m,chg,open,close,high,low,last_close,name ma5 ma89 dif difma
        self.makeMa()
        #print self.df
        #last5 = self.df[self.df['dateline'] == int(self.setting['end'])]
        #print last5
        #sys.exit()
        tmp = self.df[(self.df['dateline'] == int(self.setting['end'])) & (self.df['dif'] > self.df['difma'])]
        #print tmp
        #sys.exit()
        for code in tmp.values:
            #print code
            #sys.exit()
            if code[13] >= code[14]:
                print "%s,%s,DMA,%s" % (code[0], code[10], code[3])
                #print code
                #sys.exit()

        #print self.df
        #dif = ma(close,5) - ma(close,89)
        #difma = ma(dif,36)
