import re
import json
import requests
import psycopg2
from bs4 import BeautifulSoup


def create_connection_to_db():

    conn = psycopg2.connect("postgres://postgres:postgres@localhost:5432/postgres")
    cur = conn.cursor()

    return conn, cur

def create_table(conn,cur):
    with open('schema.sql') as f:
        cur.execute(f.read())
        conn.commit()

def get_ean(page_id):

    url = f"https://api.bazaarvoice.com/data/batch.json?passkey=caOo5Zf8xcf0uisM6mgWyAGVCeCntx4AqPZ4XuHhgsCEw&apiversion=5.5&displaycode=15804_3_0-de_de&resource.q0=products&filter.q0=id:eq:{page_id}&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale:eq:de*,de_DE&filter_reviewcomments.q0=contentlocale:eq:de*,de_DE&resource.q1=reviews&filter.q1=isratingsonly:eq:false&filter.q1=productid:eq:{page_id}&filter.q1=contentlocale:eq:de*,de_DE&sort.q1=submissiontime:desc&stats.q1=reviews&filteredstats.q1=reviews&include.q1=authors,products,comments&filter_reviews.q1=contentlocale:eq:de*,de_DE&filter_reviewcomments.q1=contentlocale:eq:de*,de_DE&filter_comments.q1=contentlocale:eq:de*,de_DE&limit.q1=4&offset.q1=0&limit_comments.q1=3&callback"
    Includes = json.loads(requests.get(url).text)['BatchedResults']['q1']['Includes']
    
    en = []
    for item in json.loads(requests.get(url).text)['BatchedResults']:
        Includes = json.loads(requests.get(url).text)['BatchedResults'][item]['Includes']
        if 'Products' in Includes:
            if page_id in Includes['Products']:
                for EANs in Includes['Products'][page_id]['EANs']:
                    en.append(EANs)
        else:
            Results = json.loads(requests.get(url).text)['BatchedResults'][item]['Results']
            if Results != []:
                for res in Results:
                    for EANs in res['EANs']:
                        en.append(EANs)

    return ",".join(list(set(en)))
        

def fetch_data():
    
    values = ""
    insert_query = """
                INSERT INTO gouglas (ern,product_name,page_url,rate,review_count,image,product_ml,price,discount_price,product_lable,art_no,alter,Effekt,Konsistenz,Hauttyp,Eigenschaft,Produktauszeichnung,Produkttyp,Anwendungsbereich,description) VALUES 
            """
    count = 0
    while True:

        url = requests.get(f"https://www.douglas.de/de/c/gesicht/gesichtsmasken/feuchtigkeitsmasken/120308?page={str(count)}")

        soup = BeautifulSoup(url.text, 'html.parser')
        if soup.find_all("a",{"class":"product-tile__main-link"}) == []:
            break

        product_name = ''
        review_count = ''
        product_ml = ''
        image = ''
        price = ''
        discount_price = ''
        art_No = ''
        alter = ''
        effekt = ''
        konsistenz = ''
        hauttyp = ''
        eigenschaft = ''
        produktauszeichnung = ''
        produkttyp = ''
        anwendungsbereich = ''
        description = '' 
       
        for item in soup.find_all("a",{"class":"product-tile__main-link"}):

            link = item['href']
            page_url = 'https://www.douglas.de' + link
            res = requests.get(page_url)

            if res.status_code == 404:
                continue
            soup2 = BeautifulSoup(res.text, 'html.parser')

            if soup2.find("div",{"class":"second-line"}) != None:
                product_name = soup2.find("div",{"class":"second-line"}).text.strip().replace("'",'')
           
            if soup2.find("span",{"class":"product-detail-header__feedback--review-count"}) != None:   
                review_count = int(soup2.find("span",{"class":"product-detail-header__feedback--review-count"}).text.replace(")","").replace("(","").strip())
            
            if soup2.find("div",{"class":"product-detail__variant-name"}) != None:
                product_ml = soup2.find("div",{"class":"product-detail__variant-name"}).text.replace(")","").replace("(","")
           
            if soup2.find("div",{"class":"zoom-image"}) .find("img") != None:
                image = soup2.find("div",{"class":"zoom-image"}).find("img")['src']
            
            if soup2.find("div",{"class":"product-price__strikethrough"}) != None:
                price = soup2.find("div",{"class":"product-price__strikethrough"}).text.strip()
            else:   
                if soup2.find("div",{"class":"product-price__base"}) != None:
                    price = soup2.find("div",{"class":"product-price__base"}).text.strip()
            
            if soup2.find("div",{"class":"product-price__discount product-price__discount"}) != None:
                discount_price = soup2.find("div",{"class":"product-price__discount product-price__discount"}).text.strip()
                
            rate = 0
            for item3 in soup2.find("span",{"class":"rating-stars"}).find_all("svg"):
                rating = item3.find("path")['fill']
                if  rating == '#3cbeaf':
                    rate += 1
                elif  rating == '#3CBEAF':
                    rate += 0.5
            
            product_lable = []
            for label_name in soup2.find_all("span",{"class":"product-label__name"}):
                product_lable.append(label_name.text.strip())
                
            detail = soup2.find("div",{"class":"product-detail-info__classifications"})

            if detail.find(text=re.compile("Art-Nr.")) != None:
                art_No =  detail.find(text=re.compile("Art-Nr.")).next_element.text.strip()
           
            if detail.find(text=re.compile("Alter")) != None:
                alter = detail.find(text=re.compile("Alter")).next_element.text.strip()
           
            if detail.find(text=re.compile("Effekt")) != None:
                effekt = detail.find(text=re.compile("Effekt")).next_element.text.strip()
            
                
            if detail.find(text=re.compile("Konsistenz")) != None:
                konsistenz = detail.find(text=re.compile("Konsistenz")).next_element.text.strip()
         
                
            if detail.find(text=re.compile("Hauttyp")) != None:
                hauttyp = detail.find(text=re.compile("Hauttyp")).next_element.text.strip()
            
            if detail.find(text=re.compile("Eigenschaft")) != None:
                eigenschaft = detail.find(text=re.compile("Eigenschaft")).next_element.text.strip()

            if detail.find(text=re.compile("Produktauszeichnung")) != None:
                produktauszeichnung = detail.find(text=re.compile("Produktauszeichnung")).next_element.text.strip().replace("'",'')
                
            if detail.find(text=re.compile("Produkttyp")) != None:
             
                produkttyp = detail.find(text=re.compile("Produkttyp")).next_element.text.strip()
            
            if detail.find(text=re.compile("Anwendungsbereich")) != None:
                anwendungsbereich = detail.find(text=re.compile("Anwendungsbereich")).next_element.text.strip()
           
            if soup2.find("div",{"class":"truncate__html-container"}) != None:
                description = soup2.find("div",{"class":"truncate__html-container"}).text.strip().replace("'",'')
                
            product_lable = ",".join(product_lable)
            ern = get_ean(link.split("/")[-1].split("?")[0])

            values += f"('{ern}','{product_name}','{page_url}',{rate},{review_count},'{image}','{product_ml}','{price}',\
            '{discount_price}','{product_lable}','{art_No}','{alter}','{effekt}','{konsistenz}','{hauttyp}','{eigenschaft}',\
                '{produktauszeichnung}','{produkttyp}','{anwendungsbereich}','{description}'),"
                
        count += 1 
    conn, cur = create_connection_to_db()
    create_table(conn=conn, cur=cur)
    query = (insert_query + values + " ON").replace(", ON", "")
    cur.execute(query)
    conn.commit()
    conn.close()

fetch_data()
