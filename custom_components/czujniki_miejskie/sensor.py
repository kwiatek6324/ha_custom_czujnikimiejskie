from datetime import timedelta
import logging
import requests
import time
import datetime
import voluptuous as vol

from homeassistant.components.sensor import (
        PLATFORM_SCHEMA, ENTITY_ID_FORMAT,
        SensorDeviceClass, 
        SensorStateClass,
        SensorEntity, 
        SensorEntityDescription 
        )

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
        CONF_NAME,
        TEMP_CELSIUS,
        CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        DEVICE_CLASS_TIMESTAMP,
        DEVICE_CLASS_NITROGEN_DIOXIDE,
        DEVICE_CLASS_OZONE,
        DEVICE_CLASS_CO,
        PERCENTAGE
        )
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
#from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.util import Throttle


_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)
SCAN_INTERVAL = timedelta(minutes=15)




DEFAULT_NAME = 'Czujniki Miejskie'
CONF_NODE_ID = "node"

_SYSTEM_PARAMS: tuple[SensorEntityDescription, ...] = (
        SensorEntityDescription(key="name", name="Stacja",
            ),
        SensorEntityDescription(key="last", name="Ostatni odczyt",
            device_class=SensorDeviceClass.TIMESTAMP
            ),
        SensorEntityDescription(key="index", name="Air Index",
            state_class=SensorStateClass.MEASUREMENT,
            ),
        SensorEntityDescription(key="temperature", name="Temperatura",
            native_unit_of_measurement=TEMP_CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            ),
        SensorEntityDescription(key="humidity", name="Wilgotność",
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.HUMIDITY,
            state_class=SensorStateClass.MEASUREMENT,
            ),
        SensorEntityDescription(key="pm1", name="PM1 Index",
            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            state_class=SensorStateClass.MEASUREMENT,
            ),
        SensorEntityDescription(key="pm2.5", name="PM2.5 Index",
            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            state_class=SensorStateClass.MEASUREMENT,
            ),
        SensorEntityDescription(key="pm10", name="PM10 Index",
            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            state_class=SensorStateClass.MEASUREMENT,
            ),
        SensorEntityDescription(key="NO₂", name="Dwutlenek azotu",
            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
#            device_class=SensorDeviceClass.DEVICE_CLASS_NITROGEN_DIOXIDE,
            state_class=SensorStateClass.MEASUREMENT,
            ),
        SensorEntityDescription(key="O₃", name="Ozon",
            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
#            device_class=SensorDeviceClass.DEVICE_CLASS_OZONE,
            state_class=SensorStateClass.MEASUREMENT,
            ),
        SensorEntityDescription(key="SO₂", name="Dwutlenek siarki",
            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
#            device_class=SensorDeviceClass.DEVICE_CLASS_SULPHUR_DIOXIDE,
            state_class=SensorStateClass.MEASUREMENT,
            ),
        SensorEntityDescription(key="C₆H₆", name="Benzen",
            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            state_class=SensorStateClass.MEASUREMENT,
            ),
        SensorEntityDescription(key="CO", name="Tlenek Wegla",
            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
#            device_class=SensorDeviceClass.DEVICE_CLASS_CO,
            state_class=SensorStateClass.MEASUREMENT,
            )
        )


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_NODE_ID): cv.string
})


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities,
    discovery_info=None):

    platform_name = config.get(CONF_NAME)
    platform_id = config.get(CONF_NODE_ID)

    _LOGGER.debug("CzujnikiMiejskie: Setup startup")
    api=CzujnikiMiejskieApi(config)
    api.update()
    _LOGGER.debug("CzujnikiMiejskie: Setup - Api Updated")
#    if not api.data:
#        raise PlatformNotReady

#    node_id = config.get(CONF_NODE_ID)
#    name = config.get(CONF_NAME)
#    uid = '{}_{}'.format(DEFAULT_NAME, node_id)
#    entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, uid, hass=hass)

    sensors: list[CzujnikiMiejskieSensor] = []

    sensors.extend([
        CzujnikiMiejskieSensor(api,description,platform_name,platform_id)
        for description in _SYSTEM_PARAMS
        if description.key in ['index','name','last']
        ])

    sensors.extend([
        CzujnikiMiejskieSensor(api,description,platform_name,platform_id)
        for description in _SYSTEM_PARAMS
        if description.key in api.indexes
        ])
    add_entities(sensors,True)
    _LOGGER.debug("CzujnikiMiejskie: Setup - Added entities")



class CzujnikiMiejskieSensor(SensorEntity):
    def __init__(self, api,description: SensorEntityDescription,platform_name,platform_id):
        self.entity_description = description
        self._platform_name = platform_name
        self._platform_id = platform_id
        self._api = api
        _LOGGER.debug("CzujnikiMiejskieSensor: initalize key %s",description.key)

    @property
    def name(self):
        return '{} - {} - {}'.format(self._platform_name, self._platform_id,self.entity_description.name)

    @property
    def unique_id(self):
        return '{} - {} - {}'.format(self._platform_name, self._platform_id,self.entity_description.key)
    
    def update(self):
#        _LOGGER.debug("CzujnikiMiejskieSensor: updating Node ID %s => key: %s",self._platform_id,self.entity_description.key)
        self._api.update();

    @property
    def native_value(self):
        value = None

        if self.entity_description.key == "index":
            value = self._api.data["values"][0]["index"]
        elif self.entity_description.key == "last":
            tmp = '{}+01:00'.format(self._api.data["values"][0]["date"])
            value=datetime.datetime.fromisoformat(tmp)
        elif self.entity_description.key == "name":
            value = '{} - {}'.format(self._api.data["name"],self._api.data["street"])
        else:
          if self.entity_description.key in self._api.indexes:
            idx = self._api.indexes[self.entity_description.key]
            if idx != '':
              value = self._api.data["values"][0]["value"][idx]
        _LOGGER.debug("CzujnikiMiejskieSensor: returning value for: %s => %s",self.entity_description.key,value)
        return value


class CzujnikiMiejskieApi:
    def __init__(self, config):
        self.address = 'https://czujnikimiejskie.pl/api/node/{}/'.format(config.get(CONF_NODE_ID))
        self.data={}
        self.indexes={}
        _LOGGER.info("CzujnikiMiejskieApi: init with URL %s",self.address)

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        headers = {
            "host": "czujnikimiejskie.pl"
        }
        _LOGGER.debug("CzujnikiMiejskieApi: updating %s",self.address)
        request = requests.get(self.address, headers=headers)
        if request.status_code == 200 and request.content.__len__() > 0:
            self.data = request.json()
            _LOGGER.debug("CzujnikiMiejskieApi: received: %s",self.data)
            for x,y in self.data["parameter"].items():
              if y != '':
                self.indexes[y]=x
#            for x,y in self.indexes.items():
#              _LOGGER.debug("CzujnikiMiejskieApi: Available Indexes: %s:%s",x,y)
