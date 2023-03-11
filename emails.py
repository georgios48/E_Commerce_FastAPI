# / Email conformation only / #

from fastapi import BackgroundTasks, UploadFile, File, Form, Depends, status, HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dotenv_values
from typing import List
from models import User
import jwt

config_credentials = dotenv_values(".env")


conf = ConnectionConfig(
    MAIL_USERNAME = config_credentials["EMAIL"],
    MAIL_PASSWORD = config_credentials["PASS"],
    MAIL_FROM = config_credentials["EMAIL"],
    MAIL_PORT = 587, # THIS IS FOR GMAIL, MIGHT NOT WORK ON OTHER PROVIDERS
    MAIL_SERVER = "smtp.gmail.com", # THIS IS FOR GMAIL MIGHT NOT WORK ON OTHER PROVIDERS
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True
)


# Generates a token from which we can identify the user
async def send_email(email: List, instance: User):
    token_data = {
        "id": instance.id,
        "username": instance.username
    }

    token = jwt.encode(token_data, config_credentials["SECRET"])


    # Used a ready template on that :x
    template = f""""
        <!DOCTYPE html>
        <html>
            <head>

            </head>
            <body>
                <div style = "display: flex; align-items: center; justify-content:
                center; flex-direction: column">

                <h3>Account Verification </h3>
                <br>

                <p> Thanks for choosing Geo Shop, verify your account using the link below. </p>

                <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem;
                font-size: 1rem; text-decoration: none; background: #0275d8; color: white";
                href="http://localhost:8000/verification/"?token={token}">Verify your account</a>
                </div>
            </body>
        </html>
    """

    message = MessageSchema(
        subject="Geo Shop Account Verification Email",
        recipients=email, # List of recipients, in our case only one
        body=template,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message=message)