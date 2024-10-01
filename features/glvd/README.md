## Feature: glvd
### Description
<website-feature>
The glvd feature provides the client for [Garden Linux Vulnerability Database](https://github.com/gardenlinux/glvd)
</website-feature>

### Features

This cli tool called `glvd` allows you to check your instance of Garden Linux for potential security issues.

If you included this feature, you can run `glvd check` to see which issues might apply for your Garden Linux version with the set of packages you installed.

Also, this feature enables a summary of potential issues in the Message of the Day.

Note: This requires the glvd client to make an HTTPS request to the glvd backend.
If you don't want this to happen, don't use this feature.

For more information on what the `glvd` cli can do and how to use it, see [its GitHub Repo](https://github.com/gardenlinux/package-glvd).

#### Configs

### Unit testing

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|None|
|excluded_features|None|
