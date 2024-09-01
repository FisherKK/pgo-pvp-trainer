import re
import random

from project.moveset import retrieve_move_type
from project.pokedex import retrieve_pokemon_type, retrieve_pokemon_base_stats
from project.iv import calculate_attack_and_cp


def get_element_type_color(type_):
    if not type_:
        return "white"
    else:
        type_colors = {
            "normal": "#A8A77A",
            "fire": "#EE8130",
            "water": "#6390F0",
            "electric": "#F7D02C",
            "grass": "#7AC74C",
            "ice": "#96D9D6",
            "fighting": "#C22E28",
            "poison": "#A33EA1",
            "ground": "#E2BF65",
            "flying": "#A98FF3",
            "psychic": "#F95587",
            "bug": "#A6B91A",
            "rock": "#B6A136",
            "ghost": "#735797",
            "dragon": "#6F35FC",
            "dark": "#705746",
            "steel": "#B7B7CE",
            "fairy": "#D685AD",
        }
        return type_colors.get(type_.lower(), "white")


def style_text(question, text, color):
    pattern = re.compile(rf"<span.*?color:.*?>{re.escape(text)}</span>", re.IGNORECASE)

    if not pattern.search(question):
        styled_text = (
            f'<span style="font-size:16px; font-weight:bold; color:{color};">{text}</span>'
        )
        question = question.replace(text, styled_text)

    return question


def generate_question(
    pokemon_database,
    pokedex_database,
    moves_database,
    max_pokemon_cp,
    attack_comparison_ratio=1,
    turn_moves_ratio=1,
    charged_moves_ratio=1,
):
    if attack_comparison_ratio == 0 and turn_moves_ratio == 0 and charged_moves_ratio == 0:
        return {}

    pokemon_names = list(pokemon_database.keys())

    total_ratio = attack_comparison_ratio + turn_moves_ratio + charged_moves_ratio
    question_types = ["attack_comparison", "fast_attack", "charged_move"]
    probabilities = [
        attack_comparison_ratio / total_ratio,
        turn_moves_ratio / total_ratio,
        charged_moves_ratio / total_ratio,
    ]

    question_type = random.choices(question_types, probabilities)[0]

    if question_type == "attack_comparison":
        pokemon1, pokemon2 = random.sample(pokemon_names, 2)
        pokemon1_type = retrieve_pokemon_type(pokemon1, pokedex_database)[0]
        pokemon2_type = retrieve_pokemon_type(pokemon2, pokedex_database)[0]

        pokemon1_base_stats = retrieve_pokemon_base_stats(pokemon1, pokedex_database)
        pokemon2_base_stats = retrieve_pokemon_base_stats(pokemon2, pokedex_database)

        ivs1 = [random.randint(0, 15), random.randint(0, 15), random.randint(0, 15)]
        ivs2 = [random.randint(0, 15), random.randint(0, 15), random.randint(0, 15)]

        pokemon1_atk, pokemon1_cp = calculate_attack_and_cp(
            base_attack=pokemon1_base_stats["atk"],
            base_defense=pokemon1_base_stats["def"],
            base_stamina=pokemon1_base_stats["hp"],
            ivs=ivs1,
            max_cp=max_pokemon_cp,
        )

        pokemon2_atk, pokemon2_cp = calculate_attack_and_cp(
            base_attack=pokemon2_base_stats["atk"],
            base_defense=pokemon2_base_stats["def"],
            base_stamina=pokemon2_base_stats["hp"],
            ivs=ivs2,
            max_cp=max_pokemon_cp,
        )

        question = f"Which Pokémon will win CMP: "
        question += f'**{pokemon1_cp} CP** **{"/".join(map(str, ivs1))}** {pokemon1}'
        question += f' or **{pokemon2_cp} CP** **{"/".join(map(str, ivs2))}** {pokemon2}?'
        answer = pokemon1 if pokemon1_atk >= pokemon2_atk else pokemon2
        answer_explanation = (
            "(" + str(round(pokemon1_atk, 2)) + " vs " + str(round(pokemon2_atk, 2)) + ")"
        )

        question = style_text(question, pokemon1, get_element_type_color(pokemon1_type))
        question = style_text(question, pokemon2, get_element_type_color(pokemon2_type))

        variants = [pokemon1, pokemon2]
        question_type = "attack_comparison"

    elif question_type == "fast_attack":
        pokemon = random.choice(pokemon_names)
        fast_attack_name, fast_attack_turns = list(
            pokemon_database[pokemon]["fast_attack"].items()
        )[0]
        fast_attack_type = retrieve_move_type(fast_attack_name, moves_database)

        question = f"How many turns does **{fast_attack_name}** take?"
        question = style_text(question, fast_attack_name, get_element_type_color(fast_attack_type))
        correct_answer = int(fast_attack_turns[0])

        variants = sorted(list(range(1, 9)))

        if correct_answer not in variants:
            variants[random.randint(0, len(variants) - 1)] = correct_answer

        answer = correct_answer
        answer_explanation = ""
        question_type = "fast_attack"

    elif question_type == "charged_move":
        pokemon = random.choice(pokemon_names)
        pokemon_type = retrieve_pokemon_type(pokemon, pokedex_database)[0]

        fast_attack_name, _ = list(pokemon_database[pokemon]["fast_attack"].items())[0]
        fast_attack_type = retrieve_move_type(fast_attack_name, moves_database)

        charge_moves = pokemon_database[pokemon]["charge_moves"]
        charge_move_name, charge_move_sequence = random.choice(list(charge_moves.items()))
        charge_move_type = retrieve_move_type(charge_move_name, moves_database)

        question = f"Give sequence of how many **{fast_attack_name}** moves are required"
        question += f" for **{pokemon}** to use **{charge_move_name}** four times in a row?"
        question = style_text(question, pokemon, get_element_type_color(pokemon_type))
        question = style_text(question, fast_attack_name, get_element_type_color(fast_attack_type))
        question = style_text(question, charge_move_name, get_element_type_color(charge_move_type))

        answer = ", ".join(map(str, charge_move_sequence))
        answer_explanation = ""
        variants = [", ".join([str(c) for c in charge_move_sequence])]

        if answer not in variants:
            variants[random.randint(0, len(variants) - 1)] = answer

        question_type = "charged_move"

    return {
        "type": question_type,
        "question": question,
        "variants": variants,
        "answer": answer,
        "answer_explanation": answer_explanation,
    }
