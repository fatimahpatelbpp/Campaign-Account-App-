"""
test_app.py

Main testing page for application
"""

# importing python libraries
import io
import pytest
import pandas as pd
from unittest.mock import patch

# stop init_db from creating a real database file when tests run
with patch("database.init_db"):
    from app import app


# set up fake browser for fake requests
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# creating sample data
def make_sample_data():
    """Return a small test DataFrame with realistic account data."""
    return pd.DataFrame([
        {"id": 1, "name": "Amazon",  "industry": "Retail", "market_size": "Enterprise", "pipeline": 1, "engagement": 80},
        {"id": 2, "name": "ASDA",    "industry": "Retail",    "market_size": "SMB",        "pipeline": 0, "engagement": 50},
        {"id": 3, "name": "Intel",   "industry": "Technology", "market_size": "SMB",        "pipeline": 0, "engagement": 30},
    ])

# testing home page load
def test_home_page_loads(client):
    response = client.get("/")
    # 200 = success
    assert response.status_code == 200


# testing for valid file upload
def test_upload_valid_csv(client):
    # Reference: io.BytesIO — https://docs.python.org/3/library/io.html#io.BytesIO
    # fake css saved to memory
    csv_data = b"name,industry,market_size,pipeline,engagement\nAmazon,Retail,Enterprise,1,80"
    file = {"csv_file": (io.BytesIO(csv_data), "test.csv")}

    # send to Flask
    with patch("app.insert_dataframe"):
        response = client.post("/upload", data=file, content_type="multipart/form-data")

    # 302 = redirect to results page if successful
    assert response.status_code == 302

# upload error test
def test_upload_wrong_columns_shows_error(client):
    csv_data = b"wrong,columns\nvalue1,value2"
    file = {"csv_file": (io.BytesIO(csv_data), "invalid_columns.csv")}
    with patch("app.insert_dataframe"):
        response = client.post("/upload", data=file, content_type="multipart/form-data")
    assert b"missing" in response.data.lower() or b"error" in response.data.lower()


# testing scoring is correct
def score(row):
    s = row["engagement"] * 0.5
    if row["pipeline"] == 1:
        s += 10
    if row["market_size"] == "Enterprise":
        s += 5
    return s

# testing full case logic
def test_score_with_all_bonuses():
    assert score({"engagement": 80, "pipeline": 1, "market_size": "Enterprise"}) == 70


def test_score_with_no_bonuses():
    assert score({"engagement": 50, "pipeline": 0, "market_size": "SMB"}) == 25


def test_score_zero_engagement():
    assert score({"engagement": 0, "pipeline": 0, "market_size": "SMB"}) == 0


# testing results page 
def test_results_page_loads(client):
    with patch("app.get_data", return_value=make_sample_data()):
        response = client.get("/results")
    assert response.status_code == 200

# testing filters work
def test_industry_filter_works(client):
    with patch("app.get_data", return_value=make_sample_data()):
        response = client.post("/results", data={"industry": "Technology"})

    # Technology should appear
    assert b"Intel" in response.data
    # Retail should be excluded
    assert b"Amazon" not in response.data

# testing if empty data can be handled
def test_empty_data_does_not_crash(client):
    empty = pd.DataFrame(columns=["id", "name", "industry", "market_size", "pipeline", "engagement"])
    with patch("app.get_data", return_value=empty):
        response = client.get("/results")
    assert response.status_code == 200


# testing export function
def test_export_downloads_csv(client):
    # Reference: Flask Response — https://flask.palletsprojects.com/en/stable/api/#flask.Response
    with patch("app.get_data", return_value=make_sample_data()):
        response = client.post("/export")

    assert response.status_code == 200
    assert "text/csv" in response.content_type
    assert "campaign_results.csv" in response.headers["Content-Disposition"]
    assert b"Amazon" in response.data

def test_export_with_filters(client):
    with patch("app.get_data", return_value=make_sample_data()):
        response = client.post("/export", data={
            "industry": "Technology",
            "market_size": "None",
            "exclude_pipeline": "False"
        })

    # Technology should be included
    assert b"Intel" in response.data
    # Retail should be excluded  
    assert b"Amazon" not in response.data
