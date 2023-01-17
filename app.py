import dash
#import dash_html_components as html
from dash import html
import plotly.graph_objects as go
#import dash_core_components as dcc
from dash import dcc
import plotly.express as px
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output
############
import pandas as pd
pd.options.mode.chained_assignment = None

#from skimage.feature._cascade import height
#import dash_bootstrap_components as dbc

# key english
key = pd.read_csv(r'https://raw.githubusercontent.com/Nostr77/bank/main/banknames.csv')
key.NKB=key.NKB.astype(int)
key=key[['NKB', 'Short_UA','Short_EN']]

def transform1(baz, bank):
    baz.DT=pd.to_datetime(baz.DT)
    if bank!=999:
        baz=baz[baz.NKB==bank].reset_index(drop=True)
    g=baz.groupby(['DT', 'TYPE'], as_index=False).agg({'DT': 'first','TYPE': 'first', 'S_UAH': 'sum', 'S_FXD': 'sum', 'S_FXU': 'sum'})
    dtl=max(g.DT)
    # Fix rate global
    Fix_Rate=sum(g.S_FXU[g.DT==max(g.DT)])/sum(g.S_FXD[g.DT==max(g.DT)])
    # slices for charts
    #Calc
    g['S_UAH']=g['S_UAH']/1000000000
    g['S_FXD']=g['S_FXD']/1000000000
    g['S_FXU']=g['S_FXU']/1000000000
    g['S_UAE']=g['S_UAH']+g['S_FXD']*Fix_Rate
    g['S_UAA']=g['S_UAH']+g['S_FXU']
    #yoy
    f=g.rename({'DT': 'DT_SHIFTED', 'S_UAH': 'S_UAH_y', 'S_FXU': 'S_FXU_y', 'S_FXD': 'S_FXD_y', 'S_UAE': 'S_UAE_y','S_UAA': 'S_UAA_y'}, axis='columns')
    g['DT_SHIFTED']=g['DT']-pd.DateOffset(years=1)
    g=g.merge(f, on=['DT_SHIFTED','TYPE'], how='left')
    g=g[g.DT.isna()==False]
    g['yoy_UAH']=g['S_UAH']/g['S_UAH_y']-1
    g['yoy_FXD']=g['S_FXD']/g['S_FXD_y']-1
    g['yoy_UAE']=g['S_UAE']/g['S_UAE_y']-1
    g['yoy_UAA']=g['S_UAA']/g['S_UAA_y']-1
    #mom
    f=g[['DT', 'TYPE', 'S_UAH', 'S_FXD', 'S_FXU', 'S_UAE','S_UAA']]
    f=f.rename({'DT': 'DT_SHIFTED', 'S_UAH': 'S_UAH_m', 'S_FXU': 'S_FXU_m', 'S_FXD': 'S_FXD_m', 'S_UAE': 'S_UAE_m','S_UAA': 'S_UAA_m'}, axis='columns')
    g['DT_SHIFTED']=g['DT']-pd.DateOffset(months=1)
    g=g.merge(f, on=['DT_SHIFTED','TYPE'], how='left')
    g=g[g.DT.isna()==False]
    g['mom_UAH']=g['S_UAH']/g['S_UAH_m']-1
    g['mom_FXD']=g['S_FXD']/g['S_FXD_m']-1
    g['mom_UAE']=g['S_UAE']/g['S_UAE_m']-1
    g['mom_UAA']=g['S_UAA']/g['S_UAA_m']-1
    #qoq
    f=g[['DT', 'TYPE', 'S_UAH', 'S_FXD', 'S_FXU', 'S_UAE', 'S_UAA']]
    f=f.rename({'DT': 'DT_SHIFTED', 'S_UAH': 'S_UAH_q', 'S_FXU': 'S_FXU_q', 'S_FXD': 'S_FXD_q', 'S_UAE': 'S_UAE_q', 'S_UAA': 'S_UAA_q'}, axis='columns')
    g['DT_SHIFTED']=g['DT']-pd.DateOffset(months=3)
    g=g.merge(f, on=['DT_SHIFTED','TYPE'], how='left')
    g=g[g.DT.isna()==False]
    g['qoq_UAH']=g['S_UAH']/g['S_UAH_q']-1
    g['qoq_FXD']=g['S_FXD']/g['S_FXD_q']-1
    g['qoq_UAE']=g['S_UAE']/g['S_UAE_q']-1
    g['qoq_UAA']=g['S_UAA']/g['S_UAA_q']-1
    g=g[['DT','TYPE','S_UAH','S_FXD','S_FXU','S_UAE','S_UAA','yoy_UAH','yoy_FXD','yoy_UAE','yoy_UAA','mom_UAH','mom_FXD','mom_UAE','mom_UAA','qoq_UAH','qoq_FXD','qoq_UAE','qoq_UAA']]
    g['Date']=g['DT']-pd.DateOffset(days=1)
    g=g[g.yoy_UAH.isna()!=True].reset_index(drop=True)
    return g

#df=transform1(pd.read_excel(r'c:\acc\r\out\OSB.xlsx', sheet_name='AGG'),999)

#baza=pd.read_csv(r'c:\acc\r\out\OSBagg.csv')
#baza.DT=pd.to_datetime(baza.DT)
#baza.info()
#pd.read_excel(r'c:\acc\r\out\OSB.xlsx', sheet_name='AGG').info()
df=transform1(pd.read_csv(r'https://raw.githubusercontent.com/Nostr77/bank/main/OSBagg.csv'),999)
dtl=max(df.DT)
dt0=min(df.DT)

