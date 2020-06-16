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
        productLink = "https://www.flipkart.com/voltas-1-5-ton-3-star-split-inverter-ac-white/p/itme691717dd8f76?pid=ACNFHHUXNFGV6KRG&lid=LSTACNFHHUXNFGV6KRGRZMCIB&marketplace=FLIPKART&spotlightTagId=BestsellerId_j9e%2Fabm%2Fc54&srno=s_1_1&otracker=search&otracker1=search&iid=c96b6e59-480f-4827-b3f1-0973cd12b995.ACNFHHUXNFGV6KRG.SEARCH&ppt=sp&ppn=sp&ssid=n4vkmbw9og0000001590327586001&qH=e2075474294983e0"
        prodRes = requests.get(productLink)
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
                commentHead = commentbox.div.div.div.p.text
            except:
                commentHead = 'No Comment Heading'
            try:
                comtag = commentbox.div.div.find_all('div', {'class': ''})
                custComment = comtag[0].div.text
            except:
                custComment = 'No Customer Comment'
            fw.write(searchString + "," + name.replace(",", ":") + "," + rating + "," + commentHead.replace(",",
                                                                                                            ":") + "," + custComment.replace(
                ",", ":") + "\n")
            mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                      "Comment": custComment}
            x = table.insert_one(mydict)
            reviews.append(mydict)
        return render_template('results.html', reviews=reviews)
    except:
    return 'something is wrong'
    # return render_template('results.html')

else:
return render_template('index.html')
if __name__ == "__main__":
    app.run(debug=True)

