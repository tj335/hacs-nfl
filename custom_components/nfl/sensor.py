import logging
import uuid

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify
from . import AlertsDataUpdateCoordinator

from .const import (
    ATTRIBUTION,
    CONF_TIMEOUT,
    CONF_TEAM_ID,
    COORDINATOR,
    DEFAULT_ICON,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_TEAM_ID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Configuration from yaml"""
    if DOMAIN not in hass.data.keys():
        hass.data.setdefault(DOMAIN, {})
        config.entry_id = slugify(f"{config.get(CONF_TEAM_ID)}")
        config.data = config
    else:
        config.entry_id = slugify(f"{config.get(CONF_TEAM_ID)}")
        config.data = config

    # Setup the data coordinator
    coordinator = AlertsDataUpdateCoordinator(
        hass,
        config,
        config[CONF_TIMEOUT],
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN][config.entry_id] = {
        COORDINATOR: coordinator,
    }
    async_add_entities([NFLScoresSensor(hass, config)], True)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup the sensor platform."""
    async_add_entities([NFLScoresSensor(hass, entry)], True)


class NFLScoresSensor(CoordinatorEntity):
    """Representation of a Sensor."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(hass.data[DOMAIN][entry.entry_id][COORDINATOR])
        self._config = entry
        self._name = entry.data[CONF_NAME]
        self._icon = DEFAULT_ICON
        self._state = "PRE"
        self._my_team_abbr = entry.data[CONF_TEAM_ID]
        self._detailed_state = None
        self._game_end_time = None
        self._game_length = None
        self._date = None
        self._week_number = None
        self._attendance = None
        self._event_name = None
        self._event_short_name = None
        self._event_type = None
        self._game_notes = None
        self._series_summary = None
        self._venue_name = None
        self._venue_city = None
        self._venue_state = None
        self._venue_capacity = None
        self._venue_indoor = None
        self._game_status = None
        self._home_team_abbr = None
        self._home_team_id = None
        self._home_team_city = None
        self._home_team_name = None
        self._home_team_logo = None
        self._home_team_score = None
        self._home_team_colors = None
        self._home_team_ls_1 = None
        self._home_team_ls_2 = None
        self._home_team_ls_3 = None
        self._home_team_ls_4 = None
        self._home_team_record = None
        self._home_team_passing_leader_stats = None
        self._home_team_passing_leader_name = None
        self._home_team_rushing_leader_stats = None
        self._home_team_rushing_leader_name = None
        self._home_team_receiving_leader_stats = None
        self._home_team_receiving_leader_name = None
        self._away_team_abbr = None
        self._away_team_id = None
        self._away_team_city = None
        self._away_team_name = None
        self._away_team_logo = None
        self._away_team_score = None
        self._away_team_colors = None
        self._away_team_ls_1 = None
        self._away_team_ls_2 = None
        self._away_team_ls_3 = None
        self._away_team_ls_4 = None
        self._away_team_record = None
        self._away_team_passing_leader_stats = None
        self._away_team_passing_leader_name = None
        self._away_team_rushing_leader_stats = None
        self._away_team_rushing_leader_name = None
        self._away_team_receiving_leader_stats = None
        self._away_team_receiving_leader_name = None
        self._kickoff_in = None
        self._tv_network = None
        self._odds = None
        self._overunder = None
        self._home_team_odds_win_pct = None
        self._away_team_odds_win_pct = None
        self._headlines = None
        self._weather_conditions = None
        self._weather_temp = None
        self._post_game_passing_leader_stats = None
        self._post_game_passing_leader_name = None
        self._post_game_rushing_leader_stats = None
        self._post_game_rushing_leader_name = None
        self._post_game_receiving_leader_stats = None
        self._post_game_receiving_leader_name = None
        self._quarter = None
        self._clock = None
        self._last_play = None
        self._current_drive_summary = None
        self._current_drive_start_position = None
        self._current_drive_elapsed_time = None
        self._down = None
        self._yard_line = None
        self._distance_to_go = None
        self._short_down_distance_text = None
        self._in_red_zone = None
        self._down_distance_text = None
        self._possession = None
        self._home_team_timeouts = None
        self._home_team_win_probability = None
        self._away_team_timeouts = None
        self._away_team_win_probability = None
        self._last_update = None
        #self._team_id = entry.data[CONF_TEAM_ID]
        self.coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    @property
    def unique_id(self):
        """
        Return a unique, Home Assistant friendly identifier for this entity.
        """
        return f"{slugify(self._name)}_{self._config.entry_id}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        elif "state" in self.coordinator.data.keys():
            return self.coordinator.data["state"]
        else:
            return None

    @property
    def extra_state_attributes(self):
        """Return the state message."""
        attrs = {}

        if self.coordinator.data is None:
            return attrs

        attrs[ATTR_ATTRIBUTION] = ATTRIBUTION
        attrs["my_team_abbr"] = self.coordinator.data["my_team_abbr"]
        attrs["detailed_state"] = self.coordinator.data["detailed_state"]
        attrs["game_end_time"] = self.coordinator.data["game_end_time"]
        attrs["game_length"] = self.coordinator.data["game_length"]
        attrs["date"] = self.coordinator.data["date"]
        attrs["week_number"] = self.coordinator.data["week_number"]
        attrs["attendance"] = self.coordinator.data["attendance"]
        attrs["event_name"] = self.coordinator.data["event_name"]
        attrs["event_short_name"] = self.coordinator.data["event_short_name"]
        attrs["event_type"] = self.coordinator.data["event_type"]
        attrs["game_notes"] = self.coordinator.data["game_notes"]
        attrs["series_summary"] = self.coordinator.data["series_summary"]
        attrs["venue_name"] = self.coordinator.data["venue_name"]
        attrs["venue_city"] = self.coordinator.data["venue_city"]
        attrs["venue_state"] = self.coordinator.data["venue_state"]
        attrs["venue_capacity"] = self.coordinator.data["venue_capacity"]
        attrs["venue_indoor"] = self.coordinator.data["venue_indoor"]
        attrs["game_status"] = self.coordinator.data["game_status"]
        attrs["home_team_abbr"] = self.coordinator.data["home_team_abbr"]
        attrs["home_team_id"] = self.coordinator.data["home_team_id"]
        attrs["home_team_city"] = self.coordinator.data["home_team_city"]
        attrs["home_team_name"] = self.coordinator.data["home_team_name"]
        attrs["home_team_logo"] = self.coordinator.data["home_team_logo"]
        attrs["home_team_score"] = self.coordinator.data["home_team_score"]
        attrs["home_team_colors"] = self.coordinator.data["home_team_colors"]
        attrs["home_team_ls_1"] = self.coordinator.data["home_team_ls_1"]
        attrs["home_team_ls_2"] = self.coordinator.data["home_team_ls_2"]
        attrs["home_team_ls_3"] = self.coordinator.data["home_team_ls_3"]
        attrs["home_team_ls_4"] = self.coordinator.data["home_team_ls_4"]
        attrs["home_team_record"] = self.coordinator.data["home_team_record"]
        attrs["home_team_passing_leader_stats"] = self.coordinator.data["home_team_passing_leader_stats"]
        attrs["home_team_passing_leader_name"] = self.coordinator.data["home_team_passing_leader_name"]
        attrs["home_team_rushing_leader_stats"] = self.coordinator.data["home_team_rushing_leader_stats"]
        attrs["home_team_rushing_leader_name"] = self.coordinator.data["home_team_rushing_leader_name"]
        attrs["home_team_receiving_leader_stats"] = self.coordinator.data["home_team_receiving_leader_stats"]
        attrs["home_team_receiving_leader_name"] = self.coordinator.data["home_team_receiving_leader_name"]
        attrs["away_team_abbr"] = self.coordinator.data["away_team_abbr"]
        attrs["away_team_id"] = self.coordinator.data["away_team_id"]
        attrs["away_team_city"] = self.coordinator.data["away_team_city"]
        attrs["away_team_name"] = self.coordinator.data["away_team_name"]
        attrs["away_team_logo"] = self.coordinator.data["away_team_logo"]
        attrs["away_team_score"] = self.coordinator.data["away_team_score"]
        attrs["away_team_colors"] = self.coordinator.data["away_team_colors"]
        attrs["away_team_ls_1"] = self.coordinator.data["away_team_ls_1"]
        attrs["away_team_ls_2"] = self.coordinator.data["away_team_ls_2"]
        attrs["away_team_ls_3"] = self.coordinator.data["away_team_ls_3"]
        attrs["away_team_ls_4"] = self.coordinator.data["away_team_ls_4"]
        attrs["away_team_record"] = self.coordinator.data["away_team_record"]
        attrs["away_team_passing_leader_stats"] = self.coordinator.data["away_team_passing_leader_stats"]
        attrs["away_team_passing_leader_name"] = self.coordinator.data["away_team_passing_leader_name"]
        attrs["away_team_rushing_leader_stats"] = self.coordinator.data["away_team_rushing_leader_stats"]
        attrs["away_team_rushing_leader_name"] = self.coordinator.data["away_team_rushing_leader_name"]
        attrs["away_team_receiving_leader_stats"] = self.coordinator.data["away_team_receiving_leader_stats"]
        attrs["away_team_receiving_leader_name"] = self.coordinator.data["away_team_receiving_leader_name"]
        attrs["kickoff_in"] = self.coordinator.data["kickoff_in"]
        attrs["tv_network"] = self.coordinator.data["tv_network"]
        attrs["odds"] = self.coordinator.data["odds"]
        attrs["overunder"] = self.coordinator.data["overunder"]
        attrs["home_team_odds_win_pct"] = self.coordinator.data["home_team_odds_win_pct"]
        attrs["away_team_odds_win_pct"] = self.coordinator.data["away_team_odds_win_pct"]
        attrs["headlines"] = self.coordinator.data["headlines"]
        attrs["weather_conditions"] = self.coordinator.data["weather_conditions"]
        attrs["weather_temp"] = self.coordinator.data["weather_temp"]
        attrs["post_game_passing_leader_stats"] = self.coordinator.data["post_game_passing_leader_stats"]
        attrs["post_game_passing_leader_name"] = self.coordinator.data["post_game_passing_leader_name"]
        attrs["post_game_rushing_leader_stats"] = self.coordinator.data["post_game_rushing_leader_stats"]
        attrs["post_game_rushing_leader_name"] = self.coordinator.data["post_game_rushing_leader_name"]
        attrs["post_game_receiving_leader_stats"] = self.coordinator.data["post_game_receiving_leader_stats"]
        attrs["post_game_receiving_leader_name"] = self.coordinator.data["post_game_receiving_leader_name"]
        attrs["quarter"] = self.coordinator.data["quarter"]
        attrs["clock"] = self.coordinator.data["clock"]
        attrs["last_play"] = self.coordinator.data["last_play"]
        attrs["current_drive_summary"] = self.coordinator.data["current_drive_summary"]
        attrs["current_drive_start_position"] = self.coordinator.data["current_drive_start_position"]
        attrs["current_drive_elapsed_time"] = self.coordinator.data["current_drive_elapsed_time"]
        attrs["down"] = self.coordinator.data["down"]
        attrs["yard_line"] = self.coordinator.data["yard_line"]
        attrs["distance_to_go"] = self.coordinator.data["distance_to_go"]
        attrs["short_down_distance_text"] = self.coordinator.data["short_down_distance_text"]
        attrs["in_red_zone"] = self.coordinator.data["in_red_zone"]
        attrs["down_distance_text"] = self.coordinator.data["down_distance_text"]
        attrs["possession"] = self.coordinator.data["possession"]
        attrs["home_team_timeouts"] = self.coordinator.data["home_team_timeouts"]
        attrs["home_team_win_probability"] = self.coordinator.data["home_team_win_probability"]
        attrs["away_team_timeouts"] = self.coordinator.data["away_team_timeouts"]
        attrs["away_team_win_probability"] = self.coordinator.data["away_team_win_probability"]
        attrs["last_update"] = self.coordinator.data["last_update"]
        #attrs["team_id"] = self.coordinator.data["team_id"]

        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
