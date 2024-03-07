from flask import Flask, render_template, request
from main import start_joining_threads

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join', methods=['POST'])
def handle_join_request():
    try:
        game_id = request.form['game_id']
        nick_start = request.form['nick_start']

        start_joining_threads(game_id, nick_start)
        # Correct the text to indicate the number of join attempts, not the duration.
        return f"Attempting to join game {game_id} with nicknames starting with {nick_start}."
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
