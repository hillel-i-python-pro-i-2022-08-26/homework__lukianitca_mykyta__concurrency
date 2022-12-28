# Async urls scraper.
![CI](https://github.com/hillel-i-python-pro-i-2022-08-26/homework__lukianitca_mykyta__scraper/actions/workflows/code_checking.yml/badge.svg)
***

## About project
#### Scraper extracts urls from web pages and follows them until given depth.
***

## Run configurations

### 📦 Run with docker(make):
``make d-homework-i-run``

### 🚮 Purge after run(make):
``make d-homework-i-purge``

### 🚫 Run without docker(make):
``make homework-i-run``

### 📋 Run with script:
``sh run.sh``

### 🖐 Run manually:
```
python3 -m venv venv &&
pip install --upgrade pip &&
pip install --requirement requirements.txt &&
python main_scraping.py
```
