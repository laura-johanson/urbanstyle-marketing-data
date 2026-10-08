import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)


def fetch_sales(start_date, end_date):
    try:
        all_data = []
        page = 0
        page_size = 1000

        while True:
            response = supabase.table("sales").select("*") \
                .gte("sale_date", start_date) \
                .lte("sale_date", end_date) \
                .range(page * page_size, (page + 1) * page_size - 1) \
                .execute()

            data = response.data

            if not data:
                break

            all_data.extend(data)
            page += 1

        df = pd.DataFrame(all_data)

        return df

    except Exception as e:
        print(f"Viga müügiandmete pärimisel: {e}")
        return pd.DataFrame()


def fetch_customers():
    try:
        all_data = []
        page = 0
        page_size = 1000

        while True:
            response = supabase.table("customers").select("*") \
                .range(page * page_size, (page + 1) * page_size - 1) \
                .execute()

            data = response.data

            if not data:
                break

            all_data.extend(data)
            page += 1

        df = pd.DataFrame(all_data)

        return df

    except Exception as e:
        print(f"Viga kliendiandmete pärimisel: {e}")
        return pd.DataFrame()


def fetch_products():
    try:
        all_data = []
        page = 0
        page_size = 1000

        while True:
            response = supabase.table("products").select("*") \
                .range(page * page_size, (page + 1) * page_size - 1) \
                .execute()

            data = response.data

            if not data:
                break

            all_data.extend(data)
            page += 1

        df = pd.DataFrame(all_data)

        return df

    except Exception as e:
        print(f"Viga tooteandmete pärimisel: {e}")
        return pd.DataFrame()