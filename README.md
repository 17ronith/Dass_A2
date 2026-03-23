Dass A2

Dependencies

- Python 3.8+
- pytest (for tests)
- requests (for blackbox tests)

Install:
- pip install pytest requests

How to run the code

Whitebox (Moneypoly):
- Run: python whitebox/code/main.py

Integration (StreetRace Manager):
- Run the scenario script: python integration/tests/integration_tests.py

Blackbox (QuickCart API tests):
- Start the QuickCart service (must be running at http://localhost:8080 by default).
- Optional env vars: QUICKCART_BASE_URL, QUICKCART_ROLL, QUICKCART_USER_ID.

How to run the tests

- Whitebox: PYTHONPATH=whitebox/code python -m pytest whitebox/tests
- Integration: PYTHONPATH=integration/code python integration/tests/integration_tests.py
- Blackbox: python -m pytest blackbox/tests
