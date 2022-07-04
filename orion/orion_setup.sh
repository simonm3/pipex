# orion commands executed after launch

printf '1\n\n/v1/storage\nv1_storage\ny' | prefect storage create
# wait for prefect to confirm execution
sleep 30
echo "storage created"