FROM golang

WORKDIR /src
COPY . .
RUN go get -d github.com/gorilla/mux

CMD ["go","run","main.go"]