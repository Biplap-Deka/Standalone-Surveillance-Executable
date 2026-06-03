## (1) Create Virtual Environment
            python -m venv venv
### Activate:
            venv\Scripts\activate
## (2) Install Dependencies
          
          pip install opencv-python
          pip install ultralytics
          pip install pandas
          pip install openpyxl
          pip install pyinstaller
          pip install pywhatkit
          
## (3) Verify:
          pip list
## (4) Test Program
    Before creating EXE:
          python surveillance.py
## (5) Create EXE file:
          pyinstaller --onefile --icon camera.ico --add-data "best.pt;." surveillance.py
### Or,
          pyinstaller --onefile --icon camera.ico --add-data "last.pt;." surveillance.py
