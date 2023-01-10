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
#from skimage.feature._cascade import height


# key english
key = pd.read_csv(r'https://raw.githubusercontent.com/Nostr77/bank/main/banknames.csv')
key.NKB=key.NKB.astype(int)
key=key[['NKB', 'Short_UA','Short_EN']]

def transform1(baza, bank):
    baza.DT=pd.to_datetime(baza.DT)
    if bank!=999:
        baza=baza[baza.NKB==bank].reset_index(drop=True)
    g=baza.groupby(['DT', 'TYPE'], as_index=False).agg({'DT': 'first','TYPE': 'first', 'S_UAH': 'sum', 'S_FXD': 'sum', 'S_FXU': 'sum'})
    dtl=max(g.DT)
    # Fix rate global
    Fix_Rate=sum(g.S_FXU[g.DT==max(g.DT)])/sum(g.S_FXD[g.DT==max(g.DT)])
    # slices for charts
    #Calc
    g['S_UAH']=g['S_UAH']/1000000000
    g['S_FXD']=g['S_FXD']/1000000000
    g['S_FXU']=g['S_FXU']/1000000000
    g['S_UAE']=g['S_UAH']+g['S_FXD']*Fix_Rate
    #yoy
    f=g.rename({'DT': 'DT_SHIFTED', 'S_UAH': 'S_UAH_y', 'S_FXU': 'S_FXU_y', 'S_FXD': 'S_FXD_y', 'S_UAE': 'S_UAE_y'}, axis='columns')
    g['DT_SHIFTED']=g['DT']-pd.DateOffset(years=1)
    g=g.merge(f, on=['DT_SHIFTED','TYPE'], how='left')
    g=g[g.DT.isna()==False]
    g['yoy_UAH']=g['S_UAH']/g['S_UAH_y']-1
    g['yoy_FXD']=g['S_FXD']/g['S_FXD_y']-1
    g['yoy_UAE']=g['S_UAE']/g['S_UAE_y']-1
    #mom
    f=g[['DT', 'TYPE', 'S_UAH', 'S_FXD', 'S_FXU', 'S_UAE']]
    f=f.rename({'DT': 'DT_SHIFTED', 'S_UAH': 'S_UAH_m', 'S_FXU': 'S_FXU_m', 'S_FXD': 'S_FXD_m', 'S_UAE': 'S_UAE_m'}, axis='columns')
    #f.columns=[ 'DT_SHIFTED', 'TYPE', 'S_UAH_y', 'S_FXD_y', 'S_FXU_y', 'S_UAE_y']
    g['DT_SHIFTED']=g['DT']-pd.DateOffset(months=1)
    g=g.merge(f, on=['DT_SHIFTED','TYPE'], how='left')
    g=g[g.DT.isna()==False]
    g['mom_UAH']=g['S_UAH']/g['S_UAH_m']-1
    g['mom_FXD']=g['S_FXD']/g['S_FXD_m']-1
    g['mom_UAE']=g['S_UAE']/g['S_UAE_m']-1
    #qoq
    f=g[['DT', 'TYPE', 'S_UAH', 'S_FXD', 'S_FXU', 'S_UAE']]
    f=f.rename({'DT': 'DT_SHIFTED', 'S_UAH': 'S_UAH_q', 'S_FXU': 'S_FXU_q', 'S_FXD': 'S_FXD_q', 'S_UAE': 'S_UAE_q'}, axis='columns')
    g['DT_SHIFTED']=g['DT']-pd.DateOffset(months=3)
    g=g.merge(f, on=['DT_SHIFTED','TYPE'], how='left')
    g=g[g.DT.isna()==False]
    g['qoq_UAH']=g['S_UAH']/g['S_UAH_q']-1
    g['qoq_FXD']=g['S_FXD']/g['S_FXD_q']-1
    g['qoq_UAE']=g['S_UAE']/g['S_UAE_q']-1
    g=g[['DT', 'TYPE', 'S_UAH', 'S_FXD', 'S_FXU', 'S_UAE', 'yoy_UAH', 'yoy_FXD', 'yoy_UAE', 'mom_UAH', 'mom_FXD', 'mom_UAE', 'qoq_UAH', 'qoq_FXD',  'qoq_UAE']]
    g['Date']=g['DT']-pd.DateOffset(days=1)
    #print(max(g.yoy_UAH))
    g=g[g.yoy_UAH.isna()!=True].reset_index(drop=True)
    return g

#df=transform1(pd.read_excel(r'c:\acc\r\out\OSB.xlsx', sheet_name='AGG'),999)

