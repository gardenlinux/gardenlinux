#!/bin/bash

sudo apt-get install golang-cfssl

rename () {
	rm -f $1.csr
	mv $1.pem $1.crt
	mv $1-key.pem $1.key
	ln -s $1.crt $2-$(openssl x509 -noout -serial -in $1.crt | cut -d'=' -f2).crt
}

if [ ! -f root.key ]; then 
	cfssl gencert -initca root.ca | cfssljson -bare root
	rename root root
fi
if [ ! -f intermediate1.key ]; then
	cfssl gencert -initca intermediate1.ca | cfssljson -bare intermediate1
	cfssl sign -ca root.crt -ca-key root.key -config profile.json -profile intermediate_ca intermediate1.csr | cfssljson -bare intermediate1
	rename intermediate1 root
fi

cfssl gencert -ca intermediate1.crt -ca-key intermediate1.key -config profile.json -profile=sign kernel.json | cfssljson -bare kernel
rename kernel intermediate1
openssl pkcs12 -export -out kernel.p12 -inkey kernel.key -in kernel.crt
#cfssl gencert -ca intermediate1.crt -ca-key intermediate1.key -config profile.json -profile=server webroot.json | cfssljson -bare webroot
#rename webroot intermediate1

#rm *.crt *.key intermediate1-* root-*
