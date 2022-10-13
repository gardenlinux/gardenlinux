# SSH

## General
Ssh (Secure Shell) is a program for logging into a remote machine and for executing commands on a remote machine. It provides secure encrypted communications between two untrusted hosts over an insecure network. X11 connections and arbitrary TCP/IP ports can also be forwarded over the secure channel. It can be used to provide applications with a secure communication channel.

## Overview
By default, `ssh` will be installed by `server` as a dependency. However, it may be safely removed if the operator does not want to use it.

## Configuration

### Defaults
The configuration gets tweaked according to the used keys and ciphers as well as of further configurations regarding the current best practices of security (mainly based on Debian's defaults) and may change frequently.