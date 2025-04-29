# Build fails in "Binary" phase, c header file is not found

If you face an issue similar to [Fix build of kernel 6.6.88 (fatal error: ssl-common.h: No such file or directory) #2986](https://github.com/gardenlinux/gardenlinux/issues/2986), you should check for the following potential issues:

- Has the new upstream kernel any changes of compiler options in makefiles?
- Are those flags actually in the gcc invocation?
- You might need to patch the makefile in debian as in [this example](https://github.com/gardenlinux/package-linux/pull/114/files)
