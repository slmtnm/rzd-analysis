# Helper scripts

## publish_dates.py

This script helps to add new dates into AMQP.
It supports three variants;

* Adding single date:
```shell
python3 ./scripts/publish_dates.py --amqp_url <amqp_url> date 1.1.2022
```

* Adding (inclusive) range of dates:
```shell
python3 ./scripts/publish_dates.py --amqp_url <amqp_url> daterange 1.1.2022 15.1.2022 # adds 15 dates
```

* Adding next N days, beginning from today:
```shell
python3 ./scripts/publish_dates.py --amqp_url <amqp_url> next 30 # adds next 15 dates
```

## points_number.py
```shell
python3 ./scripts/points_number.py <path to data dir> 
```
This script shows number of collections per date.
For example, if date 1.1.2022 was collected 10 times (on 10 different collect dates),
it will be shown as:
```
10 points for 1.1.2022
```

## export_to_mongo.py

This scripts exports all collected routes from local folder with json files
to mongodb:
```shell
python3 ./scripts/export_to_mongo.py --mongodb_url <path to data dir> 
```