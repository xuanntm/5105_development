# What we do
prerequisite thi

## 1.Install environment
move to the folder where you want to work
> 1. Clone code from github  
> $ git clone https://github.com/xuanntm/5105_development.git
> 2. Move to Git project  
> $ cd 5105_development
> 3. Create environment  
> $ python -m venv .venv  
> $ source .venv/bin/activate  
> $ pip install -r requirements.txt  
> 4. Create .env file with the some config
> SQLALCHEMY_DATABASE_URI=postgresql://admin:admin@127.0.0.1:54320/postgres  
> NEWSAPI_KEY={{YOUR_NEWS_API_KEY}}  
> BING_API_KEY={{YOUR_BING_API_KEY}}  
> 5. Download model  
> $ python src/config/model_config.py
> 6. Start environment  
> $ python backend_app.py
> 7. 
## 2.Install DB or create DB from script.
> 1. Dictionary table  
> esg_index_metric  
> esg_benchmark  
> company_profile  
> b_esg_cluster_analyis_actual_demo  
> b_esg_financial_metrics  
> b_esg_merged_financial_metrics  
> b_esg_metric_data_extracted  
> b_esg_with_trend_features  
> 2. 
## 2.Run app
## 3.Call internal API
## 4.Build docker file
## 5.Run app and call 

docker build -t my-python-app .

docker build -t my-python-app:latest .
docker run -p 5000:5000 my-python-app


## 6.

pip install sqlacodegen
sqlacodegen postgresql://username:password@localhost:5432/mydatabase --outfile models.py

sqlacodegen postgresql://admin:admin@127.0.0.1:54320/postgres --schema esg --outfile esg_models.py


sqlacodegen sqlite:////Users/XuanNguyen/Documents/NUS/DSS5105/esg.sqlite --outfile esg_sqlite_models.py

sqlacodegen --generator tables sqlite:////Users/XuanNguyen/Documents/NUS/DSS5105/esg.sqlite --outfile esg_sqlite_models.py


declarative, dataclasses, tables


SQLALCHEMY_DATABASE_URI_bk=postgresql://admin:admin@127.0.0.1:54320/postgres

SQLALCHEMY_DATABASE_URI=sqlite:////Users/XuanNguyen/Documents/NUS/DSS5105/esg.sqlite



(Base) -> (db.Model)

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


docker rmi $(docker images -q my-python-app --filter "dangling=false" --filter "label!=keep") 2>/dev/null





# Calculate sentiment stats -> redundant?

esg_sentiment_climatebert_ -> return no data