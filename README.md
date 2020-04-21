eco-data-visualizer
Data visualizer + AQI calculator from CSV provided by SaveEcoBot

# Data visualizer from SaveEcoBot. Calculate AQI.

This software up and run nice dashboard with metrics from CSV file and calculate AQI for PM2.5 and PM10

Air Quality Index calculations based on [this document](https://www.airnow.gov/sites/default/files/2018-05/aqi-technical-assistance-document-may2016.pdf)

![](docs/en/images/first-view.png)

More screenshots and usage examples [here](docs/en/screenshots.md).

---

## MENU

* [Required software](#required-software-)
* [Usage](#usage-)
  * [Quick start](#quick-start-)
  * [Screenshots and usage examples](docs/en/screenshots.md)
  * [Daily usage](#daily-usage-)
    * [Start](#start-)
    * [Stop](#stop-)
  * [Sensors data](#sensors-data-)
    * [Process new data](#process-new-data-)
    * [Add new data](#add-new-data-)
    * [Remove data](#remove-data-)
  * [Cleanup](#cleanup-)
* [Future plans](#future-plans-)
* [Want help?](#want-help-)
* [License and Copyrights](#license-and-copyrights-)


---


## Required software [`↑`](#menu)

* [`Docker`](https://docs.docker.com/get-docker/)
* [`docker-compose`](https://docs.docker.com/compose/install/) (for Linux)

## Usage [`↑`](#menu)

### Quick start [`↑`](#menu)

1. Clone this repo or [download it as zip](https://github.com/MaxymVlasov/eco-data-visualizer/archive/master.zip) and unpack.

2. Choose SaveEcoBot station [on this map](https://www.saveecobot.com/en/maps) and click 'Details'  
![](docs/en/images/map-details.png)

3. On bottom you'll see `Download raw data (CSV)`  
![](docs/en/images/download-csv.png)  
click on them and save it to `eco-data-visualizer/data/original_data/` inside download repo.

4. Open terminal in the root of `eco-data-visualizer` and run:

```bash
# Get data
docker build -t data-transformer ./data-transformer-app
docker run -v $PWD/data/:/app/data/ --rm data-transformer
# Run Grafana and DBs
docker-compose up -d
# Add data of sensors to InfluxDB
docker build -t add_influx_data ./provisioning/influx
docker run -v $PWD/data/influx/:/influx-data/ --rm --network=eco-data-visualizer_default add_influx_data
```

><sup>Depending on your internet bandwidth, CPU, Storage I/O, CSV file size and number of processed files `First Init` may take different times.  
For example, in laptop with `100Mbit/sec` bandwidth, `Intel Core i7-8550U` (max clock speed `4Ghz`), SSD disk and:</sup>  
<sup>  - 2 CSV files (together: 620MB) it takes `11m47s` (`9m39s` to transform data)</sup>  
<sup>  - 1 CSV file (513MB) - `6m16s` (`4m18s` to transform data)</sup>  
<sup>  - 1 CSV file (107MB) - `6m35s` (`4m32s` to transform data)</sup>

5. Open [http://localhost/](http://localhost/) for see visualizations!

### Daily usage [`↑`](#menu)

#### Start [`↑`](#menu)

For start visualization open terminal in the root of repo and run:

```bash
docker-compose up -d
```

Then open [http://localhost/](http://localhost/) for see visualizations.

#### Stop [`↑`](#menu)

For stop visualization open terminal in the root of repo and run:

```bash
docker-compose stop
```

### Sensors data [`↑`](#menu)

#### Process new data [`↑`](#menu)

1. Download CSV file from SaveEcoBot station
2. Move it to `data/original_data` folder in this repo.

```bash
# Remove temporary files
docker run -v $PWD/data/:/app/ --rm amancevice/pandas:1.0.3-alpine sh -c "rm -f /app/csv/*.csv /app/influx/*.influx"
# Get data
docker build -t data-transformer ./data-transformer-app
docker run -v $PWD/data/:/app/data/ --rm data-transformer
```

#### Add new data [`↑`](#menu)

For add new data open terminal in the root of repo and run:

```bash
# Start services
docker-compose up -d
# Add new data
docker build -t add_influx_data ./provisioning/influx
docker run -v $PWD/data/influx/:/influx-data/ --rm --network=eco-data-visualizer_default add_influx_data
```

#### Remove data [`↑`](#menu)

```bash
docker-compose down
docker volume rm eco-data-visualizer_sensors-data
```

### Cleanup [`↑`](#menu)

For cleanup open terminal in the root of repo and run:

```bash
# Stop services
docker-compose down
# Remove volumes with settings and user data
docker volume rm eco-data-visualizer_grafana-settings eco-data-visualizer_sensors-data
# Remove temporary files
docker run -v $PWD/data/:/app/ --rm amancevice/pandas:1.0.3-alpine sh -c "rm -f /app/csv/*.csv /app/influx/*.influx"
```

## Future plans [`↑`](#menu)

* [ ] Add Ukrainian localization
  * [ ] Code and message dashboard localization
  * [ ] README.md localization
* [ ] In Grafana Create personal graphs for each sensor with own good-bad color limits and so on as for AQI
* [ ] Grab exist metrics from 'phenomenon' colum, use `SENSORS` contant only for user friendly names and localization
* [ ] Add AQI support for all specified in [doc](https://www.airnow.gov/sites/default/files/2018-05/aqi-technical-assistance-document-may2016.pdf)
* [ ] Optimize `data-transformer-app`
  * [ ] Parallel sensors operation execution
  * [ ] Use less Disk I/O operations

## Want help? [`↑`](#menu)

You can:

* Improve this software (see [Future plans](#future-plans-) section)
* [Donate to SaveEcoBot](https://www.saveecobot.com/en/donate)
* Assemble or buy Air quality monitoring station and connect it to SaveEcoBot. SaveDnipro can assemble and connect it for you. [Buy here](https://www.savednipro.org/product/stanciya-monitoringu-yakosti-povitrya/)

## License and Copyrights [`↑`](#menu)

This software licensed by [Apache License 2.0](LICENSE)

All data from SaveEcoBot licensed by [Creative Commons Attribution License 4.0 International](https://creativecommons.org/licenses/by/4.0/legalcode)

Other data and sources can be licensed in different way.
