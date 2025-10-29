# Mangle Reasoning Sidecar
# This Docker image contains the Mangle deductive reasoning engine
# implemented in Go with gRPC server for high-performance reasoning

FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git protobuf-dev protoc

# Install Go protobuf compiler
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
RUN go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Set working directory
WORKDIR /app

# Copy Go modules files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Generate gRPC code from proto files
RUN mkdir -p generated
RUN protoc --go_out=generated --go-grpc_out=generated \
    --go_opt=paths=source_relative \
    --go-grpc_opt=paths=source_relative \
    proto/reasoning.proto

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o mangle-server ./cmd/server

# Production stage
FROM alpine:latest

# Install ca-certificates for HTTPS
RUN apk --no-cache add ca-certificates

# Create non-root user
RUN adduser -D -s /bin/sh mangleuser

WORKDIR /home/mangleuser

# Copy binary from builder
COPY --from=builder /app/mangle-server .

# Copy reasoning rules
COPY reasoning_rules.dl .

# Copy any configuration files
COPY config/ ./config/

# Change ownership
RUN chown -R mangleuser:mangleuser /home/mangleuser

# Switch to non-root user
USER mangleuser

# Expose gRPC port
EXPOSE 50051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ./mangle-server --health-check || exit 1

# Run the server
CMD ["./mangle-server", "--port=50051", "--rules=reasoning_rules.dl"]