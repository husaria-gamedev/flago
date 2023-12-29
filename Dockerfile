FROM python:3.10
WORKDIR /app

ADD server/requirements.txt .

RUN pip install -r requirements.txt

ADD server/main.py .

CMD ["python3", "-m" , "flask", "--app=main.py",  "run","--host=0.0.0.0"] 
# Or enter the name of your unique directory and parameter set.