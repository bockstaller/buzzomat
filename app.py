from flask import Flask, send_file, render_template, request
import sentry_sdk

from sentry_sdk.integrations.flask import FlaskIntegration

from pyppeteer import launch
from pathlib import Path

import asyncio
from dotenv import load_dotenv
import beeline
from beeline.middleware.flask import HoneyMiddleware
import os

from celery import Celery


load_dotenv()

if "caching" in os.environ:
    caching = os.getenv("caching") == True
else:
    raise EnvironmentError

if "baseurl" in os.environ:
    baseurl = os.getenv("baseurl")
else:
    raise EnvironmentError

if "default_content" in os.environ:
    default_content = os.getenv("default_content")
else:
    raise EnvironmentError

if "beeline_api_key" in os.environ:
    beeline_api_key = os.getenv("beeline_api_key")
else:
    raise EnvironmentError

if "dsn" in os.environ:
    dsn = os.getenv("dsn")
else:
    raise EnvironmentError

if "broker" in os.environ:
    broker = os.getenv("broker")
else:
    raise EnvironmentError

Path("img").mkdir(parents=True, exist_ok=True)


if os.getenv("FLASK_ENV") != "development":

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


app = Flask(
    __name__,
    static_url_path="/static",
    static_folder="static",
)
app.config.update(
    CELERY_BROKER_URL=broker,
)
celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)


HoneyMiddleware(app, db_events=False)


@beeline.traced("generate_preview")
async def capture(filename, buzz_id):
    try:
        browser = await launch(
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
            options={"args": ["--no-sandbox"]},
        )
        try:
            os.remove("./" + filename)
        except OSError:
            pass
        page = await browser.newPage()
        await page.setViewport({"width": 1000, "height": 800})
        url = "http://127.0.0.1:5000/loc/" + buzz_id
        await page.goto(url)
        await page.screenshot({"path": filename})
    except Exception as e:
        raise e
    finally:
        await browser.close()
    return


@celery.task
@beeline.traced("run_preview")
def background_image_generation(buzz_id):
    beeline.add_context({"buzz_id": buzz_id})
    beeline.add_context({"socialPreview": True})
    filename = "img/" + buzz_id + ".jpg"
    if os.path.isfile("./" + filename):
        return
    else:
        asyncio.get_event_loop().run_until_complete(capture(filename, buzz_id))

    return filename


@beeline.traced("return_preview")
@app.route("/img/<string:buzz_id>.jpg")
async def image_generation(buzz_id):
    beeline.add_context({"buzz_id": buzz_id})
    beeline.add_context({"socialPreview": True})
    filename = "img/" + buzz_id + ".jpg"
    background_image_generation.delay(buzz_id)
    return send_file(filename)


@beeline.traced("index")
@app.route("/<string:buzz_id>")
def index(buzz_id, local=False):

    beeline.add_context({"socialPreview": False})
    beeline.add_context({"buzz_id": buzz_id})
    print(local)
    if not local:
        print("enter background")
        promise = background_image_generation.delay(buzz_id)
        print(promise)

    url = baseurl + "/" + buzz_id
    image = baseurl + "/img/" + buzz_id + ".jpg"
    title = "voco-o-mat"
    description = "Das inoffizielle DPSG-Phrasenschwein"
    return render_template(
        "index.html", url=url, image=image, title=title, description=description
    )


@beeline.traced("index")
@app.route("/loc/<string:buzz_id>")
def index_local(buzz_id):
    index(buzz_id, local=True)


@app.route("/")
async def index_empty():
    beeline.add_context({"socialPreview": False})
    beeline.add_context({"buzz_id": " "})

    return index(default_content)
