def retrieve_move_type(move_name, move_dataset):
    for move_data in move_dataset:
        if move_data["name"].lower() == move_name.lower():
            return move_data["type"].lower()
    return None
