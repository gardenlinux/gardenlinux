#!/usr/bin/env bash
BUTANE_VERSION=$(curl -sSnL https://api.github.com/repos/coreos/butane/releases/latest | grep tag_name | sed "s/.*: \"\(.*\)\",/\1/")
curl -sSnL https://github.com/coreos/butane/releases/download/${BUTANE_VERSION}/butane-x86_64-unknown-linux-gnu -o butane
chmod +x butane

