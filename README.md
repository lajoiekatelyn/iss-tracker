# ISS Tracker

## Description
Knowing the current position and velocity of the ISS is vital to ensuring that it does not collide with anything else that is in orbit. Fortunately, data concerning the ISS' orbital ephemeris (position and velocity) is publically avaliable. However, sifting through this data for the information desired is time consuming, so the ability to query and return informaiton pertaining to a particular epoch (point in time) is important.

### Flask
This program uses the Python Flask library. Flask is a web framework used to develop generalized web applications. To install Flask, please enter the following command into your terminal:

```console
[user]:~$ pip3 install --user flask
```

### Required Data
Data required for this app is the [ISS Trajectory Data](https://spotthestation.nasa.gov/trajectory_data.cfm) provided by Spot The Station in XML format, which is accessed using the Python `requests` library. If requests is not installed on your machine, please install it using the following command in your terminal:

```console
[user]:~$ pip3 install --user requests
```
The data can also be accessed in text format (`.txt`). Both file formats contain headers, comments, metadata, and data. The important information for this app is the data, which is in the form of a state vector consisting of position (km) and velocity (km/s).

### iss_tracker.py
This script contains the application and its queries. It pulls the ISS data from the internet and allows the user to query the entire data set, a list of epochs, position at a specific epoch, and instantaneous speed at a specific epoch.

To calculate instantaenous speed, `iss_tracker.py` uses the following equation:
```math
speed = \sqrt{\dot{x}^2+\dot{y}^2+\dot{z}^2}
```

To provide latitude, longitude, and altitude, the program uses functions provided by J. Wallen in the midterm instructions:
```python
lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))                
lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 24
alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS 
```

### Docker
To ensure functionality of this program, a Docker image is utilized. To pull the associated docker image, run

#### Pull the Docker Image
```console
[user]:~$ docker pull lajoiekatelyn/iss_tracker:midterm
```

#### docker-compose
To build and then run the app and to map the Docker port to a port on your local machine, run
```console
[user]:~/iss-tracker$ docker-compose up --build
```

## Usage
To launch the app, please navigate to the root of the homework05 folder. Then, enter the following into the terminal to run the app locally in debug mode
```console
[user]:~/iss-tracker$ flask --app iss_tracker run
```
or in a container (AFTER following the Docker instructions above):
```console
[user]:~/iss-tracker$ docker-compose up
```
Then, open a new terminal on the same local machine and query the app.

### Help
To return a help text that describes each route in the app,
```console
[user]:~$ curl localhost:5000/

Usage: `curl localhost:5000/<option>`

Options:
[/]                                 Returns the entire data set
[/comment]                          Returns the comment list from the ISS data
[/header]                           Returns the header dicitonary from the ISS data
[/metadata]                         Returns the metadata dictinoary from the ISS data
[/epochs]                           Returns list of all Epochs in the data set
[/epochs?limit=int&offset=int]      Returns modified list of Epochs given query parameters
[/epochs/<int:epoch>]               Returns state vectors for a specific Epoch from the data set
[/eochs/<int:epoch>/location]       Returns latitude, longitude, altitude, and geoposition for a specific Epoch
[/epochs/<int:epoch>/speed]         Returns instantaneous speed for a specific Epoch in the data set
[/now]                              Returns the real time position of the ISS
[/help]                             Returns help text that describes each route
[/delete-data]                      Deletes all data from the dicitonary object
[/post-data]                        Reloads the dictionary object with data from the web

```

### Post Data
To post the data set to the app and recieve a `Data loaded.` message:
```console
[user]:~$ curl -X POST localhost:5000/post-data
```

### Delete Data
To delete all of the data on the app and recieve a `Data deleted.` message:
```console
[user]:~$ curl -X DELETE localhost:5000/data-delete
```

### Comment
For more technical information on the orbit of the ISS:
```console
[user]:~$ curl localhost:5000/comment
{
  "COMMENT": [
    "Units are in kg and m^2",
    "MASS=473413.00",
    "DRAG_AREA=1618.40",
    "DRAG_COEFF=2.20",
    "SOLAR_RAD_AREA=0.00",
    "SOLAR_RAD_COEFF=0.00",
    "Orbits start at the ascending node epoch",
    "ISS first asc. node: EPOCH = 2023-03-03T16:45:01.089 $ ORBIT = 2542 $ LAN(DEG) = 78.61627",
    "ISS last asc. node : EPOCH = 2023-03-18T14:19:09.505 $ ORBIT = 2773 $ LAN(DEG) = 26.64425",
    "Begin sequence of events",
    "TRAJECTORY EVENT SUMMARY:",
    null,
    "|       EVENT        |       TIG        | ORB |   DV    |   HA    |   HP    |",
    "|                    |       GMT        |     |   M/S   |   KM    |   KM    |",
    "|                    |                  |     |  (F/S)  |  (NM)   |  (NM)   |",
    "=============================================================================",
    "GMT 067 ISS Reboost   067:20:02:00.000             1.0     427.0     407.3",
    "(3.3)   (230.6)   (219.9)",
    null,
    "Crew05 Undock         068:08:00:00.000             0.0     427.0     410.8",
    "(0.0)   (230.6)   (221.8)",
    null,
    "SpX27 Launch          074:00:30:00.000             0.0     426.7     409.9",
    "(0.0)   (230.4)   (221.3)",
    null,
    "SpX27 Docking         075:12:00:00.000             0.0     426.7     409.8",
    "(0.0)   (230.4)   (221.3)",
    null,
    "=============================================================================",
    "End sequence of events"
  ]
}
```

### Header
For information on the publisher and the oldest data point in data set:
```console
[user]:~$ curl localhost:5000/header
{
  "header": {
    "CREATION_DATE": "2023-063T04:34:04.606Z",
    "ORIGINATOR": "JSC"
  }
}
```

### Metadata
For basic information on the subject of the data set and the data's timeframe:
```console
[user]:~$ curl localhost:5000/metadata
{
  "metadata": {
    "CENTER_NAME": "EARTH",
    "OBJECT_ID": "1998-067-A",
    "OBJECT_NAME": "ISS",
    "REF_FRAME": "EME2000",
    "START_TIME": "2023-062T15:47:35.995Z",
    "STOP_TIME": "2023-077T15:47:35.995Z",
    "TIME_SYSTEM": "UTC"
  }
}
```

### Raw Data
To query all of the raw data:
```console
[user]:~$ curl localhost:5000/
[
  ...
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
```console
[user]:~$ curl localhost:5000/epochs
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
```console
[user]:~$ curl 'localhost:5000/epochs?limit5&offset=5'
{
  "2023-046T12:20:00.000Z": 5,
  "2023-046T12:24:00.000Z": 6,
  "2023-046T12:28:00.000Z": 7,
  "2023-046T12:32:00.000Z": 8,
  "2023-046T12:36:00.000Z": 9
}
```

### State Vector
```console
[user]:~$ curl localhost:5000/epochs/2023-079T11:56:00.000Z
```
will return the state vector of the epoch queried as a dictionary,
```console
{
  "EPOCH": "2023-079T11:56:00.000Z",
  "X": {
    "#text": "-5278.6784637584797",
    "@units": "km"
  },
  "X_DOT": {
    "#text": "1.85340001562428",
    "@units": "km/s"
  },
  "Y": {
    "#text": "-3986.4000884792299",
    "@units": "km"
  },
  "Y_DOT": {
    "#text": "-4.7074783355013397",
    "@units": "km/s"
  },
  "Z": {
    "#text": "1546.6403334670899",
    "@units": "km"
  },
  "Z_DOT": {
    "#text": "-5.7580224140764198",
    "@units": "km/s"
  }
}
```
### Location
To query the latitude, longitude, altitude, and geoposition of a specific epoch
```console
[user]:~$ curl localhost:5000/epochs/2023-079T11:56:00.000Z/location
{
  "geo": "Somewhere over the ocean.",
  "location": {
    "altitude": {
      "units": "km",
      "value": 422.226649412044
    },
    "latitude": 13.16016247600921,
    "longitude": -117.94029757461675
  }
}
```
NOTE: in cases where `"geo": "Somewhere over the ocean.",` is returned, the ISS does not have a geolocation, as it is over an ocean.

### Speed
To query the instantaneous speed of a specific epoch:
```console
[user]:~$ curl localhost:5000/epochs/2023-079T11:56:00.000Z/speed
```
which will return the instantaneous speed of the ISS in km/s as a dictionary.
```console
{
  "speed": {
    "units": "km/s",
    "value": 7.664872211468172
  }
}
```

### Now
To find the recorded epoch closest to the time when the `now` route is queried:
```console
[user]:~$ curl localhost:5000/now
{
  "closest_epoch": "2023-064T16:55:00.000Z",
  "geo": {
    "ISO3166-2-lvl4": "CN-SC",
    "city": "Ngawa",
    "country": "China",
    "country_code": "cn",
    "county": "Ngawa County",
    "region": "Ngawa Tibetan and Qiang Autonomous Prefecture",
    "state": "Sichuan"
  },
  "location": {
    "altitude": {
      "units": "km",
      "value": 416.53947754175533
    },
    "latitude": 32.80853294941874,
    "longitude": 101.61136852015716
  },
  "seconds_from_now": 82.67322635650635,
  "speed": {
    "units": "km/s",
    "value": 7.668326332043633
  }
}
```
which gives the closest epoch, the number of seconds from the current epoch (at querying time), and the closest epoch's geolocation (`geo`), location, and speed.
