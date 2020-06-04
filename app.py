from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def test():
    print(os.system("ffmpeg"))
    return jsonify({"test" : 1})


if __name__ == '__main__':
    app.run(debug=True)