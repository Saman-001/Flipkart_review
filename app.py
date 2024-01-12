from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import csv
import os
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By
import pymongo

application = Flask(__name__) # initializing a flask app
app = application

@app.route('/',methods =['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route('/review',methods = ['POST','GET'])
@cross_origin()

def index():
    if request.method == 'POST':
        try:
            DRIVER_PATH = r"chromedriver.exe"
            #initiating the webdriver
            driver = webdriver.Chrome(DRIVER_PATH)

            searchString = request.form['content'].replace(" ","")

            flipkart_url = "https://www.flipkart.com/search?q=" + searchString

            driver.get(flipkart_url)
            flipkart_page = driver.page_source
            flipkart_html = bs(flipkart_page,'html.parser')
            bigboxes = flipkart_html.findAll('div',{'class': '_1AtVbE col-12-12'})

            del bigboxes[0:3]
            prod_link = "https://www.flipkart.com" + bigboxes[0].div.div.div.a['href']
            driver.get(prod_link)
            prod_page = driver.page_source
            prod_html = bs(prod_page,'html.parser')
            commentboxes = prod_html.find_all('div',{'class': "_16PBlm"})

            filename = searchString+".csv"
            with open (filename,'w',encoding = 'utf-8') as fw:
                headers = ["Price","Product","Customer Name","Rating","Heading","Comment" ]
                writer = csv.DictWriter(fw,headers)
                writer.writeheader()

                reviews = []

                for commentbox in commentboxes:
                    try:
                        price_ele = flipkart_html.select('div._30jeq3 _16Jk6d')[0]
                        price = price_ele.text
                    except:
                        price = "There is no price for this product"
                    try:
                        name = commentbox.div.div.find_all('span' , {'class':'B_NuCI'})[0].text
                    except:
                        name = "No name of this product"
                    try:
                        rating  = commentbox.div.div.find_all('div',{'class':'_3LWZlK _1BLPMq'})[0].text
                    except:
                        rating = "No rating for this product"
                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = "No comment heading for this product"
                    try:
                        comtag = commentbox.div.div.find_all('div',{'class':''})
                        custComment = comtag[0].div.text 
                    except Exception as e:
                        print("Exception while creating dictionary: ",e)
                    mydict = {"Price":price,"Product":searchString,"Customer Name":name,"Rating":rating,"Heading":commentHead,"Comment":custComment}  
                    reviews.append(mydict) 
                
                writer.writerows(reviews)

            
            

            
            client = pymongo.MongoClient("mongodb+srv://saman323:saman323@cluster0.9i3r4fz.mongodb.net/?retryWrites=true&w=majority")
            db = client["Flipkart_scrap"]
            review_col = db['review_scrap_data']
            review_col.insert_many(reviews)
            return render_template('results.html',reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'Something is wrong'
        
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