#Patch LFONET LFOGRO LSGGRO
df.yoy_UAH[((df.DT<'2019-07-01') & ((df.TYPE=='LFONET') | (df.TYPE=='LFOGRO')| (df.TYPE=='LSGGRO')  | (df.TYPE=='LSGNET')) )]=None
df.yoy_FXD[((df.DT<'2019-07-01') & ((df.TYPE=='LFONET') | (df.TYPE=='LFOGRO')| (df.TYPE=='LSGGRO') | (df.TYPE=='LSGNET')) )]=None
df.yoy_UAE[((df.DT<'2019-07-01') & ((df.TYPE=='LFONET') | (df.TYPE=='LFOGRO')| (df.TYPE=='LSGGRO') | (df.TYPE=='LSGNET')) )]=None
df.yoy_UAA[((df.DT<'2019-07-01') & ((df.TYPE=='LFONET') | (df.TYPE=='LFOGRO')| (df.TYPE=='LSGGRO') | (df.TYPE=='LSGNET')) )]=None
###########################

#dfb=pd.read_csv(r'https://raw.githubusercontent.com/Nostr77/bank/main/OSBbb.csv')

baza=pd.read_csv(r'https://raw.githubusercontent.com/Nostr77/bank/main/OSBbb.csv')
baza.DT=pd.to_datetime(baza.DT)
#dtl=max(baza.DT)
#################Table BB
# dates & top
dt0=dtl-pd.DateOffset(years=1)
dtw=pd.to_datetime('2022-03-01')
#dtl=pd.to_datetime('2022-11-01')
#top=7

def transformBB(type, top):
    top=int(top)
    gl=baza[(baza.DT==dtl)].reset_index(drop=True)
    #exclusion by UAE depending on D or L, breakdown=5%
    gl['S_UAE']=gl.S_UAH+gl.S_FXU
    gl=gl.groupby(['NKB','TYPE'], as_index=False).agg({'NKB': 'first', 'TYPE': 'first', 'S_UAE': 'sum'})
    glp=gl.pivot(index='NKB', columns='TYPE', values='S_UAE')
    if type[0]=='D':
        glp['exclusion']=(glp[type]<0.05*(glp.DFOOS+glp.DSG))
    elif type[0]=='L':
        glp['exclusion']=(glp[type]<0.05*(glp.LFONET+glp.LSGNET))
    elif ((type=='DSNBp') | (type=='OVDPp') ):
        glp['exclusion']=False
    glp=glp.reset_index()
    glp=glp[['NKB','exclusion']]
    #main calc
    g=baza.groupby(['NKB','TYPE', 'DT'], as_index=False).agg({'DT': 'first', 'NKB': 'first', 'TYPE': 'first', 'S_UAH': 'sum', 'S_FXD': 'sum', 'S_FXU': 'sum'})
    Fix_Rate=sum(g.S_FXU[g.DT==max(g.DT)])/sum(g.S_FXD[g.DT==max(g.DT)])
    g['S_UAH']=g['S_UAH']/1000000000
    g['S_FXD']=g['S_FXD']/1000000000
    g['S_UAE']=g['S_UAH']+g['S_FXD']*Fix_Rate
    g['S_UAA']=g['S_UAH']+g['S_FXU']/1000000000
    g0=g[(g.TYPE==type) & (g.DT==dt0)].reset_index(drop=True)
    g0=g0.drop(columns=['TYPE', 'S_FXU', 'DT'])
    g0=g0.rename({'S_UAH': 'S_UAH0', 'S_FXD': 'S_FXD0', 'S_UAE': 'S_UAE0', 'S_UAA': 'S_UAA0'}, axis='columns')
    gw=g[(g.TYPE==type) & (g.DT==dtw)].reset_index(drop=True)
    gw=gw.drop(columns=['TYPE', 'S_FXU', 'DT'])
    gw=gw.rename({'S_UAH': 'S_UAHW', 'S_FXD': 'S_FXDW', 'S_UAE': 'S_UAEW', 'S_UAA': 'S_UAAW'}, axis='columns')
    g=g[(g.TYPE==type) & (g.DT==dtl)].reset_index(drop=True)
    g=g.drop(columns=['TYPE', 'S_FXU', 'DT'])
    g=g.merge(g0, on='NKB', how='left')
    g=g.merge(gw, on='NKB', how='left')
    g=g.merge(glp, on='NKB', how='left')
    g['yoy_UAH']=g.S_UAH/g.S_UAH0-1
    g['wow_UAH']=g.S_UAH/g.S_UAHW-1
    g['yoy_FXD']=g.S_FXD/g.S_FXD0-1
    g['wow_FXD']=g.S_FXD/g.S_FXDW-1
    g['yoy_UAE']=g.S_UAE/g.S_UAE0-1
    g['wow_UAE']=g.S_UAE/g.S_UAEW-1
    g['yoy_UAA']=g.S_UAA/g.S_UAA0-1
    g['wow_UAA']=g.S_UAA/g.S_UAAW-1
    g['yoyn_UAH']=g.S_UAH-g.S_UAH0
    g['wown_UAH']=g.S_UAH-g.S_UAHW
    g['yoyn_FXD']=g.S_FXD-g.S_FXD0
    g['wown_FXD']=g.S_FXD-g.S_FXDW
    g['yoyn_UAE']=g.S_UAE-g.S_UAE0
    g['wown_UAE']=g.S_UAE-g.S_UAEW
    g['yoyn_UAA']=g.S_UAA-g.S_UAA0
    g['wown_UAA']=g.S_UAA-g.S_UAAW
    gg=g
    g=g[g.exclusion!=True].reset_index(drop=True)
    g['ryoy_UAE'] = (1/g['yoy_UAE']).rank(na_option='bottom').astype(int)
    g['rS_UAE'] = (1/g['S_UAE']).rank(na_option='bottom').astype(int)
    g['ryoyn_UAE'] = (1/g['yoyn_UAE']).rank(na_option='bottom').astype(int)
    g['rwow_UAE'] = (1/g['wow_UAE']).rank(na_option='bottom').astype(int)
    g['rwown_UAE'] = (1/g['wown_UAE']).rank(na_option='bottom').astype(int)
    g.loc[((g['ryoy_UAE'] > top) & (g['ryoy_UAE'] < max(g['ryoy_UAE'])-top)), 'ryoy_UAE'] = 'Other'
    g.loc[((g['ryoyn_UAE'] > top) & (g['ryoyn_UAE'] < max(g['ryoyn_UAE'])-top)), 'ryoyn_UAE'] = 'Other'
    g.loc[(g['rS_UAE'] > top), 'rS_UAE'] = 'Other'
    g.loc[((g['rwow_UAE'] > top) & (g['rwow_UAE'] < max(g['rwow_UAE'])-top)), 'rwow_UAE'] = 'Other'
    g.loc[((g['rwown_UAE'] > top) & (g['rwown_UAE'] < max(g['rwown_UAE'])-top)), 'rwown_UAE'] = 'Other'
    g.ryoy_UAE = g.ryoy_UAE.astype(str)
    g.ryoyn_UAE = g.ryoyn_UAE.astype(str)
    g.rS_UAE = g.rS_UAE.astype(str)
    g.rwow_UAE = g.rwow_UAE.astype(str)
    g.rwown_UAE = g.rwown_UAE.astype(str)
    g=g[['NKB', 'ryoy_UAE','ryoyn_UAE', 'rS_UAE', 'rwow_UAE','rwown_UAE']]
    g=gg.merge(g, on='NKB', how='left')
    g.ryoy_UAE=g.ryoy_UAE.fillna('Other')
    g.ryoyn_UAE=g.ryoyn_UAE.fillna('Other')
    g.rS_UAE=g.rS_UAE.fillna('Other')
    g.rwow_UAE=g.rwow_UAE.fillna('Other')
    g.rwown_UAE=g.rwown_UAE.fillna('Other')
    #g['Date']=g['DT']-pd.DateOffset(days=1)
    g=pd.merge(g, key, how="left", on=['NKB'])
    return g

