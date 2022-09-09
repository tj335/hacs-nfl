# NFL game data in Home Assistant

This integration fetches data for an NFL team's current/future game, and creates a sensor with attributes for the details of the game. 

The integration is a shameless fork of the excellent [NFL](https://github.com/zacs/ha-nfl) custom component by @zacs.

## Sensor Data

### State
The sensor is pretty simple: the main state is `PRE`, `IN`, `POST`, `BYE` or `NOT_FOUND`, but there are attributes for pretty much all aspects of the game, when available. State definitions are as you'd expect:
- `PRE`: The game is in pre-game state. This happens on the first day of the game week, which seems to be Tuesday evenings around midnight Eastern time (once all the games through the Monday Night Football game are wrapped up). 
- `IN`: The game is in progress.
- `POST`: The game has completed. 
- `BYE`: Your given team has a bye week this week. Note that attributes available are limited in this case (only abreviation, name, logo, and last updated time will be available). 
- `NOT_FOUND`: There is no game found for your team, nor is there a bye. This should only happen at the end of the season, and once your team is eliminated from postseason play. 

### Attributes
The attributes available will change based on the sensor's state, a small number are always available (team abbreviation, team name, and logo), but otherwise the attributes only populate when in the current state. The table below lists which attributes are available in which states. 

| Name | Value | Relevant States |
| --- | --- | --- |
| `my_team_abbr` | The abbreviation of your team, used to match against the home or away team. | `PRE` `IN` `POST` `BYE` |
| `detailed_state` | A more detailed state of the sensor.  STATUS_SCHEDULED, STATUS_IN_PROGRESS, etc. | `PRE` `IN` `POST` |
| `game_end_time` | Date and time that the game ended | `POST` |
| `game_length` | Length of the game | `POST` |
| `date` | Date and time of the game | `PRE` `IN` `POST` |
| `attendance` | Number of fans in attendance | `POST` |
| `event_name` | Name of the event (eg. "New York Giants at Tennessee Titans") | `PRE` `IN` `POST` |
| `event_short_name` | Short name of the event (eg. "NYG @ TEN") | `PRE` `IN` `POST` |
| `event_type` | Type of event (eg. "STD" for Normal Regular Season, etc.) | `PRE` `IN` `POST` |
| `game_notes` | Game notes | `POST` |
| `series_summary` | Series summary | `POST` |
| `venue_name` | The name of the stadium where the game is being played (eg. "Nissan Stadium") | `PRE` `IN` `POST` |
| `venue_city` | The city where the game is being played (eg. "Nashville") | `PRE` `IN` `POST` |
| `venue_state` | The state where the game is being played (eg. "TN") | `PRE` `IN` `POST` |
| `venue_capacity` | The seating capacity of the stadium | `PRE` `IN` `POST` |
| `venue_indoor` | Indicator if the stadium is indoors (true) or outdoors (false) | `PRE` `IN` `POST` |
| `game_status` | Game status, depends on the state. (eg. "9/11 - 4:25 PM EDT" when in PRE). | `PRE` `IN` `POST` |
| `home_team_abbr` | The abbreviation for the home team (ie. `TEN` for the Titans). | `PRE` `IN` `POST` `BYE` |
| `home_team_id` | A numeric ID for the home team, used to match `possession` above. | `PRE` `IN` `POST` |
| `home_team_city` | The home team's city (eg. "Tennessee"). Note this does not include the team name. | `PRE` `IN` `POST` `BYE` |
| `home_team_name` | The home team's name (eg. "Titans"). Note this does not include the city name. | `PRE` `IN` `POST` `BYE` |
| `home_team_logo` | A URL for a 500px wide PNG logo for the home team. | `PRE` `IN` `POST` `BYE` |
| `home_team_score` | The home team's score. An integer. | `IN` `POST` |
| `home_team_colors` | An array with two hex colors. The first is the home team's primary color, and the second is their secondary color. | `PRE` `IN` `POST` |
| `home_team_ls_1` | The home team's score in the 1st quarter. An integer. | `IN` `POST` |
| `home_team_ls_2` | The home team's score in the 2nd quarter. An integer. | `IN` `POST` |
| `home_team_ls_3` | The home team's score in the 3rd quarter. An integer. | `IN` `POST` |
| `home_team_ls_4` | The home team's score in the 4th quarter. An integer. | `IN` `POST` |
| `home_team_record` | The home team's current record (eg. "2-3"). | `PRE` `IN` `POST` |
| `away_team_abbr` | The abbreviation for the away team (ie. `NYG` for the Giants). | `PRE` `IN` `POST` |
| `away_team_id` | A numeric ID for the away team, used to match `possession` above. | `PRE` `IN` `POST` |
| `away_team_city` | The away team's city (eg. "New York"). Note this does not include the team name. | `PRE` `IN` `POST` |
| `away_team_name` | The away team's name (eg. "Giants"). Note this does not include the city name. | `PRE` `IN` `POST` |
| `away_team_logo` | A URL for a 500px wide PNG logo for the away team. | `PRE` `IN` `POST` |
| `away_team_score` | The away team's score. An integer. | `IN` `POST` |
| `away_team_colors` | An array with two hex colors. The first is the away team's primary color, and the second is their secondary color. Unless you're the Browns, in which case they are the same. | `PRE` `IN` `POST` |
| `away_team_ls_1` | The away team's score in the 1st quarter. An integer. | `IN` `POST` |
| `away_team_ls_2` | The away team's score in the 2nd quarter. An integer. | `IN` `POST` |
| `away_team_ls_3` | The away team's score in the 3rd quarter. An integer. | `IN` `POST` |
| `away_team_ls_4` | The away team's score in the 4th quarter. An integer. | `IN` `POST` |
| `away_team_record` | The away team's current record (eg. "2-3"). | `PRE` `IN` `POST` |
| `kickoff_in` | Human-readable string for how far away the game is (eg. "in 30 minutes" or "tomorrow") |  `PRE` `IN` `POST` |
| `tv_network` | The TV network where you can watch the game (eg. "NBC" or "NFL"). Note that if there is a national feed, it will be listed here, otherwise the local affiliate will be listed. | `PRE` `IN` `POST` |
| `odds` | The betting odds for the game (eg. "PIT -5.0") | `PRE` |
| `overunder` | The over/under betting line for the total points scored in the game (eg. "42.5"). | `PRE` |
| `home_team_odds_win_pct` | Chance that the home team has to win, according to ESPN. | ? |
| `away_team_odds_win_pct` | Chance that the away team has to win, according to ESPN. | ? |
| `headlines` | Headline for the game. | `PRE` `IN` `POST` |
| `weather_conditions` | Expected weather conditions at kickoff (eg. "Mostly sunny"). | `PRE` `IN` `POST` |
| `weather_temp` | Expected temperature at kickoff (eg. "84") | `PRE` `IN` `POST` |
| `quarter` | The current quarter of gameplay | `IN` |
| `clock` | The clock value within the quarter (should never be higher than 15:00) | `IN` |
| `last_play` | Sentence describing the most recent play, usually including the participants from both offense and defense, and the resulting yards. Note this can be null on posession changes or in between quarters. | `IN` |
| `down_distance_text` | String for the down and yards to go (eg. "2nd and 7"). | `IN` |
| `possession` | The ID of the team in possession of the ball. This will correlate to `away_team_id` or `home_team_id` below. Note that this value will be null in between posessions (after a score, etc). | `IN` |
| `home_team_timeouts` | The number of remaining timeouts the home team has. | `IN` |
| `home_team_win_probability` | The real-time chance the home team has to win, according to ESPN. A percentage, but presented as a float. Note that this value can become null in between posession changes. | `IN` |
| `away_team_timeouts` | The number of remaining timeouts the away team has. | `IN` |
| `away_team_win_probability` | The real-time chance the away team has to win, according to ESPN. A percentage, but presented as a float. Note that this value can become null in between posession changes. | `IN` |
| `last_update` | A timestamp for the last time data was fetched for the game. If you watch this in real-time, you should notice it updating every 10 minutes, except for during the game (and for the ~20 minutes pre-game) when it updates every 5 seconds. | `PRE` `IN` `POST` `BYE` |

## Installation

### Manually

Clone or download this repository and copy the "nfl" directory to your "custom_components" directory in your config directory

```<config directory>/custom_components/nfl/...```
  
### HACS

1. Open the HACS section of Home Assistant.
2. Click the "..." button in the top right corner and select "Custom Repositories."
3. In the window that opens paste this Github URL.
4. In the window that opens when you select it click om "Install This Repository in HACS"
  
## Configuration

You'll need to know your team ID, which is a 2- or 3-letter acronym (eg. "SEA" for Seattle or "NE" for New England). You can find yours at https://espn.com/nfl in the top scores UI. 

### Via the "Configuration->Integrations" section of the Home Assistant UI

Look for the integration labeled "NFL" and enter your team's acronym in the UI prompt. You can also enter a friendly name. If you keep the default, your sensor will be `sensor.nfl`, otherwise it will be `sensor.friendly_name_you_picked`. 

### Manually in your `configuration.yaml` file

To create a sensor instance add the following configuration to your sensor definitions using the team_id found above:

```
- platform: nfl
  team_id: 'SEA'
```

After you restart Home Assistant then you should have a new sensor called `sensor.nfl` in your system.

You can overide the sensor default name (`sensor.nfl`) to one of your choosing by setting the `name` option:

```
- platform: nfl
  team_id: 'SEA'
  name: Seahawks
```

Using the configuration example above the sensor will then be called "sensor.seahawks".
