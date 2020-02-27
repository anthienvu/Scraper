from bs4 import BeautifulSoup
import requests
import pandas as pd
from validate_email import validate_email
from bs4.element import Comment


USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

              
def fetch_results(search_term, number_results, language_code,sup_page=None):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'

    escaped_search_term = search_term.replace(' ', '+')
    if type(sup_page)==str:
        sup_page_term = sup_page.replace(' ', '+')
        escaped_search_term = escaped_search_term + '+' + sup_page_term

    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
 
    return search_term, response.text
    
    
def parse_results(html, keyword):
    soup = BeautifulSoup(html, 'html.parser')
 
    found_results = pd.DataFrame(columns = ['keyword', 'title', 'rank', 'link'])
    rank = 1
    result_block = soup.find_all('div', attrs={'class': 'g'})
    for result in result_block:
 
        link = result.find('a', href=True)
        title = result.find('h3')
        #description = result.find('span', attrs={'class': 'st'})
        if link and title:
            link = link['href']
            title = title.get_text()
            #if description:
            #    description = description.get_text()
            if link != '#':
                found_results=found_results.append({'keyword': keyword,'title':title,'rank':rank,'link':link},ignore_index=True)
                rank += 1
    return found_results
    
    
def scrape_google(search_term, number_results, language_code,sup_page=None,info=["Điện thoại", "Email"]):
    try:
        keyword, html = fetch_results(search_term, number_results, language_code,sup_page)
        results_list = parse_results(html, keyword)
        
        return results_list
    except AssertionError:
        raise Exception("Incorrect arguments parsed to function")
    except requests.HTTPError:
        raise Exception("You appear to have been blocked by Google")
    except requests.RequestException:
        raise Exception("Appears to be an issue with your connection")
        
        
def get_info_wiki(link,info=["Điện thoại", "Email"]):
    request = requests.get(link)
    html = BeautifulSoup(request.text)
    table = html.find_all('table',{'class':'infobox'})[0]
    tr_list = table.find_all('tr')
    result = {}
    for tr in tr_list:
        if tr.find('th'):
            if tr.find('th').text in info:
                result[tr.find('th').text] = tr.find('td').text
    return result
    

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    #soup = BeautifulSoup(body, 'html.parser')
    texts = body.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)
    

def getFullText(html,part='body'):
    texts =html.find(part)
    texts = text_from_html(texts)
    return texts
    
    
def getVaildEmail(texts):
    texts_list = texts.split(" ")
    mail_list = []
    for text in texts_list:
        if validate_email(text):
            mail_list.append(text)
    return mail_list
    
    
def getPhoneNumber(texts):
    texts = texts.split(" ")
    number_phones = []
    for i in range(len(texts)):
        text = texts[i].replace(".","")
        if 7<=len(text)<=11 and text.isdigit():
            number_phones.append(text)
            continue
        if "84" in texts[i]:
            if texts[i+1].isdigit():
                if text[i+2].isdigit():
                    number_phones.append(texts[i] + texts[i+1] + texts[i+2])
                else:
                    number_phones.append(texts[i] + texts[i+1])
    return number_phones
    
    
def runScraper(text):
    number_result = 30
    results = scrape_google(text, number_result, 'vi')

    info_list = pd.DataFrame(columns = ['Title', 'Email', 'Phone'])
    for link, title in zip(results['link'], results['title']):
        try:
            request = requests.get(link)
            html = BeautifulSoup(request.text, "lxml")
            texts = getFullText(html)
            try:
                emails = getVaildEmail(texts)
                emails = list(set(emails))
            except:
                pass
            try:
                number_phone = getPhoneNumber(texts)
                number_phone = list(set(number_phone))
            except:
                pass
            info_list = info_list.append({'Title':title,'Email':emails,'Phone':number_phone}, ignore_index = True)
        except:
            pass
        
    info_list['Email'] = info_list['Email'].str.join(';')
    info_list['Phone'] = info_list['Phone'].str.join(';')
    
    return info_list
    
    
    