import json
def add_response_to_db(response, data_file):
    if data_file.exists():
        with open(data_file, 'r') as f:
            data = json.load(f)
    else:
        data = {}
    data.update(response)
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

