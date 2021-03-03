Creates certificates needed

but actually maintains a whole CA with keys and serials beneath it

make SIGN_CERT=bar.ca foo.sign.p12

does all needed for certain signtools:
  - ensures ths CA exists
    CA - key and cert is root.key root.crt
  - creates an intermediate CA named bar.ca
  - signs the intermediate bar.ca with root CA
  - creates a signing request for foo.sign.crt
    (sign in the suffix makes sure it has signing capabilities)
  - signes the foo.sign.crt with the intermediate bar.ca
  - packages a pks12 archive of foo.sign.crt and foo.sign.key named foo.sign.p12


make SIGN_CERT=horst.ca HOSTNAME=test.com,example.com www.server.crt

- sign can only sign
- client can sign and authenticate as a client
- server can act as a server and provides next to the cn a set of SAN's
- peer can act as server and client with SAN's
- ca can act as a ca and sign  
