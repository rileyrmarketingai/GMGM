import os
from supabase import create_client
from utils.google_maps_scraper import GoogleMaps
import time

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_unused_searches():
    response = supabase.table("Google_Maps Searches").select("*").eq("searchUSED", False).execute()
    return response.data if response.data else []

def mark_search_used(search):
    supabase.table("Google_Maps Searches").update({"searchUSED": True}).eq("Searches", search).execute()

def insert_leads(leads):
    for lead in leads:
        try:
            supabase.table("Roofing Leads New").insert(lead).execute()
        except Exception as e:
            if "duplicate key value violates unique constraint" in str(e):
                print(f"Duplicate lead skipped: {lead.get('title', '')}")
            else:
                print(f"Error inserting lead: {lead} -- {e}")

def main():
    searches = get_unused_searches()
    row_number = int(time.time())  # timestamp base for unique RowNumbers
    scraper = GoogleMaps(headless=True, verbose=False)
    for row in searches:
        search_term = row["Searches"]
        leads = scraper.scrape(search_term, row_number_start=row_number)
        insert_leads(leads)
        mark_search_used(search_term)
        row_number += len(leads)

if __name__ == "__main__":
    main()
