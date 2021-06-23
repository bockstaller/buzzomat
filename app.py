from flask import Flask, send_file, render_template
from pyppeteer import launch
from pathlib import Path


app = Flask(
    __name__,
    static_url_path="/static",
    static_folder="static",
)

caching = False
baseurl = "https://8bb4e6978fc8.ngrok.io"
default_content = "896701"
Path("img").mkdir(parents=True, exist_ok=True)


@app.route("/img/<string:buzz_id>.jpg")
async def test(buzz_id):

    if caching:
        try:
            return send_file("img/" + buzz_id + ".jpg")
        except:
            pass

    browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
    page = await browser.newPage()
    await page.setViewport({"width": 1000, "height": 750})
    url = "http://127.0.0.1:5000/" + buzz_id
    await page.goto(url)
    await page.screenshot({"path": "img/" + buzz_id + ".jpg"})
    await browser.close()
    return send_file("img/" + buzz_id + ".jpg")


@app.route("/<string:buzz_id>")
def index(buzz_id):
    url = baseurl + "/" + buzz_id
    image = baseurl + "/img/" + buzz_id + ".jpg"
    title = "voco-o-mat"
    description = "Das inoffizielle DPSG-Phrasenschwein"
    return render_template(
        "index.html", url=url, image=image, title=title, description=description
    )


@app.route("/")
def index_empty():
    return index(default_content)
