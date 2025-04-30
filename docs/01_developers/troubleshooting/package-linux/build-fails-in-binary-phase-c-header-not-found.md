# Build fails in "Binary" phase, c header file is not found

If you face an issue similar to [Fix build of kernel 6.6.88 (fatal error: ssl-common.h: No such file or directory) #2986](https://github.com/gardenlinux/gardenlinux/issues/2986) with a build output like this:

```
gcc -g -O2 -Werror=implicit-function-declaration -fstack-protector-strong -fstack-clash-protection -Wformat -Werror=format-security -mbranch-protection=standard -Wall -Wdate-time -D_FORTIFY_SOURCE=2 -I/tmp/tmp.Es0yXHtwaT/src/certs -I/tmp/tmp.Es0yXHtwaT/src/debian/build/build-tools/certs -isystem /tmp/tmp.Es0yXHtwaT/src/debian/build/build-tools/include -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64 -Wl,-z,relro  /tmp/tmp.Es0yXHtwaT/src/certs/extract-cert.c  -lcrypto -o extract-cert
/tmp/tmp.Es0yXHtwaT/src/certs/extract-cert.c:34:10: fatal error: ssl-common.h: No such file or directory
   34 | #include "ssl-common.h"
      |          ^~~~~~~~~~~~~~
compilation terminated.
make[3]: *** [<builtin>: extract-cert] Error 1
make[2]: *** [debian/rules.real:589: build_kbuild] Error 2
make[1]: *** [debian/rules.gen:187: build-arch_arm64_kbuild] Error 2
make: *** [debian/rules:44: build-arch] Error 2
dpkg-buildpackage: error: debian/rules binary-arch subprocess returned exit status 2
```

You should check for the following potential issues:

- Has the new upstream kernel any changes of compiler options in makefiles?
- Are those flags actually in the gcc invocation?
- You might need to patch the makefile in debian as in [this example](https://github.com/gardenlinux/package-linux/pull/114/files)
