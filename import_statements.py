from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse, HTMLResponse
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
import sys
import time
from supabase import create_async_client, Client as SupabaseClient
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime,asyncio
import textwrap
import concurrent.futures

load_dotenv("keys.env")




