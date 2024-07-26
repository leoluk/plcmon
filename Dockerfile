FROM golang:1.22

COPY go.mod go.sum /src/
COPY src /src/src

WORKDIR /src

RUN go mod download
RUN CGO_ENABLED=0 go build -o plcmon github.com/leoluk/plcmon/src/cmd/plcmon

FROM scratch
COPY --from=0 /src/plcmon /usr/local/bin/plcmon

CMD ["plcmon"]
