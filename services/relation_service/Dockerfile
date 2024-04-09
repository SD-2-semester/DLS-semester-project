FROM rust:latest as builder

RUN USER=root cargo new --bin relation_service
WORKDIR /relation_service

COPY ./Cargo.toml ./Cargo.toml
COPY ./Cargo.lock ./Cargo.lock

# Cache dependencies
RUN cargo build --release
RUN rm src/*.rs

COPY ./src ./src

# Rebuild only the changed source files
RUN rm ./target/release/deps/relation_service*
RUN cargo build --release

FROM debian:bookworm

# Copy the binary from the builder stage
COPY --from=builder /relation_service/target/release/relation_service /usr/local/bin/relation_service

CMD ["relation_service"]