def NameFigAgg(TYPE):
    if (TYPE=='DFOOS'):
        return 'Retail Deposits'
    elif (TYPE=='DSG'):
        return 'Corporate Deposits'
    elif (TYPE=='LFONET'):
        return 'Retail Loans (Net)'
    elif (TYPE=='LSGNET'):
        return 'Corporate Loans (Net)'
    elif (TYPE=='LFOGRO'):
        return 'Retail Loans (Gross)'
    elif (TYPE=='LSGGRO'):
        return 'Corporate Loans (Gross)'
    elif (TYPE=='DSNBp'):
        return 'Certificates of Deposit'
    elif (TYPE=='OVDPp'):
        return 'Internal Government Loan Bonds'

def NameFigAggUkr(TYPE):
    if (TYPE=='DFOOS'):
        return 'Кошти фізичних осіб'
    elif (TYPE=='DSG'):
        return 'Кошти суб`єктів господарювання'
    elif (TYPE=='LFONET'):
        return 'Кредити фізичним особам (Чисті)'
    elif (TYPE=='LSGNET'):
        return 'Кредити суб`єктам господарювання (Чисті)'
    elif (TYPE=='LFOGRO'):
        return 'Кредити фізичним особам (Валові)'
    elif (TYPE=='LSGGRO'):
        return 'Кредити суб`єктам господарювання (Валові)'
    elif (TYPE=='DSNBp'):
        return 'Депозитні сертифікати НБУ (основний борг)'
    elif (TYPE=='OVDPp'):
        return 'ОВДП (основний борг)'


app = dash.Dash()
#server=app.server  #############################################################################

