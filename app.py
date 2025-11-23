import random
import csv
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, send_file
from weasyprint import HTML
import pandas as pd
from flask_cors import CORS
from cs50 import SQL
import secrets
import os
from werkzeug.utils import secure_filename
import string
import io
import xlsxwriter
from dotenv import load_dotenv
import pandas as pd
from cs50 import SQL
import requests
import io
from dotenv import load_dotenv
from flask_cors import CORS
#load virtual environment
load_dotenv()

db = SQL("sqlite:///student_feedback.db")
templ_db = SQL("sqlite:///templates.db")
#excel creating function
GEMINI_URL = os.environ.get("GEMINI_URL")
def generate_csv(prompt, data):
    meta_prompt = f'''Act as a professional data parser. The accompanying raw data includes the final desired CSV header row on the very first line. Parse the rest of the unstructured text line-by-line, structuring it to fit the specified columns.
        Your entire response MUST be ONLY the raw CSV text. Start directly with the header row provided in the input. Do not add any extra text or formatting, If the 'prompt' says anything about making an excel file, ignore it and proceed with making your CSV.
        data:
            {data}
        prompt:
            {prompt}
        '''
    
    print("prompt", meta_prompt)
    """
    Sends a prompt to the Gemini API to request a full HTML template.
    """
    # NOTE: You should ensure 'requests' and 'GEMINI_URL' are imported/defined
    # and that the API key is secured (e.g., loaded from an environment variable).

    headers = {
        "Content-Type": "application/json"
    }
    
    # It is strongly recommended to use a secured environment variable for your key
    # api_key = os.environ.get("GEMINI_API_KEY") 
    params = {
        # The key should be handled securely, this is just for structure:
        "key": os.environ.get("GEMINI_KEY")
    }
    
    # The payload is structured to ask the model for a text response
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": meta_prompt
                    }
                ]
            }
        ]
    }

    try:
        # Assuming GEMINI_URL is defined (e.g., the URL for generateContent)
        # and 'requests' is imported
        response = requests.post(GEMINI_URL, headers=headers, params=params, json=data, timeout=120)
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Extract the HTML text from the response
        response_json = response.json()
        
        # Safely navigate the JSON structure to get the text content
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            html_template = response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            print("Error: No candidates found in the response.")
            return None
            
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
        return None
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
        return None
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")
        return None
    except KeyError:
        print("Error: Malformed JSON response from API.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during API call: {e}")
    #file creation
    response = html_template
    response.replace("'''"," ")
    print(response)
    response = io.StringIO(response)
    df = pd.read_csv(response)
    print("structured data: \n",df)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Parsed Data')
    output.seek(0)
    return output

app = Flask(__name__)
CORS(app)
app.secret_key = "secret_key"
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/message")
def message():
    return render_template("message.html")
@app.route("/excel_maker")
def excel_maker():
    return render_template("excel_maker.html")
@app.route("/get_excel_data", methods=["POST","GET"])
def get_excel_data():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        info =data.get("data")
        print("data:", data)
        prompt = data.get("prompt")
        excel= generate_csv(prompt, info)
        return send_file(
            excel,
            download_name="Xl.xlsx", # Changed filename to Xl.xlsx as requested
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
@app.route("/submit_survey", methods=["POST"])
def submit_survey():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        print(f"[Timestamp: {datetime.now()}, Feedback status: successful]")
        academic_year = data["academic_year"]
        location = data['location']
        problem_description = data['problem_description']
        solution_suggestion = data['solution_suggestion']
        db.execute("INSERT INTO feedback(academic_year, location, problem_description, solution_suggestion) VALUES(?,?,?,?)", academic_year,location,problem_description,solution_suggestion)
        return jsonify({'response':"successful"})
@app.route("/fetch_survey", methods=["POST"])
def fetch_survey():
    if request.method == "POST":
        info = db.execute("SELECT * FROM feedback")
        return jsonify(info)
@app.route("/survey_admin",methods=["GET","POST"])
def survey_admin():
    return render_template("survey_admin.html")
@app.route("/pdf_maker",methods=["GET","POST"])
def pdf_maker():
    return render_template("pdf_maker.html")
#get user input
#put it in structured form
#put into AI prompt
#get three AI templates
#store it in temporary templates dict
#create link for created templates

#required variables including environment ones
#----------------
#this hold the prompts


#this hold the templates temporarily|
#MAX HOLD TIME: 5 minutes



#this function gets the data
def get_data():
    templates = templ_db.execute("SELECT * FROM template_data")
    return templates
#this function views the template functions
def view_data():
    templates = templ_db.execute("SELECT * FROM template_data")
    for template in templates:
        print("|" * 200) 
        print(template)
#templ_db is the SQL object for the templates database
#This holds the "keys" which is metadata for the templates in the templates list, so as to prevent the existence of identical variables 
keys = []
#html_doc_maker function, this function makes html doc
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")
def html_doc_maker(prompt):
    """
    Sends a prompt to the Gemini API to request a full HTML template.
    """
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY
    }
    
    # The payload is structured to ask the model for a text response
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, params=params, json=data, timeout=120)
        
        # Raise an exception for bad status codes
        response.raise_for_status()

        # Extract the HTML text from the response
        response_json = response.json()
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            html_template = response_json['candidates'][0]['content']['parts'][0]['text']
            html_template = html_template.replace("'''", "")
            return html_template
        else:
            print("Error: No candidates found in the response.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Network or API Error: {e}")
        return '''<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Document</title>
                    </head>
                    <body>
                        <h1>This is a test document, to  test template generation temporarily, cause i ain't got no data, help me 😭 😯😟 </h1>
                        <h1></h1>
                    </body>
                    </html>
                '''
