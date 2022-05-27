CERT_KEY_ALGO=rsa
CERT_KEY_SIZE=4096
CERT_NAME_C=DE
CERT_NAME_L=Walldorf
CERT_NAME_O=SAP SE
CERT_NAME_OU=Garden Linux
CERT_NAME_E=contact@gardenlinux.io

GPG_KEY_TYPE=RSA
GPG_KEY_LENGTH=4096
GPG_NAME=Garden Linux Maintainers
GPG_EMAIL=contact@gardenlinux.io

export CERT_KEY_ALGO CERT_KEY_SIZE CERT_NAME_C CERT_NAME_L CERT_NAME_O CERT_NAME_OU CERT_NAME_E GPG_KEY_TYPE GPG_KEY_LENGTH GPG_NAME GPG_EMAIL

ifdef HOSTNAME
HOSTNAME_ARG=--hostname '$(HOSTNAME)'
endif

.PHONY: default clean
.PRECIOUS: %.crt

ifndef CA
default: $(PREFIX)kernel.sign.crt $(PREFIX)secureboot.pk.auth $(PREFIX)secureboot.null.pk.auth $(PREFIX)secureboot.kek.auth $(PREFIX)secureboot.db.auth $(PREFIX)sign.pub

$(PREFIX)intermediate.ca.crt: $(PREFIX)root.ca.crt

$(PREFIX)kernel.sign.crt: $(PREFIX)intermediate.ca.crt

$(PREFIX)secureboot.pk.ca.crt: $(PREFIX)intermediate.ca.crt
$(PREFIX)secureboot.kek.ca.crt: $(PREFIX)secureboot.pk.ca.crt
$(PREFIX)secureboot.db.sign.crt: $(PREFIX)secureboot.kek.ca.crt

$(PREFIX)secureboot.pk.auth: $(PREFIX)secureboot.pk.ca.crt
$(PREFIX)secureboot.kek.auth: $(PREFIX)secureboot.pk.ca.crt
$(PREFIX)secureboot.db.auth: $(PREFIX)secureboot.kek.ca.crt
$(PREFIX)secureboot.key.auth: $(PREFIX)secureboot.pk.ca.crt
$(PREFIX)secureboot.null.pk.auth: $(PREFIX)secureboot.pk.ca.crt
else
default:
	@echo "Not building default targets when custom CA specified. Please build explicit certificate or omit CA argument." >&2
	@exit 1
endif

GUID.txt:
	uuidgen --random > '$@'

%.crt: cert.json config.json $(CA)
	@./gencert --cert '$(word 1,$^)' --conf '$(word 2,$^)' --ca '$(word 3,$^)' $(HOSTNAME_ARG) '$@'

%.auth: %.ca.crt GUID.txt $(CA)
	@./genefiauth --guid-file '$(word 2,$^)' --ca '$(word 3,$+)' '$<' '$@'

%.auth: %.sign.crt GUID.txt $(CA)
	@./genefiauth --guid-file '$(word 2,$^)' --ca '$(word 3,$+)' '$<' '$@'

%.null.pk.auth: GUID.txt $(CA)
	@./genefiauth --guid-file '$(word 1,$^)' --ca '$(word 2,$^)' --null '$@'

%.pub: gpg.conf
	@./gengpg --conf '$<' '$@'

clean:
	@echo "Removing *.crt *.key *.chain GUID.txt *.esl *.auth but nothing starting with gardenlinux-"
	@find . \( -name '*.pub' -o -name '*.crt' -o -name '*.key' -o -name '*.chain' -o -name 'GUID.txt' -o -name '*.esl' -o -name '*.auth' \) -a -not -name 'gardenlinux-*' -delete

distclean:
	@echo "Removing *.crt *.key *.chain *.esl *.auth"
	@find . \( -name '*.pub' -o -name '*.crt' -o -name '*.key' -o -name '*.chain' -o -name '*.esl' -o -name '*.auth' \) -delete
