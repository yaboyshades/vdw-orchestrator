module github.com/vdw-orchestrator/mangle

go 1.21

require (
    google.golang.org/grpc v1.59.0
    google.golang.org/protobuf v1.31.0
    github.com/sirupsen/logrus v1.9.3
    github.com/spf13/cobra v1.7.0
    github.com/spf13/viper v1.16.0
)

require (
    github.com/golang/protobuf v1.5.3 // indirect
    github.com/inconshreveable/mousetrap v1.1.0 // indirect
    github.com/spf13/pflag v1.0.5 // indirect
    golang.org/x/net v0.17.0 // indirect
    golang.org/x/sys v0.13.0 // indirect
    golang.org/x/text v0.13.0 // indirect
    google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b // indirect
)

// For Datalog engine, we'll use a simple implementation
// In production, this would be replaced with a more sophisticated engine
require (
    github.com/antlr/antlr4/runtime/Go/antlr v1.4.10
)