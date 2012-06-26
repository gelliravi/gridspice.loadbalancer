from flask import Flask, request
from SimulationManager import SimulationManager

app = Flask(__name__)

"""
TODO
- handle favicon.io and other similar things
- handle POST
"""

sim_manager = SimulationManager()

@app.route('/StartSimulation')
def startSimulation():
    return sim_manager.start_simulation(request)

@app.route('/<request_type>', methods=['GET', 'POST'])
def handle_generic_request(request_type):
    return sim_manager.handle_generic_result()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2160, debug=True)