#baza=pd.read_csv(r'c:\acc\r\out\OSBagg.csv')
#baza.DT=pd.to_datetime(baza.DT)
#baza.info()
#pd.read_excel(r'c:\acc\r\out\OSB.xlsx', sheet_name='AGG').info()
df=transform1(pd.read_csv(r'https://raw.githubusercontent.com/Nostr77/bank/main/OSBagg.csv'),999)

#df=transform1(pd.read_excel(r'c:\acc\r\out\OSB.xlsx', sheet_name='BB'),46)

#def topbanks(baza,type,dt0,dtw,dtl):
    # make exclusions (if type<0.05*instrument) 

baza=pd.read_csv(r'https://raw.githubusercontent.com/Nostr77/bank/main/OSBbb.csv')
baza.DT=pd.to_datetime(baza.DT)
dtl=max(baza.DT)
#################Table BB
# dates & top
dt0=dtl-pd.DateOffset(years=1)
dtw=pd.to_datetime('2022-03-01')
#dtl=pd.to_datetime('2022-11-01')
#top=7

def transformBB(type, top):
    top=int(top)
    gl=baza[(baza.DT==dtl)].reset_index(drop=True)
    #type='DFOOS'
    gl['S_UAE']=gl.S_UAH+gl.S_FXU
    
    gl=gl.groupby(['NKB','TYPE'], as_index=False).agg({'NKB': 'first', 'TYPE': 'first', 'S_UAE': 'sum'})
    glp=gl.pivot(index='NKB', columns='TYPE', values='S_UAE')
    if type[0]=='D':
        glp['exclusion']=(glp[type]<0.05*(glp.DFOOS+glp.DSG))
    elif type[0]=='L':
        glp['exclusion']=(glp[type]<0.05*(glp.LFONET+glp.LSGNET))
    glp=glp.reset_index()
    glp=glp[['NKB','exclusion']]
    
    g=baza.groupby(['NKB','TYPE', 'DT'], as_index=False).agg({'DT': 'first', 'NKB': 'first', 'TYPE': 'first', 'S_UAH': 'sum', 'S_FXD': 'sum', 'S_FXU': 'sum'})
    Fix_Rate=sum(g.S_FXU[g.DT==max(g.DT)])/sum(g.S_FXD[g.DT==max(g.DT)])
    g['S_UAH']=g['S_UAH']/1000000000
    g['S_FXD']=g['S_FXD']/1000000000
    g['S_UAE']=g['S_UAH']+g['S_FXD']*Fix_Rate
    g0=g[(g.TYPE==type) & (g.DT==dt0)].reset_index(drop=True)
    g0=g0.drop(columns=['TYPE', 'S_FXU', 'DT'])
    g0=g0.rename({'S_UAH': 'S_UAH0', 'S_FXD': 'S_FXD0', 'S_UAE': 'S_UAE0'}, axis='columns')
    gw=g[(g.TYPE==type) & (g.DT==dtw)].reset_index(drop=True)
    gw=gw.drop(columns=['TYPE', 'S_FXU', 'DT'])
    gw=gw.rename({'S_UAH': 'S_UAHW', 'S_FXD': 'S_FXDW', 'S_UAE': 'S_UAEW'}, axis='columns')
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
    g['yoyn_UAH']=g.S_UAH-g.S_UAH0
    g['wown_UAH']=g.S_UAH-g.S_UAHW
    g['yoyn_FXD']=g.S_FXD-g.S_FXD0
    g['wown_FXD']=g.S_FXD-g.S_FXDW
    g['yoyn_UAE']=g.S_UAE-g.S_UAE0
    g['wown_UAE']=g.S_UAE-g.S_UAEW
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

#g=transformBB('DFOOS','5').Short_EN


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

#baza=pd.read_excel(r'c:\acc\r\out\OSB.xlsx', sheet_name='AGG')

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]
app = dash.Dash()
server=app.server


