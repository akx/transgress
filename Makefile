turku-route-rate.json: turku-bus-routes.geojson turku-points.geojson
	python route_rate.py -p turku-points.geojson -r turku-bus-routes.geojson -o turku-route-rate.json

gtfs-turku:
	curl -L -o gtfs-turku.zip http://data.foli.fi/gtfs/gtfs.zip
	unzip gtfs-turku.zip -d gtfs-turku

turku-bus-routes.geojson: gtfs-turku
	python gtfs_to_geojson.py -d gtfs-turku -o turku-bus-routes.geojson

turku-points.geojson:
	$(error You need to provide turku-points.geojson yourself)
