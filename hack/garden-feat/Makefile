all:
	docker run -v ~/gardenlinux/hack/garden-feat:/go/src -ti golang:latest bash -c "cd /go/src; go mod init garden-feat.go; go mod tidy -go=1.16; go mod tidy -go=1.17; go build garden-feat.go;"

clean:
	rm -f go.mod go.sum garden-feat
