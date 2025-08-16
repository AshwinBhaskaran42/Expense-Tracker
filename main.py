from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse, HTMLResponse
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
# from dotenv import load_dotenv

# load_dotenv("keys.env")
account_sid=os.getenv("account_sid")
auth_token=os.getenv("auth_token")
client= Client(account_sid,auth_token)

def parse_expense_message_by_line(body):
    # Split the message into lines and strip extra spaces
    lines = body.strip().split('\n')
    result = []
    for line in lines:
        line = line.strip()  # remove leading/trailing spaces
        if not line:  # skip empty lines
            continue
        tokens = line.split()
        amount = None
        words = []
        for token in tokens:
            if token.isdigit():
                amount = int(token)
            else:
                words.append(token)
        # Join all words as a single item
        item = " ".join(words)
        if item and amount is not None:
            result.append((item, amount))
    return result

def format_expense_message(expense_list):
    col_width = 19  # width of the item-name column
    lines = []

    # Header
    lines.append(f"{'Item-name'.ljust(col_width)}Amount")
    lines.append('-' * (col_width + 6))

    for item, amt in expense_list:
        if len(item) <= col_width:
            lines.append(f"{item.ljust(col_width)}{amt}")
        else:
            # wrap long item names
            words = item.split()
            line = ""
            first_line = True
            for word in words:
                if len(line + (' ' if line else '') + word) <= col_width:
                    line += (' ' if line else '') + word
                else:
                    if first_line:
                        lines.append(f"{line.ljust(col_width)}{amt}")
                        first_line = False
                    else:
                        lines.append(line.ljust(col_width))
                    line = word
            # remaining words
            if first_line:
                lines.append(f"{line.ljust(col_width)}{amt}")
            else:
                lines.append(line.ljust(col_width))

    # Join all lines and wrap in triple backticks for WhatsApp monospace
    return "```\n" + "\n".join(lines) + "\n```"


app = FastAPI()

@app.get('/', response_class=HTMLResponse)
async def home():
    with open("home.html", "r") as f:
        home_content= f.read()
    return HTMLResponse(content=home_content)

@app.get('/about', response_class=HTMLResponse)
async def about():
    with open("about.html", "r") as f1:
        about_content= f1.read()
    return HTMLResponse(content=about_content)

@app.post("/whatsapp")
# async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
async def whatsapp_webhook(request:Request):

    form_data= await request.form()
    fdata=dict(form_data)

    From= fdata.get("From")
    Body= fdata.get("Body")
    To= fdata.get("To")
    print(f"Message from {From}: {Body}")

    resp1= parse_expense_message_by_line(Body)
    reply1=format_expense_message(resp1)

    try:
        client.messages.create(
            from_=To,
            to=From,
            body=reply1

        )

    except TwilioRestException as e:
        print("Twilio error: ",e)

    # #reply to user
    # try:
    #     client.messages.create(
    #         from_=To,
    #         to=From,
    #         body=f"Got your msg: {Body}"
    #     )
    # except TwilioRestException as e:
    #     print("Twilio error: ",e)

    # return PlainTextResponse("OK")
