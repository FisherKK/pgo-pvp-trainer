import json


def load_json(file):
    data = json.load(file)
    return data


def save_dict_to_json(data, output_filepath):
    with open(output_filepath, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Dictionary saved to {output_filepath}")
