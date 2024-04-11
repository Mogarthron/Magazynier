from Flask_server import app
import sys


if __name__ == "__main__":
    if len(sys.argv) == 1:
        app.run(debug=True, host="127.0.0.1", port=5000)
    else:
        app.run(debug=True, host=sys.argv[1], port=sys.argv[2])