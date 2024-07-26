FROM golang:1.22

COPY go.mod go.sum /src/
COPY src /src/src

WORKDIR /src

RUN go mod download
RUN CGO_ENABLED=0 go build -o plcmon github.com/leoluk/plcmon/src/cmd/plcmon

FROM alpine:3.20
COPY --from=0 /src/plcmon /usr/local/bin/plcmon
COPY entrypoint.sh /entrypoint.sh

CMD ["sh", "/entrypoint.sh"]
