turku-route-rate.json: turku-bus-routes.geojson turku-points.geojson
	python route_rate.py -p turku-points.geojson -r turku-bus-routes.geojson -o turku-route-rate.json

gtfs-turku.hdf5:
	curl -L -o gtfs-turku.zip http://data.foli.fi/gtfs/gtfs.zip
	python gtfs_to_hdf5.py -z gtfs-turku.zip -o $@

turku-bus-routes.geojson: gtfs-turku.hdf5
	python gtfs_to_geojson.py -i gtfs-turku.hdf5 -o turku-bus-routes.geojson

turku-points.geojson:
	$(error You need to provide turku-points.geojson yourself)
