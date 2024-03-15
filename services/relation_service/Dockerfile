FROM rust:latest as builder

# Create a new empty shell project
RUN USER=root cargo new --bin relation_service
WORKDIR /relation_service

# Copy dependencies
COPY ./Cargo.toml ./Cargo.toml
COPY ./Cargo.lock ./Cargo.lock

#  cache dependencies
RUN cargo build --release
RUN rm src/*.rs

# copy source code
COPY ./src ./src

RUN rm ./target/release/deps/relation_service*
RUN cargo build --release

FROM rust:latest
COPY --from=builder /relation_service/target/release/relation_service /usr/local/bin
CMD ["relation_service"]
