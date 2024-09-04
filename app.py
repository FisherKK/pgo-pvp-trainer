import os
from flask import Flask, render_template, request, jsonify, session
from project.generator import generate_question
from project.io import load_json

app = Flask(__name__)

# Load databases
def load_databases():
    pokedex_filename = [f for f in os.listdir("data") if f.startswith("pokedex_")][0]
    pokedex_filepath = os.path.join("data", pokedex_filename)
    with open(pokedex_filepath, "r") as file:
        pokedex = load_json(file)

    moves_filename = [f for f in os.listdir("data") if f.startswith("moves_")][0]
    moves_filepath = os.path.join("data", moves_filename)
    with open(moves_filepath, "r") as file:
        moves = load_json(file)

    return pokedex, moves, pokedex_filename, moves_filename

pokedex_database, moves_database, pokedex_filename, moves_filename = load_databases()

@app.route('/')
def index():
    if 'pokemon_max_cp' not in session:
        session['pokemon_max_cp'] = 1500
    if 'pokemon_database' not in session:
        session['pokemon_database'] = {}
    if 'current_question' not in session:
        session['current_question'] = None
    return render_template('index.html')

@app.route('/get_sidebar_data')
def get_sidebar_data():
    return jsonify({
        'pokedex_filename': pokedex_filename,
        'moves_filename': moves_filename,
        'pokemon_max_cp': session.get('pokemon_max_cp', 1500),
        'dataset_files': [f for f in os.listdir("datasets") if f.endswith(".json")]
    })

@app.route('/update_max_cp', methods=['POST'])
def update_max_cp():
    max_cp = request.json['max_cp']
    session['pokemon_max_cp'] = max_cp
    return jsonify({'success': True, 'new_max_cp': max_cp})

@app.route('/load_dataset', methods=['POST'])
def load_dataset():
    dataset_filepath = request.json['dataset_filepath']
    with open(os.path.join("datasets", dataset_filepath), "r") as file:
        pokemon_database = load_json(file)
        session['pokemon_database'] = pokemon_database
    return jsonify({'success': True, 'message': f'Dataset {dataset_filepath} loaded successfully!'})

@app.route('/get_question', methods=['POST'])
def get_question():
    attack_comparison_ratio = float(request.json.get('attack_comparison_ratio', 1.0))
    fast_attacks_ratio = float(request.json.get('fast_attacks_ratio', 1.0))
    charged_moves_ratio = float(request.json.get('charged_moves_ratio', 1.0))

    if attack_comparison_ratio == 0 and fast_attacks_ratio == 0 and charged_moves_ratio == 0:
        return jsonify({
            'question': 'All questions disabled - check settings.',
            'type': 'disabled'
        })

    question_data = generate_question(
        session.get('pokemon_database', {}),
        pokedex_database,
        moves_database,
        session.get('pokemon_max_cp', 1500),
        attack_comparison_ratio,
        fast_attacks_ratio,
        charged_moves_ratio
    )
    session['current_question'] = question_data
    return jsonify(question_data)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    user_input = request.json['user_input']
    current_question = session.get('current_question')
    
    if not current_question:
        return jsonify({'error': 'No current question'})

    question_type = current_question['type']
    correct_answer = current_question['answer']
    answer_explanation = current_question['answer_explanation']
    
    if question_type == 'charged_move':
        user_sequence = [int(x.strip()) for x in user_input.replace(' ', '').split(',') if x.strip()]
        correct_sequence = [int(x.strip()) for x in correct_answer.replace(' ', '').split(',') if x.strip()]
        is_correct = user_sequence == correct_sequence
    else:
        is_correct = str(user_input).strip() == str(correct_answer).strip()
    
    return jsonify({
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'answer_explanation': answer_explanation
    })


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))