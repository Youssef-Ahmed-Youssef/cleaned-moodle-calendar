import os
import requests
from requests.adapters import HTTPAdapter, Retry
from icalendar import Calendar, Event

def clean_ics(url, output_path):
    # Setup session with retries
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Fetch the calendar
    response = session.get(url, timeout=15)  # 15-second timeout
    response.raise_for_status()

    # Parse and clean the calendar
    cal = Calendar.from_ical(response.text)
    new_cal = Calendar()
    
    for prop in cal.property_items():
        new_cal.add(prop[0], prop[1])

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        summary = str(component.get('SUMMARY', ''))
        categories = component.get('CATEGORIES', '')

        if "Attendance" in summary:
            continue

        new_event = Event()
        for key, value in component.items():
            new_event[key] = value
        if categories:
            new_event['SUMMARY'] = f"[{categories}] {summary}"

        new_cal.add_component(new_event)

    with open(output_path, "wb") as f:
        f.write(new_cal.to_ical())

if __name__ == "__main__":
    ical_url = os.environ.get("ICAL_URL")
    if not ical_url:
        raise EnvironmentError("ICAL_URL environment variable is missing.")
    clean_ics(ical_url, "cleaned_calendar.ics")
