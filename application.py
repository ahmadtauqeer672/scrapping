from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

application= Flask(__name__)
app=application

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route('/review', methods=['POST', 'GET'])
def review():
    if request.method == 'POST':
        try:
            search_string = request.form['content'].replace(" ", "")
            flipkart_url = f"https://www.flipkart.com/search?q={search_string}"
            
            # Fetch Flipkart search results
            uclient = uReq(flipkart_url)
            flipkart_page = uclient.read()
            flipkart_html = bs(flipkart_page, "html.parser")
            bigbox = flipkart_html.findAll("div", {"class": "cPHDOP col-12-12"})
            if len(bigbox) < 4:
                return "No results found, please try a different product."

            # Extract first product link
            box = bigbox[3]  # Using index 3 to skip ads
            product_link = "https://www.flipkart.com" + box.div.div.div.a['href']

            # Fetch product page
            product_req = requests.get(product_link)
            product_req.encoding = 'utf-8'
            prod_html = bs(product_req.text, "html.parser")

            # Extract reviews
            comment_box = prod_html.find_all("div", {"class": "RcXBOT"})
            reviews = []
            for comment in comment_box:
                try:
                    name = comment.div.div.find_all("p", {"class": "_2NsDsF AwS1CA"})[0].text
                except:
                    name = "Anonymous"
                try:
                    rating = comment.div.div.div.div.text
                except:
                    rating = "No rating"
                try:
                    comment_head = comment.div.div.p.text
                except:
                    comment_head = "No comment heading"
                try:
                    comment_text = comment.div.div.find_all("div", {"class": ""})[0].div.text
                except:
                    comment_text = "No comment"

                reviews.append({
                    "Product": search_string,
                    "Name": name,
                    "Rating": rating,
                    "CommentHead": comment_head,
                    "Comment": comment_text
                })

            return render_template('result.html', reviews=reviews)

        except Exception as e:
            print(f"Exception occurred: {e}")
            return render_template('error.html', message="Something went wrong, please try again.")

    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
