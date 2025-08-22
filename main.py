from import_statements import *
from util_functions.util1 import *

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

    From= fdata.get("From") # gives: "whatsapp:+91xxxxxxxxxx"
    Body= fdata.get("Body")
    To= fdata.get("To")
    print(f"Message from {From}: {Body}")

    resp1= parse_expense_message_by_line(Body)
    reply1=format_expense_message(resp1)
    cln_number= clean_number(From)
    supclient = await get_supabase()
    ###############
    if not await check_if_user_exists(supclient, cln_number):
        await register_user(supclient, cln_number)
        print("Welcome message sent! to",cln_number)
    ###############
    else:
        if Body.startswith("/"):
            cmd = Body.split()[0].lower()
            if cmd == "/help":
                reply1 = handle_help()
            elif cmd == "/totalexpenseoftoday":
                reply1 = await handle_total_today(supclient, cln_number)
            elif cmd == "/delete_account":
                reply1 = await handle_delete_account(supclient, cln_number, Body)
            else:
                reply1 = "Unknown command. Type /help to see available commands."+ "\n" + handle_help()
        else:
            reply1=format_expense_message(resp1)

            try:
                supclient = await get_supabase()
                for item,amt in resp1:
                    await supclient.table("expenses_record").insert({
                        "mobile_number":cln_number,
                        "item_name":item,
                        "amount":amt,
                        "timestamp":int(time.time())
                    }).execute()
            except Exception as e:
                print("Supabase error: ",e)
            print("HelloTest")

        #################################################################################################
        # replying with a formatted response of the expenses sent by user
        try:
            await send_whatsapp_message(
                from_=To,
                to=From,
                body=reply1
            )
        except TwilioRestException as e:
            print("Twilio error: ",e)
        #################################################################################################
        # #simple reply to user
        # try:
        #     await send_whatsapp_message(
        #         from_=To,
        #         to=From,
        #         body=f"Received your message: {Body}"
        #     )
        # except TwilioRestException as e:
        #     print("Twilio error: ",e)
        #################################################################################################
        # return PlainTextResponse("OK")

        #################################################################################################

# For testing asyncioscheduler:
# async def printhello():
#     print("Hellotesting...")

# Background scheduler
scheduler = AsyncIOScheduler()
# Run every day at 21:00 (9 PM) → adjust time as you like
# scheduler.add_job(lambda: asyncio.run(send_daily_summary()), "cron", hour=12, minute=36) #previous version
scheduler.add_job((send_daily_summary), "cron", hour=18, minute=29) # pass function, not call
# scheduler.add_job((printhello), "interval", seconds=5)
scheduler.start()