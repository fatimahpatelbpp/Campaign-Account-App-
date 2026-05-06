# from flask library import tools
from flask import Flask, render_template, request, redirect, url_for, Response
# used to read and transform CSV file into table
import pandas as pd
# used for CSV export
import io

# functions from database.py
from database import init_db, insert_dataframe, get_data

# creates web application
app = Flask(__name__)
init_db()

# Scoring function - takes one row of info and calculates score based on engagement, pipeline, market size
def score(row):
    s = 0
    s += row["engagement"] * 0.5

    if row["pipeline"] == 1:
        s += 10

    if row["market_size"] == "Enterprise":
        s += 5

    return s


# upload page
# -----------
#@app.route tells flask to run upload page when user visits
@app.route("/")
def upload_page():
    return render_template("upload.html")


# runs when data is sent to /upload via file upload
@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("csv_file")

        # if no file uploaded -> error message
        if not file or file.filename == "":
            return render_template("upload.html", error="Please upload a CSV file.")

        # if not right file type -> error message
        if not file.filename.endswith(".csv"):
            return render_template("upload.html", error="Only CSV files are allowed.")

        # convert uploaded file into a table
        df = pd.read_csv(file)
        # remove spaces and convert to lowercase
        df.columns = df.columns.str.strip().str.lower()

        # define necessary columns
        required = ["name", "industry", "market_size", "pipeline", "engagement"]
        # check if necessary columns are missing
        missing = [col for col in required if col not in df.columns]

        # handling missing columns by stopping processing and showing what's missing
        if missing:
            return render_template("upload.html", error=f"Missing columns: {', '.join(missing)}")

        # save to database
        insert_dataframe(df)

        # send user to results page
        return redirect(url_for("results"))

    # for any errors occurred, show upload page again
    except Exception as e:
        return render_template("upload.html", error=f"Error: {str(e)}")


# results funcions
# allow for two types of requests - visiting the page, submitting filters
@app.route("/results", methods=["GET", "POST"])
def results():

    # calls function from database.py which returns results in table
    df = get_data()

    industry = request.form.get("industry")
    market_size = request.form.get("market_size")
    exclude_pipeline = request.form.get("exclude_pipeline")

    # checkbox converted to boolean
    exclude_pipeline_bool = True if exclude_pipeline == "on" else False
    
    # dictionary to pass active filters for display
    filters = {
        "industry": industry,
        "market_size": market_size,
        "exclude_pipeline": exclude_pipeline_bool
    }

    # apply filters
    if industry:
        df = df[df["industry"] == industry]

    if market_size:
        df = df[df["market_size"] == market_size]

    if exclude_pipeline_bool:
        df = df[df["pipeline"] == 0]

    df = df.copy()

    # calculate score for each row and order from highest to lowest
    # ensures table has rows and prevents errors for empty datasets
    if not df.empty:
        df["score"] = df.apply(score, axis=1)
        df = df.sort_values(by="score", ascending=False)
    else:
        df["score"] = []

    # removes ID column before displaying
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    # create top accounts for display based on top 3 scores
    top_accounts = df.to_dict(orient="records")[:3] if not df.empty else []

    # send data to results.html page
    return render_template(
        "results.html",
        tables=[df.to_html(index=False)] if not df.empty else [],
        filters=filters,
        top_accounts=top_accounts
    )

# export download feature
@app.route("/export", methods=["POST"])
def export():
    df = get_data()

    # read filter values passed from the results page
    industry = request.form.get("industry")
    market_size = request.form.get("market_size")
    exclude_pipeline = request.form.get("exclude_pipeline")

    # apply the same filters as the results page
    if industry and industry != "None":
        df = df[df["industry"] == industry]

    if market_size and market_size != "None":
        df = df[df["market_size"] == market_size]

    if exclude_pipeline == "True":
        df = df[df["pipeline"] == 0]

    output = io.StringIO()
    df.to_csv(output, index=False)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=campaign_results.csv"}
    )

# only runs the server if this file is executed directly, not when imported
if __name__ == "__main__":
    app.run(debug=True)