#triple doc_maker function
def triple_doc_maker(prompt):
    templates = []
    while len(templates) != 3:
        template = html_doc_maker(prompt)
        templates.append(template)
    return templates

#this is a random number generator that ensures that prevents identical keys
def random_num_gen():
    num = random.randint(1, 100)
    num = "0" * (4 - len(str(num))) + str(num)
    if num in keys:
        print(f"Total keys:{len(keys)}")
        print(f"Index of common keys: {keys.index(num)}")
        print(f"Generated keys:{num}")
        print(keys)
        print("_" * 100)
        num = random.randint(1,1000)
    else:
        keys.append(num)
        print(f"Inserted number:{num}")
        print(keys)
        print("_" * 100)
    return num
#----------------
@app.route("/doc_maker", methods=["GET", "POST"])
def doc_maker():
    if request.method == "POST":
        data = request.get_json()
        #the user's data is added to the prompt
        prompt = '''
            |----------------------------------------------------------------------|
            |                                                                      |
            | You are a desktop publisher and a front end designer,                |
            | your task is to make documents as html templates with the info below,|
            | do not use jinja notation                                            |
            |----------------------------------------------------------------------|
        '''
        prompt += f'''
        INFO :
        {data}
        '''
        #http request is made to API * 3
        #the triple doc maker function is interim, it is meant to make an http reqest to an actual API
        gened_templates = triple_doc_maker(prompt)
        key = random_num_gen()
        for template in gened_templates:
            data_log = {"key":key, "template":template}
            templ_db.execute("INSERT INTO template_data(key, template) VALUES(?,?)", data_log['key'], data_log['template'])
            print(f"[Timestamp:{datetime.now()}Data entered into templates.db => {data_log}]")
        #return statement returns the link to the created templates in the frontend
        return jsonify({"response":"successful", "url":f"http://127.0.0.1:2000/view_doc/{key}"})
#pdf doc viewer
@app.route("/view_doc/<key>", methods=["GET", "POST"])
def view_doc(key):
    templates_to_view = templ_db.execute("SELECT * FROM template_data WHERE key = ?", str(key))
    for template in templates_to_view:
        template['subkey'] = templates_to_view.index(template)
    print("got something")
    print("TEMPLATES_TO_VIEW: ")
    print(templates_to_view)
    return render_template("doc_viewer.html", templates=templates_to_view)
#download html route
#i think the index is the sub key from the physical notes i made
@app.route("/download_doc/<key>/<subkey>")
def download_doc(key, subkey):
    templates = templ_db.execute("SELECT * FROM template_data WHERE key = ?", str(key))
    print(templates)
    html_content = templates[int(subkey)]['template']
    html_content = html_content.replace("'''", "")
    pdf_io = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_io)
    return send_file(
        pdf_io,
        as_attachment=True,
        download_name = 'report.pdf',
        mimetype = 'application/pdf'
    )
if __name__=="__main__":
    app.run(debug=True, port=2000)