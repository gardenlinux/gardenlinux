SIGN_CA=root.ca
SIGN_CERT=intermediate.ca
MAINTAINER=Garden Linux Maintainers
MAINTAINER_EMAIL=contact@gardenlinux.io
KEYTYPE=RSA
KEYLENGTH=4096
HOSTNAME=

#internal
INTERNAL_HOSTNAME=$(shell [ -n "$(HOSTNAME)" ] && printf "%s=%s" "-hostname" "$(HOSTNAME)" )

define cert
{
  "CN": "%%CN%%",
  "key": { "algo": "$(shell echo $(KEYTYPE) | tr '[:upper:]' '[:lower:]')", "size": $(KEYLENGTH) },
  "names": [
  	{ "C": "DE", "L": "Walldorf", "O": "SAP SE", "OU": "Garden Linux", "E": "$(MAINTAINER_EMAIL)" }
  ]
}
endef
export cert

define profile
{"signing":
    {"default":
	{"expiry":"8760h"},
	"profiles":{
	    "ca":{
		"usages":["signing","digital signature","key encipherment","cert sign","crl sign","server auth","client auth"],
		"ca_constraint":{"is_ca":true,"max_path_len":0,"max_path_len_zero":true},
		"expiry":"43800h"
	    },
	    "peer":{
		"usages":["signing","digital signature","key encipherment","client auth","server auth"],
		"expiry":"8760h"
	    },
	    "server":{
		"usages":["signing","digital signing","key encipherment","server auth"],
		"expiry":"8760h"
	    },
	    "client":{
		"usages":["signing","digital signature","key encipherment","client auth"],
		"expiry":"8760h"
	    },
	    "sign":{
		"usages":["signing","digital signature","key encipherment"],
		"expiry":"8760h"
	    }
	}
    }
}
endef
export profile

define sign_gpg
%no-protection
Key-Type: $(shell echo $(KEYTYPE) | tr '[:lower:]' '[:upper:]')
Key-Length: $(KEYLENGTH)
Key-Usage: sign
Name-Real: $(MAINTAINER)
Name-Email: $(MAINTAINER_EMAIL)
Expire-Date: 0
endef
export sign_gpg

