import os
import httplib
import urllib
import urllib2
import json
import copy

from elementtree.ElementTree import XML, Element

"""
TODO
- document
    - server_config.json

"""

# TODO - hardcoded for now. will be abstracted out
HOST = 'localhost'
PORT = 5000

# Server Config File
SERVER_CONFIG_FILE = "server_config.json"

# File system settings
SIM_DIR = "simulations"

# Initialization functions

class SimulationManager():

    def __init__(self):
        # instance variables
        self.servers = []
        self.curr_server_index = 0

        # init subroutines
        self.__init_server_config()
        self.__prepare_file_system()

    def start_simulation(self, request):
        # TODO remove hardcoding
        # should be selected from self.servers, which is initialized from the 
        # config file. Right now we're just always running the model on 
        # localhost, which is not useful
        host = 'localhost'
        port = '5000'

        response = {}
        simulation_id = request.args.get('simulationId', '')
        if simulation_id == '':
            return 'Must supply a simulation id'
        old_xml = request['xml']
        for split_simulation in __split_models(self, old_xml):
            model_id = split_simulation[0]
            sim_xml = split_simulation[1]
            request['xml'] = sim_xml 
            try:
                url = 'http://%s:%d/StartSimulation?%s' % (host, port, 
                    urllib.urlencode(request.args))
                r = urllib2.urlopen(url) 
                response[model_id] = r.read()
                self.__log_to_disk(host, port, simulation_id, model_id)
            except httplib.HTTPException:
                response[model_id] = 'error - server returned error'
            except urllib2.URLError:
                response[model_id] = 'error - could not connect to server'
        return str(response)

    def handle_generic_request(request_type, request):
        r = None
        if request.method == "GET":
            simulation_id = request.args.get('simulationId', '')
            model_id = request.args.get('modelId', '')
            if simulation_id == '':
                return 'Must supply a simulation id'
            elif model_id == '':
                return 'Must supply a model id'
            else:
                try:
                    with open('%s/%s/%s.json' % (SIM_DIR, simulation_id, model_id)) as f:
                        simulation_info = json.load(f) # TODO handle exception here
                        url = 'http://%s:%s/%s?%s' % (simulation_info['host'], 
                            simulation_info['port'], request_type, 
                            urllib.urlencode(request.args))
                        r = urllib2.urlopen(url) # TODO handle exceptions here
                        return r.read()
                except IOError:
                    return 'invalid simulation id'
        elif request.method == "POST":
            #TODO - handle post requests
            pass

        return "nothing happened"

    def __init_server_config(self):
        with open(SERVER_CONFIG_FILE) as f:
            server_config = json.load(f)
            self.servers = server_config['servers']

    def __prepare_file_system(self):
        if not os.path.exists(SIM_DIR):
            os.mkdir(SIM_DIR)
        elif not os.path.isdir(SIM_DIR):
            os.rmdir(SIM_DIR)
            os.mkdir(SIM_DIR)

    def __split_models(self, xmlDoc):
        """generator that takes parameter xmlDoc and splits it into many
        xml files, with only one model per each"""
        elem = XML(xmlDoc)
        models = elem.find("Models")
        if models:
            elem.remove(models)
            for model in models:    
                to_return = copy.deepcopy(elem)    
                new_models = Element("Models")
                for a in models.attrib:
                    new_models.attrib[a] = models.attrib[a]
                new_models.append(model)
                to_return.append(new_models)
                yield (model.attrib['id'], to_return)
        else:
            pass #TODO return error

    def __log_to_disk(self, host, port, simulation_id, model_id):
        simulation_directory = '%s/%s' % (SIM_DIR, simulation_id)
        file_path = '%s/%s.json' % (simulation_directory, model_id)
        if not os.path.exists(simulation_directory): 
            os.mkdir(simulation_directory)
        with open(file_path, 'w')  as f:
            info = {
                'host': host,
                'port': port
            }
            json.dump(info, f)
