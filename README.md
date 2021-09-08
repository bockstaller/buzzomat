# Installation

1. Download repository into home
2. Setup .env file
3. Create venv `cd vocomat && python3 -m venv venv && source venv/bin/activate`
4. Install dependencies `pip3 install -r requirements.txt`
5. Add domain `uberspace web domain add vocomat.de`
6. Setup nginx `uberspace web backend set / --http --port 5000`
7. Copy `flask.ini` to `~/etc/services.d/flask.ini`
8. Kick supervisord `supervisorctl reread`, `supervisorctl update` `supervisorctl status`
