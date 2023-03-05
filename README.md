# ISS Tracker

## Description
Knowing the current position and velocity of the ISS is vital to ensuring that it does not collide with anything else that is in orbit. Fortunately, data concerning the ISS' orbital ephemeris (position and velocity) is publically avaliable. However, sifting through this data for the information desired is time consuming, so the ability to query and return informaiton pertaining to a particular epoch (point in time) is important.

### Flask
This program uses the Python Flask library. Flask is a web framework used to develop generalized web applications. To install Flask, please enter the following command into your terminal:

```
$ pip3 install --user flask
```

### Required Data
Data required for this app is the [ISS Trajectory Data](https://spotthestation.nasa.gov/trajectory_data.cfm) provided by Spot The Station in XML format, which is accessed using the Python `requests` library. If requests is not installed on your machine, please install it using the following command in your terminal:

```
$ pip3 install --user requests
```
The data can also be accessed in text format (`.txt`). Both file formats contain headers, comments, metadata, and data. The important information for this app is the data, which is in the form of a state vector consisting of position (km) and velocity (km/s).

### iss_tracker.py
This script contains the application and its queries. It pulls the ISS data from the internet and allows the user to query the entire data set, a list of epochs, position at a specific epoch, and instantaneous speed at a specific epoch.

To calculate instantaenous speed, `iss_tracker.py` uses the following equation:
```math
speed = \sqrt{\dot{x}^2+\dot{y}^2+\dot{z}^2}
```

### Docker
To ensure functionality of this program, a Docker image is utilized. To pull the associated docker image, run

#### Pull the Docker Image
```
docker pull lajoiekatelyn/iss_tracker:midterm

#### docker-compose
To build and then run the app with debug mode OFF and to map the Docker port to a port on your local machine, run
```
docker-compose up
```

## Usage
To launch the app, please navigate to the root of the homework05 folder. Then, enter the following into the terminal to run the app locally in debug mode
```
$ flask --app iss_tracker run
```
or in a container with debug mode off (AFTER following the Docker instructions above):
```
docker-compose up
```
Then, open a new terminal on the same local machine and query the app.

### Help
To return a help text that describes each route in the app,
```
$ curl localhost:5000/help
[/]   Returns the entire data set
[/epochs]  Returns list of all Epochs in the data set
[/epochs?limit=int&offset=int] Returns modified list of Epochs given query parameters
[/epochs/<int:epoch>]    Returns state vectors for a specific Epoch from the data set
[/epochs/<int:epoch>/speed]  Returns instantaneous speed for a specific Epoch in the data set
[/help]  Returns help text that describes each route
[/delete-data] Deletes all data from the dicitonary object
[/post-data]  Reloads the dictionary object with data from the web
```

### Post Data
To post the data set to the app and recieve a `Data loaded.` message:
```
curl -X POST localhost:5000/post-data
```

### Delete Data
To delete all of the data on the app and recieve a `Data deleted.` message:
```
curl -X DELETE localhost:5000/data-delete
```

### Raw Data
To query all of the raw data (with the headers, comments, and metadata removed):
```
$ curl localhost:5000/
[
  {
    "EPOCH": "2023-046T12:00:00.000Z",
    "X": {
      "#text": "-4788.3685075076201",
      "@units": "km"
    },
    "X_DOT": {
      "#text": "-4.4731764053264502",
      "@units": "km/s"
    },
    "Y": {
      "#text": "1403.5496223712601",
      "@units": "km"
    },
    "Y_DOT": {
      "#text": "-5.4438825894668401",
      "@units": "km/s"
    },
    "Z": {
      "#text": "-4613.1094793006896",
      "@units": "km"
    },
    "Z_DOT": {
      "#text": "2.9970573852109199",
      "@units": "km/s"
    }
  },
  ...

```

### List of Epochs
To obtain a dictionary of all the epochs in the data and their respective indicies, such that they can be called to find a specific position vector:
```
$ curl localhost:5000/epochs
{
  "2023-046T12:00:00.000Z": 0,
  "2023-046T12:04:00.000Z": 1,
  "2023-046T12:08:00.000Z": 2,
  "2023-046T12:12:00.000Z": 3,
  "2023-046T12:16:00.000Z": 4,
  "2023-046T12:20:00.000Z": 5,
  "2023-046T12:24:00.000Z": 6,
  "2023-046T12:28:00.000Z": 7,
  "2023-046T12:32:00.000Z": 8,
  "2023-046T12:36:00.000Z": 9,
  "2023-046T12:40:00.000Z": 10,
  ...
```
A limited number of epochs and/or an offset set of Epochs can be queries as well. For example,
```
$ curl 'localhost:5000/epochs?limit5&offset=5'
{
  "2023-046T12:20:00.000Z": 5,
  "2023-046T12:24:00.000Z": 6,
  "2023-046T12:28:00.000Z": 7,
  "2023-046T12:32:00.000Z": 8,
  "2023-046T12:36:00.000Z": 9
}
```

### Position Vector
```
$ localhost:5000/epoch/0
```
will return the position of the top of the data file as a dictionary, where `x`, `y`, and `z` are in km.
```
{"x":"-4788.3685075076201","y":"1403.5496223712601","z":"-4613.1094793006896"}
```
### Speed
Finally, speed can also be queried:
```
$ localhost:5000/epoch/0/speed
```
which will return the instantaneous speed of the ISS in km/s as a dictionary.
```
{"speed":7.656860830086751}
```
