#!/usr/bin/env python3

import datetime
import json
import grpc
import pyvelociraptor
from pyvelociraptor import api_pb2, api_pb2_grpc

# -----------------------------
# CONFIGURATION
# -----------------------------
API_CONFIG_PATH = "/opt/velociraptor_installer/api.config.yaml"    # update path if needed
ARTIFACT = "Server.Utils.DeleteMonitoringData"
ARTIFACT_REGEX = "Windows.Hayabusa.Monitoring"
HOSTNAME_REGEX = "."
ONLY_REGISTERED = False
REALLY_DO_IT = True           # set to False to test dry-runs
LOG_FILE = "/var/log/velociraptor_delete_monitoring.log"
# -----------------------------


def run_vql_query(query: str, env_dict: dict):
    config = pyvelociraptor.LoadConfigFile(API_CONFIG_PATH)

    creds = grpc.ssl_channel_credentials(
        root_certificates=config["ca_certificate"].encode("utf8"),
        private_key=config["client_private_key"].encode("utf8"),
        certificate_chain=config["client_cert"].encode("utf8"),
    )

    options = (("grpc.ssl_target_name_override", "VelociraptorServer"),)

    with grpc.secure_channel(config["api_connection_string"], creds, options) as channel:
        stub = api_pb2_grpc.APIStub(channel)

        env = [dict(key=k, value=v) for k, v in env_dict.items()]

        request = api_pb2.VQLCollectorArgs(
            org_id="",
            max_wait=1,
            max_row=100,
            timeout=0,
            Query=[api_pb2.VQLRequest(Name="DeleteMonitoring", VQL=query)],
            env=env,
        )

        for response in stub.Query(request):
            if response.Response:
                yield json.loads(response.Response)

            elif response.log:
                yield {"log": response.log}


def main():
    # Compute DateBefore = now - 7 days
    date_before = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    vql = f"""
SELECT * FROM Artifact.{ARTIFACT}(
    DateBefore='{date_before}',
    ArtifactRegex='{ARTIFACT_REGEX}',
    HostnameRegex='{HOSTNAME_REGEX}',
    ReallyDoIt={str(REALLY_DO_IT).lower()}
)
""".strip()

    # Run query and capture output
    output_lines = []
    for result in run_vql_query(vql, env_dict={}):
        output_lines.append(result)

    # Write logs
    with open(LOG_FILE, "a") as f:
        f.write(f"\n--- {datetime.datetime.utcnow()} ---\n")
        f.write(f"Ran DeleteMonitoringData with DateBefore = {date_before}\n")
        f.write(json.dumps(output_lines, indent=2))
        f.write("\n")

    print(f"Completed. Logs written to: {LOG_FILE}")


if __name__ == "__main__":
    main()
