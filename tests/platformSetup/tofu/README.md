## use locally encrypted state

```
# export TF_ENCRYPTION env variable

export TF_ENCRYPTION='''{
  "key_provider": {
    "pbkdf2": {
      "passphrase": {
        "passphrase": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      } 
    }
  },
  "method": {
    "aes_gcm": {
      "method": {
         "keys": "${key_provider.pbkdf2.passphrase}"
      }
    }
  },
  "state": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  },
  "plan": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  }
}'''

# initialize local backend
tofu init
```


## create encrypted state backend in S3

```
# export TF_ENCRYPTION env variable

export TF_ENCRYPTION='''{
  "key_provider": {
    "pbkdf2": {
      "passphrase": {
        "passphrase": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      } 
    }
  },
  "method": {
    "aes_gcm": {
      "method": {
         "keys": "${key_provider.pbkdf2.passphrase}"
      }
    }
  },
  "state": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  },
  "plan": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  }
}'''

# initialize local backend
tofu init

# create dedicated workspace for state
tofu workspace select -or-create tfstate

# create S3 state resources
tofu apply -var deploy_state_aws=true

# migrate to S3 backend
cp backend.tf.example backend.tf

# get created bucket
tofu output -raw state_aws_bucket_name

# reference current region/bucket
vim backend.tf

# migrate state
tofu init -migrate-state

# switch back to default workspace
tofu workspace select default
```

## create TF_ENCRYPTION environment variable for github actions

```
# export TF_ENCRYPTION env variable

export TF_ENCRYPTION='''{
  "key_provider": {
    "pbkdf2": {
      "passphrase": {
        "passphrase": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      } 
    }
  },
  "method": {
    "aes_gcm": {
      "method": {
         "keys": "${key_provider.pbkdf2.passphrase}"
      }
    }
  },
  "state": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  },
  "plan": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  }
}'''

# encode in base64 to put in TF_ENCRYPTION secret

echo $TF_ENCRYPTION | base64 -w0
```
