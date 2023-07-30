import requests
import json

def _request_schedule():
    url = "https://registrar.kfupm.edu.sa/api/academic-calendar?term_code=202230"
    response = requests.get(url)
    data = json.loads(response.text)
    return data

def get_schedule():
    data = _request_schedule()
    output = data["title"] + "\n"
    for event in data["events"]:
        output += f"{event['event']} on {event['start_date']}\n"
    return output

if __name__ == "__main__":
    import pprint
    pprint.pprint(_request_schedule())