app.layout = html.Div(id = 'parent', children = [
    html.H1(id = 'H1', children = 'Banking sector of Ukraine, Loans and Deposits / Кредити та депозити в банках України', style = {'textAlign':'center',\
                                            'marginTop':40,'marginBottom':40}),
        dcc.Dropdown( id = 'dropdown',
        options = [
            {'label':'Retail Deposits / Кошти фізосіб', 'value':'DFOOS' },
            {'label':'Corporate Deposits / Кошти суб`єктів господарювання', 'value':'DSG'},
            {'label':'Retail Loans (Net) / Чисті кредити фізособам (резерви враховано)', 'value':'LFONET'},
            {'label':'Corporate Loans (Net) / Чисті кредити фізособам (резерви враховано)', 'value':'LSGNET'},
            {'label':'Retail Loans (Gross) / Валові кредити фізособам (резерви не враховано)', 'value':'LFOGRO'},
            {'label':'Corporate Loans (Gross) / Валові кредити суб`єктів господарювання (резерви не враховано)', 'value':'LSGGRO'},
            ],
        value = 'DFOOS'),

        dcc.Graph(id = 'bar_plot'),
        dcc.Graph(id = 'bar_plot1'),
        dcc.Dropdown( id = 'dropdown2',
        options = [
            {'label':'UAH / Гривня', 'value':'UAH' },
            {'label':'FX (USD equivalent) / Іноземна валюта (доларовий еквівалент)', 'value':'FXD'},
            {'label':'All currencies (Fixed exchange rate) / Усі валюти, фіксований на останню дату курс, гривневий еквівалент', 'value':'UAE'},
            ],
        value = 'UAH'),

        dcc.Graph(id = 'bar_plot2'),

        dcc.Dropdown( id = 'dropdown3',
        options = [
            {'label':'Top 5 banks / Кількість топ банків - 5', 'value':'5' },
            {'label':'Top 10 banks / Кількість топ банків - 10', 'value':'10' },
            {'label':'Top 20 banks / Кількість топ банків - 20', 'value':'20' }
            ],
        value = '10')
    ])

@app.callback(Output(component_id='bar_plot', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])

def graph_update(dropdown_value):
    fig = make_subplots(rows=1, cols=3, 
        subplot_titles=['National Currency','FX Currency','Fixed rate'], 
        vertical_spacing=0.15, horizontal_spacing=0.15, 
        specs=[   [{"secondary_y": True}, {"secondary_y": True}, {"secondary_y": True}]  ])
    for i in fig['layout']['annotations']: i['font']['size'] = 12 
    fig.layout.font.family='Arial' #'Rockwell' 
    fig.update_layout(legend_orientation="h")
    fig.update_layout(margin=dict(l=5, r=5, t=25, b=15))
    fig.update_layout(showlegend=True)
    fig.update_layout(height=350)
    #fig.update_layout(yaxis_tickformat = '%')
    fig.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.S_UAH[df.TYPE=='{}'.format(dropdown_value)], name='UAH' , line=dict(color="#0000ff")),
        row=1, col=1)
    fig.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.yoy_UAH[df.TYPE=='{}'.format(dropdown_value)]*100, name="yoy", line=dict(color="#ff6600")),
        row=1, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.S_FXD[df.TYPE=='{}'.format(dropdown_value)], name='FXD' , line=dict(color="#0000ff")),
        row=1, col=2, secondary_y=False)
    fig.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.yoy_FXD[df.TYPE=='{}'.format(dropdown_value)], name="yoy", line=dict(color="#ff6600")),
        row=1, col=2, secondary_y=True)
    fig.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.S_UAE[df.TYPE=='{}'.format(dropdown_value)], name='All' , line=dict(color="#0000ff")),
        row=1, col=3, secondary_y=False)
    fig.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.yoy_UAE[df.TYPE=='{}'.format(dropdown_value)], name="yoy", line=dict(color="#ff6600")),
        row=1, col=3, secondary_y=True)

    return fig  

@app.callback(Output(component_id='bar_plot1', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])

