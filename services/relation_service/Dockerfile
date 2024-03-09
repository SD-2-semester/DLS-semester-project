# Use the official Rust image as a parent image
FROM rust:latest as builder

# Create a new empty shell project
RUN USER=root cargo new --bin relation_service
WORKDIR /relation_service

# Copy over your manifests
COPY ./Cargo.toml ./Cargo.toml
COPY ./Cargo.lock ./Cargo.lock

# This build step will cache your dependencies
RUN cargo build --release
RUN rm src/*.rs

# Now that the dependencies are cached, copy your source code
COPY ./src ./src

# Build for release
RUN rm ./target/release/deps/relation_service*
RUN cargo build --release

# The final image will use the debian buster-slim image as its base
FROM debian:buster-slim
ARG APP=/usr/src/app

# Copy the binary and extra files ("." relative to the build context) to the app directory
FROM rust:latest
COPY --from=builder /relation_service/target/release/relation_service /usr/local/bin
CMD ["relation_service"]