def retrieve_pokemon_type(pokemon_name, pokedex):
    pokemon_name = pokemon_name.lower().strip()
    forms = ["alolan", "galarian", "hisuan", "mega"]
    form = next((f for f in forms if f in pokemon_name), None)
    clean_name = pokemon_name.replace("shadow", "").strip()
    if form:
        clean_name = clean_name.replace(form, "").strip()

    for pokemon in pokedex:
        name = pokemon["speciesName"].lower()
        if form:
            if form in name and clean_name in name:
                return pokemon["types"]
        else:
            if clean_name == name or clean_name in name:
                return pokemon["types"]

    return [None, None]


def retrieve_pokemon_base_stats(pokemon_name, pokedex):
    pokemon_name = pokemon_name.lower().strip()
    forms = ["alolan", "galarian", "hisuan", "mega"]
    form = next((f for f in forms if f in pokemon_name), None)
    clean_name = pokemon_name.replace("shadow", "").strip()
    if form:
        clean_name = clean_name.replace(form, "").strip()

    for pokemon in pokedex:
        name = pokemon["speciesName"].lower()
        if form:
            if form in name and clean_name in name:
                return pokemon["baseStats"]
        else:
            if clean_name == name or clean_name in name:
                return pokemon["baseStats"]

    return {"atk": 0, "def": 0, "hp": 0}
