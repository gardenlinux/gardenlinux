MAKEFLAGS += --no-builtin-rules

.SILENT:
.DELETE_ON_ERROR:

.PHONY: dist clean

dist: .build/dist.tar.gz

clean:
	rm -f dist.tar.gz runtime-*.tar.gz

.build:
	mkdir .build

.build/dist.tar.gz: util/build_dist.sh .build/runtime-x86_64.tar.gz .build/runtime-aarch64.tar.gz conftest.py $(wildcard plugins/*.py) $(wildcard test_*.py) | .build
	./$< $@ x86_64:$(word 2,$^) aarch64:$(word 3,$^)

.build/runtime-%.tar.gz: util/build_runtime.sh util/requirements.txt | .build
	./$< $* $(word 2,$^) $@
