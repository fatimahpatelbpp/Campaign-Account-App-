Campaign Targeting Tool App

A web-based application that allows users to upload account data, apply filters and generate scores for recommended accounts in B2B campaign targeting using Python and Flask.

What it does:
- Upload a CSV file containing account data
- Automatically scores each sccount based on engagement, pipeline status/activity and market size
- Filter results based on industry, market size and pipeline status/activity
- View the top 3 recommended accounts
- Export results as a CSV file

How to run:
1. Clone the repository
    git clone https://github.com/fatimahpatelbpp/Campaign-Account-App-.git
    cd Campaign-Account-App- 
2. Create and activate a virtual environment
   python -m venv venv
   venv\Scripts\activate
3. Install dependencies
   pip install flask pandas pytest
5. Run the application
   python app.py
7. Open the browser pop-up or visit http://127.0.0.1:5000/

Required format for CSV upload:
Your CSV file must contain the following columns: name, industry, market_size, pipeline, engagement

Scoring algorithm:
Each account is scored based on the following:
 - Base score = engagement*0.5
 - +10 if the account is in the pipeline
 - +5 if the account's market size is Enterprise
Accounts are ranked in ascending order.


