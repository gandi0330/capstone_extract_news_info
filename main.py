from selenium import webdriver
from bs4 import BeautifulSoup
from krwordrank.sentence import summarize_with_sentences
from notion.client import *
from notion.block import *
from datetime import datetime
from krwordrank.word import KRWordRank
from textrank import KeywordSummarizer
from textrank import KeysentenceSummarizer
from konlpy.tag import Komoran
# 언론사 : 중앙일보
# 언론사 랭킹 페이지의 상위 5개 기사를 크롤링

komoran = Komoran()
news_naver_url = 'https://news.naver.com'


def komoran_tokenizer(sent):
    words = komoran.pos(sent, join=True)
    words = [w for w in words if ('/NN' in w or'XR' in w or 'VA' in w or  '/VV' in w)]
    return words

def get_day():
    now = datetime.now()
    day = f"{now.year}년 {now.month}월 {now.day}일 {now.hour:02}시"

    return day

def add_page(news):
    client = NotionClient(
        token_v2="f10e360c3a7c361fbd31374cb9aae04182bd722c88f7a22b50d43764a62a76339b9ecf5c75ba24b73e48b82f6782216cb64e17f136cf60111bb7e24dfa5d3992abed023b83926c4e53e530807b2f")
    notion_url1 = 'https://www.notion.so/defbfed3d23d4261895352f7fcfb3483'
    homepage1 = client.get_block(notion_url1)

    day = get_day()
    for i in homepage1.children[3:] : i.remove()

    homepage1.children.add_new(TextBlock, title=day+'에 만들어진 데이터 입니다.')
    homepage1.children.add_new(TextBlock, title='')

    for news_list in news:
        summary_list=[str(i[0]) for i in news_list[5]]
        keyword_list=[str('#'+i.split('.')[0]+' ')for i in news_list[4]]

        sub_header=homepage1.children.add_new(SubheaderBlock)
        sub_header.title = news_list[0]+'\n'+''.join(keyword_list)

        toggle= homepage1.children.add_new(ToggleBlock)
        toggle.title = '요약문, 원문 보기'

        toggle.children.add_new(TextBlock,title='')
        toggle.children.add_new(SubsubheaderBlock,title='요약문')
        toggle.children.add_new(BulletedListBlock, title=summary_list[0])
        toggle.children.add_new(BulletedListBlock, title=summary_list[1])
        toggle.children.add_new(BulletedListBlock, title=summary_list[2])
        toggle.children.add_new(TextBlock,title='')
        toggle.children.add_new(SubsubheaderBlock, title='본문')
        toggle.children.add_new(TextBlock,title=news_list[1])

        homepage1.children.add_new(TextBlock,title='')
        homepage1.children.add_new(TextBlock,title='')




def add_page_textrank(sen,key,news):
    client = NotionClient(
        token_v2="f10e360c3a7c361fbd31374cb9aae04182bd722c88f7a22b50d43764a62a76339b9ecf5c75ba24b73e48b82f6782216cb64e17f136cf60111bb7e24dfa5d3992abed023b83926c4e53e530807b2f")
    notion_url2 = 'https://www.notion.so/textrank-615ed4d640e04625a819f2e1715e7821'

    homepage2 = client.get_block(notion_url2)
    day = get_day()
    for i in homepage2.children[3:]: i.remove()

    homepage2.children.add_new(TextBlock, title=day + '에 만들어진 데이터 입니다.')
    homepage2.children.add_new(TextBlock, title='')

    for index,news_list in enumerate(news):
        summary_list = [i for i in sen[index]]
        keyword_list = ['#' + str(i) + ' ' for i in key[index]]

        sub_header = homepage2.children.add_new(SubheaderBlock)
        sub_header.title = news_list[0] + '\n' + ''.join(keyword_list)

        toggle = homepage2.children.add_new(ToggleBlock)
        toggle.title = '요약문, 원문 보기'

        toggle.children.add_new(TextBlock, title='')
        toggle.children.add_new(SubsubheaderBlock, title='요약문')
        toggle.children.add_new(BulletedListBlock, title=summary_list[0])
        toggle.children.add_new(BulletedListBlock, title=summary_list[1])
        toggle.children.add_new(BulletedListBlock, title=summary_list[2])
        toggle.children.add_new(TextBlock, title='')
        toggle.children.add_new(SubsubheaderBlock, title='본문')
        toggle.children.add_new(TextBlock, title=news_list[1])

        homepage2.children.add_new(TextBlock, title='')
        homepage2.children.add_new(TextBlock, title='')


#각 언론사에 해당하는 url을 넣으면 언론사의 뉴스 순위 페이지에서 순서대로 url을 크롤링하는 함수
def news_url_crawl(press_url):
    news_url_li = []
    news_url_sample = []

    driver = webdriver.Chrome(executable_path='chromedriver')
    driver.get(url=news_naver_url + press_url)

    rankpage_html= driver.page_source
    soup=BeautifulSoup(rankpage_html,"html.parser")
    content_html= soup.find_all('div',{'class':'list_content'})

    for i in content_html:
        a_class = i.find('a')
        news_url_li.append(a_class.attrs['href'])
        news_url_sample = news_url_li[0:5]
    driver.close()
    return news_url_sample

