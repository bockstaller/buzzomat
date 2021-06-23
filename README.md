# Installation

1. Download repository into home
2. Create venv `cd vocomat && python3 -m venv venv && source venv/bin/activate`
3. Install dependencies `pip3 install -r requirements.txt`
4. Setup nginx `uberspace web backend set / --http --port 5000
5. Copy `flask.ini` to ~/etc/services.d/flask.ini