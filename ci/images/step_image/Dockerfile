FROM eu.gcr.io/gardener-project/component/cli:latest AS component-cli
FROM eu.gcr.io/gardener-project/cc/job-image-base:latest

COPY --from=component-cli /component-cli /bin/component-cli
COPY requirements.txt /tmp/

RUN pip3 install --upgrade \
  pip \
  wheel \
&& pip3 install --no-cache-dir --upgrade -r /tmp/requirements.txt

