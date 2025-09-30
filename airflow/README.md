Airflow ETL Weather

Comandos úteis
- Subir serviços: `docker compose -f airflow/docker-compose.yaml up -d`
- Ver status: `docker compose -f airflow/docker-compose.yaml ps`
- Logs do Airflow: `docker compose -f airflow/docker-compose.yaml logs -f airflow`
- Parar serviços: `docker compose -f airflow/docker-compose.yaml down`

Primeira inicialização (se necessário)
- Inicializar DB: `docker compose -f airflow/docker-compose.yaml run --rm airflow airflow db init`
- Criar usuário admin:
  `docker compose -f airflow/docker-compose.yaml run --rm airflow \
   airflow users create --username admin --password admin \
   --firstname Admin --lastname User --role Admin --email admin@example.com`

Configurações principais
- Executor: LocalExecutor (não usa Celery/Redis)
- Banco metadata: MySQL em `mysql:3306` (`root`/`root`)
- Fernet key: definida no compose (não alterar após inicializar o DB)
- DAG: `tempo_etl` agenda diário às 09:00 (`schedule: 0 9 * * *`)

Troubleshooting rápido
- Health do webserver: `curl http://localhost:8080/health`
- DAG não aparece: veja `docker exec airflow bash -lc "sed -n '1,200p' /opt/airflow/logs/dag_processor_manager/dag_processor_manager.log"`
- Erro MySQL: confirme que o host no DAG é `mysql` e credenciais `root`/`root`.

