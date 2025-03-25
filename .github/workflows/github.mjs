export function getPlatformForCName(cname) {
    const platform = cname.split("-", 1)[0];
    return platform;
}
