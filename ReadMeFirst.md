# What we do
## 1.Install environment
## 2.Install DB or create DB from script.
## 2.Run app
## 3.Call internal API
## 4.Build docker file
## 5.Run app and call 

docker build -t my-python-app .

docker build -t my-python-app:latest .
docker run -p 5000:5000 my-python-app


pip install sqlacodegen
sqlacodegen postgresql://username:password@localhost:5432/mydatabase --outfile models.py

sqlacodegen postgresql://admin:admin@127.0.0.1:54320/postgres --schema esg --outfile esg_models.py

(Base) -> (db.Model)

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


docker rmi $(docker images -q my-python-app --filter "dangling=false" --filter "label!=keep") 2>/dev/null





# Calculate sentiment stats -> redundant?

esg_sentiment_climatebert_ -> return no data