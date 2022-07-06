import os
import sys
import secrets
from PIL import Image
from flask import url_for, current_app, render_template
from flask_mail import Message

from flaskinventory import mail

import datetime
from dateutil import parser
import re

import plotly
import plotly.graph_objs as go

import math
# import pandas as pd
import numpy as np
import json
from os import path

from urllib import error
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup

def save_picture(form_picture):
    #print("AAAAAAAAAAAAAAAAAAA")
    random_hex = secrets.token_hex(8)
    _, f_ext = path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = path.join(current_app.root_path, 'static/media/plpic', picture_fn)
    #limit image size
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:

{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def wave_chunk(A,f,st,et,sr,th):
    amplitude = A
    frequency = f
    start_time = st
    end_time = et
    sample_rate = sr
    theta = th

    time = np.arange(start_time, end_time, 1/sample_rate)
    fn = amplitude*np.cos(2*math.pi*frequency*time+theta)

    return [ time , fn ]


def gcoords(t):
    tod = t
    A = -10
    f = 0.04
    var=A*math.cos(2*f*math.pi*t)
    return var

def create_p2(tod):
    # nite1, day, nite2
    #amp, f, st,stp,period, theta
    sr=8
    ss=17
    SS = gcoords(sr)
    SR = gcoords(ss)
    ti= [tod.hour,tod.minute]
    time = ((float(ti[0])*60+float(ti[1]))/60)

    parameters = [ 
        (-10,0.04,0,sr,1436,0),
        (-10,0.04,sr,ss,1436,0),
        (-10,0.04,ss,23.93,1436,0)
    ]
    parts=[]
    for i in range(len(parameters)):
        parts.append([])

    for x in range(0,len(parameters)):
        parts[x] = wave_chunk(parameters[x][0],parameters[x][1],parameters[x][2],parameters[x][3],parameters[x][4],parameters[x][5])

    xnite1 = parts[0][0]
    ynite1 = parts[0][1]
    xday = parts[1][0]
    yday = parts[1][1]
    xnite2 = parts[2][0]
    ynite2 = parts[2][1]

    t = np.linspace(0, 23.93, 100)

    # Create traces 
    trace0 = go.Scatter(
        x = xday,
        y = yday,
        name = 'Light hours',
        mode = 'lines', 
        showlegend=False,
        line = {'color': 'rgb(244, 232, 104)', 'width': 3},
        connectgaps= True,
        stackgroup = 'one'
    )
    trace1 = go.Scatter(
        x = xnite1,
        y = ynite1,
        name = 'Night hours',
        mode = 'lines', 
        showlegend = False,
        line = {'color': 'rgb(0, 164, 244)', 'width': 3},
        connectgaps= True,
        stackgroup = 'two'
    )

    trace2 = go.Scatter(
        x = xnite2,
        y = ynite2,

        name = 'Night hours',
        mode = 'lines', 
        showlegend = False,
        line = {'color': 'rgb(0, 164, 244)', 'width': 3},
        connectgaps= True,
        stackgroup = 'three'
    )
    trace3 = go.Scatter(
        x = [time,time],
        y = [-10,10],

        name = 'ToD',
        mode = 'lines', 
        showlegend = False,
        line = {'color': 'rgb(255, 0, 0)', 'width': 3},
        connectgaps= True,
        stackgroup = 'four'
    )
    trace4 = go.Scatter(
        x = [0,23.93],
        y = [SR,SS],

        name = 'Horizon',
        mode = 'lines', 
        showlegend = False,
        line = {'color': 'rgb(200, 150, 100)', 'width': 3},
        connectgaps= True,
        stackgroup = 'five'
    )

    data = [trace0, trace1,trace2,trace3,trace4]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON


def montoint(mon):
    month = ['Jan','Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul' ,'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    return month.index(mon)+1

def inttomon(mon):
    month = ['Jan','Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul' ,'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    return month[mon-1]

def cal_space(area,pspacing, qty):
    q = int(qty)
    print(type(q),q)
    A = float(area)
    print(type(A),A)
    print(type(pspacing),pspacing)
    rad = float(pspacing)/2
    print(type(rad),rad)
    Punit = (rad*rad)*math.pi
    Aused = float("{:.2f}".format(Punit*q))
    pcentused = float("{:.2f}".format((Aused/A)*100))
    print(Aused, pcentused)

    return Aused, pcentused 

def planting_interval(prod_name,variety,DTM,SowInt,sowtype,FFD, SFD):
    todays_date = datetime.datetime.now()
    ffd = datetime.datetime(todays_date.year,montoint(FFD[4:7]),int(FFD[1:3]))
    sfd = datetime.datetime(todays_date.year,montoint(SFD[4:7]),int(SFD[1:3]))
    sowint = SowInt
    sowint = int(sowint.strip("'"))
    Prod_name = prod_name
    planting_dates = []
    inlist = []
    dtm = int(DTM.strip("'"))
    i = 1
    gen_sow_int = {
    "Onion" : 63,
    "Broccoli" : 38,
    "Corn": 365,
    "Peas": 21,
    "Beans": 20,
    "Celery": 70,
    "Brassica": 49,
    "Cucumbers": 30,
    "Squash": 28,
    "Tomato": 45,
    "Peppers": 56,
    "Potato": 45,
    "Beet": 30,
    "Carrot": 18,
    }
    
    if sowint == "0":
        if Prod_name in gen_sow_int:
            sowint = int(gen_sow_int[Prod_name])

    if sowtype == "'Direct'":
        first_plant = sfd + datetime.timedelta(days=7)
        start = first_plant
    #if direct sow
    else :
        first_plant = sfd - datetime.timedelta(days=sowint)
        start = first_plant + datetime.timedelta(days=(sowint))

    for i in range(0,7):#7
        inlist.append(start + datetime.timedelta(days=(sowint*i)))

        if inlist[i] <= (ffd-datetime.timedelta(days=(sowint))) and inlist[i].year == todays_date.year :
            planting_dates.append(str(inlist[i].day)+'-'+inttomon(inlist[i].month))
        else:
            break

    return planting_dates



def growth_status(planted_date,dtm,germ):
    pdate = planted_date
    todays_date = datetime.datetime.now()
    start_date = datetime.datetime(todays_date.year,montoint(pdate[3:7]),int(pdate[0:2]))
    germdate = start_date + datetime.timedelta(days=germ)
    matdate = start_date + datetime.timedelta(days=dtm) 
    harvdate = matdate + datetime.timedelta(days=25)
    
    if todays_date.day == start_date.day:
        days =0
    else:
        days = str(todays_date-start_date)
        days = int(days[:-21])

    if todays_date < germdate :
        status = 0
    elif todays_date < matdate :
        status = 1
    elif todays_date < harvdate :
        status = 2
    else:
        status = 3
    
    return  days,status

def db_convert(data):
    st = '('
    ed = ')'
    D = str(data)
    start = D.index(st) + len(st)
    end = D.index(ed, start + 1)
    d = re.split(r',',D[start:end])

    return d

def process_data(data):
    topic = data.title.string
    topic = topic.replace("|", "-")

    table = data.find("div",attrs={"class": "table-container"})
    table_rows = table.find_all('tr')
    hes = []

    for td in table.find_all("th"):
        tr = td.find_all("th")
        headings = td.text.strip()
        if headings:
            hes.append(headings)

    res=[]
    for tr in table.tbody.find_all_next("tr"):
        td = tr.find_all('td')
        row = [tr.text.strip() for tr in td]
        if row:
            res.append(row)
    df = pd.DataFrame(res, columns=hes)
    return df#, topic



def getfrosty(local):
    loca = local
    #url = 'https://www.veseys.com/ca/canada-hardiness-zones-frost-dates'
    url = 'http://192.168.0.156:5001/vessy/'
    er = None
    try:
        req = Request(url , headers={'User-Agent': 'Mozilla/6.0'})
    #user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
        webpage = urlopen(req).read().decode("utf-8")

    except error.URLError as e:
        if hasattr(e,'reason'):
            er = 1
        elif hasattr(e,'code'):
            er = 1
        else:
            er = 0
    except Exception as err:
        print(f'Other error occurred: {err}') 
        er = 1


    if er == 0:
        page_soup = soup(webpage, "lxml")#"html.parser")#
        df = process_data(page_soup)

        for i in range(len(df.Location)):
            if loca == df.Location[i]:
                indx = i 
        d = dict(df.iloc[indx])
        sfd = re.split(r' ',d.get('First Frost'))
        ffd = re.split(r' ',d.get('Last Frost'))
        sday = re.split(r'-',sfd[1])
        sday = str(int(round(float(sday[0])+((float(sday[1]) - float(sday[0]))/2))))
        fday = re.split(r'-',ffd[1])
        fday = str(int(round(float(fday[0])+((float(fday[1]) - float(fday[0]))/2))))
        smon = sfd[0][:3]
        fmon = ffd[0][:3]
        stsfd = str(sday+'-'+smon)
        stffd = str(fday+'-'+fmon)

    elif er == 1:
        stsfd = 0 
        stffd = 0
    else:
        pass

    return stffd, stsfd, er 

def str2int2str(st,tz):

    b = st
    b = int(b.strip('"'))
    a = str(b+tz)
    return a

def getastrodata(lat,lon,tz):
#https://sunrise-sunset.org/api
    url = f'https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=1'
    er = None
    try:
        req = Request(url , headers={'User-Agent': 'Mozilla/6.0'})
    #user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
        webpage = urlopen(req).read().decode("utf-8")

    except error.URLError as e:
        if hasattr(e,'reason'):
            print(e.reason)
            er = 1
        elif hasattr(e,'code'):
            er = 1
            print(e.code)
        else:
            er = 0
    except Exception as err:
        print(f'Other error occurred: {err}') 
        er = 1

    if er == 1:
        astrodata=(0,0,0,0,0,er)
        return astrodata

    else:
        data = re.split(r',',webpage)

        sr = re.split(r':',data[0])
        ss = re.split(r':',data[1])
        dl = re.split(r':',data[3])
        dwnst = re.split(r':',data[4])
        dwnsp = re.split(r':',data[5])

        sun_rise = str(str2int2str(sr[2],tz)+':'+sr[3]+':'+sr[4].strip('"'))
        sun_set =  str(str2int2str(ss[1],tz)+':'+ss[2]+':'+ss[3].strip('"'))
        day_len = str(dl[1].strip('"')+':'+dl[2]+':'+dl[3].strip('"'))
        dwnst = str(str2int2str(dwnst[1],tz)+':'+dwnst[2]+':'+dwnst[3].strip('"'))
        dwnsp = str(str2int2str(dwnsp[1],tz)+':'+dwnsp[2]+':'+dwnsp[3].strip('"'))

        astrodata=(sun_rise,sun_set,day_len,dwnst,dwnsp,er)
        return astrodata
   
def str2bool(v):
#     return v.lower() in ("yes", "true", "t", "1")
    if type(v) == str:
        return v.lower() in ("yes", "true", "t", "1")
    else:
        v=str(v)
        return v.lower() in ("yes", "true", "t", "1")

def stripper(data):
    if type(data) != str:#is list?
        f=[]
        for i in range(len(data)):
            # print(data[i])
            data[i] = str(data[i])
            f.append(re.sub("([(,)'])","",data[i]))
            # print(type(f[i]), f[i])
    else:
        f = re.sub(',()','',data)
        # print('strip AAAAA',f)
    return f


def update_sorter(pro,pd):
    form_dict = {}
    db_dict = {}
    #load dictionaries
    # print('database',pro)
    # print('web form',pd)
    for x in range(0,len(pd)):
        form_dict[x]=pd[x]

    for i in range(0,len(pro)):
        db_dict[i]=pro[i].strip("'")
    #search for changes & update db list

    for key in range(len(form_dict.items())):
        if (db_dict[key] != form_dict[key]):
            if form_dict[key] != None:
                if form_dict[key] != '':
                    db_dict[key] = form_dict[key]
            else:
                pass
    for k in range(17,28):
        db_dict[k] = str2bool(form_dict[k])  

    # print('out put ',db_dict)
    return db_dict
    