app.layout = html.Div(id = 'parent', children = [

    dcc.RadioItems(id = 'lang', 
        options = ['Eng', 'Ukr'], value ='Eng' ,
        style={'width': '97%', 'height': '35px', 'background-color':'black', 'color': 'gray', 'font-size': '15px', 'font-family': 'Arial', 'textAlign':'right'}),
    
    html.H2(id = 'H1', children = '1. Banking sector of Ukraine, Loans and Deposits / Кредити та депозити в банках України', 
            style = {'textAlign':'center', 'marginTop':30,'marginBottom':0,
                     'background-color': 'black', 'color': 'white', 'border-radius':'1%' }),
    html.H3(id = 'H2', children = 'All solvent banks as of end date / Платоспроможні банки на кінець періоду', 
            style = {'textAlign':'center', 'marginTop':5,'marginBottom':20,
                     'background-color': 'black', 'color': 'white', 'border-radius':'1%'}),
        dcc.Dropdown( id = 'dropdown',
        options = [
            {'label':'Retail Deposits / Кошти фізосіб', 'value':'DFOOS' },
            {'label':'Corporate Deposits / Кошти суб`єктів господарювання', 'value':'DSG'},
            {'label':'Retail Loans (Net) / Чисті кредити фізособам (резерви враховано)', 'value':'LFONET'},
            {'label':'Corporate Loans (Net) / Чисті кредити фізособам (резерви враховано)', 'value':'LSGNET'},
            {'label':'Retail Loans (Gross) / Валові кредити фізособам (резерви не враховано)', 'value':'LFOGRO'},
            {'label':'Corporate Loans (Gross) / Валові кредити суб`єктів господарювання (резерви не враховано)', 'value':'LSGGRO'},
            {'label':'Certificates of Deposit (principal) / Депозитні сертифікати НБУ (основний борг)', 'value':'DSNBp'},
            {'label':'Internal Government Loan Bonds (principal) / ОВДП (основний борг)', 'value':'OVDPp'}
            ],
        value = 'DFOOS'
        , style={'width': '100%', 'height': '35px', 'background-color':'#f5b7b1', 'font-size': '15px', 'font-family': 'Arial'}),

        dcc.Graph(id = 'bar_plot', style = {'textAlign':'center', 'marginTop':20,'marginBottom':20, 'background-color': 'black', 'color': 'white'}),

    #dcc.Slider(2019,2023,1, value=2020, marks={
    #    i: {            "label": f"  {i}",
    #                    "style": {"transform": "rotate(0deg)", "white-space": "nowrap", 'color': 'white', 'font-size': '15px', 'font-family': 'Arial', 'textAlign':'left'},}
    #    for i in range(2019, 2024)    }, id='slider', included=False,
    #    tooltip='Starting year for all charts'),
        dcc.Graph(id = 'bar_plot1', style = {'textAlign':'center', 'marginTop':20,'marginBottom':20,
                     'background-color': 'black', 'color': 'white'}),
        
        html.Div(id='textarea',
        style = {'textAlign':'center', 'marginTop':20,'marginBottom':10, 'background-color': 'black', 'color': 'white', 'width': '90%', 'height': '70%', 'font-size': '150%', 'font-family': 'Times New Roman'}),
        
        dcc.Dropdown( id = 'dropdown2',
        options = [
            {'label':'UAH / Гривня', 'value':'UAH' },
            {'label':'FX (USD equivalent) / Іноземна валюта (доларовий еквівалент)', 'value':'FXD'},
            {'label':'All currencies, UAH equivalent (Fixed exchange rate) / Усі валюти, фіксований на останню дату курс, гривневий еквівалент', 'value':'UAE'},
            {'label':'All currencies, UAH equivalent / Усі валюти, гривневий еквівалент', 'value':'UAA'}],
        value = 'UAH', style={'width': '100%', 'height': '100%', 'background-color':'#f5b7b1', 'font-size': '15px', 'font-family': 'Arial'}),

        dcc.Dropdown( id = 'dropdown3',
        options = [
            {'label':'Top 5 banks / Топ 5 банків', 'value':'5' },
            {'label':'Top 10 banks / Топ 10 банків', 'value':'10' },
            {'label':'Top 15 banks / Топ 15 банків', 'value':'15' },
            {'label':'Top 20 banks / Топ 20 банків', 'value':'20' },
            ],
        value = '10', style={'width': '100%', 'height': '100%', 'background-color':'#fadbd8', 'font-size': '15px', 'font-family': 'Arial'}),

        dcc.Graph(id = 'bar_plot2', style = {'textAlign':'center', 'marginTop':20,'marginBottom':20,'background-color': 'black', 'color': 'white'}),

        html.Div(id='text4',
        style = {'textAlign':'center', 'marginTop':20,'marginBottom':10, 'background-color': 'black', 'color': 'white', 'width': '90%', 'height': '70%', 'font-size': '150%', 'font-family': 'Times New Roman'}),

        dcc.Dropdown( id = 'nkb4',
        options = [
        {'label':'Privatbank : Приватбанк', 'value':'46' },
        {'label':'Oschad : Ощад', 'value':'6' },
        {'label':'Ukrexim : Укрексім', 'value':'2' },
        {'label':'Raif : Райф', 'value':'36' },
        {'label':'Ukrgaz : Укргаз', 'value':'274' },
        {'label':'FUIB : ПУМБ', 'value':'115' },
        {'label':'Ukrsib : УкрСиб', 'value':'136' },
        {'label':'OTP : ОТП', 'value':'296' },
        {'label':'Universal : Універсал', 'value':'242' },
        {'label':'Alfa/Sens : Альфа/Ceнс', 'value':'272' },
        {'label':'Credit Agr : К-Агріколь', 'value':'171' },
        {'label':'Citi : СІТІ', 'value':'297' },
        {'label':'Pivdenny : Південний', 'value':'106' },
        {'label':'Credo : Кредо', 'value':'88' },
        {'label':'Procredit : Прокредит', 'value':'298' },
        {'label':'Tascom : Таском', 'value':'62' },
        {'label':'C-Dnipro : К-Дніпро', 'value':'270' },
        {'label':'Vostok : Восток', 'value':'305' },
        {'label':'A-Bank : А', 'value':'96' },
        {'label':'ING : ІНГ', 'value':'295' },
        {'label':'MTB : МТБ', 'value':'105' },
        {'label':'Accord : Акорд', 'value':'392' },
        {'label':'Alliance : Альянс', 'value':'29' },
        {'label':'Pravex : Правекс', 'value':'153' },
        {'label':'Avgd : Авангард', 'value':'553' },
        {'label':'Lviv : Львів', 'value':'91' },
        {'label':'MIB : МІБ', 'value':'389' },
        {'label':'Piraeus : Піреус', 'value':'251' },
        {'label':'Globus : Глобус', 'value':'386' },
        {'label':'Deutche Bank : Дойчебанк', 'value':'407' },
        {'label':'Idea : Ідея', 'value':'142' },
        {'label':'Concorde : Конкорд', 'value':'326' },

        {'label':'Policom : Поліком', 'value':'49' },
        {'label':'Family : Фамільний', 'value':'72' },
        {'label':'Oksi : Оксі', 'value':'95' },
        {'label':'Industrial : Індустріал', 'value':'101' },
        {'label':'Poltava : Полтава', 'value':'113' },
        {'label':'Grant : Грант', 'value':'123' },
        {'label':'Sky : Скай', 'value':'128' },
        {'label':'BTA : БТА', 'value':'129' },
        {'label':'ASVIO : АСВІО', 'value':'133' },
        {'label':'Cominvest : Комінвест', 'value':'143' },
        {'label':'Ukrcapital : Укркапітал', 'value':'146' },
        {'label':'Meta : Мета', 'value':'205' },
        {'label':'Unex : Юнекс', 'value':'231' },
        {'label':'KIB : КІБ', 'value':'240' },
        {'label':'IBOX : Айбокс', 'value':'241' },
        {'label':'Rada : Рада', 'value':'286' },
        {'label':'Clearing : Кліринговий', 'value':'288' },
        {'label':'Firstinvest : Перший інв.', 'value':'290' },
        {'label':'Trust-c : Траст-капітал', 'value':'311' },
        {'label':'UBRD : УБРР', 'value':'313' },
        {'label':'BIZ : БІЗ', 'value':'320' },
        {'label':'Forward : Форвард', 'value':'325' },
        {'label':'C-Europe : К-Європа', 'value':'329' },
        {'label':'Creditvest : Кредитвест', 'value':'331' },
        {'label':'Ukrbudinvest : Укрбудінвест', 'value':'377' },
        {'label':'Motor : Мотор', 'value':'381' },
        {'label':'AP : АП', 'value':'387' },
        {'label':'Bank 3/4 : Банк 3/4', 'value':'394' },
        {'label':'Europrom : Європром', 'value':'395' },
        {'label':'SEB corp : СЕБ Корп.', 'value':'455' },
        {'label':'Alpari : Альпарі', 'value':'512' },
        {'label':'Portal : Портал', 'value':'634' },
        {'label':'Kristall : Кристал', 'value':'694' },
        {'label':'RVS : РВС', 'value':'774' },
        {'label':'Alt : Альт', 'value':'43' },        
        {'label':'PFB : ПФБ', 'value':'294' }
            ],
        value = '46', style={'width': '100%', 'height': '100%', 'background-color':' #fadbd8', 'font-size': '15px', 'font-family': 'Arial'}),

        dcc.Graph(id = 'bar_plot4', style = {'textAlign':'center', 'marginTop':20,'marginBottom':40, 'background-color': 'black', 'color': 'white'}),
        
        html.Div(id='notes', style = {'textAlign':'left', 'background-color': 'black', 'color': 'white', 'width': '100%', 'font-size': '80%', 'font-family': 'Arial'}),        
        
    ], style={'background-color':'black'})


