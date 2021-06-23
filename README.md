# Installation

1. Download repository into home
2. Setup .env file
3. Create venv `cd vocomat && python3 -m venv venv && source venv/bin/activate`
4. Install dependencies `pip3 install -r requirements.txt`
5. Setup nginx `uberspace web backend set / --http --port 5000`
6. Copy `flask.ini` to ~/etc/services.d/flask.ini
7. Kick supervisord `supervisorctl reread`, `supervisorctl update` `supervisorctl status`