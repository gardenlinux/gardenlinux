## Feature: capi
### Description
<website-feature>
This feature is supposed to just group a set of features used in IronCore and ConvergedCloud.
This is supposed to be used only with the metal platform.
</website-feature>

### Features
This is grouping a set of features needed when network bootstrapping servers in order to be used in a Kubernetes cluster.
The only thing special about this feature is the replacement of ignition with ignition-legacy which is adding support for v2 ignition configs.
This is required because only ignition v2 is supported when ignition is being used as the configuration engine for bootstrapping workload cluster machines with the Kubernetes cluster-api. 
