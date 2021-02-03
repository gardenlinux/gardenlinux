#!/bin/bash

gpg --generate-key --batch sign.gpg
gpg --export --armor contact@gardenlinux.io > sign.pub
