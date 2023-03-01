from flask import Flask, request
import requests
import xmltodict
import math
from typing import List
import yaml

app = Flask(__name__)

data = None

def iss_data() -> dict:
    """
    Pulls trajectory data (position, velocity) from the ISS from NASA.
 
    Arguments:
        None
    Returns:
        iss_data (dict): a dictionary of trajectory data for the ISS in km and km/s.
    """
    r = requests.get('https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    return xmltodict.parse(r.text)

@app.route('/', methods=['GET'])
def data_set() -> List[dict]:
    """
    Provides ISS Trajectory data as a list of dictionaries.

    Arguments:
        None
    Returns:
        iss_data (List[dict]): a list of dictionaries containing trajectory data for the ISS in km and km/s.
    """
    global data
    temp = iss_data()
    data = temp['ndm']['oem']['body']['segment']['data']['stateVector']
    return data 

@app.route('/epochs', methods=['GET'])
def list_of_all_epochs() -> dict:
    """
    This function lists all of the epochs provided in the data pulled from NASA.

    Arguments:
        None
    Returns:
        epochs (dict): dict of all epochs in the data set and their indicies, epochs in J2000 format.
    """

    try:
        len(data)
    except TypeError:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400

    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', len(data))

    if offset:
        try:
            offset = int(offset)
        except ValueError:
            return 'Invalid offset parameter; offset must be an integer.\n', 400
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return 'Invalid limit parameter; limit must be an integer.\n', 400
        
    epochs = {}
    for i in range(limit):
        epochs[data[i+offset]['EPOCH']] = i+offset
    return epochs

@app.route('/epochs/<int:epoch>', methods=['GET'])
def state_vector(epoch:int) -> dict:
    """
    Returns the position of the ISS at a specified epoch.

    Arguments:
        epoch (int): index of the epoch of interest.
    Returns:
        state vector (dict): x, y, and z position vector of the ISS in km.
    """
    try:
        len(data)
    except TypeError:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400

    epoch_data = data[epoch]
    d = {}
    d['x'] = epoch_data['X']['#text']
    d['y'] = epoch_data['Y']['#text']
    d['z'] = epoch_data['Z']['#text']
    return d

@app.route('/epochs/<int:epoch>/speed', methods=['GET'])
def inst_speed(epoch:int) -> dict:
    """
    Returns the instantaneous speed of the ISS at a specified epoch.

    Arguments:
        epoch (int): index of the epoch of interest.
    Returns:
        state vector (dict): speed of the ISS in km/s.
    """
    try:
        len(data)
    except TypeError:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400

    epoch_data = data[epoch]
    d = {}
    xdot = float(epoch_data['X_DOT']['#text'])
    ydot = float(epoch_data['Y_DOT']['#text'])
    zdot = float(epoch_data['Z_DOT']['#text'])
    d['speed'] = math.sqrt(xdot*xdot + ydot*ydot + zdot*zdot)
    return d

@app.route('/delete-data', methods=['DELETE'])
def delete_data() -> str:
    """
    Arguments:
        None
    Returns:
        deletion_success (str): deletion success message
    """

    global data
    data = None
    return 'Data deleted.\n'

@app.route('/post-data', methods=['POST'])
def post_data() -> str:
    """
    Arguments:
        None
    Returns:
        post_success (str): post success message
    """

    global data
    temp = iss_data()
    data = temp['ndm']['oem']['body']['segment']['data']['stateVector']
    return 'Data reloaded.\n'

@app.route('/help', methods=['GET'])
def help() -> str:
    """
    Arguments:
        None
    Returns:
        help_msg (str): message containing information on all routes in app
    """

    base = '[/]   Returns the entire data set \n'
    epochs = '[/epochs]  Returns list of all Epochs in the data set\n'
    epochs_spec = '[/epochs?limit=int&offset=int] Returns modified list of Epochs given query parameters\n'
    epoch = '[/epochs/<int:epoch>]    Returns state vectors for a specific Epoch from the data set\n'
    speed = '[/epochs/<int:epoch>/speed]  Returns instantaneous speed for a specific Epoch in the data set\n'
    h = '[/help]  Returns help text that describes each route\n'
    delete_data = '[/delete-data] Deletes all data from the dicitonary object\n'
    post = '[/post-data]  Reloads the dictionary object with data from the web\n'
    
    return base + epochs + epochs_spec + epoch + speed + h + delete_data + post

def get_config() -> dict:
    """
    Aruguments:
        None
    Returns:
        config (dict): debug parameter
    """

    default_config = {"debug": False}
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Couldn't load the config file; details: {e}")
    # if we couldn't load the config file, return the default config
    return default_config

if __name__ == '__main__':
    config = get_config()
    if config.get('debug', True):
        app.run(debug=True, host='0.0.0.0')
    else:
        app.run(host='0.0.0.0')
