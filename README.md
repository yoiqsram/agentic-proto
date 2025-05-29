# Agentic Proto

Prototype for an Agentic AI case.

## How to setup?

Beforehand, make sure you installed `uv`. Please look at [the official installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### 1. Environment

Create new local uv environment by running the following command.

**Development**

```sh
uv sync --all-packages
```

**Production**

```sh
uv sync --all-packages --no-dev
```

### 2. Database

Prepare new Sqlite database by running the following command.

```sh
uv run database
```

### 3. Pipelines

First, initialize the database and pipeline.

```sh
uv run packages/market-pipeline/src/init.py
```

Populate daily stock historical data.

```sh
uv run packages/market-pipeline/src/daily.py
```
