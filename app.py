from threading import Thread
from time import perf_counter, sleep

from flask import request, g, Flask, jsonify

from config import Config
from models import get_stats, get_attackers, add_stat, setup_db

app = Flask("__name__")
app.config.from_object(Config)


@app.before_request
def start_timer():
    g.start = perf_counter()


@app.teardown_request
def update_stats(exception=None):
    duration = perf_counter() - g.start
    t = Thread(target=add_stat, args=(duration,))
    t.start()


@app.route('/api/v1/attack', methods=["GET"])
def attack():
    vm_id = request.args.get('vm_id', '')
    return jsonify(get_attackers(vm_id))


@app.route('/api/v1/stats')
def stats():
    return jsonify(get_stats())


setup_db()

app.run(host='127.0.0.1', port=8080, threaded=True)
