from import_statements import *

supabase: SupabaseClient = None  # cached client

twilio_client = None

# create a global thread pool executor
executor = concurrent.futures.ThreadPoolExecutor()

async def get_twilio_client():
    global twilio_client
    if twilio_client is None:
        twilio_account_sid=os.getenv("twilio_account_sid")
        twilio_auth_token=os.getenv("twilio_auth_token")
        twilio_client= Client(twilio_account_sid,twilio_auth_token)
        return twilio_client
    return twilio_client

async def get_supabase(): 
    """
    Returns a cached Supabase client if available,
    otherwise creates a new one and reuses it.
    """
    global supabase
    if supabase is None:  # first time only
        supabase_url = os.getenv("supabase_url")
        supabase_key = os.getenv("supabase_key")
        supabase = await create_async_client(supabase_url, supabase_key)
    return supabase

def parse_expense_message_by_line(body):
    # Split the message into lines and strip extra spaces
    lines = body.strip().split('\n')
    result = []
    for line in lines:
        line = line.strip()  # remove leading/trailing spaces
        if not line:  # skip empty lines
            continue
        tokens = line.split()
        amount=None
        len_tokens=len(tokens)
        # now for sample tokens=('apple', '50'), check if last value is a digit, if yes, simply consider it as amount.
        if tokens[len_tokens-1].isdigit():
            amount=tokens.pop(len_tokens-1)
            item=" ".join(tokens)
            result.append((item, int(amount)))
            continue
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
    # sample:
    # body="""Apple 5 kg 50
    # rice 2 kg 60
    # 80      kiwi
    # chicken 65 65
    # """
    # sample result: [('Apple 5 kg', 50), ('rice 2 kg', 60), ('kiwi', 80), ('chicken 65', 65)]
    # still dosen't handle '120 chicken 65' , it gives ('120 chicken', 65)

def format_expense_message(expense_list):
    col_width = 19
    lines = [f"{'Item-name'.ljust(col_width)}Amount", '-' * (col_width + 6)]
    for item, amt in expense_list:
        wrapped = textwrap.wrap(item, width=col_width)
        # when sample item='word1 word2 word3 word4' then wrapped stores a List-of-Strings like ['word1 word2 word3', 'word4']
        for i, line in enumerate(wrapped):
            if i == 0:
                lines.append(f"{line.ljust(col_width)}{amt}")
            else:
                lines.append(line.ljust(col_width))
    return "```\n" + "\n".join(lines) + "\n```"
    # Joins all lines in the lines(variable having the list of strings) into a single string using \n (new line character).
    # "```\n" and "\n```" are used to format the string to monospace-format, suitable for whatsapp chat.

    #Sample return value:
    # Item-name         Amount
    # ------------------------
    # apple             50
    # word1 word2 word3 60
    # word4              
    # kiwi              70

def clean_number(raw_number):
    if raw_number.startswith("whatsapp:"):
        return raw_number.replace("whatsapp:","")
    return raw_number

def handle_help():
    return (
        "Hi! Here are the commands you can use:\n"
        "/help — Used to Check Out the Commands \n"
        "/TotalExpenseOfToday — get today’s total and item breakdown\n"
        "/Delete_Account — delete your account & all expenses (requires confirmation)\n\n"
        # "📌 Examples of adding expenses:\n"
        "📌 Guidelines-Examples for sending expenses:\n"
        # "Apple 50\n"
        # "50 Banana"
        "Format:\n"
        "Item name (along with quantity - optional) followed by amount.\n"
        "Each new entry must start on a new line.\n"
        # "\r{Item name} \r{Quantity}(Optional) \r{Amount}\n"
        "Apple 50 ✅\n"
        # "50 Apple ✅\n\n"
        "Wheat 5kg 100 ✅\n"
        # "100 Wheat 5kg ✅\n\n"
        "Wheat 5 kg 100 ✅"
        # "100 Wheat 5 kg ❌"
    )


def get_today_epoch_range():
    """Return start and end epoch timestamps for today"""
    now = datetime.datetime.now()
    start_of_day = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    end_of_day = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
    return int(start_of_day.timestamp()), int(end_of_day.timestamp())


async def send_whatsapp_message(from_, to, body):
    loop = asyncio.get_running_loop()  # get current event loop
    # run blocking Twilio call in a separate thread
    twilclient = await get_twilio_client()
    await loop.run_in_executor(executor, lambda: twilclient.messages.create(from_=from_, to=to, body=body)
    )

