import re
from collections import defaultdict
import os  ## in case you need environment variables

import requests

# Forgive me for not using pandas and namedtuple
# I'm having issues installing pandas to AppDaemon in Hass.IO
# That's why I don't have pandas here.

# The URL you post to in the first step.
URL_V_DATA = r'https://skl-api.bookmyvaccine.covid19.health.nz/public/appointments/get'

# You can just use string instead. Just don't publish it.
# You may need to restart your machine to have new OS variables effective.
PHONE = os.environ.get('a_phone')  # or '+6421000000'
CONFIRMATIONCODE = os.environ.get('a_confirmation_code')

# These are dates of interest
# Some clinics keep changing their available dates that's annoying.
STARTDATE = '2021-08-20'
ENDDATE = '2021-10-31'


def get_v_data(**kwargs):

    r = requests.post(
        URL_V_DATA,
        json=kwargs
    )

    c = r.json()['appointments']
    
    [jab_first, _] = c 
    
    return {
        'locationId':jab_first["locationId"],
        'vaccineData': jab_first["vaccineData"]
    }

def get_dates(locationId, vaccineData):

    url = f'https://skl-api.bookmyvaccine.covid19.health.nz/public/locations/{locationId}/availability'

    payload = {
        'startDate': STARTDATE,
        'endDate': ENDDATE,
        'vaccineData': vaccineData,
        'doseNumber': 1,
    }
        
    r = requests.post(url, json=payload)

    a = r.json()['availability']

    dates = [
        i['date'] for i in a
            if i['available']
               #if re.search('(?:2021-09-0[12]|2021-08-)', i['date']) 
    ]

    if dates:

        return dates

def get_slots(dates, vaccineData):
    
    a_dict = defaultdict(dict)

    for a_date in dates:
        
        url = f'https://skl-api.bookmyvaccine.covid19.health.nz/public/locations/a0R4a000000RxNXEA0/date/{a_date}/slots'
        
        payload = {
            'vaccineData': vaccineData,
            'groupSize': 1
        }

        r = requests.post(url, json=payload).json()

        slots = r['slotsWithAvailability']

        a_dict[r['date']] = [
            slot['localStartTime']
                for slot in slots
        ]

    return a_dict

def main():

    v_data = get_v_data(
        phone=PHONE,
        confirmationCode=CONFIRMATIONCODE
    )
    
    dates = get_dates(
        v_data['locationId'],
        v_data['vaccineData']
    )

    if dates:
        slots = get_slots(
            dates=dates,
            vaccineData=v_data['vaccineData']
        )

        for d, s in slots.items():
            print(d,s)
    
    else:
        print('NO VACCANCY')

if __name__ == '__main__':

    main()
