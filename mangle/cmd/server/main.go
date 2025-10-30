package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"

	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	"google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection"

	pb "github.com/yaboyshades/vdw-orchestrator/mangle/generated/reasoning"
)

type reasoningServer struct {
	pb.UnimplementedReasoningServiceServer
	rulesFile string
	rules     []string
}

// ApplyRules implements the reasoning logic
func (s *reasoningServer) ApplyRules(ctx context.Context, req *pb.ReasoningRequest) (*pb.ReasoningResponse, error) {
	log.Printf("Received reasoning request with %d facts", len(req.Facts))
	
	// Simple mock reasoning - in a real implementation, this would use
	// a proper reasoning engine like Datalog, Prolog, or custom logic
	conclusions := make([]string, 0)
	appliedRules := make([]string, 0)
	
	// Example reasoning: if we have facts about being human and mortal
	for _, fact := range req.Facts {
		if strings.Contains(fact, "human") {
			conclusions = append(conclusions, "mortal")
			appliedRules = append(appliedRules, "human -> mortal")
		}
		if strings.Contains(fact, "bird") && strings.Contains(fact, "can_fly") {
			conclusions = append(conclusions, "aerial_creature")
			appliedRules = append(appliedRules, "bird ∧ can_fly -> aerial_creature")
		}
	}
	
	return &pb.ReasoningResponse{
		Conclusions:   conclusions,
		AppliedRules:  appliedRules,
		Success:       true,
		ErrorMessage:  "",
	}, nil
}

// HealthCheck implements health checking
func (s *reasoningServer) HealthCheck(ctx context.Context, req *pb.HealthCheckRequest) (*pb.HealthCheckResponse, error) {
	return &pb.HealthCheckResponse{
		Healthy: true,
		Status:  "OK",
	}, nil
}

// LoadRules loads new reasoning rules
func (s *reasoningServer) LoadRules(ctx context.Context, req *pb.LoadRulesRequest) (*pb.LoadRulesResponse, error) {
	// Parse rules content
	rules := strings.Split(req.RulesContent, "\n")
	validRules := make([]string, 0)
	
	for _, rule := range rules {
		rule = strings.TrimSpace(rule)
		if rule != "" && !strings.HasPrefix(rule, "//") {
			validRules = append(validRules, rule)
		}
	}
	
	s.rules = validRules
	
	return &pb.LoadRulesResponse{
		Success:      true,
		ErrorMessage: "",
		RulesLoaded:  int32(len(validRules)),
	}, nil
}

func main() {
	var (
		port      = flag.String("port", "50051", "The server port")
		rulesFile = flag.String("rules", "reasoning_rules.dl", "Path to reasoning rules file")
		healthCheck = flag.Bool("health-check", false, "Perform health check and exit")
	)
	flag.Parse()
	
	if *healthCheck {
		// Simple health check - just verify the server can start
		lis, err := net.Listen("tcp", ":"+*port)
		if err != nil {
			log.Fatalf("Health check failed: %v", err)
		}
		lis.Close()
		fmt.Println("Health check passed")
		os.Exit(0)
	}
	
	lis, err := net.Listen("tcp", ":"+*port)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}
	
	// Create gRPC server
	s := grpc.NewServer()
	
	// Create reasoning server instance
	reasoningServer := &reasoningServer{
		rulesFile: *rulesFile,
		rules:     make([]string, 0),
	}
	
	// Load initial rules if file exists
	if _, err := os.Stat(*rulesFile); err == nil {
		log.Printf("Loading rules from %s", *rulesFile)
		// In a real implementation, you would parse the Datalog file
		// For now, just log that we found the file
	}
	
	// Register services
	pb.RegisterReasoningServiceServer(s, reasoningServer)
	
	// Register health service
	healthServer := health.NewServer()
	grpc_health_v1.RegisterHealthServer(s, healthServer)
	healthServer.SetServingStatus("", grpc_health_v1.HealthCheckResponse_SERVING)
	
	// Register reflection service (useful for debugging)
	reflection.Register(s)
	
	log.Printf("Starting mangle reasoning server on port %s", *port)
	log.Printf("Rules file: %s", *rulesFile)
	
	// Handle graceful shutdown
	go func() {
		c := make(chan os.Signal, 1)
		signal.Notify(c, os.Interrupt, syscall.SIGTERM)
		<-c
		log.Println("Shutting down server...")
		s.GracefulStop()
	}()
	
	if err := s.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}