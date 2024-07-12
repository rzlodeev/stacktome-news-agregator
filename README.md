# Stacktome News Aggregator

## Overview

Stacktome News Aggregator is a FastAPI-based application that aggregates news from RSS feeds, filters them using Google Trends RSS, and exposes an endpoint to access trending articles.

## Features

- **FastAPI** server for handling requests
- **Celery** for task management and scheduling
- **RabbitMQ** as the message broker for Celery
- **OpenAI API** for calculating sentiment score for each article
- **SQLite** database for storing resulting articles
- Aggregates and filters news using RSS feeds
- Exposes an endpoint to access trending articles

Once running, system will automatically update - fetch and filters new articles every minute.
Fetched from news aggregator articles will be filtered by keywords fetched from Google Trends by
direct comparing of matched words in article text. Keywords are also filtered by length - only words with 4 or more
letters will be included. This was made for filtering out words without semantic meaning, like 'and', 'or', etc.
If there's a match between at least one word in article text and trending keywords - article will be added to database
with matched keyword specified.

For each new article sentiment score will be generated. Due to high cost usage of OpenAI, with every step only 10 articles will be proceed.
You can turn this off and proceed all articles that will fit in LLM context window by adding DEVELOPER_MODE=false to .env

Articles are present by descending order of sentiment score.

## Prerequisites

- Docker
- Docker Compose

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/rzlodeev/stacktome-news-agregator.git
    cd stacktome-news-agregator
    ```

2. **Create .env file:**

    ```sh
    nano .env
    ```

    _(or by preferred way of creating files, it's up to you)_

    and past there your OPENAI_API_KEY.
    _Optional: add DEVELOPER_MODE=false to calculate sentiment score for all articles at once. WARNING: This my result in
    high cost usage of OpenAI API (~$5 for initiating ~700 articles.)_

    Yor .env file should look like this:

    ```
    OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    DEVELOPER_MODE=false (optional)

3. **Create and activate a virtual environment (optional but recommended):**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4. **Install the Python dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

5. **Build and start the Docker containers:**

    ```sh
    docker-compose up --build
    ```

## Usage

Once the containers are up and running, the FastAPI server will be accessible at `http://127.0.0.1:8000`. The endpoint for trending articles is:

```sh
http://127.0.0.1:8000/trending_articles
```

## Project structure:

Here's brief overview of project files:

stacktome-news-agregator/

│

├── app.py                   # FastAPI entry point

│

├── app/

│   ├── backend.py           # Endpoints definition for FastAPI

│   ├── celery_config.py     # Celery worker definition

│   ├── tasks.py             # Celery tasks for fetching and filtering RSS feeds

│   ├── database.py          # SQLAlchemy definition of database

│   ├── models.py            # Database model for resulting news

│   ├── news_feed.py         # Module for fetching news articles from RSS

│   ├── openai_client.py     # OpenAI client for calculating sentiment score

│   └── trends_analytics.py  # Module for fetching keywords of trending news from Google Trends

│

├── docker-compose.yml       # Docker Compose file for defining services

├── Dockerfile               # Dockerfile for building the FastAPI application image

├── requirements.txt         # Python dependencies

└── README.md                # This file