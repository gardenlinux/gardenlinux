## Feature: FIPS
### Description
<website-feature>
This features checks that Garden Linux has the FIPS feature prepared and enabled.
</website-feature>

### Features

This enables the [FIPS-140-3](https://csrc.nist.gov/pubs/fips/140-3/final) feature for Garden Linux. 

As of now, there are restriction for the following packages:

 - OpenSSL: A problem exists with the negotiation of hash functions during the download of packages from packages.gardenlinux.io
 - GNUTLS: Fail to execute the selftest.

### Unit testing
ToDo

### Meta
|   |   |
|---|---|
|type|flag|
|artifact|None|
|included_features|base|
|excluded_features|None|