def graph_update(dropdown_value):
    # FIG1 ##################################
    fig1 = make_subplots(rows=1, cols=3, 
        subplot_titles=['Growth yoy, %','Growth 3 Months Trailing, % ', 'Growth mom, %'], 
        y_title='billions', 
        vertical_spacing=0.15, horizontal_spacing=0.15, 
        specs=[   [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]  ])
    for i in fig1['layout']['annotations']: i['font']['size'] = 12 
    fig1.layout.font.family='Arial' #'Rockwell' 
    fig1.update_layout(legend_orientation="h")
    fig1.update_layout(margin=dict(l=5, r=5, t=25, b=15))
    fig1.update_layout(showlegend=True)
    fig1.update_layout(height=350)
    #fig1.update_layout(yaxis_tickformat = '%')
    # 2 row 1 col
    fig1.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.yoy_UAH[df.TYPE=='{}'.format(dropdown_value)], 
        name='UAH' , line=dict(color='blue')),        row=1, col=1, secondary_y=False)
    fig1.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.yoy_FXD[df.TYPE=='{}'.format(dropdown_value)], 
        name="FX", line=dict(color='green')), row=1, col=1)
    fig1.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.yoy_UAE[df.TYPE=='{}'.format(dropdown_value)], 
        name="Fixed Exchange Rate", line=dict(color='goldenrod')), row=1, col=1)
    # 2 row 2 col
    fig1.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.qoq_UAH[df.TYPE=='{}'.format(dropdown_value)], 
        name='UAH' , line=dict(color='blue')), row=1, col=2, secondary_y=False)
    fig1.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.qoq_FXD[df.TYPE=='{}'.format(dropdown_value)], 
        name="FX", line=dict(color='green')), row=1, col=2)
    fig1.add_trace(go.Scatter(x=df.Date[df.TYPE=='{}'.format(dropdown_value)], y=df.qoq_UAE[df.TYPE=='{}'.format(dropdown_value)], 
        name="Fixed Exchange Rate", line=dict(color='goldenrod')), row=1, col=2)
    # 2 row 3 col
    fig1.add_trace(go.Bar(x=df.Date[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], y=df.mom_UAH[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], 
        name='UAH', marker_color='blue', showlegend=True), row=1, col=3, secondary_y=False)
    fig1.add_trace(go.Bar(x=df.Date[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], y=df.mom_FXD[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], 
        name="FX", marker_color='green', showlegend=True), row=1, col=3)
    fig1.add_trace(go.Bar(x=df.Date[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], y=df.mom_UAE[(df.TYPE=='{}'.format(dropdown_value)) & (pd.DatetimeIndex(df.Date).year>=max(pd.DatetimeIndex(df.Date).year)-1)], 
        name="Fixed Exchange Rate", marker_color='goldenrod', showlegend=True), row=1, col=3)

    return fig1  


@app.callback(Output(component_id='bar_plot2', component_property= 'figure'),
              [Input('dropdown', 'value'), Input('dropdown2', 'value'), Input('dropdown3', 'value')])

def graph_update(dropdown_value, dropdown2_value, dropdown3_value):
    # FIG1 ##################################
    fig1 = make_subplots(rows=1, cols=3, 
        subplot_titles=['Stock, billions','Change yoy, billions', 'Change yoy, %'], 
        y_title='billions', 
        vertical_spacing=0.15, horizontal_spacing=0.15, 
        specs=[   [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]  ])
    for i in fig1['layout']['annotations']: i['font']['size'] = 12 
    fig1.layout.font.family='Arial' #'Rockwell' 
    fig1.update_layout(legend_orientation="h")
    fig1.update_layout(margin=dict(l=5, r=5, t=15, b=0))
    fig1.update_layout(showlegend=True)
    fig1.update_layout(height=350)
    #fig1.update_layout(yaxis_tickformat = '%')
    # 3 row 1 col
    slice=transformBB('{}'.format(dropdown_value), '{}'.format(dropdown3_value))
    fig1.add_trace(go.Bar(x=slice.sort_values(by='S_'+'{}'.format(dropdown2_value), ascending=False).Short_EN[slice.rS_UAE!='Other'], y=slice.sort_values(by='S_'+'{}'.format(dropdown2_value), ascending=False)['S_'+'{}'.format(dropdown2_value)][slice.rS_UAE!='Other'], 
        name=NameFigAgg('{}'.format(dropdown_value))+' {}'.format(dropdown2_value), marker_color='green', showlegend=True), row=1, col=1, secondary_y=False)
    # 3 row 2 col
    fig1.add_trace(go.Bar(x=slice.sort_values(by='yoyn_'+'{}'.format(dropdown2_value), ascending=False).Short_EN[slice.rS_UAE!='Other'], y=slice.sort_values(by='yoyn_'+'{}'.format(dropdown2_value), ascending=False)['yoyn_'+'{}'.format(dropdown2_value)][slice.rS_UAE!='Other'], 
        name='{}'.format(dropdown2_value), marker_color='blue', showlegend=True), row=1, col=2, secondary_y=False)    
    # 3 row 3 col
    fig1.add_trace(go.Bar(x=slice.sort_values(by='yoy_'+'{}'.format(dropdown2_value), ascending=False).Short_EN[slice.rS_UAE!='Other'], y=slice.sort_values(by='yoy_'+'{}'.format(dropdown2_value), ascending=False)['yoy_'+'{}'.format(dropdown2_value)][slice.rS_UAE!='Other'], 
        name='{}'.format(dropdown2_value), marker_color='goldenrod', showlegend=True), row=1, col=3, secondary_y=False)    

    return fig1  



if __name__ == '__main__': 
    app.run_server()
    
    
    
    
    
