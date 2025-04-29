# Build fails in "Source" phase, patch is rejected

Most probably, if applying a patch fails this is because we're upgrading the upstream kernel patch version (like from `6.12.24` to `6.12.25`).
Chances are that this is a patch coming from [Debian's kernel build](https://salsa.debian.org/kernel-team/linux).

Probable error causes to check for:
- Is there a better `debian_ref` available?
  - `debian_ref` is a variable in the `prepare_sources` script that defines which git tag is taken from [Debian's kernel build](https://salsa.debian.org/kernel-team/linux)
  - Check the git tags in [Debian's kernel build](https://salsa.debian.org/kernel-team/linux)
  - In an ideal world, this should be the same version as the upstream kernel we're building, but this is not always possible
  - Debian might have a few days of delay for kernel versions they still maintain (like 6.12 as of April 2025)
  - For kernel versions they don't maintain (like 6.6 as of April 2025), we need to patch conflicts on our own
  - Refer to [Create or fix Patches](https://github.com/gardenlinux/package-build/blob/main/PATCHING.MD) for cases when you need to work with patches
  - It might be as simple as 'refreshing' a patch using quilt, like in cases where only one or two lines moved in a patched source file

In some cases, we need to remove a patch that debian applies because the same change was added to the upstream kernel itself.
You can find an example for this [here](https://github.com/gardenlinux/package-linux/commit/d5b4647c816a58057c65cdde00822ba00b988a1d).