@app.callback(Output(component_id='bar_plot', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value'), Input('lang', 'value')])

def graph_update(dropdown_value, lang_value):
    dfc=df #[df.DT.dt.year>=slider_value].reset_index(drop=True)
    if lang_value=='Eng':
        l1=[NameFigAgg('{}'.format(dropdown_value))+': National Currency, UAH billion ',NameFigAgg('{}'.format(dropdown_value))+': FX, USD billion',NameFigAgg('{}'.format(dropdown_value))+': All currencies, Fixed Exchange Rate, UAH billion']    
        l2='Stock, billion'
        l3='yoy (r.h.s.)'
    elif lang_value=='Ukr':
        l1=[NameFigAggUkr('{}'.format(dropdown_value))+': Національна валюта, млрд грн ',NameFigAggUkr('{}'.format(dropdown_value))+': Іноземна валюта, дол. екв., млрд дол США ',NameFigAggUkr('{}'.format(dropdown_value))+': Усі валюти, фікс. на кінець періоду курс, млрд грн ']    
        l2='Залишки, млрд од валюти'
        l3='p/p (п.ш.)'
    fig = make_subplots(rows=1, cols=3, 
        subplot_titles=l1, 
        vertical_spacing=0.12, horizontal_spacing=0.12, 
        specs=[   [{"secondary_y": True}, {"secondary_y": True}, {"secondary_y": True}] ])
    for i in fig['layout']['annotations']: i['font']['size'] = 14 
    fig.layout.font.family='Arial' #'Rockwell' 
    fig.update_layout(legend_orientation="h")
    fig.update_layout(margin=dict(l=25, r=15, t=25, b=25))
    fig.update_layout(showlegend=True)
    fig.update_layout(height=370)
    fig.update_layout(plot_bgcolor='#e5e8e8')
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_xaxes(rangeslider_thickness = 0.07)

    fig.update_layout(yaxis_tickformat = '0',yaxis2_tickformat = '0.0%', yaxis3_tickformat = '0', yaxis4_tickformat = '0.0%', yaxis5_tickformat = '0', yaxis6_tickformat = '0.0%')
    #fig.update_layout(xaxis_tickformat = 'mm.yy',xaxis2_tickformat = 'mm.yy', xaxis3_tickformat = 'mm.yy')
    fig.add_trace(go.Bar(x=dfc.Date[dfc.TYPE=='{}'.format(dropdown_value)], y=dfc.S_UAH[dfc.TYPE=='{}'.format(dropdown_value)], name=l2 , marker_color='#87CEEB', showlegend=True),
        row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x=dfc.Date[dfc.TYPE=='{}'.format(dropdown_value)], y=dfc.yoy_UAH[dfc.TYPE=='{}'.format(dropdown_value)], name=l3, line=dict(color="#ff6600"), showlegend=True),
        row=1, col=1, secondary_y=True)
    fig.add_trace(go.Bar(x=dfc.Date[dfc.TYPE=='{}'.format(dropdown_value)], y=dfc.S_FXD[dfc.TYPE=='{}'.format(dropdown_value)], name='FXD' , marker_color='#87CEEB', showlegend=False),
        row=1, col=2, secondary_y=False)
    fig.add_trace(go.Scatter(x=dfc.Date[dfc.TYPE=='{}'.format(dropdown_value)], y=dfc.yoy_FXD[dfc.TYPE=='{}'.format(dropdown_value)], name="yoy", line=dict(color="#ff6600"), showlegend=False),
        row=1, col=2, secondary_y=True)
    fig.add_trace(go.Bar(x=dfc.Date[dfc.TYPE=='{}'.format(dropdown_value)], y=dfc.S_UAE[dfc.TYPE=='{}'.format(dropdown_value)], name='All' , marker_color='#87CEEB', showlegend=False),
        row=1, col=3, secondary_y=False)
    fig.add_trace(go.Scatter(x=dfc.Date[dfc.TYPE=='{}'.format(dropdown_value)], y=dfc.yoy_UAE[dfc.TYPE=='{}'.format(dropdown_value)], name="yoy", line=dict(color="#ff6600"), showlegend=False),
        row=1, col=3, secondary_y=True)
    return fig  

@app.callback(Output(component_id='bar_plot1', component_property= 'figure'),
              [Input('dropdown', 'value'), Input('lang', 'value')])

def graph_update(dropdown_value,lang_value):
    if lang_value=='Eng':
        l1=['Growth yoy, %','Growth mom, %', 'Dollarization, %']    
        l3='UAH'
        l4='FX (USD eq.)'
        l5='All currencies, Fixed exchange rate'
    elif lang_value=='Ukr':
        l1=['Приріст р/р, %', 'Приріст за місяць, %','Доларизація (частка валютної складової), %']    
        l3='Національна валюта'
        l4='Іноземна валюта, доларовий еквівалент'
        l5='Усі валюти, за фіксованим курсом на кінець періоду'

    # FIG1 ##################################
    fig1 = make_subplots(rows=1, cols=3, 
        subplot_titles=l1, 
        vertical_spacing=0.14, horizontal_spacing=0.14, 
        specs=[   [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]  ])
    for i in fig1['layout']['annotations']: i['font']['size'] = 14 
    fig1.layout.font.family='Arial' #'Rockwell' 
    fig1.update_layout(legend_orientation="h")
    fig1.update_layout(margin=dict(l=45, r=105, t=25, b=25))
    fig1.update_layout(showlegend=True)
    fig1.update_layout(height=370)
    fig1.update_layout(plot_bgcolor=' #e5e8e8 ')
    fig1.update_xaxes(rangeslider_visible=True)
    fig1.update_xaxes(rangeslider_thickness = 0.07)

    fig1.update_layout(yaxis_tickformat = '.0%',yaxis2_tickformat = '.0%',yaxis3_tickformat = '.0%')
    # 2 row 1 col
    fig1.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.yoy_UAH[df.TYPE=='{}'.format(dropdown_value)], 
        name='UAH' , line=dict(color='blue'), showlegend=False),        row=1, col=1, secondary_y=False)
    fig1.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.yoy_FXD[df.TYPE=='{}'.format(dropdown_value)], 
        name="FX", line=dict(color='green'), showlegend=False), row=1, col=1)
    fig1.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.yoy_UAE[df.TYPE=='{}'.format(dropdown_value)], 
        name="Fixed Exchange Rate", line=dict(color='goldenrod'), showlegend=False), row=1, col=1)
    # 2 row 2 col
    fig1.add_trace(go.Bar(x=df.Date[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], y=df.mom_UAH[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], 
        name=l3, marker_color='blue', showlegend=True), row=1, col=2, secondary_y=False)
    fig1.add_trace(go.Bar(x=df.Date[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], y=df.mom_FXD[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], 
        name=l4, marker_color='green', showlegend=True), row=1, col=2)
    fig1.add_trace(go.Bar(x=df.Date[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], y=df.mom_UAE[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], 
        name=l5, marker_color='goldenrod', showlegend=True), row=1, col=2)
    # 2 row 3 col
    fig1.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.S_FXU[df.TYPE=='{}'.format(dropdown_value)]/df.S_UAA[df.TYPE=='{}'.format(dropdown_value)], 
        name='UAH' , line=dict(color='blue'), showlegend=False),        row=1, col=3, secondary_y=False)
    return fig1  


