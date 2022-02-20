[![GitHub Latest Release][releases_shield]][latest_release]
[![GitHub All Releases][downloads_total_shield]][releases]

[latest_release]: https://github.com/kwiatek6324/ha_custom_czujnikimiejskie/releases/latest
[releases_shield]: https://img.shields.io/github/release/kwiatek6324/ha_custom_czujnikimiejskie.svg?style=popout

[releases]: https://github.com/kwiatek6324/ha_custom_czujnikimiejskie/releases
[downloads_total_shield]: https://img.shields.io/github/downloads/kwiatek6324/ha_custom_czujnikimiejskie/total

# CzujnikiMiejskie Air Parameters

This custom integration retrieves data from [https://czujnikimiejskie.pl]

![screenshot](/screenshot.png)


## Installation

### Manual
To install this integration manuall you have to download [*czujniki_miejskie.zip*](https://github.com/kwiatek6324/ha_custom_czujnikimiejskie/releases/latest/download/czujniki_miejskie.zip) and extract its contents to `config/custom_components/czujniki_miejskie` directory:

```shell
mkdir -p custom_components/czujnikimiejskie
wget https://github.com/kwiatek6324/ha_custom_czujnikimiejskie/releases/latest/download/czujniki_miejskie.zip
unzip czujniki_miejskie.zip
rm czujniki_miejskie.zip
```


## Configuration

| Key | Type | Required | Value | Description |
|---|---|---|---|---|
| `platform` | string | true | `czujniki_miejskie` | Name of a platform |
| `node` | string | true |   | ID of station to receive data) |

### How to retrieve node id ###

You have to visit page [https://czujniki_miejskie.pl](https://czujniki_miejskie.pl)
Please click link on section **Czujniki smogu** and find nearest sensor for your location.
Before clicking, please open developpers tools(CTRL+Shift+K) and **Network section**.
After cliking in history you should find a request for URL:
`http://czujnikimiejskie.pl/api/node/42/`
In this URL **42** is your node ID.


## Example configuration

```yaml
sensor:
  - platform: czujniki_miejskie
    node: "42"
```

