# Lightweight AWS ETL with Docker, Terraform, S3, and Postgres

This is a small but realistic data engineering project designed to run on AWS Free Tier and local Docker. It builds an end-to-end ETL pipeline that moves data from a local CSV file into AWS S3 and then into a Postgres database running in Docker.

## Architecture

- **Data source**
  - `data/input.csv` (local test data)

- **Storage**
  - S3 raw bucket: `${project_name}-raw`
  - S3 processed bucket: `${project_name}-processed`

- **Compute**
  - `etl_extract` container
    - Reads local CSV with pandas
    - Adds a `load_timestamp` column
    - Uploads processed CSV to `s3://RAW_BUCKET_NAME/input/...`
  - `etl_transform` container
    - Finds the latest CSV in the S3 raw bucket
    - Reads it into pandas
    - Loads data into Postgres table `fact_payments` using SQLAlchemy
    - Uses a staging table and `ON CONFLICT` upsert to avoid duplicates

- **Database**
  - Postgres running in Docker, initialized by `db/init.sql` with table:
    - `fact_payments(id, date, amount, load_timestamp)`

- **Infrastructure (Terraform)**
  - Creates S3 raw and processed buckets
  - Creates an IAM user with access limited to these buckets
  - Creates IAM access keys and exposes them as Terraform outputs

- **Orchestration**
  - Docker Compose to run Postgres and ETL containers
  - Makefile with shortcuts for Terraform and ETL commands

## Prerequisites

- Docker and Docker Compose
- Terraform
- AWS account
- AWS CLI configured with a profile that Terraform will use

## Setup

You’re right: the steps look broken because fences and headings aren’t closed/structured cleanly.

Here’s a **fixed, clean section** you can paste over your current “Setup” + “Running the ETL” parts. It keeps the same content but with correct Markdown and formatting.

```markdown
## Setup

### 1. Clone repo and configure AWS

```bash
git clone https://github.com/vijayaleti/aws-docker-etl-s3-postgres.git
cd aws-docker-etl-s3-postgres
```

Make sure your AWS CLI is configured (for example, run `aws configure` and use the `default` profile).

### 2. Provision AWS infrastructure with Terraform

```bash
cd infra
terraform init
terraform apply
```

After `terraform apply` completes, note these outputs:

- `etl_access_key_id`
- `etl_secret_access_key`
- `raw_bucket_name`
- `processed_bucket_name`

### 3. Create `.env` in repo root

Back in the repo root (one level above `infra`), create a `.env` file:

```env
AWS_ACCESS_KEY_ID=YOUR_ETL_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_ETL_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION=us-east-1

RAW_BUCKET_NAME=your-raw-bucket-name
PROCESSED_BUCKET_NAME=your-processed-bucket-name

POSTGRES_USER=etl_user
POSTGRES_PASSWORD=etl_password
POSTGRES_DB=etl_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Replace the placeholders with the actual Terraform output values.

### 4. Prepare sample CSV data

From the repo root:

```bash
mkdir -p data
cat > data/input.csv << 'EOF'
id,date,amount
1,2024-01-01,10.50
2,2024-01-02,20.00
3,2024-01-03,15.25
EOF
```

You can change these values later to test upsert behavior.

### 5. Start Postgres with Docker Compose

```bash
docker compose up -d db
```

This starts the Postgres container, runs `db/init.sql`, and creates the `fact_payments` table.

## Running the ETL

### Step 1: Extract (local CSV → S3 raw)

```bash
docker compose run --rm etl_extract
```

This will:

- Read `data/input.csv` with pandas  
- Add a `load_timestamp` column  
- Write a processed CSV to `s3://RAW_BUCKET_NAME/input/processed_<uuid>.csv`

### Step 2: Transform and load (S3 raw → Postgres)

```bash
docker compose run --rm etl_transform
```

This will:

- Find the latest CSV in `s3://RAW_BUCKET_NAME/input/`  
- Read it into pandas  
- Load rows into a staging table in Postgres  
- Upsert into `fact_payments` using `ON CONFLICT (id) DO UPDATE`

### Step 3: Verify data in Postgres

```bash
docker exec -it etl_db psql -U etl_user -d etl_db -c "SELECT * FROM fact_payments ORDER BY id;"
```
To test the upsert logic, change `data/input.csv` to include an existing `id` with a new `amount` and some new `id`s, re-run extract + transform, and query the table again. Existing rows are updated; new rows are inserted.

## Using the Makefile (optional shortcuts)

A `Makefile` is included in the repo root with common commands.

Examples:

```bash
# Terraform
make infra-init      # terraform init
make infra-plan      # terraform plan
make infra-apply     # terraform apply
make infra-destroy   # terraform destroy

# Docker / ETL
make docker-up       # docker compose up -d db
make etl-extract     # run extract step
make etl-transform   # run transform step
make etl-all         # run extract + transform
make docker-down     # docker compose down

### Notes
Buckets are minimal and private, so they fit AWS Free Tier usage.

IAM user is limited to the raw and processed buckets following least-privilege practices.

The staging + upsert pattern makes the load idempotent and closer to real-world data engineering pipelines.

You can extend this project with:

Additional transformations and quality checks

Moving or copying files from raw to processed bucket after successful load

Scheduled runs via cron, ECS, or workflows in a future iteration.

