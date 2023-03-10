from flask import Flask, request
import requests
import xmltodict
import math
import yaml
from geopy.geocoders import Nominatim
import time

app = Flask(__name__)

def iss_data() -> dict:
    """
    Pulls the complete ISS dataset from the web.
 
    Arguments:
        None
    Returns:
        iss_data (dict): a dictionary data for the ISS, including position and velocity in km and km/s, respectively..
    """

    r = requests.get('https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    return xmltodict.parse(r.text)

# load ISS data into global data variable, same as iss_data() below.
data = iss_data()
MEAN_EARTH_RADIUS = 6371

@app.route('/', methods=['GET'])
def data_set() -> dict:
    """
    Provides ISS Trajectory data as a list of dictionaries.

    Arguments:
        None
    Returns:
        iss_data (dict): dictionaries containing information on the ISS' position and location over a span of 15 days.
    """
    if not data:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400

    return data 

@app.route('/comment', methods=['GET'])
def comment() -> dict:
    """
    Provides the comment heading from the pulled dataset.

    Arguments:
        None
    Returns
        comment (dict): summarizes trajectory events and provides mass, ascending node passings with units, and coefficients.
    """
    if not data:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400
    
    return {'COMMENT': data['ndm']['oem']['body']['segment']['data']['COMMENT']}

@app.route('/header', methods=['GET'])
def header() -> dict:
    """
    Provides the header for the pulled dataset.

    Arguments:
        None
    Returns:
        header (dict): the start time of the data set and the publisher.
    """
    
    if not data:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400
    
    return {'header': data['ndm']['oem']['header']}

@app.route('/metadata', methods=['GET'])
def metadata() -> dict:
    """
    Provides the metadata from the pulled dataset.

    Arguments:
        None
    Returns:
        metadata (dict): identifies the object and its orbit and the start and end time of the data set.
    """
    
    if not data:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400
    
    return {'metadata': data['ndm']['oem']['body']['segment']['metadata']}

@app.route('/epochs', methods=['GET'])
def list_of_all_epochs() -> dict:
    """
    This function lists all of the epochs provided in the data pulled from NASA.

    Arguments:
        None
    Returns:
        epochs (dict): dict of all epochs in the data set and their indicies, epochs in J2000 format.
    """

    if not data:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400

    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', len(data['ndm']['oem']['body']['segment']['data']['stateVector']))

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
        epochs[data['ndm']['oem']['body']['segment']['data']['stateVector'][i+offset]['EPOCH']]=i+offset
    return epochs

@app.route('/epochs/<string:epoch>', methods=['GET'])
def state_vector(epoch:str) -> dict:
    """
    Returns the state vector of the ISS at a specified epoch.

    Arguments:
        epoch (int): index of the epoch of interest.
    Returns:
        state vector (dict): x, y, and z position and velocity vectors of the ISS in km and km/s, respectively..
    """
    if not data:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400
    
    for item in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        if item['EPOCH'] == epoch:
            return item

    return 'Requested epoch does not exist in data set.\n', 400

@app.route('/epochs/<string:epoch>/location', methods=['GET'])
def location(epoch:str) -> dict:
    """
    This function returns the latitude and longitude of the ISS at a given epoch, a long with details covering the area over which the ISS is passing.

    Arguments:
        epoch (int): index of the epoch of interest
    Returns:
        location (dict): latitude, longitude, and geoposition (if it is over land) of the ISS.    

    """

    if not data:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400
    
    epoch_data = state_vector(epoch)
    if not isinstance(epoch_data, dict):
        return epoch_data

    hrs = int(epoch_data['EPOCH'][9:11]) 
    mins = int(epoch_data['EPOCH'][12:14])

    x = float(epoch_data['X']['#text'])
    y = float(epoch_data['Y']['#text'])
    z = float(epoch_data['Z']['#text'])
    
    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))                
    lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 24
    alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS 
    
    d = {
            'location': {
                'latitude': lat,
                'longitude': lon,
                'altitude': {
                    'value': alt,
                    'units': 'km'
                    }
                }
         }

    geocoder = Nominatim(user_agent='iss_tracker')
    geoloc = geocoder.reverse((lat, lon), zoom=15, language='en')
    
    try:
        geoloc = geoloc.raw
    except AttributeError:
        d['geo'] = 'Somewhere over the ocean.'
        return d
          
    d['geo'] = geoloc["address"]

    return d 