async def handle_total_today(supclient, mobile):
    start, end = get_today_epoch_range()
    supclient = await get_supabase()
    res = await supclient.table("expenses_record") \
        .select("item_name, amount") \
        .eq("mobile_number", mobile) \
        .gte("timestamp", start) \
        .lt("timestamp", end) \
        .execute()

    rows = res.data or []
    if not rows:
        return "No expenses recorded today."
    
    expense_list = [(r["item_name"], r["amount"]) for r in rows]

    total = sum(r["amount"] for r in rows)

    formatted = format_expense_message(expense_list)
    message = "Today's Expenses:\n" + f"\n{formatted}" + "```\n"+f"{'-'*25}\nTotal = {total}"+ "\n```"

    return message

async def handle_delete_account(supclient, cln_number, Body):
    parts = Body.split()  # split message into words
    # Example: ["/delete_account", "confirm"]

    # Check if user added "confirm"
    if len(parts) > 1 and parts[1].lower() == "confirm":
        try:
            # Delete all expense records for this user
            await supclient.table("expenses_record") \
                .delete() \
                .eq("mobile_number", cln_number) \
                .execute()
            # Delete user record from 'users' table
            await supclient.table("users") \
                .delete() \
                .eq("mobile_number", cln_number) \
                .execute()
            return "✅ Your account and all expenses have been deleted."
        except Exception as e:
            print("Supabase delete error:", e)
            return "❌ Error while deleting your account. Please try again."
    else:
        # Ask user to confirm
        return (
            "⚠️ This will permanently delete your account and all expenses.\n"
            "If you’re sure, reply:\n\n"
            "/Delete_Account confirm"
        )
###########################
async def check_if_user_exists(supclient, mobile):
    """Check if a user with this mobile already exists in Supabase."""
    # supclient = await get_supabase()
    result = await supclient.table("users").select("*").eq("mobile_number", mobile).execute()
    return len(result.data) > 0

async def register_user(supclient, mobile):
    data = {"mobile_number": mobile}
    await supclient.table("users").insert(data).execute()

    # Send welcome message
    await send_whatsapp_message(
        from_="whatsapp:+14155238886",   # Twilio sandbox / business number
        to=f"whatsapp:{mobile}",
        # body=(
        #     "🎉 Welcome to the WhatsApp Expense Tracker!\n\n"
        #     "You can now start adding your expenses.\n"
        #     "👉 Example: 'Apple 50'\n"
        #     "👉 At the end of the day, you'll receive your daily summary.\n\n"
        #     "Type /help to see all available commands."
        # ) ✅ ❌
        body=(
            "🎉 Welcome to the WhatsApp Expense Tracker!\n\n"
            "You can now start adding your expenses.\n"
            "Guidelines-Examples for sending expenses:\n"
            "Apple 50 ✅\n"
            "50 Apple ✅\n\n"
            "Wheat 5kg 100 ✅\n"
            "100 Wheat 5kg ✅\n\n"
            "Wheat 5 kg 100 ✅"
            "100 Wheat 5 kg ❌"
            "🌟 At the end of the day, you'll receive your daily summary.\n\n"
            "Type /help to see all available commands."
        )
    )
    return True
#############################

async def send_daily_summary():

    """Fetch today's expenses for all users and send WhatsApp summary"""
    try:
        supclient = await get_supabase()
        start_epoch, end_epoch = get_today_epoch_range()

        # Get all users who have expenses today
        data = await supclient.table("expenses_record") \
            .select("*") \
            .gte("timestamp", start_epoch) \
            .lte("timestamp", end_epoch) \
            .execute()

        rows = data.data
        if not rows:
            print("No expenses recorded today.")
            return

        # Group expenses by mobile_number
        user_expenses = {}
        for r in rows:
            user_expenses.setdefault(r["mobile_number"], []).append(r)

        # Send each user their own summary
        for mobile, items in user_expenses.items():
            total = sum(r["amount"] for r in items)
            # lines = [f"{r['item_name']} - {r['amount']}" for r in items]
            expense_list = [(r["item_name"], r["amount"]) for r in items]
            lines = format_expense_message(expense_list)
            message = "Today's Expenses:\n" + f"\n{lines}" + "```\n"+f"{'-'*25}\nTotal = {total}"+ "\n```"
            print(message)
            # Send via Twilio
            await send_whatsapp_message(
                from_= "whatsapp:+14155238886",
                to=f"whatsapp:{mobile}",   # add prefix back
                body=message
            )
            print(f"✅ Daily summary sent to {mobile}")

    except Exception as e:
        print("Error in daily summary:", e)