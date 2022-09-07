""" NFL Team Status """
import logging
from datetime import timedelta
import arrow

import aiohttp
from async_timeout import timeout
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_ENDPOINT,
    CONF_TIMEOUT,
    CONF_TEAM_ID,
    COORDINATOR,
    DEFAULT_TIMEOUT,
    DOMAIN,
    ISSUE_URL,
    PLATFORMS,
    USER_AGENT,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load the saved entities."""
    # Print startup message
    _LOGGER.info(
        "NFL version %s is starting, if you have any issues please report them here: %s",
        VERSION,
        ISSUE_URL,
    )
    hass.data.setdefault(DOMAIN, {})

    if entry.unique_id is not None:
        hass.config_entries.async_update_entry(entry, unique_id=None)

        ent_reg = async_get(hass)
        for entity in async_entries_for_config_entry(ent_reg, entry.entry_id):
            ent_reg.async_update_entity(entity.entity_id, new_unique_id=entry.entry_id)

    # Setup the data coordinator
    coordinator = AlertsDataUpdateCoordinator(
        hass,
        entry.data,
        entry.data.get(CONF_TIMEOUT)
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
    }

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, config_entry):
    """Handle removal of an entry."""
    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
        _LOGGER.info("Successfully removed sensor from the " + DOMAIN + " integration")
    except ValueError:
        pass
    return True


async def update_listener(hass, entry):
    """Update listener."""
    entry.data = entry.options
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "sensor"))

async def async_migrate_entry(hass, config_entry):
     """Migrate an old config entry."""
     version = config_entry.version

     # 1-> 2: Migration format
     if version == 1:
         _LOGGER.debug("Migrating from version %s", version)
         updated_config = config_entry.data.copy()

         if CONF_TIMEOUT not in updated_config.keys():
             updated_config[CONF_TIMEOUT] = DEFAULT_TIMEOUT

         if updated_config != config_entry.data:
             hass.config_entries.async_update_entry(config_entry, data=updated_config)

         config_entry.version = 2
         _LOGGER.debug("Migration to version %s complete", config_entry.version)

     return True

class AlertsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NFL data."""

    def __init__(self, hass, config, the_timeout: int):
        """Initialize."""
        self.interval = timedelta(minutes=10)
        self.name = config[CONF_NAME]
        self.timeout = the_timeout
        self.config = config
        self.hass = hass

        _LOGGER.debug("Data will be updated every %s", self.interval)

        super().__init__(hass, _LOGGER, name=self.name, update_interval=self.interval)

    async def _async_update_data(self):
        """Fetch data"""
        async with timeout(self.timeout):
            try:
                data = await update_game(self.config)
                # update the interval based on flag
                if data["private_fast_refresh"] == True:
                    self.update_interval = timedelta(seconds=5)
                else:
                    self.update_interval = timedelta(minutes=10)
            except Exception as error:
                raise UpdateFailed(error) from error
            return data
        


async def update_game(config) -> dict:
    """Fetch new state data for the sensor.
    This is the only method that should fetch new data for Home Assistant.
    """

    data = await async_get_state(config)
    return data

