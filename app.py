from flask import Flask,request,redirect,render_template,url_for
# from flask_restful import Api,Resource,reqparse
from google.cloud import bigquery
import config
import pandas as pd
import pdfkit
from flask import Flask
from io import BytesIO
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


app = Flask(__name__)




@app.route('/categories', endpoint = "category")
def category():
    client = bigquery.Client(credentials=config.CREDENTIALS, project=config.CREDENTIALS.project_id)
    query = """
    SELECT *
    FROM `dna-staging-test.IMS.categories`
    """
    try:
        query_job = client.query(query)
        df = query_job.to_dataframe()
        print(df)
    except Exception as e:
        print(f"Error executing query: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame if there was an error

    setup = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    template = render_template('report_template.html', data=df.to_dict(orient='records'))

    pdfkit.from_string(template, 'pdf2.pdf', configuration=setup)

    # Set up the email components
    msg = MIMEMultipart()
    msg['From'] = 'bandile.mashile@rentoza.co.za'
    msg['To'] = 'lesego.dhlamini@rentoza.co.za'
    msg['Subject'] = 'PDF attachment'
    # Add the PDF attachment to the email
    filename = 'pdf2.pdf'
    with open(filename, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='pdf')
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(attachment)
    # Send the email
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'bandile.mashile@rentoza.co.za'
    smtp_password = 'Bandile97'
    smtp_conn = smtplib.SMTP(smtp_server, smtp_port)
    smtp_conn.starttls()
    smtp_conn.login(smtp_username, smtp_password)
    smtp_conn.sendmail(msg['From'], msg['To'], msg.as_string())
    smtp_conn.quit()
    # Delete the PDF file from the local directory
    # os.remove(filename)
    return 'succcess'