# 중앙일보 전용 추출함수 ( 뉴스 제목과 내용 추출 )
def 중앙일보_extract_newsdata (news_link):
    news = []
    driver = webdriver.Chrome(executable_path='chromedriver')

    for i in news_link:
        title = ''
        content = ''
        stopwords_중앙일보 = ['본문 내용 ', 'TV플레이어 ', '// TV플레이어 ', '// 본문 내용 ', '', ' ','▶ ']

        driver.get(url=news_naver_url+i)
        news_html = driver.page_source
        soup=BeautifulSoup(news_html,"html.parser")

        title =soup.find('h3',{'class':'tts_head'}).text
        content_all= soup.find(attrs={'id':'articleBodyContents'})

        for child in content_all.children:
            if str(child.name) == 'None' or str(child.name) == 'span' :
                string=str(child.string).lstrip()
                if string not in stopwords_중앙일보:
                    content = content + string

        news.append([title,content,news_naver_url+i])

    driver.close()
    news = 중앙일보_split_sentence(news)

    return news


# 내용을 문장단위로 끊어주는 함수
# news[[title,content,url],..] -> news[[title,[sentence,sentence ...],url],..]
def 중앙일보_split_sentence(news):

    for i in news:
        content = i[1].split('다.')
        for sentence in range(len(content)-1):
            content[sentence]=content[sentence].lstrip()+'다.'
        i.append(content[:len(content)-1])

    return news

def extract_key_sen_textrank(news):
    keyword_extractor = KeywordSummarizer(
        tokenize=komoran_tokenizer,
        min_count=3

    )
    summarizer = KeysentenceSummarizer(tokenize = komoran_tokenizer)

    textrank_sentences= []
    textrank_keywords=[]
    for i in news:
        keysents = summarizer.summarize(i[3],topk=3)
        keywords = keyword_extractor.summarize(i[3],topk=5)
        keywords = [j[0].split('/')[0] for j in keywords]
        textrank_sentences.append([i[2] for i in keysents])
        textrank_keywords.append(keywords)
    return textrank_sentences,textrank_keywords


# news[[title,[sentence, ..],url]..] -> news[[title,[sentences],url,extract_keys,extract_sentences]..]
def extract_key_sen(news):
    stopwords = {'했다', '있다', '하다', '었다','했다.','굉장히','말했다.','지난'}


    for i in news:

        keywords,smz_sentences = summarize_with_sentences(
            i[3],
            stopwords=stopwords,
            min_count = 3,
            num_keywords =5,
            num_keysents=3,
            diversity=0.3,
            verbose=False,
            penalty = lambda x:0 if (25 <= len(x) <= 80) else 1
        )
        keywords = list(keywords.keys())

        i.append(keywords)
        i.append(smz_sentences)

    return news

# 요약된 문장을 기사 원문과 비교하여 인덱스를 붙이고 순서대로 정렬하는 함수
def sort_extract_sen(news):

    for i in news:
        new_extract_sen = []

        for j in i[5] :
            num=i[3].index(j)
            new_extract_sen.append([j,num])
        new_extract_sen = sorted(new_extract_sen, key=lambda x : x[1])

        i[5]= new_extract_sen


def 중앙일보_crawl():
    중앙일보_url = '/main/ranking/office.nhn?officeId=025'

    중앙일보url_list = news_url_crawl(중앙일보_url) # url['기사 url','기사 url'...]
    news_middle = 중앙일보_extract_newsdata(중앙일보url_list) # news_middle = [[title,[sentences]] , [title,[...]]]

    news_last = extract_key_sen(news_middle) # news_last = [[title,[sentences],[keywords],[summarize sentences], ..]
    sort_extract_sen(news_last)
    return news_last


def measure_kr(keywords, sentences):
    ref = len(keywords)
    hyp = 0
    sen = ''


    sentences = [i[0] for i in sentences]

    for i in sentences:
        sen += i

    for i in keywords:

        if i in sen:
            hyp += 1

    recall = hyp / ref
    return recall

def measure_text(keywords, sentences):
    ref = len(keywords)
    hyp = 0
    sen = ''

    for i in sentences:
        sen +=i

    for i in keywords:

        if i in sen:
            hyp += 1

    recall = hyp / ref
    return recall





def print_element(news_data):

    for i in news_data:
         print('title : '+i[0])
         print('content : ',end='')
         print(i[3])
         print('url : '+i[2])
         print('keyword : ',end='')
         print(i[4])
         print('extract_sentences : ',end='')
         print(i[5])


def print_notion(news_data):
    sen, key = extract_key_sen_textrank(news_data)
    add_page(news_data)
    add_page_textrank(sen,key,news_data)



def print_performance(news_data):

    avg_wordrank = 0
    avg_textrank = 0

    for i in news_data:
        avg_wordrank += measure_kr(i[4],i[5])


    for i in range(5):
        sen, key = extract_key_sen_textrank(news_data)
        avg_textrank +=measure_text(key[i],sen[i])

    avg_wordrank = avg_wordrank/5
    avg_textrank = avg_textrank/5

    print(f'kr-wordrank : {avg_wordrank}')
    print(f'textrank : {avg_textrank}')



if __name__=='__main__':
    news_data = 중앙일보_crawl()
    print_element(news_data)
    print_performance(news_data)

# 1 title str
# 2 content str
# 3 url str
# 4 content list [ sentences ]
# 5 keyword [ keywords ]
# 6 summary sentence [[ sentence , index ],]