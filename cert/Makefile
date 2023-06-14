CERT_C=DE
CERT_L=Walldorf
CERT_O=SAP SE
CERT_OU=Garden Linux
CERT_E=contact@gardenlinux.io

GPG_KEY_TYPE=RSA
GPG_KEY_LENGTH=4096
GPG_NAME=Garden Linux Maintainers
GPG_EMAIL=contact@gardenlinux.io

export CERT_C CERT_L CERT_O CERT_OU CERT_E GPG_KEY_TYPE GPG_KEY_LENGTH GPG_NAME GPG_EMAIL

ifdef USE_KMS
export AWS_DEFAULT_REGION AWS_REGION AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
GENCERT_OPTS=--aws-kms-key-spec RSA_4096
endif

.PHONY: default clean distclean
.PRECIOUS: %.crt

ifndef CA
default: $(PREFIX)kernel-sign.crt $(PREFIX)secureboot.pk.auth $(PREFIX)secureboot.null.pk.auth $(PREFIX)secureboot.kek.auth $(PREFIX)secureboot.db.auth $(PREFIX)secureboot.aws-efivars $(PREFIX)sign.pub

$(PREFIX)intermediate-ca.crt: $(PREFIX)root-ca.crt
$(PREFIX)kernel-sign.crt: $(PREFIX)intermediate-ca.crt

gardenlinux.io.crt: $(PREFIX)intermediate-ca.crt

$(PREFIX)secureboot.pk.crt: $(PREFIX)intermediate-ca.crt
$(PREFIX)secureboot.kek.crt: $(PREFIX)secureboot.pk.crt
$(PREFIX)secureboot.db.crt: $(PREFIX)secureboot.kek.crt

$(PREFIX)secureboot.pk.auth: $(PREFIX)secureboot.pk.crt
$(PREFIX)secureboot.kek.auth: $(PREFIX)secureboot.pk.crt
$(PREFIX)secureboot.db.auth: $(PREFIX)secureboot.kek.crt
$(PREFIX)secureboot.key.auth: $(PREFIX)secureboot.pk.crt
$(PREFIX)secureboot.null.pk.auth: $(PREFIX)secureboot.pk.crt
else
default:
	@echo "Not building default targets when custom CA specified. Please build explicit certificate or omit CA argument." >&2
	@exit 1
endif

GUID.txt:
	uuidgen --random > '$@'

%.crt: %.conf $(CA)
	@./gencert --conf '$(word 1,$+)' --ca '$(word 2,$+)' $(GENCERT_OPTS) '$@'

%.auth: %.crt GUID.txt $(CA)
	@./genefiauth --guid-file '$(word 2,$+)' --ca '$(word 3,$+)' '$<' '$@'

%.null.pk.auth: GUID.txt $(CA)
	@./genefiauth --guid-file '$(word 1,$+)' --ca '$(word 2,$+)' --null '$@'

%.aws-efivars: %.pk.auth %.kek.auth %.db.auth
	@uefivars.py -i none -o aws -O '$@' -P '$*.pk.esl' -K '$*.kek.esl' -b '$*.db.esl'

%.pub: gpg.conf
	@./gengpg --conf '$<' '$@'

clean:
	@echo "Removing *.pub *.crt *.csr *.key *.arn *.chain GUID.txt *.esl *.auth *.aws-efivars but nothing starting with gardenlinux-"
	@find . \( -name '*.pub' -o -name '*.crt' -o -name '*.csr' -o -name '*.key' -o -name '*.arn' -o -name '*.chain' -o -name 'GUID.txt' -o -name '*.esl' -o -name '*.auth' -o -name '*.aws-efivars' \) -a -not -name 'gardenlinux-*' -delete

distclean:
	@echo "Removing *.pub *.crt *.csr *.key *.arn *.chain GUID.txt *.esl *.auth *.aws-efivars"
	@find . \( -name '*.pub' -o -name '*.crt' -o -name '*.csr' -o -name '*.key' -o -name '*.arn' -o -name '*.chain' -o -name 'GUID.txt' -o -name '*.esl' -o -name '*.auth' -o -name '*.aws-efivars' \) -delete
