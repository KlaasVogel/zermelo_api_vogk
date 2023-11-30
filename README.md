## zermelo_api_vogk
A Module to create a Zermelo access token and put data from Zermelo in dataclasses

# V0.2.4
 - added getting appointments

# V0.2.3
 - changed getting lesgroepen only as return so not part of branch anymore
 - removed lastcheck from lesgroepen

# V0.2.2
 - bugfix lesgroepen
 - added write to logger (debug)
 - changed repr of Users

# V0.2.1
 - added datetime to each branch
 - init of branches is now only datestring, year will be determined internally

# V0.2.0
 - changed decorator from_zermelo_dict to function

# V0.1.3
- added lesgroepen

# V0.1.2
- added Vakken

# V0.1.1
  - added groepen / groups
  - First setup of vakken
  - cleanup of code

# V0.1.0: First Refactoring already:
- deleted fields.py and moved usefull functions to zermelo_api
- loading of data for (zermelo)list generalized in zermelo_api

# V0.0.8:
 - Added loading of Users (Leerlingen & Medewerkers)
 - Added backtracker to MyLogger

# V0.0.7:
- Added Loading of Branches

# V0.0.1 -> V0.0.5:
- Experimenting with creating of own package and major structure of project