@app.callback(Output(component_id='bar_plot2', component_property= 'figure'),
              [Input('dropdown', 'value'), Input('dropdown2', 'value'), Input('dropdown3', 'value'), Input('lang', 'value')])

def graph_update(dropdown_value, dropdown2_value, dropdown3_value, lang_value):
    if lang_value=='Eng':
        l1=[NameFigAgg('{}'.format(dropdown_value))+' : ({}'.format(dropdown2_value)+') : Stock, billions as of '+str(dtl)[:10],NameFigAgg('{}'.format(dropdown_value))+': Change yoy, billions as of '+str(dtl)[:10], NameFigAgg('{}'.format(dropdown_value))+': Change yoy, % as of '+str(dtl)[:10]]    
        l2=NameFigAgg('{}'.format(dropdown_value))+' {}'.format(dropdown2_value)
        l3='EN'
    elif lang_value=='Ukr':
        l1=[NameFigAggUkr('{}'.format(dropdown_value))+' : ({}'.format(dropdown2_value)+') : залишки, млрд од валюти на '+str(dtl)[:10],NameFigAggUkr('{}'.format(dropdown_value))+': зміна р/р, млрд од валюти на '+str(dtl)[:10], NameFigAggUkr('{}'.format(dropdown_value))+': зміна р/р, % на '+str(dtl)[:10]]    
        l2=NameFigAggUkr('{}'.format(dropdown_value))+' {}'.format(dropdown2_value)
        l3='UA'

    # FIG1 ##################################
    fig1 = make_subplots(rows=1, cols=3, 
        subplot_titles=l1, 
        vertical_spacing=0.14, horizontal_spacing=0.14, 
        specs=[   [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]  ])
    for i in fig1['layout']['annotations']: i['font']['size'] = 14 
    fig1.layout.font.family='Arial' #'Rockwell' 
    fig1.update_layout(legend_orientation="v")
    fig1.update_layout(margin=dict(l=45, r=105, t=25, b=25))
    fig1.update_layout(showlegend=False) ##################
    fig1.update_layout(height=370)
    fig1.update_layout(plot_bgcolor=' #e5e8e8 ')
    fig1.update_layout(yaxis_tickformat = '0',yaxis2_tickformat = '0',yaxis3_tickformat = '.0%')
    # 3 row 1 col
    slice=transformBB('{}'.format(dropdown_value), '{}'.format(dropdown3_value))
    fig1.add_trace(go.Bar(x=slice.sort_values(by='S_'+'{}'.format(dropdown2_value), ascending=False)['Short_{}'.format(l3)][slice.rS_UAE!='Other'], y=slice.sort_values(by='S_'+'{}'.format(dropdown2_value), ascending=False)['S_'+'{}'.format(dropdown2_value)][slice.rS_UAE!='Other'], name=l2, marker_color='green', showlegend=True), row=1, col=1, secondary_y=False)
    # 3 row 2 col
    fig1.add_trace(go.Bar(x=slice.sort_values(by='yoyn_'+'{}'.format(dropdown2_value), ascending=False)['Short_{}'.format(l3)][slice.rS_UAE!='Other'], y=slice.sort_values(by='yoyn_'+'{}'.format(dropdown2_value), ascending=False)['yoyn_'+'{}'.format(dropdown2_value)][slice.rS_UAE!='Other'], name='{}'.format(dropdown2_value), marker_color='blue', showlegend=True), row=1, col=2, secondary_y=False)    
    # 3 row 3 col
    fig1.add_trace(go.Bar(x=slice.sort_values(by='yoy_'+'{}'.format(dropdown2_value), ascending=False)['Short_{}'.format(l3)][slice.rS_UAE!='Other'], y=slice.sort_values(by='yoy_'+'{}'.format(dropdown2_value), ascending=False)['yoy_'+'{}'.format(dropdown2_value)][slice.rS_UAE!='Other'],        name='{}'.format(dropdown2_value), marker_color='goldenrod', showlegend=True), row=1, col=3, secondary_y=False)    
    return fig1  


