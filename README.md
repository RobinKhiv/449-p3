# 449-project 3

Directions to create sharded databases.

Option 1:</br>
  first create the single database supplied by Professor Kenytt Avery <br/>
  by running the python script in ./bin/stats.py </br>
  then shard that single database into 4 (1 users database and 3 games database) </br>
  with the python script in ./bin/sharddata.py </br>
  
Option 2:</br>
  Run the sql dump files to create the databases </br>
  ./bin/init.sh</br>
  

LoadBalancing Setup

follow below steps:
1.Install Traefik on machine
2.Take the (traefik.toml, routes.toml) configuration files from the traefikconfig folder of the project and place in the traefik directory
 
3.Run the below command to start traefik

./traefik  --configFile=traefik.toml

4. Uncomment below piece of code from statsFromShardedDB.py,statsFromShardedDB1.py,statsFromShardedDB2.py files to test with traefik
 app = FastAPI(root_path="/api/v1")
 
4.foreman start-which will start 3 instances of stats service
5.All the 3 instances can be accessed through below url

Proxy Url-http://127.0.0.1:9999/api/v1/docs