define BASH_BUILD
git clone https://github.com/cloudflare/cfssl.git
cd cfssl
make
mv bin/* /build
endef
export BASH_BUILD

all: Kernel.sign.crt sign.pub
test:
	echo "$(INTERNAL_HOSTNAME)"

#### cfssl
cfssl/cfssl cfssl/cfssljson:
	@echo "Building cfssl / cfssljson"
	@mkdir -p cfssl
	@docker run --volume "$$(realpath cfssl):/build" --rm -ti golang:latest bash -c "$$BASH_BUILD"

#### CA
.PHONY: %.ca
%.ca: cfssl/cfssl cfssl/cfssljson
	@echo "Recreating CN=Garden Linux $(@:.ca=) CA"
	@rm -rf $@*.crt
	@echo "$$cert" | sed "s/%%CN%%/Garden Linux $(@:.ca=) CA/" | cfssl/cfssl gencert -initca - | cfssl/cfssljson -bare -stdout | ./rename $@

.PRECIOUS: %.ca.key
%.ca.csr: %.ca ;
%.ca.key: %.ca ;

.PRECIOUS: $(SIGN_CA).crt $(SIGN_CA).key
$(SIGN_CA).crt: $(SIGN_CA).key
	@rm -rf $(SIGN_CA).csr

.PRECIOUS: %.ca.crt
%.ca.crt: %.ca.key $(SIGN_CA).crt
	@echo "Signing CA $(@:.ca.crt=) by $(SIGN_CA)"
	$(eval tmpfile := $(shell mktemp))
	@echo "$$profile" > $(tmpfile)
	@cfssl/cfssl sign -ca $(SIGN_CA).crt -ca-key $(SIGN_CA).key -config $(tmpfile) -profile ca $(<:.key=.csr) | cfssl/cfssljson -bare -stdout | ./rename $(@:.crt=) $(SIGN_CA)
	@rm -rf $(tmpfile) $(<:.key=.csr)

#### signature
.PHONY: %.sign
%.sign: cfssl/cfssl cfssl/cfssljson
	@echo "Recreating CN=Garden Linux $(@:.sign=) Signature"
	@echo "$$cert" | sed "s/%%CN%%/Garden Linux $(@:.sign=) Signature/" | cfssl/cfssl genkey - | cfssl/cfssljson -bare -stdout | ./rename $@

.PRECIOUS: %.sign.key
%.sign.csr: %.sign ;
%.sign.key: %.sign ;

.PRECIOUS: %.sign.crt
%.sign.crt: %.sign.key $(SIGN_CERT).crt
	@echo "Signing Signature Certificate $(@:.sign.crt=) by $(SIGN_CERT)"
	$(eval tmpfile := $(shell mktemp))
	@echo "$$profile" > $(tmpfile)
	@cfssl/cfssl sign -ca $(SIGN_CERT).crt -ca-key $(SIGN_CERT).key -config $(tmpfile) -profile=sign $(<:.key=.csr) | cfssl/cfssljson -bare -stdout | ./rename $(@:.crt=) $(SIGN_CERT)
	@rm -rf $(tmpfile) $(<:.key=.csr)

#### client
.PHONY: %.client
%.client: cfssl/cfssl cfssl/cfssljson
	@echo "Recreating CN=Garden Linux $(@:.client=) Client"
	@echo "$$cert" | sed "s/%%CN%%/Garden Linux $(@:.client=) Signature/" | cfssl/cfssl genkey - | cfssl/cfssljson -bare -stdout | ./rename $@

.PRECIOUS: %.client.key
%.client.csr: %.client ;
%.client.key: %.client ;

.PRECIOUS: %.client.crt
%.client.crt: %.client.key $(SIGN_CERT).crt
	@echo "Signing Signature Certificate $(@:.client.crt=) by $(SIGN_CERT)"
	$(eval tmpfile := $(shell mktemp))
	@echo "$$profile" > $(tmpfile)
	@cfssl/cfssl sign -ca $(SIGN_CERT).crt -ca-key $(SIGN_CERT).key -config $(tmpfile) -profile=client $(<:.key=.csr) | cfssl/cfssljson -bare -stdout | ./rename $(@:.crt=) $(SIGN_CERT)
	@rm -rf $(tmpfile) $(<:.key=.csr)

#### server
.PHONY: %.server
%.server: cfssl/cfssl cfssl/cfssljson
	@echo "Recreating CN=Garden Linux $(@:.server=) Server"
	@echo "$$cert" | sed "s/%%CN%%/Garden Linux $(@:.server=) Server/" | cfssl/cfssl genkey - | cfssl/cfssljson -bare -stdout | ./rename $@

.PRECIOUS: %.server.key
%.server.csr: %.server ;
%.server.key: %.server ;

.PRECIOUS: %.server.crt
%.server.crt: %.server.key $(SIGN_CERT).crt
	@echo "Signing Server Certificate $(@:.server.crt=) by $(SIGN_CERT)"
	@find . -lname $@ -exec rm -rf {} \;
	$(eval tmpfile := $(shell mktemp))
	@echo "$$profile" > $(tmpfile)
	@cfssl/cfssl sign -ca $(SIGN_CERT).crt -ca-key $(SIGN_CERT).key -config $(tmpfile) -profile=server $(INTERNAL_HOSTNAME)  $(<:.key=.csr) | cfssl/cfssljson -bare -stdout | ./rename $(@:.crt=) $(SIGN_CERT)
	@rm -rf $(tmpfile) $(<:.key=.csr)

#### peer
.PHONY: %.peer
%.peer: cfssl/cfssl cfssl/cfssljson
	@echo "Recreating CN=Garden Linux $(@:.peer=) Peer"
	@echo "$$cert" | sed "s/%%CN%%/Garden Linux $(@:.peer=) Server/" | cfssl/cfssl genkey - | cfssl/cfssljson -bare -stdout | ./rename $@

.PRECIOUS: %.peer.key
%.peer.csr: %.peer ;
%.peer.key: %.peer ;

.PRECIOUS: %.peer.crt
%.peer.crt: %.peer.key $(SIGN_CERT).crt
	@echo "Signing Server Certificate $(@:.peer.crt=) by $(SIGN_CERT)"
	@find . -lname $@ -exec rm -rf {} \;
	$(eval tmpfile := $(shell mktemp))
	@echo "$$profile" > $(tmpfile)
	@cfssl/cfssl sign -ca $(SIGN_CERT).crt -ca-key $(SIGN_CERT).key -config $(tmpfile) -profile=peer $(INTERNAL_HOSTNAME)  $(<:.key=.csr) | cfssl/cfssljson -bare -stdout | ./rename $(@:.crt=) $(SIGN_CERT)
	@rm -rf $(tmpfile) $(<:.key=.csr)

#### format change
.PRECIOUS: %.p12
%.p12: %.crt %.key
	openssl pkcs12 -export -out $@ -inkey $(@:.p12=).key -in $(@:.p12=).crt -passout pass:""


#### GPG signature
sign.pub:
ifeq ($(shell gpg --list-keys $(MAINTAINER_EMAIL) 2> /dev/null), )
	@echo "GPG: creating a new key $(MAINTAINER_EMAIL)"
	echo "$$sign_gpg" | gpg --generate-key --batch -;
endif
	@echo "GPG: exporting public key $(MAINTAINER_EMAIL)"
	gpg --export --armor $(MAINTAINER_EMAIL) > sign.pub

sign.key:
	@echo "GPG: exporting private key $(MAINTAINER_EMAIL)"
	gpg --export-secret-key --armor $(MAINTAINER_EMAIL) > sign.key

#### cleaning
PHONY: clean
clean:
	@echo "removing *.full  *.chain *.crt *.key *.csr *.p12 but nothing with gardenlinux.*"
	@find . \( -name '*.full' -o -name '*.crt' -o -name '*.pub' -o -name '*.key' -o -name '*.csr' -o -name '*.p12' -o -name '*.chain' \) -a -not -name 'gardenlinux.*' -exec rm -rf {} \;

PHONY: superclean
superclean: clean
	rm -rf cfssl
