from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
# from dotenv import load_dotenv

# load_dotenv("keys.env")
account_sid=os.getenv("account_sid")
auth_token=os.getenv("auth_token")
client= Client(account_sid,auth_token)

app = FastAPI()

@app.post("/whatsapp")
# async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
async def whatsapp_webhook(request:Request):

    form_data= await request.form()
    fdata=dict(form_data)

    From= fdata.get("From")
    Body= fdata.get("Body")
    To= fdata.get("To")
    print(f"Message from {From}: {Body}")

    #reply to user
    try:
        client.messages.create(
            from_=To,
            to=From,
            body=f"Got your msg: {Body}"
        )
    except TwilioRestException as e:
        print("Twilio error: ",e)

    # return PlainTextResponse("OK")
