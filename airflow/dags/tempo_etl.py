from airflow import DAG
from airflow.operators.python import PythonOperator # pyright: ignore[reportMissingImports]
from datetime import datetime, timedelta
import requests
import pandas as pd
from sqlalchemy import create_engine

# ------------------------------
# Configurações iniciais
# ------------------------------
API_KEY = 'd7bf832c29e1c11a07d8ee3f29f9dcd8'  
CITIES = ['Porto Alegre', 'São Paulo', 'Rio de Janeiro']
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_HOST = 'mysql'
MYSQL_DB = 'tempo_db'

# ------------------------------
# Funções das tarefas
# ------------------------------
def extract_data():
    all_data = []
    for city in CITIES:
        params = {'q': city, 'appid': API_KEY}
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            all_data.append(response.json())
    return all_data  # retorna lista de dicionários

def process_data(ti):
    data = ti.xcom_pull(task_ids='extract_data')
    records = []
    for item in data:
        main = item['main']
        weather = item['weather'][0]
        record = {
            'city_id': item['id'],
            'city_name': item['name'],
            'temperature': round(main['temp'] - 273.15, 2),      # Kelvin → Celsius
            'feels_like': round(main['feels_like'] - 273.15, 2),
            'temp_min': round(main['temp_min'] - 273.15, 2),
            'temp_max': round(main['temp_max'] - 273.15, 2),
            'pressure': main['pressure'],
            'humidity': main['humidity'],
            'weather_code': weather['id'],
            'weather_main': weather['main'],
            'weather_description': weather['description']
        }
        records.append(record)
    df = pd.DataFrame(records)
    ti.xcom_push(key='processed_data', value=df.to_dict(orient='records'))

def load_data(ti):
    engine = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:3306/{MYSQL_DB}"
    )
    records = ti.xcom_pull(task_ids='process_data', key='processed_data')
    df = pd.DataFrame(records)
    df.to_sql('WeatherData', con=engine, if_exists='append', index=False)
    df_cities = df[['city_id','city_name']].drop_duplicates()
    df_cities.to_sql('Cities', con=engine, if_exists='append', index=False)

# ------------------------------
# Definição do DAG
# ------------------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'tempo_etl',
    default_args=default_args,
    description='ETL diário de dados meteorológicos',
    schedule='0 9 * * *', 
    catchup=False
)

# ------------------------------
# Definição das tarefas
# ------------------------------
t1 = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag
)

t2 = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    dag=dag
)

t3 = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag
)

t1 >> t2 >> t3

# ------------------------------
# Ordem de execução
# ------------------------------
