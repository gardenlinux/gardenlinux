import glci.model

str_parsable_to_int = str
str_parsable_to_architecture = str
strs_separated_by_comma = str

def release_identifier(
    build_committish: str,
    version: str,
    gardenlinux_epoch: str_parsable_to_int,
    architecture: str_parsable_to_architecture,
    platform: glci.model.Platform,
    modifiers: strs_separated_by_comma,
):
    modifiers = tuple((m for m in modifiers.split(',') if m))

    # always use <epoch>-<commit-hash> as version
    # -> version denotes the intended, future release version, which is only relevant for marking
    #    a flavourset as actually being released
    upload_version = f'{gardenlinux_epoch}-{committish[:6]}'

    return glci.model.ReleaseIdentifier(
        build_committish=build_committish,
        version=upload_version,
        gardenlinux_epoch=int(gardenlinux_epoch),
        architecture=glci.model.Architecture(architecture),
        platform=platform,
        modifiers=modifiers,
    )
