E-Commerce Order Analytics

An end-to-end data analytics project using Python, Pandas, SQLite, and SQL to process and analyze e-commerce order data.

Features
Generate realistic e-commerce CSV data
Clean and validate data using Pandas
Load cleaned data into SQLite
Perform basic, intermediate, and advanced SQL analysis
Generate daily, weekly, and monthly reports
Handle and test common data-quality edge cases
Technologies
Python
Pandas
SQLite
SQL
Project Structure
data/
├── raw/
└── cleaned/

database/
└── ecommerce.db

scripts/
├── generate_data.py
├── clean_data.py
├── load_database.py
├── check_database.py
├── report.py
└── tests.py

sql/
└── queries.py

reports/
└── data_quality_report.txt
How to Run
python scripts/generate_data.py
python scripts/clean_data.py
python scripts/load_database.py
python scripts/check_database.py
python sql/queries.py
python scripts/report.py
python scripts/tests.py

The project demonstrates a complete workflow from raw data generation → cleaning → database loading → SQL analysis → reporting → testing.