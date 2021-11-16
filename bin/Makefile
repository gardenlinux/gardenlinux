SCRIPTDIR=$(realpath .)

define BASH_BUILD
go install golang.org/x/lint/golint@latest
cd /go/src
golint garden-feat.go
go mod init garden-feat.go
go mod tidy -go=1.16
go mod tidy -go=1.17
go build garden-feat.go
endef
export BASH_BUILD

.PHONY: all
all: garden-feat

garden-feat: *.go
	docker run -v $(SCRIPTDIR):/go/src -ti golang:latest bash -c "$$BASH_BUILD"
	rm -f go.mod go.sum

.PHONY: clean
clean:
	rm -f go.mod go.sum garden-feat
