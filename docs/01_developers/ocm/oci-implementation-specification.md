# OCI Implementation 

### Upload
Automated uploads are mandatory for the Garden Linux OCI framework. For this, we use re-usable github actions. 


```yaml
name: Upload Artifact to OCI Registry

on:
  workflow_call:
    inputs:
      artifact_path:
        description: 'Path to the artifact file to upload'
        required: true
        type: string
      tag_name:
        description: 'Tag name to assign to the uploaded artifact'
        required: true
        type: string
      registry_url:
        description: 'OCI Registry URL (e.g., myregistry.io/myapp)'
        required: true
        type: string

jobs:
  upload:
    runs-on: ubuntu-latest
    name: Upload to OCI Registry
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Login to OCI Registry
        run: echo ${{ secrets.REGISTRY_PASSWORD }} | oras login --username ${{ secrets.REGISTRY_USERNAME }} --password-stdin ${{ inputs.registry_url }}
      
      - name: Upload Artifact
        run: oras push ${{ inputs.registry_url }}:${{ inputs.tag_name }} ${{ inputs.artifact_path }}

      - name: Logout from OCI Registry
        run: oras logout ${{ inputs.registry_url }}
```

And it can be used like this:
```yaml
name: Example Usage Workflow

on: [push]

jobs:
  call-upload-workflow:
    uses: ./.github/workflows/upload-to-oci.yml@main
    with:
      artifact_path: './path/to/your/artifact/file.tar.gz'
      tag_name: 'v1.0.0'
      registry_url: 'myregistry.io/myapp'
    secrets:
      REGISTRY_USERNAME: ${{ secrets.REGISTRY_USERNAME }}
      REGISTRY_PASSWORD: ${{ secrets.REGISTRY_PASSWORD }}
```



### Download 

It can be a helpful to be able to download artefacts from OCI in a GitHub actions step.
This allows to easily discover and download the correct container image for a given task (e.g. test container). 


```yaml
name: 'Download Artifact from OCI Registry'
description: 'Downloads an artifact from an OCI registry using a tag'
inputs:
  tag_name:
    description: 'Tag name of the artifact to download'
    required: true
  registry_url:
    description: 'OCI Registry URL (e.g., myregistry.io/myapp)'
    required: true
  output_path:
    description: 'Path to save the downloaded artifact'
    required: true

runs:
  using: 'composite'
  steps:
    - name: Login to OCI Registry
      run: echo "${{ secrets.REGISTRY_PASSWORD }}" | oras login --username ${{ secrets.REGISTRY_USERNAME }} --password-stdin ${{ inputs.registry_url }}
      shell: bash

    - name: Download Artifact
      run: oras pull -a -o ${{ inputs.output_path }} ${{ inputs.registry_url }}:${{ inputs.tag_name }}
      shell: bash

    - name: Logout from OCI Registry
      run: oras logout ${{ inputs.registry_url }}
      shell: bash

```

And it can be used like this:

```yaml
jobs:
  download-artifact:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      
      - name: Download OCI Artifact
        uses: ./.github/actions/download-from-oci@main
        with:
          tag_name: 'v1.0.0'
          registry_url: 'myregistry.io/myapp'
          output_path: './path/for/artifact'
        env:
          REGISTRY_USERNAME: ${{ secrets.REGISTRY_USERNAME }}
          REGISTRY_PASSWORD: ${{ secrets.REGISTRY_PASSWORD }}

```
