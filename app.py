from flask import Flask, send_file, render_template
import sentry_sdk

from sentry_sdk.integrations.flask import FlaskIntegration

from pyppeteer import launch
from pathlib import Path

from dotenv import load_dotenv
import beeline
from beeline.middleware.flask import HoneyMiddleware
import os


load_dotenv()

caching = os.getenv("caching")
baseurl = os.getenv("baseurl")
default_content = os.getenv("default_content")
beeline_api_key = os.getenv("beeline_api_key")
dsn = os.getenv("dsn")


Path("img").mkdir(parents=True, exist_ok=True)


sentry_sdk.init(
    dsn=dsn,
    integrations=[FlaskIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # By default the SDK will try to use the SENTRY_RELEASE
    # environment variable, or infer a git commit
    # SHA as release, however you may want to set
    # something more human-readable.
    # release="myapp@1.0.0",
)


beeline.init(
    writekey=beeline_api_key,
    # The name of your app is a good choice to start with
    dataset="vocomat",
    service_name="vocomat-app",
    debug=False,  # defaults to False. if True, data doesn't get sent to Honeycomb
)


app = Flask(
    __name__,
    static_url_path="/static",
    static_folder="static",
)
HoneyMiddleware(app, db_events=False)


@app.route("/img/<string:buzz_id>.jpg")
async def test(buzz_id):
    beeline.add_context({"buzz_id": buzz_id})

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
    beeline.add_context({"buzz_id": buzz_id})
    print(baseurl)
    print(buzz_id)
    url = baseurl + "/" + buzz_id
    image = baseurl + "/img/" + buzz_id + ".jpg"
    title = "voco-o-mat"
    description = "Das inoffizielle DPSG-Phrasenschwein"
    return render_template(
        "index.html", url=url, image=image, title=title, description=description
    )


@app.route("/")
def index_empty():
    beeline.add_context({"buzz_id": " "})
    print(default_content)

    return index(default_content)
