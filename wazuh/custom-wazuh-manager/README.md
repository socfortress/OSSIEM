# Wazuh Manager Docker Image Build Script
<br>
A modified Wazuh Manager image build script to replace Filebeat with Fluent Bit for log shipping to Graylog. Only tested on >4.9.0.
<br><br>
## Disclaimer: 
<br>
This will break your Wazuh Dashboard's ability to visualize data residing in your Indexer. Use Grafana instead to create dashboards and visualize your log data.
<br><br>
## Build:
<br>
```
docker build -t dloprodz/wazuh-manager:[WAZUH_VERSION] --build-arg WAZUH_VERSION=[WAZUH_VERSION] --build-arg WAZUH_TAG_REVISION=[WAZUH_TAG_REVISION] .
```
<br><br>
Tested Version:
<br><br>
```
docker build -t dloprodz/wazuh-manager:4.9.0 --build-arg WAZUH_VERSION=4.9.0 --build-arg WAZUH_TAG_REVISION=1 .
```
<br><br>
## Usage: 
<br>
The file config/fluent-bit.conf holds the predefined config for FluentBit to ship Wazuh alerts in the alerts.json log file to Graylog on port 5555, change this before building if you want to set a 
different port to connect to Graylog.
<br><br>
## Caveats:
<br>
When spinning up the container for the first time, you will see an error regarding the wazuh-alerts index as it has still not been created. Only after integrating Graylog into the stack will this 
error be fixed.
<br><br>
If you already have a working docker implementation all that is needed is to change the image in the docker compose file and recreate the container, you should now be able to ship your logs to Graylog.