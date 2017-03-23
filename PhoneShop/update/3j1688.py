import requests
from bs4 import BeautifulSoup
import time
import pymysql
import random
import json
import re
import time

def load_mysql_setting():
    f=open('./mysql_setting.json','r',encoding='utf8')
    data=json.load(f)
    return data

def insert_into_mysql(result,table):
    userdata=load_mysql_setting()
    conn=pymysql.connect(host=userdata['host'],user=userdata['user'],passwd=userdata['passwd'],db=userdata['db'],port=userdata['port'],charset=userdata['charset'])
    cur=conn.cursor()
    timenow=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    for item in result:
        row=cur.execute('update %s set products="%s",pub_date="%s",price="%s" where goodsNum=%s'%(table,str(item['products']),timenow,str(item['price']),str(item['goodsNum'])))
        if row==0:
            line=[]
            for key in ['goodsNum','price','goodsName','brand','des', 'products', 'configuration']:
                try:
                    line.append(str(item[key]))
                except:
                    line.append('')
            line.append(timenow)
            try:
                cur.execute('insert into %s(goodsNum,price,goodsName,brand,des,products,configuration,pub_date) values'%(table)+str(tuple(line)))
            except:
                pass
    conn.commit()
    cur.close()
    conn.close()

def get_headers():
    headers = {
        "X-Forwarded-For":'%s.%s.%s.%s'%(random.randint(0, 255),random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)),
        'Host':"www.3j1688.com",
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate'}
    return headers

def login():
    f=open('login.json','r')
    data=json.load(f)
    session=requests.session()
    html=session.post('http://www.3j1688.com/member/index.html',data=data,headers=get_headers()).text
    return session

def get_phones(session):
    '''
    html=session.get('http://www.3j1688.com/goods/lj/3/bjd.html',headers=get_headers()).text.replace('\r','').replace('\n','').replace('\t','').replace(' ','')
    table=re.findall('varsg={(.*?)}',html)[0].split(',')
    keys=[]
    for item in table:
        try:
            keys.append(item.split(':')[0])
        except:
            continue
    '''
    keys=['小米','乐视', '华为', '荣耀', '苹果', '三星', '魅族', '大神', '酷派', '诺基亚', '联想', '中兴', 'HTC', 'TCL','努比亚', '美图', '索尼', '微软', '摩托罗拉','锤子', '奇酷', '小辣椒', '一加']
    phones=[]
    for key in keys:
        try:
            html=session.post('http://www.3j1688.com/goods/lj/bjdjsonByBrand.html',data={'brandName':key},headers=get_headers()).text
            data=json.loads(html)['data']
            for item in data:
                item['brand']=key
                if key=='荣耀':
                    item['brand']='华为'
                if key=='努比亚':
                    item['brand']='中兴'
                phones.append(item)
        except:
            continue
        print(key)
    return phones

def get_phone(item,session):
    html=session.get('http://www.3j1688.com/goods/detail/%s.html?s=bjd'%item['goodsNum'],headers=get_headers()).text
    soup=BeautifulSoup(html).find('div',id='xq_mian')
    table=soup.find('div',{'class':'xq_main_02_let_03'}).find_all('div',{'class':'xq_main_02_let_02'})
    products=[]
    configuration=[]
    try:
        for li in soup.find('div',{'class':'xq_main_01_jage'}).find_all('li'):
            configuration.append(li.get_text().replace('\n','').replace('\t',''))
    except:
        pass
    for div in table:
        try:
            tds=div.find('tr').find_all('td')
            phone_infor=[]
            for td in tds[1:6]:
                try:
                    phone_infor.append(td.get_text())
                except:
                    phone_infor.append('')
            try:
                phone_infor.append(tds[-1].get_text().replace('\r','').replace('\n','').replace('\t','').replace(' ',''))
            except:
                phone_infor.append('-')
            price=div.find('h4').get_text().replace('\r','').replace('\n','').replace('\t','').replace(' ','').replace('/','')
            products.append({'infor':phone_infor,'price':price})
        except:
            continue
    imgs=soup.find('div',{'class':'goods_main_contents'}).find_all('img')
    des=[]
    for img in imgs:
        des.append(img.get('src'))
    item['des']=des
    item['products']=products
    item['configuration']=configuration
    return item

def get_tablets(session):
    keys=['小米', '华为', '荣耀', '苹果',  '三星','诺基亚', '联想', '微软', '台电', '酷比','亚马逊']
    tablets=[]
    for key in keys:
        try:
            html=session.post('http://www.3j1688.com/goods/pb/bjdjsonByBrand.html',data={'brandName':key},headers=get_headers()).text
            data=json.loads(html)['data']
            for item in data:
                item['brand']=key
                if key=='荣耀':
                    item['brand']='华为'
                tablets.append(item)
        except:
            continue
        print(key)
    return tablets

def get_tablet(item,session):
    html=session.get('http://www.3j1688.com/goods/detail/%s.html'%item['goodsNum'],headers=get_headers()).text
    soup=BeautifulSoup(html).find('div',id='xq_mian')
    table=soup.find('div',{'class':'xq_main_02_let_03'}).find_all('div',{'class':'xq_main_02_let_02'})
    products=[]
    configuration=[]
    try:
        for li in soup.find('div',{'class':'xq_main_01_jage'}).find_all('li'):
            configuration.append(li.get_text().replace('\n','').replace('\t',''))
    except:
        pass
    for div in table:
        try:
            tds=div.find('tr').find_all('td')
            phone_infor=[]
            for td in tds[1:6]:
                try:
                    phone_infor.append(td.get_text())
                except:
                    phone_infor.append('')
            try:
                phone_infor.append(tds[-1].get_text().replace('\r','').replace('\n','').replace('\t','').replace(' ',''))
            except:
                phone_infor.append('-')
            price=div.find('h4').get_text().replace('\r','').replace('\n','').replace('\t','').replace(' ','').replace('/','')
            products.append({'infor':phone_infor,'price':price})
        except:
            continue
    imgs=soup.find('div',{'class':'goods_main_contents'}).find_all('img')
    des=[]
    for img in imgs:
        des.append(img.get('src'))
    item['des']=des
    item['products']=products
    item['configuration']=configuration
    return item

def update():
    session=login()
    phones=get_phones(session)
    result=[]
    for phone in phones:
        try:
            item=get_phone(phone,session)
        except:
            print(phone['goodsNum'],phone['goodsName'],'failed')
        result.append(item)
        timenow=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        print(timenow,phone['goodsNum'],phone['goodsName'],'ok')
    insert_into_mysql(result,'mainsite_phone')
    tablets=get_tablets(session)
    result=[]
    for tablet in tablets:
        try:
            item=get_phone(tablet,session)
        except:
            print(tablet['goodsNum'],tablet['goodsName'],'failed')
            continue
        result.append(item)
        timenow=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        print(timenow,tablet['goodsNum'],tablet['goodsName'],'ok')
    insert_into_mysql(result,'mainsite_tablet')

while True:
    timenow=time.strftime("%H:%M",time.localtime())
    if '14:3' in timenow:
        update()
        time.sleep(3600*10)
    time.sleep(300)
