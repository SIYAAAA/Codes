from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
import pymongo
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)


app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

app.route('/review', methods=['POST'])
def reviews():
    searchString = request.form['content'].replace(" ","")
    dbConn = pymongo.MongoClient("mongodb://localhost:27017/")  # opening a connection to Mongo
    db = dbConn['crawlerDB']
    reviews = db[searchString].find({})
    if reviews.count() > 0:
        return render_template('results.html', reviews=reviews)
    else:
        flipkart_url = "https://www.flipkart.com/search?q=" + searchString
        uClient = uReq(flipkart_url)
        flipkartPage = uClient.read()
        uClient.close()
        flipkart_html = bs(flipkartPage, "html.parser")
        bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})
        del bigboxes[0:2]
        box = bigboxes[0]
        productlink="https://www.flipkart.com" + box.div.div.div.a['href']
        prodRes = requests.get(productlink)
        prod_html = bs(prodRes.text, "html.parser")
        commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"})

        table = db[searchString]
        filename = searchString + ".csv"
        fw = open(filename, "w")
        headers = "Product, Customer Name, Rating, Heading, Comment \n"
        fw.write(headers)
        reviews = []
        for commentbox in commentboxes:
            try:
                name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text

            except:
                name = 'No Name'

            try:
                rating = commentbox.div.div.div.div.text
            except:
                rating = 'No Rating'

            try:
                commenthead = commentbox.div.div.div.p.text
            except:
                commenthead = 'No Comment Heading'
            try:
                comtag = commentbox.div.div.find_all('div', {'class': ''})
                custcomment = comtag[0].div.text
            except:
                custcomment = 'No Customer Comment'
                fw.write(searchString + "," + name.replace(",", ":") + "," + rating + "," + commenthead.replace(",",
                                                                                                            ":") + "," + custcomment.replace(
                ",", ":") + "\n")
                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commenthead,
                      "Comment": custcomment}
                x = table.insert_one(mydict)
                reviews.append(mydict)
                return render_template('results.html', reviews=reviews)


if __name__ == "__main__":
    app.run(debug=True)