@app.route('/epochs/<string:epoch>/speed', methods=['GET'])
def inst_speed(epoch:str) -> dict:
    """
    Returns the instantaneous speed of the ISS at a specified epoch.

    Arguments:
        epoch (int): index of the epoch of interest.
    Returns:
        speed (dict): speed of the ISS in km/s.
    """
    
    if not data:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400

    epoch_data = state_vector(epoch)
    if not isinstance(epoch_data, dict):
        return epoch_data

    d = {}
    xdot = float(epoch_data['X_DOT']['#text'])
    ydot = float(epoch_data['Y_DOT']['#text'])
    zdot = float(epoch_data['Z_DOT']['#text'])
    d['value'] = math.sqrt(xdot*xdot + ydot*ydot + zdot*zdot)
    d['units'] = 'km/s'
    return {'speed': d}

@app.route('/now', methods=['GET'])
def now() -> dict:
    """
    Finds the epoch nearest to the current time and returns its location and speed.

    Argumentes:
        None
    Returns:
        current_iss_data (dict): location (latitude, longitude, geoposition) and speed of the ISS at the \"current\" time (closest epoch and time difference specified).

    """
    
    if not data:
        return 'Empty data; repost data using \'curl -X POST localhost:5000/post-data\'\n', 400

    time_now = time.time()
    epochs = list_of_all_epochs()
    epochs = list(epochs.keys())

    closest_epoch = None
    error = float('inf')
    ind = None
    for i in range(len(epochs)):
        epoch = epochs[i]
        time_epoch = time.mktime(time.strptime(epoch[:-5], '%Y-%jT%H:%M:%S'))
        difference = time_now - time_epoch
        if (abs(difference) < abs(error)):
            error = difference
            closest_epoch = epoch
            ind = i
        d = {
                'closest_epoch': closest_epoch,
                'seconds_from_now': error
            }
    
    d.update(inst_speed(closest_epoch))
    d.update(location(closest_epoch))
   
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
    data.clear()    
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
    data = iss_data()
    return 'Data reloaded.\n'

@app.route('/help', methods=['GET'])
def help() -> str:
    """
    Arguments:
        None
    Returns:
        help_msg (str): message containing information on all routes in app
    """

    top = '\nUsage: `curl localhost:5000/<option>` \n\nOptions: \n'
    base = '[/]                                 Returns the entire data set \n'
    comment = '[/comment]                          Returns the comment list from the ISS data\n'
    header = '[/header]                           Returns the header dicitonary from the ISS data\n'
    metadata = '[/metadata]                         Returns the metadata dictinoary from the ISS data\n'
    epochs = '[/epochs]                           Returns list of all Epochs in the data set\n'
    epochs_spec = '[/epochs?limit=int&offset=int]      Returns modified list of Epochs given query parameters\n'
    epoch = '[/epochs/<int:epoch>]               Returns state vectors for a specific Epoch from the data set\n'
    location = '[/eochs/<int:epoch>/location]       Returns latitude, longitude, altitude, and geoposition for a specific Epoch \n'
    speed = '[/epochs/<int:epoch>/speed]         Returns instantaneous speed for a specific Epoch in the data set\n'
    now = '[/now]                              Returns the real time position of the ISS\n'
    h = '[/help]                             Returns help text that describes each route\n'
    delete_data = '[/delete-data]                      Deletes all data from the dicitonary object\n'
    post = '[/post-data]                        Reloads the dictionary object with data from the web\n'
    ret=top+base+comment+header+metadata+epochs+epochs_spec+epoch+location+speed+now+h+delete_data+post+'\n'

    return ret

def get_config() -> dict:
    """
    Aruguments:
        None
    Returns:
        config (dict): debug parameter
    """

    default_config = {"debug": True}
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
