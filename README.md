ETLWeather — Airflow ETL de Clima

Resumo
- Pipeline ETL no Apache Airflow que coleta clima atual de cidades via OpenWeather API e grava em MySQL.
- Ambiente dockerizado com `airflow` (webserver + scheduler) e `mysql`.

Stack
- Apache Airflow 2.7.2 (LocalExecutor)
- MySQL 8
- Python (requests, pandas, SQLAlchemy, PyMySQL)
- Docker Compose

Estrutura do Projeto
- `airflow/` — Infra e código do Airflow
  - `airflow/docker-compose.yaml` — Compose do ambiente
  - `airflow/Dockerfile` — Imagem do serviço `airflow`
  - `airflow/dags/tempo_etl.py` — DAG principal (ETL de clima)
  - `airflow/README.md` — Comandos e dicas específicas do Airflow
- `volumes/` — (criado pelo Docker) dados persistentes do MySQL

Pré‑requisitos
- Docker e Docker Compose
- Porta `8080` livre (UI do Airflow) e `3307` para MySQL host

Subir o Ambiente
- `docker compose -f airflow/docker-compose.yaml up -d`
- UI: http://localhost:8080 (login: `admin` / `admin`)

Primeira Inicialização (se necessário)
- Inicializar DB do Airflow:
  `docker compose -f airflow/docker-compose.yaml run --rm airflow airflow db init`
- Criar usuário admin:
  `docker compose -f airflow/docker-compose.yaml run --rm airflow \
   airflow users create --username admin --password admin \
   --firstname Admin --lastname User --role Admin --email admin@example.com`

DAG: tempo_etl
- Caminho: `airflow/dags/tempo_etl.py`
- Agenda: diário às 09:00 (cron `0 9 * * *`)
- Fluxo:
  - `extract_data`: consulta OpenWeather API para as cidades configuradas
  - `process_data`: normaliza e prepara DataFrame
  - `load_data`: grava em MySQL (`WeatherData` e `Cities`)

Configuração
- Executor: LocalExecutor (não requer Celery/Redis)
- Banco metadata (Airflow): MySQL `mysql:3306` (`root`/`root`)
- Conector MySQL (DAG): `mysql+pymysql` para host `mysql`
- Fernet Key: definida em `AIRFLOW__CORE__FERNET_KEY` no compose

Variáveis/Segredos
- OpenWeather API Key atualmente definida dentro do DAG (`API_KEY`).
  - Recomendado: mover para Variable do Airflow (`Admin > Variables`) ou env var e ler via `os.environ`.

Comandos Úteis
- Status dos serviços: `docker compose -f airflow/docker-compose.yaml ps`
- Logs do Airflow: `docker compose -f airflow/docker-compose.yaml logs -f airflow`
- Desligar: `docker compose -f airflow/docker-compose.yaml down`
- Listar DAGs: `docker exec airflow airflow dags list`
- Despausar/Executar DAG: `docker exec airflow airflow dags unpause tempo_etl && docker exec airflow airflow dags trigger tempo_etl`

Troubleshooting
- UI não abre: verifique `docker compose -f airflow/docker-compose.yaml logs --tail=200 airflow`
- DAG não aparece: `docker exec airflow bash -lc "sed -n '1,200p' /opt/airflow/logs/dag_processor_manager/dag_processor_manager.log"`
- Erro de driver MySQL: confirme que a URL usa `mysql+pymysql` e que `PyMySQL` está instalado na imagem (Dockerfile).
- Erro de Fernet: a chave deve ser 32 bytes base64 url‑safe; alterá-la após inicialização exige reinicializar metadata.

Próximos Passos (opcional)
- Migrar `API_KEY` do DAG para Variables/Connections.
- Adicionar validação/unique keys nas tabelas MySQL e `if_exists='append'`/`replace` conforme necessidade.
- Adicionar testes simples de DAG com `airflow dags test`.