@app.callback(Output(component_id='textarea', component_property= 'children'),
              [Input('dropdown', 'value'), Input('lang', 'value')])

def text_update(dropdown_value, lang_value):
    if lang_value=='Eng':
        return '2. Top Banks by '+NameFigAgg('{}'.format(dropdown_value))
    elif lang_value=='Ukr':
        return '2. Найбільші банки за показником '+NameFigAggUkr('{}'.format(dropdown_value))   

@app.callback(Output(component_id='text4', component_property= 'children'),
              [Input('dropdown', 'value'), Input('nkb4', 'value'), Input('lang', 'value')])

def text_update(dropdown_value, nkb4_value, lang_value):
    if lang_value=='Eng':
        return '3. '+NameFigAgg('{}'.format(dropdown_value))+' :    Bank ' +max(key.Short_EN[key.NKB==int(('{}'.format(nkb4_value)))])    
    elif lang_value=='Ukr':
        return '3. '+NameFigAggUkr('{}'.format(dropdown_value))+' :    Банк ' +max(key.Short_UA[key.NKB==int(('{}'.format(nkb4_value)))])    

@app.callback(Output(component_id='bar_plot4', component_property= 'figure'),
              [Input('dropdown', 'value'), Input('nkb4', 'value'), Input('lang', 'value')])

