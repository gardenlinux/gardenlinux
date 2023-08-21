#!/usr/bin/jq -f

{
        "current": "gardenlinux",
        "profiles": [
                {
                        "name": "gardenlinux",
                        "mode": "AK",
                        "access_key_id": .alicloud["gardenlinux-platform-test"].access_key_id,
                        "access_key_secret": .alicloud["gardenlinux-platform-test"].access_key_secret,
                        "sts_token": "",
                        "ram_role_name": "",
                        "ram_role_arn": "",
                        "ram_session_name": "",
                        "private_key": "",
                        "key_pair_name": "",
                        "expired_seconds": 0,
                        "verified": "",
                        "region_id": .alicloud["gardenlinux-platform-test"].region,
                        "output_format": "json",
                        "language": "en",
                        "site": "",
                        "retry_timeout": 0,
                        "connect_timeout": 0,
                        "retry_count": 0,
                        "process_command": ""
                }
        ],
        "meta_path": ""
}
