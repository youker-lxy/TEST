# -*- coding: UTF-8 -*-
import urllib
import urllib2
import json
import re
from bs4 import BeautifulSoup
from pprint import pprint

def urlsDownLoad(baseurl,offset):
    data = {
        'offset': offset,   #请求资源起始位置
        'format': 'json',
        'keyword': '教育 西安',
        'autoload': 'true',
        'count': '20',  #一次请求数目
        'cur_tab': 1
    }
    params = urllib.urlencode(data)
    url = baseurl + '?' + params
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    return response.read()

#解析json格式的页面
def urlsParse(page):
    jsondata = json.loads(page)
    d = jsondata.get('data')#data为字典列表
    #pprint(d)
    #经分析dispaly为有效url
    urls = [article.get('display_url') for article in d if article.get('display_url')]
    #pprint(urls)   #格式化查看urls
    return urls

def htmlDownLoad(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    page = response.read()
    return page

def htmlParse(page):
    soup = BeautifulSoup(page, 'html.parser')
    content = {}  # 字典，存放新闻标题，来源，发布时间，文章内容，其中内容对应value为存放多个p段落文字的list
    #剔除掉其他网站的新闻页面，统一提取页面
    if soup.select(r'link[media="only screen and (max-width: 640px)"]') == []:
        return content
    #剔除掉内容为非文章以及非教育（如问答模块）的页面
    if soup.select(r'a[ga_event=="click_channel"]') != []:
        print soup.select(r'a[ga_event=="click_channel"]')[0].get_text().encode("utf-8")
        if soup.select(r'a[ga_event=="click_channel"]')[0].get_text().encode("utf-8") == "其它":
            return content
    content["title"] = soup.select(r"#article-main h1")[0].get_text() #标题
    content["sourse"] = soup.select(r"#article-main .src")[0].get_text().strip() #去除空格 #来源
    content["time"] = soup.select(r"#article-main .time")[0].get_text().strip() #去除空格 #发布时间
    content["article"] = soup.select(r"#article-main .article-content p") #文章
    content["imags"] = soup.select(r"#article-main .article-content img") #图片
    return content

def save(content):
    fout = open(u'E:\\新闻爬取结果.txt', 'a')
    fout.write('新闻标题:   ' + content["title"].encode("utf-8") + '\n')
    fout.write('新闻来源:   ' + content["sourse"].encode("utf-8") + '\n')
    fout.write('新闻发布时间:   ' + content["time"].encode("utf-8") + '\n')
    #迭代文章p段落
    fout.write('新闻内容:\n\n')
    for p in content["article"]: #p为标签
        fout.write(p.get_text().encode("utf-8") + "\n")
    fout.write("\n")
    if content["imags"] != []:
        fout.write("新闻图片URL:\n")
    for imag in content["imags"]:
        fout.write(imag.get('src') + "\n")
    fout.write("\n-------------------------分隔符----------------------------------\n\n")
    fout.close()

def main():
    baseurl = "https://www.toutiao.com/search_content/"
    #offset每次20个的偏移，“教育 西安”搜索内容最大至220，该offset不定，策略待改变
    urls = []
    try:
        for offset in range(0, 200 + 1)[::20]:
            print offset
            page = urlsDownLoad(baseurl, offset)
            urls += urlsParse(page)
        count = 0
        pattern = re.compile(r"http://toutiao.com/group/")
        for url in urls:
            #过滤掉其他网页的页面
            if re.match(pattern, url):
                count += 1
                print count
                print url
        count = 0
        for url in urls:
            if re.match(pattern, url):
                count += 1
                print count
                print url
                page = htmlDownLoad(url)
                content = htmlParse(page)
                if content:
                    save(content)
        print u"已爬取至本地！"
    except urllib2.HTTPError, e:
        print e.code
        print e.reason
    except urllib2.URLError, e:
        print e.reason

if __name__ == "__main__":
    main()

