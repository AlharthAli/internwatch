# InternWatch

An automated pipeline that continuously discovers software engineering internship
postings from real company job boards, deduplicates them, and keeps a running
record of what it finds.

## The problem

Checking dozens of individual company career pages for new internship postings
is repetitive and easy to fall behind on. InternWatch automates that check,
running on its own, in the background, without needing to be manually
triggered.

## How it works

1. **Discovery** — every 30 minutes, an AWS Lambda function polls the
   [Greenhouse](https://developers.greenhouse.io/job-board.html) public job
   board API for each company in a tracked list, pulling the current list of
   open roles.
2. **Filtering** — each job title is checked against a word-boundary regex
   (`\bintern\b`) combined with an "engineer" keyword match, correctly
   distinguishing genuine internship postings (e.g. "Software Engineer,
   Intern") from unrelated roles that merely contain "intern" as a substring
   (e.g. "Internal Product Engineer").
3. **Deduplication** — every posting has a real, unique ID from Greenhouse.
   Before inserting a new record, the pipeline checks whether that ID already
   exists in the database. A `UNIQUE` constraint on the column enforces this
   at the database level as a second line of defense.
4. **Persistence** — new postings are stored in PostgreSQL (company, title,
   location, application link, and discovery timestamp), building a
   permanent, queryable history rather than a one-time snapshot.
5. **Export** — a separate script reads the current database contents and
   writes them to an Excel spreadsheet, giving a plain, shareable view of
   discovered postings without requiring direct database access.

## Architecture

```
EventBridge (30-minute schedule)
        |
        v
   AWS Lambda  --->  Greenhouse Job Board APIs (per tracked company)
        |
        v
  PostgreSQL (RDS)  --->  export.py  --->  Excel spreadsheet
```

## Why serverless

Unlike this portfolio's other projects, which run persistent backend servers
on ECS, InternWatch's workload is short, infrequent, and stateless between
runs — it wakes up, checks for new postings, and goes back to being idle for
30 minutes. AWS Lambda, triggered by an EventBridge scheduled rule, is a
better architectural fit for this shape of problem than a continuously
running server would be, and comes with a generous, ongoing free tier for
usage at this scale.

## Infrastructure as code

The Lambda function, its IAM execution role, and the EventBridge schedule
are all defined in Terraform (`main.tf`). The entire setup was manually
built once to confirm the design worked, then torn down and recreated
entirely from the Terraform configuration to verify the infrastructure
definition was correct and self-sufficient.

## Tech stack

Python · PostgreSQL · AWS Lambda · Amazon EventBridge · Terraform ·
Greenhouse Job Board API · openpyxl

## Local development

```bash
pip3 install requests psycopg2-binary python-dotenv openpyxl

# Create a .env file with:
# DB_HOST=...
# DB_PORT=5432
# DB_NAME=...
# DB_USER=...
# DB_PASSWORD=...

python3 create_db.py          # one-time: creates the postings table
python3 test_lambda_locally.py  # runs the discovery logic locally
python3 export.py             # generates internships.xlsx from current data
```

## Deploying changes

```bash
rm -rf package lambda_deployment.zip
mkdir package
pip3 install --target ./package requests --break-system-packages
pip3 install --target ./package --platform manylinux2014_x86_64 --only-binary=:all: psycopg2-binary --break-system-packages
cp lambda_function.py companies.py ./package/
cd package && zip -r ../lambda_deployment.zip . && cd ..
terraform apply
```

## Known limitations

- Coverage is limited to companies that use Greenhouse and are explicitly
  added to the tracked list in `companies.py` — there is no way to discover
  postings from companies on other platforms (Lever, Workday, custom career
  pages) without separate integrations.
- The keyword filter (`intern` + `engineer`) is deliberately simple and may
  miss postings with unconventional titles, or occasionally include a false
  positive if a non-internship role happens to contain both words.