def graph_update(dropdown_value, nkb4_value, lang_value):
    if lang_value=='Eng':
        l1=[NameFigAgg('{}'.format(dropdown_value))+': National Currency, UAH billion ',NameFigAgg('{}'.format(dropdown_value))+': FX, USD billion',NameFigAgg('{}'.format(dropdown_value))+': All currencies, Fixed Exchange Rate, UAH billion']    
        l2='Stock, billion'
        l3='yoy (r.h.s.)'
    elif lang_value=='Ukr':
        l1=[NameFigAggUkr('{}'.format(dropdown_value))+': Національна валюта, млрд грн ',NameFigAggUkr('{}'.format(dropdown_value))+': Іноземна валюта, дол. екв., млрд дол США ',NameFigAggUkr('{}'.format(dropdown_value))+': Усі валюти, фікс. на кінець періоду курс, млрд грн ']    
        l2='Залишки, млрд од валюти'
        l3='p/p (п.ш.)'

    # FIG1 ##################################
    dfa=transform1(baza,int(nkb4_value))
    #dfa=dfa[dfa.DT.dt.year>=slider_value]
    #Patch LFONET LFOGRO LSGGRO
    dfa.yoy_UAH[((dfa.DT<'2019-07-01') & ((dfa.TYPE=='LFONET')| (dfa.TYPE=='LFOGRO')| (dfa.TYPE=='LSGGRO') | (dfa.TYPE=='LSGNET')) )]=None
    dfa.yoy_FXD[((dfa.DT<'2019-07-01') & ((dfa.TYPE=='LFONET')| (dfa.TYPE=='LFOGRO')| (dfa.TYPE=='LSGGRO') | (dfa.TYPE=='LSGNET')) )]=None
    dfa.yoy_UAE[((dfa.DT<'2019-07-01') & ((dfa.TYPE=='LFONET')| (dfa.TYPE=='LFOGRO')| (dfa.TYPE=='LSGGRO') | (dfa.TYPE=='LSGNET')) )]=None
    dfa.yoy_UAA[((dfa.DT<'2019-07-01') & ((dfa.TYPE=='LFONET')| (dfa.TYPE=='LFOGRO')| (dfa.TYPE=='LSGGRO') | (dfa.TYPE=='LSGNET')) )]=None
    ###########################

    fig1 = make_subplots(rows=1, cols=3, 
        subplot_titles=l1, 
        vertical_spacing=0.12, horizontal_spacing=0.12, 
        specs=[   [{"secondary_y": True}, {"secondary_y": True}, {"secondary_y": True}]  ])
    for i in fig1['layout']['annotations']: i['font']['size'] = 14 
    fig1.layout.font.family='Arial' #'Rockwell' 
    fig1.update_layout(legend_orientation="h")
    fig1.update_layout(margin=dict(l=25, r=15, t=25, b=25))
    fig1.update_layout(showlegend=True)
    fig1.update_layout(height=370)
    fig1.update_layout(plot_bgcolor='#e5e8e8')
    fig1.update_xaxes(rangeslider_visible=True)
    fig1.update_xaxes(rangeslider_thickness = 0.07)
    fig1.update_layout(yaxis_tickformat='0',yaxis2_tickformat='0.0%',yaxis3_tickformat='0',yaxis4_tickformat='0.0%',yaxis5_tickformat='0',yaxis6_tickformat='0.0%')

    fig1.add_trace(go.Bar(x=dfa.Date[dfa.TYPE=='{}'.format(dropdown_value)], y=dfa.S_UAH[dfa.TYPE=='{}'.format(dropdown_value)], name=l2, marker_color='#87CEEB', showlegend=True), row=1, col=1, secondary_y=False)
    fig1.add_trace(go.Scatter(x=dfa.Date[dfa.TYPE=='{}'.format(dropdown_value)], y=dfa.yoy_UAH[dfa.TYPE=='{}'.format(dropdown_value)], name=l3, line=dict(color="#ff6600"), showlegend=True), row=1, col=1, secondary_y=True)

    fig1.add_trace(go.Bar(x=dfa.Date[dfa.TYPE=='{}'.format(dropdown_value)], y=dfa.S_FXD[dfa.TYPE=='{}'.format(dropdown_value)], name='Stock, billion' , marker_color='#87CEEB', showlegend=False), row=1, col=2, secondary_y=False)
    fig1.add_trace(go.Scatter(x=dfa.Date[dfa.TYPE=='{}'.format(dropdown_value)], y=dfa.yoy_FXD[dfa.TYPE=='{}'.format(dropdown_value)], name="yoy", line=dict(color="#ff6600"), showlegend=False), row=1, col=2, secondary_y=True)

    fig1.add_trace(go.Bar(x=dfa.Date[dfa.TYPE=='{}'.format(dropdown_value)], y=dfa.S_UAE[dfa.TYPE=='{}'.format(dropdown_value)], name='Stock, billion' , marker_color='#87CEEB', showlegend=False), row=1, col=3, secondary_y=False)
    fig1.add_trace(go.Scatter(x=dfa.Date[dfa.TYPE=='{}'.format(dropdown_value)], y=dfa.yoy_UAE[dfa.TYPE=='{}'.format(dropdown_value)], name="yoy", line=dict(color="#ff6600"), showlegend=False), row=1, col=3, secondary_y=True)

    return fig1  

@app.callback(Output(component_id='notes', component_property= 'children'),
              [Input('lang', 'value')])

def text_update(lang_value):
    if lang_value=='Eng':
        return 'Source - National Bank of Ukraine (balance sheet https://bank.gov.ua/files/stat/OSB_bank_2022-12-01.xlsx). The sample of banks consists of the banks that were solvent as of the last reporting date. The data include accrued interest as of the end of the period (month, quarter, year), unless otherwise specified. Gross loans are loans not adjusted for provisions against asset-side banking transactions. “Fixed-exchange-rate-based change” refers to the foreign-currency sum of an instrument being calculated using the exchange rate at the end of the period. Data on corporate loans and deposits include data on nonbank financial institutions. Retail deposits include certificates of deposit'
 
    elif lang_value=='Ukr':
        return 'Джерело даних – Національний банк України (Оборотно-сальдовий баланс банків, https://bank.gov.ua/files/stat/OSB_bank_2022-12-01.xlsx). До вибірки банків належать платоспроможні станом на останню звітну дату. Дані наведено з урахуванням нарахованих відсотків на кінець періоду (місяць, квартал, рік), якщо не зазначено інше. Валові кредити – кредити, не скориговані на резерви за активними операціями банків. Зміна за фіксованим курсом означає, що сума інструменту в іноземній валюті розраховується за курсом на кінець періоду. Дані за кредитами та коштами суб’єктів господарювання включають дані небанківських фінансових установ. Кошти фізичних осіб включають ощадні сертифікати'


if __name__ == '__main__': 
    app.run_server()
    
    

    
    
    