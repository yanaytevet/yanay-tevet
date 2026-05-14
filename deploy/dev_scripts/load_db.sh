read -p "Enter local container name " container_name
read -p "Enter local container name " dump_path

echo "Loading dump into local docker..."
docker cp $dump_path "$container_name":dump-fragments.tar.gz

echo "Destroying the local database..."
docker exec $container_name dropdb -U admin yanay_tevet_db

wait  # Wait for the background process to finish

echo "Creating new database..."
docker exec -it "$container_name" createdb -U admin yanay_tevet_db

wait  # Wait for the background process to finish

echo "UnCompressing dump..."
docker exec "$container_name" tar -xzvf dump-fragments.tar.gz

echo "Uploading dump to local database..."
docker exec "$container_name" pg_restore -U admin -d yanay_tevet_db --jobs=5 -Fd ./dump-fragments

wait  # Wait for the background process to finish

echo "Cleaning up..."
docker exec "$container_name" rm -r ./dump-fragments
rm -r "$dump_path"

echo "Finished!"
