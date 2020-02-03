# -*- coding: utf-8 -*-
"""
@author: 冰蓝
@site: http://lanbing510.info
"""

import re
import urllib2  
import sqlite3
import random
import threading
import bs4
import cookielib
import requests
import lxml
import pandas as pd
import sys
import csv
reload(sys)
sys.setdefaultencoding("utf-8")




# 登录，不登录不能爬取三个月之内的数据

# import LianJiaLogIn


# Some User Agents
hds=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},\
    {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},\
    {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},\
    {'User-Agent':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},\
    {'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'},
     ]
    


# cookie

cks = {'CNZZDATA1253477573': '273638410-1580391282-https%253A%252F%252Fwww.lianjia.com%252F%7C1580391282',
            'CNZZDATA1254525948': '1116419940-1580393606-https%253A%252F%252Fwww.lianjia.com%252F%7C1580393606',
            'CNZZDATA1255604082': '1786673009-1580392101-https%253A%252F%252Fwww.lianjia.com%252F%7C1580392101',
            'CNZZDATA1255633284': '989309920-1580388999-https%253A%252F%252Fwww.lianjia.com%252F%7C1580394400',
            '_qzja': '1.2027823537.1580394332836.1580394332836.1580394332837.1580394370420.1580394474767.0.0.0.3.1',
            '_qzjb': '1.1580394332837.3.0.0.0',
            '_qzjc': '1',
            '_qzjto': '3.1.0',
           }


# cookieLib用于保存网页交互中产生的cookie，进行后续操作

# cookie = cookielib.CookieJar()

# urllib2 网页抓取，就是把URL地址中指定的网络资源从网络流中读取出来，保存到本地。
# 自定义opener,并将opener跟CookieJar对象绑定,opener是urllib2.OpenerDirectory的实例,用于打开网页
# opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
# 安装opener,此后调用urlopen()时都会使用安装过的opener对象

# opener.addheaders.append(('Cookie','cookiename=cookievalue'))
# urllib2.install_opener(opener)

http_session = requests.session()
requests.utils.add_dict_to_cookiejar(http_session.cookies, cks)

# 北京区域列表
regions=[u"东城",u"西城",u"朝阳",u"海淀",u"丰台",u"石景山",u"通州",u"昌平",u"大兴",u"亦庄开发区",u"顺义",u"房山",u"门头沟",u"平谷",u"怀柔",u"密云",u"延庆",u"燕郊"]
# 加u的作用是后面字符串以 Unicode 格式 进行编码，一般用在中文字符串前面，防止因为源码储存格式问题，导致再次使用时出现乱码。

lock = threading.Lock()

def visit_page(url_page):
    try:
        response = requests.get(url_page, headers=hds[random.randint(0,len(hds)-1)])
        file_obj = open('lianjia.html', 'w')  # 以写模式打开名叫 douban.html的文件
        # 如果打开网页显示的是乱码那么就用下一行代码
        # file_obj = open('douban.html', 'w', encoding="utf-8")  # 以写模式打开名叫 douban.html的文件，指定编码为utf-8
        file_obj.write(response.content.decode('utf-8'))  # 把响应的html内容
        file_obj.close()  # 关闭文件，结束写入
        file_obj = open('lianjia.html', 'r')  # 以读方式打开文件名为douban.html的文件
        html = file_obj.read()  # 把文件的内容全部读取出来并赋值给html变量
        file_obj.close()  # 关闭文件对象
        soup = bs4.BeautifulSoup(html, 'lxml')
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        exit(-1)
    except Exception,e:
        print e
        exit(-1)
    return soup



def region_spider(city_String):
    """
    爬取页面链接中的城市分区信息
    """
    url_page = u"https://"+unicode(city_String)+u".lianjia.com/xiaoqu/"
    soup=visit_page(url_page)
    xiaoqu=soup.find('div',{'data-role': 'ershoufang'})
    xiaoqu_list=xiaoqu.find_all('a')
    xiaoQuList=[]
    print("所有区县如下：")
    for i in range(len(xiaoqu_list)):
        print(xiaoqu_list[i].text)
        xiaoQuList.append(xiaoqu_list[i].text)
    return xiaoQuList




def xiaoqu_spider(region, A, city_String):
    """
       爬取页面链接中的区县小区房价信息
    """

    url=u"https://"+unicode(city_String)+u".lianjia.com/xiaoqu/rs"+unicode(region) + u"/"

    soup=visit_page(url)
    all_houses = soup.findAll('li', {'class': 'clear xiaoquListItem'})
    i=0
    sum=0
    for house in all_houses:
        A[0].append(region)
        A[1].append(str(house.find('a', {'class': 'bizcircle'}).text))
        A[2].append(house.find('div', {'class': 'tagList'}).text)
        content=house.find('div', {'class': 'positionInfo'}).text
        B=content.split('\n')
        A[3].append(B[4].strip().replace(u'\xa0', u' '))
        A[4].append(B[5].strip().replace(u'\xa0', u' '))
        A[5].append(house.find('div', {'class': 'totalPrice'}).text)
        C=house.find('div', {'class': 'totalPrice'}).text.split("元")
        if(len(C)>1):
            sum=sum+int(C[0])
            i = i + 1
        A[6].append(house.find('a')['href'])
    print(region+"区县信息搜集完成")
    if(i>0):
        print(region + "区县的平均二手房价为："+str(sum/i))
        B = sum/i
    else:
        print(region + "暂无二手房价信息")
        B = "None"
    return A, B

def City(city):
    if(city == "北京"):
        return "bj"
    elif(city == "上海"):
        return "sh"
    elif(city == "深圳"):
        return "sz"
    elif(city == "广州"):
        return "gz"
    elif(city == "杭州"):
        return "hz"
    elif (city == "武汉"):
        return "wh"
    elif (city == "天津"):
        return "tj"
    elif (city == "青岛"):
        return "qd"
    elif (city == "大连"):
        return "dl"
    elif (city == "重庆"):
        return "cq"
    elif (city == "南京"):
        return "nj"
    else:
        print("没有该城市的信息")
        return "error"


if __name__ == "__main__":
    city = raw_input("想要查询的城市：")
    city_string=City(city)
    if(city_string != "error"):
        list=region_spider(city_string)
        A=[[],[],[],[],[],[],[]]
        record=[]
        for region in list:
            A, B = xiaoqu_spider(region, A, city_string)
            record.append(B)

        out = open("record/"+city_string+'Record.csv', 'a')
        csv_write = csv.writer(out, dialect='excel')
        listForRecord=[]
        for qu in list:
            listForRecord.append(qu.decode("utf-8").encode("gbk"))
        csv_write.writerow(listForRecord)
        csv_write.writerow(record)
        xinXi = ["所属区县", "所在小区", "交通位置", "建筑风格", "建成时间", "参考价格", "网址"]
        dataframe = pd.DataFrame({xinXi[0]: A[0], xinXi[1]: A[1], xinXi[2]: A[2], xinXi[3]: A[3], xinXi[4]: A[4], xinXi[5]: A[5], xinXi[6]: A[6]})
        dataframe.to_csv("result/"+city_string+"LianJia.csv", index=False, sep=',', encoding="gbk")