async def async_get_state(config) -> dict:
    """Query API for status."""

    values = {}
    headers = {"User-Agent": USER_AGENT, "Accept": "application/ld+json"}
    data = None
    url = API_ENDPOINT
    team_id = config[CONF_TEAM_ID]
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
            _LOGGER.debug("Getting state for %s from %s" % (team_id, url))
            if r.status == 200:
                data = await r.json()

    found_team = False
    if data is not None:
        for event in data["events"]:
            #_LOGGER.debug("Looking at this event: %s" % event)
            if team_id in event["shortName"]:
                _LOGGER.debug("Found event; parsing data.")
                
                found_team = True
                # Determine whether our team is Competitor 0 or 1
                team_index = 0 if event["competitions"][0]["competitors"][0]["team"]["abbreviation"] == team_id else 1
                team_home_away = event["competitions"][0]["competitors"][team_index]["homeAway"]
                oppo_index = abs((team_index-1))
                
                # state will be one of: pre, in, post
                try:
                    values["state"] = event["status"]["type"]["state"].upper()
                except:
                    values["state"] = None
                
                # detailed_state will be one of: STATUS_SCHEDULED, STATUS_IN_PROGRESS, STATUS_FINAL
                try:
                    values["detailed_state"] = event["status"]["type"]["name"]
                except:
                    values["detailed_state"] = None
                
                # Attempt to calculate the length of the game
                #try:
                #    if prior_state in ['STATUS_IN_PROGRESS'] and values["state"] in ['STATUS_FINAL']:
                #        _LOGGER.debug("Calulating game time for %s" % (team_id))
                #        values["game_end_time"] = arrow.now().format(arrow.FORMAT_W3C)
                #        values["game_length"] = str(values["game_end_time"] - event["date"])
                #    elif values["state"] not in ['STATUS_FINAL']:
                #        values["game_end_time"] = None
                #        values["game_length"] = None
                #except:
                values["game_end_time"] = None
                values["game_length"] = None
                
                try:
                    values["date"] = event["date"]
                except:
                    values["date"] = None
                
                try:
                    values["attendance"] = event["competitions"][0]["attendance"]
                except:
                    values["attendance"] = None
                
                # Formatted as full team names like "New York Giants at Tennessee Titans"
                try:
                    values["event_name"] = event["name"]
                except:
                    values["event_name"] = None
                
                # Formatted as abbreviations like "NYG @ TEN"
                try:
                    values["event_short_name"] = event["shortName"]
                except:
                    values["event_short_name"] = None

                # Formatted as "STD", "RD16", "QTR"
                try:
                    values["event_type"] = event["competitions"][0]["type"]["abbreviation"]
                except:
                    values["event_type"] = None
                
                # Formatted as ???
                try:
                    values["game_notes"] = event["competitions"][0]["notes"][0]["headline"]
                except:
                    values["game_notes"] = None
                
                # Formatted as ???
                try:
                    values["series_summary"] = event["competitions"][0]["series"]["summary"]
                except:
                    values["series_summary"] = None
                
                try:
                    values["venue_name"] = event["competitions"][0]["venue"]["fullName"]
                except:
                    values["venue_name"] = None
                
                try:
                    values["venue_city"] = event["competitions"][0]["venue"]["address"]["city"]
                except:
                    values["venue_city"] = None
                
                try:
                    values["venue_state"] = event["competitions"][0]["venue"]["address"]["state"]
                except:
                    values["venue_state"] = None
                
                try:
                    values["venue_capacity"] = event["competitions"][0]["venue"]["capacity"]
                except:
                    values["venue_capacity"] = None
                
                # Formatted as true/false
                try:
                    values["venue_indoor"] = event["competitions"][0]["venue"]["indoor"]
                except:
                    values["venue_indoor"] = None

                
                # featuredAthletes for post-game???


                try:
                    values["game_status"] = event["status"]["type"]["shortDetail"]
                except:
                    values["game_status"] = None
                
                try:
                    values["home_team_abbr"] = event["competitions"][0]["competitors"][0]["team"]["abbreviation"]
                except:
                    values["home_team_abbr"] = None
                
                try:
                    values["home_team_id"] = event["competitions"][0]["competitors"][0]["team"]["id"]
                except:
                    values["home_team_id"] = None
                    
                try:
                    values["home_team_city"] = event["competitions"][0]["competitors"][0]["team"]["location"]
                except:
                    values["home_team_city"] = None
                
                try:
                    values["home_team_name"] = event["competitions"][0]["competitors"][0]["team"]["name"]
                except:
                    values["home_team_name"] = None
                
                try:
                    values["home_team_logo"] = event["competitions"][0]["competitors"][0]["team"]["logo"]
                except:
                    values["home_team_logo"] = None
                
                try:
                    values["home_team_score"] = event["competitions"][0]["competitors"][0]["score"]
                except:
                    values["home_team_score"] = None

                try:
                    values["home_team_colors"] = [''.join(('#',event["competitions"][0]["competitors"][0]["team"]["color"])), 
                        ''.join(('#',event["competitions"][0]["competitors"][0]["team"]["alternateColor"]))]
                except:
                    values["home_team_colors"] = ['#013369','#013369']
                
                # Need to check if this is used while in progress
                try:
                    values["home_team_ls_1"] = event["competitions"][0]["competitors"][0]["linescores"][0]["value"]
                except:
                    values["home_team_ls_1"] = None

                try:
                    values["home_team_ls_2"] = event["competitions"][0]["competitors"][0]["linescores"][1]["value"]
                except:
                    values["home_team_ls_2"] = None

                try:
                    values["home_team_ls_3"] = event["competitions"][0]["competitors"][0]["linescores"][2]["value"]
                except:
                    values["home_team_ls_3"] = None
                
                try:
                    values["home_team_ls_4"] = event["competitions"][0]["competitors"][0]["linescores"][3]["value"]
                except:
                    values["home_team_ls_4"] = None
                
                try:
                    values["home_team_record"] = event["competitions"][0]["competitors"][0]["records"][0]["summary"]
                except:
                    values["home_team_record"] = None
                
                try:
                    values["away_team_abbr"] = event["competitions"][0]["competitors"][1]["team"]["abbreviation"]
                except:
                    values["away_team_abbr"] = None
                    
                try:
                    values["away_team_id"] = event["competitions"][0]["competitors"][1]["team"]["id"]
                except:
                    values["away_team_id"] = None
                
                try:
                    values["away_team_city"] = event["competitions"][0]["competitors"][1]["team"]["location"]
                except:
                    values["away_team_city"] = None
                
                try:
                    values["away_team_name"] = event["competitions"][0]["competitors"][1]["team"]["name"]
                except:
                    values["away_team_name"] = None
                
                try:
                    values["away_team_logo"] = event["competitions"][0]["competitors"][1]["team"]["logo"]
                except:
                    values["away_team_logo"] = None
                
                try:
                    values["away_team_score"] = event["competitions"][0]["competitors"][1]["score"]
                except:
                    values["away_team_score"] = None
                    
                try:
                    values["away_team_colors"] = [''.join(('#',event["competitions"][0]["competitors"][1]["team"]["color"])), 
                        ''.join(('#',event["competitions"][0]["competitors"][1]["team"]["alternateColor"]))]
                except:
                    values["away_team_colors"] = ['#D50A0A','#D50A0A']
                
                try:
                    values["away_team_ls_1"] = event["competitions"][0]["competitors"][1]["linescores"][0]["value"]
                except:
                    values["away_team_ls_1"] = None

                try:
                    values["away_team_ls_2"] = event["competitions"][0]["competitors"][1]["linescores"][1]["value"]
                except:
                    values["away_team_ls_2"] = None

                try:
                    values["away_team_ls_3"] = event["competitions"][0]["competitors"][1]["linescores"][2]["value"]
                except:
                    values["away_team_ls_3"] = None

                try:
                    values["away_team_ls_4"] = event["competitions"][0]["competitors"][1]["linescores"][3]["value"]
                except:
                    values["away_team_ls_4"] = None
                
                try:
                    values["away_team_record"] = event["competitions"][0]["competitors"][1]["records"][0]["summary"]
                except:
                    values["away_team_record"] = None
                
                try:
                    values["kickoff_in"] = arrow.get(event["date"]).humanize()
                except:
                    values["kickoff_in"] = None
                
                try:
                    values["tv_network"] = event["competitions"][0]["broadcasts"][0]["names"][0]
                except:
                    values["tv_network"] = None
                
                try:
                    values["odds"] = event["competitions"][0]["odds"][0]["details"]
                except:
                    values["odds"] = None
                    
                try:
                    values["overunder"] = event["competitions"][0]["odds"][0]["overUnder"]
                except:
                    values["overunder"] = None
                
                try:
                    values["home_team_odds_win_pct"] = event["competitions"][0]["odds"][1]["homeTeamOdds"]["winPercentage"]
                except:
                    values["home_team_odds_win_pct"] = None
                
                try:
                    values["away_team_odds_win_pct"] = event["competitions"][0]["odds"][1]["awayTeamOdds"]["winPercentage"]
                except:
                    values["away_team_odds_win_pct"] = None
                
                try:
                    values["headlines"] = event["competitions"][0]["headlines"][0]["shortLinkText"]
                except:
                    values["headlines"] = None

                # Formatted like "Mostly clear"
                try:
                    values["weather_conditions"] = event["weather"]["displayValue"]
                except:
                    values["weather_conditions"] = None

                # Integer like "68"
                try:
                    values["weather_temp"] = event["weather"]["temperature"]
                except:
                    values["weather_temp"] = None
                    
                if event["status"]["type"]["state"].lower() in ['pre', 'post']: # could use status.completed == true as well
                    values["quarter"] = None
                    values["clock"] = None
                    values["last_play"] = None
                    values["down_distance_text"] = None
                    values["possession"] = None
                    values["home_team_timeouts"] = 3
                    values["away_team_timeouts"] = 3
                    values["home_team_win_probability"] = None
                    values["away_team_win_probability"] = None
                else:
                    values["quarter"] = event["status"]["period"]
                    values["clock"] = event["status"]["displayClock"]
                    values["last_play"] = event["competitions"][0]["situation"]["lastPlay"]["text"]
                    try:
                        values["down_distance_text"] = event["competitions"][0]["situation"]["downDistanceText"]
                    except:
                        values["down_distance_text"] = None
                    try:
                        values["possession"] = event["competitions"][0]["situation"]["possession"]
                    except:
                        values["possession"] = None
                    try:
                        values["home_team_timeouts"] = event["competitions"][0]["situation"]["homeTimeouts"]
                    except:
                        values["home_team_timeouts"] = None
                    try:
                        values["away_team_timeouts"] = event["competitions"][0]["situation"]["awayTimeouts"]
                    except:
                        values["away_team_timeouts"] = None
                    try:
                        values["home_team_win_probability"] = event["competitions"][0]["situation"]["lastPlay"]["probability"]["homeWinPercentage"]
                    except:
                        values["home_team_win_probability"] = None
                    try:
                        values["away_team_win_probability"] = event["competitions"][0]["situation"]["lastPlay"]["probability"]["awayWinPercentage"]
                    except:
                        values["away_team_win_probability"] = None
                    
                values["last_update"] = arrow.now().format(arrow.FORMAT_W3C)
                values["private_fast_refresh"] = False
        
        # Never found the team. Either a bye or a post-season condition
        if not found_team:
            _LOGGER.debug("Did not find a game with for the configured team. Checking if it's a bye week.")
            found_bye = False
            values = await async_clear_states(config)
            try: # look for byes in regular season
                for bye_team in data["week"]["teamsOnBye"]:
                    if team_id.lower() == bye_team["abbreviation"].lower():
                        _LOGGER.debug("Bye week confirmed.")
                        found_bye = True
                        values["home_team_abbr"] = bye_team["abbreviation"]
                        values["home_team_name"] = bye_team["shortDisplayName"]
                        values["home_team_logo"] = bye_team["logo"]
                        values["state"] = 'BYE'
                        values["last_update"] = arrow.now().format(arrow.FORMAT_W3C)
                if found_bye == False:
                        _LOGGER.debug("Team not found in active games or bye week list. Have you missed the playoffs?")
                        values["home_team_abbr"] = None
                        values["home_team_name"] = None
                        values["home_team_logo"] = None
                        values["state"] = 'NOT_FOUND'
                        values["last_update"] = arrow.now().format(arrow.FORMAT_W3C)
            except:
                _LOGGER.debug("Team not found in active games or bye week list. Have you missed the playoffs?")
                values["home_team_abbr"] = None
                values["home_team_name"] = None
                values["home_team_logo"] = None
                values["state"] = 'NOT_FOUND'
                values["last_update"] = arrow.now().format(arrow.FORMAT_W3C)

        if values["state"] == 'PRE' and ((arrow.get(values["date"])-arrow.now()).total_seconds() < 1200):
            _LOGGER.debug("Event is within 20 minutes, setting refresh rate to 5 seconds.")
            values["private_fast_refresh"] = True
        elif values["state"] == 'IN':
            _LOGGER.debug("Event in progress, setting refresh rate to 5 seconds.")
            values["private_fast_refresh"] = True
        elif values["state"] in ['POST', 'BYE']: 
            _LOGGER.debug("Event is over, setting refresh back to 10 minutes.")
            values["private_fast_refresh"] = False

    return values

