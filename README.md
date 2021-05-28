Small parser job to:
 - listen to RuuviTag messages with Bleak (wonderful device, wonderful package)
 - parse measurements
 - dumping parsed measurements into local db

Comes with definitions for Grafana dashboards containing separate views for
- latest measurements
- measurement timeseries

Comes with zero error handling, lots of better examples around GitHub & blogs. Try them first

TODO:
- Add containers now that M1 has them
- clean PostgreSQL backup script to cloud
- PostgreSQL installation & role creation automation
- Grafana installation automation
