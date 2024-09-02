import os
import streamlit as st

from project.generator import generate_question
from project.io import load_json

st.set_page_config(page_title="PGO PvP Trainer", page_icon="🎮", layout="centered", initial_sidebar_state="collapsed")
st.sidebar.title("Settings")

# Dataset Settings Section
with st.sidebar.expander("Dataset Settings", expanded=True):
    if "pokedex_database" not in st.session_state:
        pokedex_filename = [f for f in os.listdir("data") if f.startswith("pokedex_")][0]
        pokedex_filepath = os.path.join("data", pokedex_filename)
        with open(pokedex_filepath, "r") as file:
            pokedex = load_json(file)
            st.session_state.pokedex_database = pokedex
            st.session_state.pokedex_database_filename = pokedex_filename

    if "moves_database" not in st.session_state:
        moves_filename = [f for f in os.listdir("data") if f.startswith("moves_")][0]
        moves_filepath = os.path.join("data", moves_filename)
        with open(moves_filepath, "r") as file:
            moves = load_json(file)
            st.session_state.moves_database = moves
            st.session_state.moves_database_filename = moves_filename

    if "pokedex_database_filename" in st.session_state:
        st.text(f"Pokédex file: {st.session_state.pokedex_database_filename}")
    if "moves_database_filename" in st.session_state:
        st.text(f"Moves file: {st.session_state.moves_database_filename}")

    data_source = st.radio("Select Data Source", ("Select Database", "Load Database"), index=0)
    dataset_filepath = None

    if data_source == "Load Database":
        dataset_filepath = st.file_uploader("Load Pokémon JSON File", type=["json"])
    elif data_source == "Select Database":
        dataset_files = [f for f in os.listdir("datasets") if f.endswith(".json")]
        dataset_filepath = st.selectbox("Select a Dataset", dataset_files)
        if st.button("Load"):
            with open(os.path.join("datasets", dataset_filepath), "r") as file:
                pokemon_database = load_json(file)
                st.session_state.pokemon_database = pokemon_database
                st.success(f"{dataset_filepath} loaded successfully!")

# Pokemon Max CP Settings Section
with st.sidebar.expander("Pokemon Max CP Settings", expanded=False):
    if "pokemon_max_cp" not in st.session_state:
        st.session_state.pokemon_max_cp = 1500

    max_cp_options = {500: "500", 1500: "1500", 2500: "2500", "Max": "Max"}
    cols = st.columns(2)
    for i, (value, label) in enumerate(max_cp_options.items()):
        if cols[i % 2].button(label, key=f"cp_{label}", use_container_width=True):
            st.session_state.pokemon_max_cp = value

    st.write(f"Selected Max Pokémon CP: {st.session_state.pokemon_max_cp}")

# Question Generation Settings Section
with st.sidebar.expander("Question Generation Settings", expanded=False):
    attack_comparison_ratio = st.slider(
        "Attack Comparison Question Ratio",
        0.0,
        1.0,
        1.0,
        help="Adjust the ratio of Attack Comparison questions occurrence",
    )
    fast_attacks_ratio = st.slider(
        "Fast Attacks Question Ratio",
        0.0,
        1.0,
        1.0,
        help="Adjust the ratio of Fast Attacks questions occurrence",
    )
    charged_moves_ratio = st.slider(
        "Charged Moves Question Ratio",
        0.0,
        1.0,
        1.0,
        help="Adjust the ratio of Charged Moves questions occurrence",
    )

if data_source == "Load Database" and dataset_filepath:
    pokemon_database = load_json(dataset_filepath)
    st.session_state.pokemon_database = pokemon_database
    st.sidebar.success("Pokémon data loaded successfully!")

if "pokedex_database" not in st.session_state:
    st.session_state.pokedex_database = {}

if "moveset_database" not in st.session_state:
    st.session_state.moveset_database = {}

if "pokemon_database" not in st.session_state:
    st.session_state.pokemon_database = {}

if "question_data" not in st.session_state:
    st.session_state.question_data = None

if "last_answer_correct" not in st.session_state:
    st.session_state.last_answer_correct = None

if "user_input" not in st.session_state:
    st.session_state.user_input = ""


def validate_charge_move_input(user_input, correct_answer):
    if not user_input:
        return False

    user_sequence = [int(x.strip() if x != " " else "0") for x in user_input.split(",")]
    correct_sequence = [int(x.strip()) for x in correct_answer.split(",")]
    return all(correct_sequence[i] == user_sequence[i] for i in range(len(correct_sequence)))


st.title("PGO PvP Trainer")

if st.session_state.pokemon_database:
    cols = st.columns(2)
    next_question_clicked = cols[0].button("Next Question")
    show_answer_clicked = cols[1].button("Show Answer")

    if next_question_clicked or st.session_state.question_data is None:
        st.session_state.question_data = generate_question(
            st.session_state.pokemon_database,
            st.session_state.pokedex_database,
            st.session_state.moves_database,
            st.session_state.pokemon_max_cp,
            attack_comparison_ratio,
            fast_attacks_ratio,
            charged_moves_ratio,
        )
        st.session_state.last_answer_correct = None
        st.session_state.user_input = ""

    if st.session_state.question_data:
        question = st.session_state.question_data["question"]
        variants = st.session_state.question_data["variants"]
        correct_answer = st.session_state.question_data["answer"]
        answer_explanation = st.session_state.question_data["answer_explanation"]

        st.markdown(f"**Question**: {question}", unsafe_allow_html=True)

        if show_answer_clicked:
            st.markdown(
                f"**Answer**: {correct_answer} {answer_explanation}", unsafe_allow_html=True
            )

        if st.session_state.question_data["type"] == "charged_move":
            keyboard = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], [",", "Enter", "X"]]

            for row in keyboard:
                cols = st.columns(3)
                for i, key in enumerate(row):
                    with cols[i]:
                        if st.button(key, key=f"key_{row}_{i}", use_container_width=True):
                            if key == "Enter":
                                if validate_charge_move_input(
                                        st.session_state.user_input, correct_answer
                                ):
                                    st.session_state.last_answer_correct = True
                                else:
                                    st.session_state.last_answer_correct = False
                            elif key == "X":
                                st.session_state.user_input = st.session_state.user_input[:-1]
                            elif key == "," and not st.session_state.user_input.endswith(", "):
                                st.session_state.user_input += ", "
                            else:
                                st.session_state.user_input += key

            st.text_area(
                "Your Input:", value=st.session_state.user_input, key="input_area", disabled=True
            )

            if st.session_state.last_answer_correct is not None:
                if st.session_state.last_answer_correct:
                    st.markdown(
                        f'<span style="color: green;">Correct!</span>', unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<span style="color: red;">Incorrect! The correct answer is: {correct_answer}</span>',
                        unsafe_allow_html=True,
                    )
        else:
            cols = st.columns(2)
            for idx, variant in enumerate(variants):
                col = cols[idx % 2]
                if col.button(str(variant), key=f"btn_{idx}", use_container_width=True):
                    if variant == correct_answer:
                        st.session_state.last_answer_correct = True
                        st.markdown(
                            f'<span style="color: green;">Correct! {answer_explanation}</span>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.session_state.last_answer_correct = False
                        st.markdown(
                            f'<span style="color: red;">Incorrect! The correct answer is: {correct_answer} {answer_explanation}</span>',
                            unsafe_allow_html=True,
                        )
else:
    st.info("Please select or upload a Pokémon database to start the quiz.")