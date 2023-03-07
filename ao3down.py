import requests,re,csv,time,os
from bs4 import BeautifulSoup
import bs4
import json


#合法化文件名，去除无法作为命名的特殊字符
rstr = r"[\/\\\:\*\?\"\<\>\|\t\n\r\0]+|[ \.]+$|^[\. ]+" # '/ \ : * ? " < > | \t \n \r \0



#断点续传，仅仅在做了一半停的时候需要填写修改，然后把main()改为【2】or【3】
thepath = r"D:\MY_CODE\ao3download\Bavaria (Hetalia)"#断点续传存储目录
ddxc2=0 #获取下载链接 【2】workdiclist = getdownurl(workdiclist,thepath)
ddxc3=0 #正式下载文件 【3】fail_list = downworks(workdiclist,thepath)
workdiclist =  []


#为了防止被封间隔 time.sleep(slptm)
slptm = 5

#代理不能用的时候改为官方（需要挂梯）
ao3url="https://nightalk.cc" 
#ao3url="https://archiveofourown.org"



#有效的链接示例（多个用列表形式）：个人主页works页、某个系列点进去后的works页、标签works页、筛选后works页
demolist='''["https://archiveofourown.org/tags/Cuba*s*Russia%20(Hetalia)/works",
"https://archiveofourown.org/users/Oplusplus/pseuds/Oplusplus/works",
"https://archiveofourown.org/series/1785298",
"https://nightalk.cc/works?commit=Sort+and+Filter&work_search%5Bsort_column%5D=revised_at&include_work_search%5Bcharacter_ids%5D%5B%5D=201802&work_search%5Bother_tag_names%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=&fandom_id=12845&pseud_id=Aridna&user_id=Aridna"]'''


#多个series列表循环,也可也输入是用户所有works界面，筛选tag界面等等
#每个链接可能不止一页，每页最多20个works，每个works请求2次，每次请求后停顿slptm秒
surlist=["https://nightalk.cc/works?work_search%5Bsort_column%5D=revised_at&work_search%5Bother_tag_names%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=zh&commit=Sort+and+Filter&tag_id=Austria*s*Prussia+%28Hetalia%29"]#"https://nightalk.cc/tags/England*s*Prussia%20(Hetalia)/works"
#↑↑↑↑↑↑每次打开后只需要修改此链接↑↑↑↑↑↑



if surlist ==[]:
    if not os.path.exists('surlist.txt'):
        print("没有检测到surlist.txt文件，创建了示范surlist.txt文件")
        print("可打开surlist.txt修改（多个链接用列表形式）。也可也打开py文件修改surlist=[]行")
        print(demolist,file=open("surlist.txt","w",encoding="utf-8"))
        input("修改完surlist.txt后输入任意键继续(自备梯子开全局，不然连不上ao3)")

    fr = open('surlist.txt', 'r+', encoding='utf-8')
    surlist = json.loads(fr.read())
    fr.close()
    print("从surlist.txt文件中获取的待爬取链接列表：",surlist)
    input("输入任意键继续")

    



def main_moresurl(surlist):
    #多个链接形成的列表，每个存储在一个文件夹
    for i in range(len(surlist)):
        print("——————————————\n【0】当前文件夹进度：",i,"of",len(surlist),"\n——————————————\n")
        surl = surlist[i]
        print(surl)
        #【1】获取作品链接
        workdiclist,thepath = theseries(surl)
        #【2】获取下载链接
        workdiclist = getdownurl(workdiclist,thepath)
        #【3】下载文件
        fail_list = downworks(workdiclist,thepath)
        print("——————————————\n当前文件夹下载完毕，失败：",fail_list,
              "\n——————————————\n")

    print("——————————————\n所有文件夹全部下载完毕\n——————————————\n")
            




