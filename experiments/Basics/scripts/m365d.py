import requests
import json

def query_events(access_token, query, output_path=None):
    # Set API URL
    api_url = "https://api.security.microsoft.com/api/advancedhunting/run"
    query_property = "Query"

    # Prepare the HTTP Body
    query_body = {
        query_property: query
    }

    # Prepare the HTTP Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    # Prepare the HTTP Params
    http_params = {
        'method': 'POST',
        'url': api_url,
        'json': query_body,
        'headers': headers
    }

    # Send the HTTP Request
    response = requests.post(**http_params)
    response_data = response.json()

    all_events = response_data.get('Results', [])

    if not all_events:
        print("[!] No events found")
        return None
    else:
        print(f"[+] Found {len(all_events)} events")

    if output_path:
        print(f"[+] Exporting all events to {output_path}")
        with open(output_path, 'w', encoding='utf-8', errors='ignore') as file:
            for event in all_events:
                line = json.dumps(event, separators=(',', ':'))
                file.write(line + '\n')
    else:
        print("[+] Returning all events")
        return all_events

import requests
import json

def get_alerts(aadToken, incidentId):
    # Remove leading and trailing whitespace from the incident ID
    incidentId = incidentId.strip()

    # Construct the URL
    url = f"https://api.securitycenter.windows.com/api/alerts?$filter=incidentId eq {incidentId}"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': "Bearer " + aadToken
    }

    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        # If the request was successful (status code 200)
        data_str = response.content.decode('utf-8')
        json_data = json.loads(data_str)
        return json_data
    else:
        # Handle HTTP errors here if needed
        print("HTTP Error:", response.status_code)
        return None