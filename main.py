import requests
from bs4 import BeautifulSoup
import os
import urllib.request
from PIL import Image,ImageFile
from tqdm import tqdm
import time
ImageFile.LOAD_TRUNCATED_IMAGES = True
def search_manga(tle,url):
    
    tle = tle.replace(' ','_')
    search_url = url +'/search/story/'+ tle
    r = requests.get(search_url)

    soup = BeautifulSoup(r.content,'html5lib')
    table = soup.find('div',attrs={'class':'panel_story_list'})
    if (table == None):
        print("not found")
        main()
    manga_title = []
    manga_link = []
    list_div = table.findAll('div',attrs={'class':'story_item'})

    if (len(list_div) == 0 or list_div == ''):
        print("not found")
        main()
    all_manga_det= soup.findAll('a',attrs={'class':'link no-decoration one-line'})
    for t in list_div:
        name = t.find('div',attrs={'class':'story_item_right'})
        
        #name = t.text.replace(' ','')
        manga_title.append(name.h3.a.text)
        manga_link.append(name.h3.a['href'])
        
    return manga_title,manga_link

def find_chapter(link):
    

    r = requests.get(link)

    soup = BeautifulSoup(r.content,'html5lib')

    colum = soup.find('div',attrs={'class':'panel-story-chapter-list'})
    
    box = colum.findAll('li',attrs = {'class':'a-h'})
    name = []
    link = []
    time = []
    for i in box:
        t = i.find('span',attrs={'class':'chapter-time text-nowrap'})
        time.append(t.text)
        name.append(i.a.text)
        link.append(i.a['href'])
    
    return name[::-1],link[::-1],time[::-1]


def select_chapter(chapter_name,chapter_link):
    print("use coma for particular chapters like 2,3,4 ")
    print("Choose chapter by range 2-9")
    print("Type \'ALL\'to downlaod all chapters")
    print('---------------------------------------')
    d_link = []
    d_name = []
    u_input = input("enter chapter to download")
    if u_input == "ALL":
        d_link = chapter_link
        d_name = chapter_name
    elif ('-' in u_input):
        u_input = u_input.replace(' ','')
        u_input  = u_input.split('-')
        for i in range(int(u_input[0]),int(u_input[1])+1):
            d_link.append(chapter_link[i])
            d_name.append(chapter_name[i])
    elif (',' in u_input):
        u_input = u_input.replace(' ','')
        u_input  = u_input.split(',')
        
       
        
        for i in range(len(u_input)):
            d = int(u_input[i])
            
            d_link.append(chapter_link[d])
            d_name.append(chapter_name[d])
            

    else:
        print("error")
    return d_name,d_link

def download_chapter(c_list,c_link,path):
    headers = {
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
  ,'Referer':'https://readmanganato.com/' ,
    "sec-ch-ua-platform": "Windows"}
    
    print("downloading")
    for i in range(len(c_list)):
        r = requests.get(c_link[i])
        soup = BeautifulSoup(r.content,'html5lib')
        div = soup.find('div',attrs={'class':'container-chapter-reader'})
        img = []
        for j in div.findAll('img'):
            
            img.append(j['src'])
        c_list[i] = c_list[i].replace('.','').replace(':','')
        p = path+"/"+c_list[i]
        if not os.path.exists(p):
            os.mkdir(p)
        for a in tqdm(range(len(img)),desc= c_list[i]):
            res = requests.get(img[a],headers = headers)
            f_name = p+"/"+str(a+10)+".jpeg"
            
            with open(f_name,'wb') as f:
                f.write(res.content)
        print("converting to pdf")
        to_pdf(p,path,c_list[i])
        print("Done")
        print('---------------------------------------')
            
def to_pdf(p,path,name):
   

    dirt = sorted(os.listdir(p))
    dirt.sort()
    pdf_path = p+"/"+name+".pdf"
 
    im_list = []
    for image in dirt:
        im = Image.open(p+"/"+image)
        #im = im.resize((1049, 1500))
        im.convert('RGB')
        im_list.append(im)
        if os.path.exists(p+"/"+image): #to remove images after making pdf
            os.remove(p+"/"+image)
    image1 = im_list[0]
    im_list.pop(0)
   
    image1.save(pdf_path,save_all=True,append_images = im_list)
        
        




    
def main():
    url = 'https://mangakakalot.com'
    tle = input("Manga name")
    tle_info,tle_link = search_manga(tle,url)
    z = 0
    for i in range(len(tle_info)):

        print("[",i,"]"," ",tle_info[i],tle_link[i])
        if z==5:
            break
        z = z+1
    print('---------------------------------------')
    
    n = int(input("type number to choose"))
    folder_name = tle_info[n].replace('\n','').replace('?','')
    path = "C:/Users/NAMIT/Desktop/Manga/"+folder_name
    if not os.path.exists(path):
        os.mkdir(path)
    chapter_name , chapter_link,chapter_time = find_chapter(tle_link[n])
    
    for i in range(len(chapter_name)):
        print("[",i,"]"," ",chapter_name[i],'\t',chapter_time[i])
    print('---------------------------------------')
            
        
    chapter_list,nchapter_link = select_chapter(chapter_name,chapter_link)
    download_chapter(chapter_list,nchapter_link,path)
    print('---------------------------------------')
    print("closig in 5 sec")
    time.sleep(5)
    


if __name__ == '__main__':
    main()