def theseries(surl):
    print("——————————————\n【1】批量获取作品链接\n——————————————\n")
    try:
       r=requests.get(surl)
    except:
       print("【！】网络错误！【！】")
       print("【！】可能是：1)请求太频繁，2)没挂梯，3)没开全局，4)输入网址有误！【！】")
       os.system('pause')
    #r.raise_for_status()
    #r.encoding=r.apparent_encoding
    #在用户界面和tag筛选界面，编码类型是Windows-1254，如果加上上面两行就会中文乱码
    #在series界面，编码类型是urf-8，不论如何都不会乱码
    print(r.apparent_encoding)
    #print(type(r))
    soup = BeautifulSoup(r.text,"html.parser")
    #print(soup)


    #soup》》title 每个链接生成一个总目录文件夹
    title = soup.find('title').string
    title = re.sub(rstr, "-", title)
    pattern = re.compile(r"-[ ]+(.*?)[ ]+-")
    title = pattern.search(title).group(1)
    print(title)

    thepath = os.path.join(os.getcwd(), title)
    print(thepath)
    check_path(thepath)
    

    #while遍历该目录每一页得到worklist
    pageflag = True
    worklist = []
    pagi=1
    while(pageflag):
        
        #soup》》worklist
        worklist = worklist + soup.find_all('li',{"id":re.compile("work_[0-9]+")})
        print(len(worklist))
        #print(worklist)
        #print(worklist,file=open("output_list2.html","w",encoding="utf-8"))
        
        #soup》》nexturl or 跳出while循环
        try:
            #得到总页数
            pagelist = soup.find('ol',{"title":"pagination"})
            pattern = re.compile(r'>([0-9]+)</a></li> <li class="next" title="next">')
            pagenum = pattern.search(str(pagelist)).group(1)
            print("发现不止一页，当前{}of{}页".format(pagi,pagenum))
            pagi=pagi+1
            #得到下一页编码
            nexturl = soup.find('a',{"rel":"next"})
            nexturl = ao3url + nexturl["href"]
            print("下一页是")
            print(nexturl)
        except:
            print("已到最后一页")
            break
        
        time.sleep(slptm)
        
        #soup》》newsoup 得到新soup
        r=requests.get(nexturl)
        #r.raise_for_status()
        #r.encoding=r.apparent_encoding
        #在用户界面和tag筛选界面，编码类型是Windows-1254，如果加上上面两行就会中文乱码
        #在series界面，编码类型是urf-8，不论如何都不会乱码
        #print(r.apparent_encoding)
        #print(type(r))
        soup = BeautifulSoup(r.text,"html.parser")

    #while遍历每一页后得到worklist
    print(worklist)

    
    #worklist》》workdiclist
    #细化处理每个文档模块
    workdiclist=[]
    for i in range(len(worklist)):

        onework = worklist[i].find('a',{"href":re.compile("/works/[0-9]{3,}$")})
        url=ao3url+onework["href"]
        word=onework.string
        word = re.sub(rstr, "-", word)
        print(onework,url,word)     
        aut = worklist[i].find('a',{"rel":"author"}).string
        print(aut)    
        try:
            ser = worklist[i].find('a',{"href":re.compile("/series/[0-9]{3,}$")}).string
        except:
            ser = ""
        print(ser)        
        workdiclist.append({"url":url,"word":word,"aut":aut,"ser":ser})
    print(workdiclist,file=open(thepath+"\\workdiclist_0.txt","w",encoding="utf-8"))
    print("存储了文件")
    print(workdiclist)

    return workdiclist,thepath




    
        


def getdownurl(workdiclist,thepath):
    print("——————————————\n【2】开始获取下载链接（为了防止频繁设置了间隔）\n——————————————\n")

    for i in range(ddxc2,len(workdiclist)):
        print(i,"of",len(workdiclist))

        url=workdiclist[i]["url"]
        print(url)

        r=requests.get(url)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        
        soup = BeautifulSoup(r.text,"html.parser")
        #print(soup)


        downl = soup.find('li',{"class":"download"})

        #print(downl)
        downl = downl.find_all("a")
        print(downl[2])
        workdiclist[i]["downurl"]=ao3url+downl[2]["href"]
        #print(workdiclist)

        print(workdiclist,file=open(thepath+"\\workdiclist.txt","w",encoding="utf-8"))

        time.sleep(slptm)
        

    return workdiclist



  

    
def downworks(workdiclist,thepath):


    print("——————————————\n【3】开始下载内容（为了防止频繁设置了间隔）\n——————————————\n")
    fail_list =[]



 
    for i in range(ddxc3,len(workdiclist)):
        print(i,"of",len(workdiclist))



        #filename = thepath+workdiclist[i]["word"]+".epub"
        onepath = os.path.join(thepath, workdiclist[i]["aut"],workdiclist[i]["ser"])
        print(onepath)
        check_path(onepath)
        filename = os.path.join(onepath ,workdiclist[i]["word"]+".epub")
        print(filename)

        fileurl =workdiclist[i]["downurl"]
        print(workdiclist[i]["word"])
        try:
            #urllib.request.urlretrieve(fileurl,filename=filename) #这个为请求下载存储一体，能用，但是容易超时 因此用request代替urllib
            ##请求资源
            r = requests.get(fileurl)
            ##打开文件并写入
            #print(r.content,file=open(filename,'w'))          
            with open(filename,'wb') as f:
                f.write(r.content)
                
            print("下载成功")
        except:
            print("下载失败")
            print("【！】网络错误！【！】")
            print("【！】可能是：1)请求太频繁，2)没挂梯，3)没开全局，4)输入网址有误！【！】")
            fail_list.append(workdiclist[i])
            print(fail_list)
        print(fail_list,file=open(thepath+"\\faillist.txt","w",encoding="utf-8"))
        time.sleep(slptm)
    return fail_list



def check_path(path):
    if not os.path.isdir(path):
        os.makedirs(path)
        print("创建目录")



if __name__ == "__main__":
    #多个链接形成的列表，每个存储在一个文件夹
    main_moresurl(surlist)




