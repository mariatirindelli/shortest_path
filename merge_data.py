import pandas as pd
import argparse
import os
import string
import random
from itertools import permutations


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_distance(line_in, line_out):
    if line_in != line_out != "walk":
        return 5
    else:
        return 0


def main(data_root):

    input_files = [os.path.join(data_root, item) for item in os.listdir(data_root) if "csv" in item]

    combined_dataset = {"from_stop_I": [], "to_stop_I": [], "d": [], "n_vehicles": []}

    ordered_input_files = [item for item in input_files if "n_vehicles" in pd.read_csv(item, delimiter=";").columns]

    for item in input_files:
        if item not in ordered_input_files:
            ordered_input_files.append(item)

    # merging all the files together
    for file_path in ordered_input_files:
        data_frame = pd.read_csv(file_path, delimiter=";")
        if len(data_frame.columns) < 3:
            data_frame = pd.read_csv(file_path, delimiter=",")

        if len(data_frame.columns) < 3:
            print("not using file: ", file_path)
            continue

        if "from_stop_I" not in data_frame.columns or "to_stop_I" not in data_frame.columns \
                or "d" not in data_frame.columns:
            continue

        combined_dataset["from_stop_I"].extend(data_frame["from_stop_I"].tolist())
        combined_dataset["to_stop_I"].extend(data_frame["to_stop_I"].tolist())
        combined_dataset["d"].extend(data_frame["d"].tolist())

        if "n_vehicles" in data_frame.columns:
            combined_dataset["n_vehicles"].extend(data_frame["n_vehicles"].tolist())

        else:

            vehicle = id_generator(size=4) if "walk" not in os.path.split(file_path)[-1] else "walk"
            if vehicle != "walk":
                assert vehicle not in combined_dataset["n_vehicles"]
            combined_dataset["n_vehicles"].extend([vehicle for _ in data_frame["from_stop_I"].tolist()])

    # generating the transfer delays file with constant transfer delays
    vehicles = list(set(combined_dataset["n_vehicles"]))
    # vehicles_combinations = list(permutations(vehicles, 2))

    vehicles_combinations = []
    for vehicle_in in vehicles:
        for vehicle_out in vehicles:
            if vehicle_in != vehicle_out:
                vehicles_combinations.append((vehicle_in, vehicle_out))

    transition_time = {"n_vehicles_in": [item[0] for item in vehicles_combinations],
                       "n_vehicles_out": [item[1] for item in vehicles_combinations],
                       "d": [get_distance(item[0], item[1]) for item in vehicles_combinations]}
    transition_frame = pd.DataFrame(transition_time)
    transition_frame.drop_duplicates()
    transition_frame.to_csv(os.path.join(data_root, "transition_time.csv"), index=False, sep=";")

    data_frame = pd.DataFrame(combined_dataset)
    data_frame.to_csv(os.path.join(data_root, "network.csv"), index=False, sep=";")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kirby and Potts expansion')
    parser.add_argument('--data_root', type=str, default="data/example2", help='an integer for the accumulator')
    args = parser.parse_args()

    main(args.data_root)
