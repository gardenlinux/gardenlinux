#!/usr/bin/env python3
import json
import argparse

from urllib.request import urlopen

sapmachine_releases_json_url = 'https://sap.github.io/SapMachine/assets/data/sapmachine-releases-website.json'


def loadReleases():
    with urlopen(sapmachine_releases_json_url) as response:
        releases = json.loads(response.read().decode())
        return releases


def loadChecksum(url):
    with urlopen(url) as checksum:
        checksum_file_content: str = checksum.read().decode()
        # Need to split because the file contains the checksum and the file name
        # We only want the checksum which is the first element in the line
        checksum = checksum_file_content.split(' ')[0]
        return checksum


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--majorJreVersion', type=str)
    args = parser.parse_args()
    major_jre_version = args.majorJreVersion
    releases = loadReleases()
    tag: str = releases['assets'][major_jre_version]['releases'][0]['tag']
    version = tag.split('-')[1]
    downloadUrlSapMachineBinary_amd64: str = releases['assets'][major_jre_version]['releases'][0]['jre']['linux-x64']
    downloadUrlSapMachineBinary_aarch64: str = releases['assets'][major_jre_version]['releases'][0]['jre']['linux-aarch64']
    downloadUrlSapMachineChecksum_amd64 = downloadUrlSapMachineBinary_amd64.replace('.tar.gz', '.sha256.txt')
    downloadUrlSapMachineChecksum_aarch64 = downloadUrlSapMachineBinary_aarch64.replace('.tar.gz', '.sha256.txt')
    checksumAmd = loadChecksum(downloadUrlSapMachineChecksum_amd64)
    checksumArm = loadChecksum(downloadUrlSapMachineChecksum_aarch64)
    print(f'SAPMACHINE_JRE_VERSION={version}')
    print(f'CHECKSUM_X64={checksumAmd}')
    print(f'CHECKSUM_AARCH={checksumArm}')


if __name__ == '__main__':
    main()