async def async_clear_states(config) -> dict:
    """Clear all state attributes"""
    
    values = {}
    # Reset values
    values = {
        "detailed_state": None,
        "game_end_time": None,
        "game_length": None,
        "date": None,
        "attendance": None,
        "event_name": None,
        "event_short_name": None,
        "event_type": None,
        "game_notes": None,
        "series_summary": None,
        "venue_name": None,
        "venue_city": None,
        "venue_state": None,
        "venue_capacity": None,
        "venue_indoor": None,
        "game_status": None,
        "home_team_abbr": None,
        "home_team_id":  None,
        "home_team_city": None,
        "home_team_name": None,
        "home_team_logo": None,
        "home_team_score": None,
        "home_team_colors": None,
        "home_team_ls_1": None,
        "home_team_ls_2": None,
        "home_team_ls_3": None,
        "home_team_ls_4": None,
        "home_team_record": None,
        "away_team_abbr": None,
        "away_team_id":  None,
        "away_team_city": None,
        "away_team_name": None,
        "away_team_logo": None,
        "away_team_score": None,
        "away_team_colors": None,
        "away_team_ls_1": None,
        "away_team_ls_2": None,
        "away_team_ls_3": None,
        "away_team_ls_4": None,
        "away_team_record": None,
        "kickoff_in": None,
        "tv_network": None,
        "odds": None,
        "overunder": None,
        "home_team_odds_win_pct": None,
        "away_team_odds_win_pct": None,
        "headlines": None,
        "weather_conditions": None,
        "weather_temp": None,
        "quarter": None,
        "clock": None,
        "last_play": None,
        "down_distance_text": None,
        "possession": None,
        "home_team_timeouts": None,
        "away_team_timeouts": None,
        "home_team_win_probability": None,
        "away_team_win_probability": None,
        "last_update": None,
        "team_id": None,
        "private_fast_refresh": False
    }

    return values
