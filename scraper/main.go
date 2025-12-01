package main

import (
	"bytes"
	"context"
	"flag"
	"fmt"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"io"
	"log/slog"
	"net/http"
	"os/signal"
	"syscall"
	"time"
)

const (
	CarsEndpoint = "https://greenmobility.frontend.fleetbird.eu/api/prod/v1.06/cars/"
	Bucket       = "dokploy-green"
	KeyPrefix    = "cars"
)

func fetchAndSave(endpoint string) error {
	resp, err := http.Get(endpoint)
	if err != nil {
		return fmt.Errorf("fetch error: %w", err)
	}
	defer resp.Body.Close()

	timestamp := time.Now().Format("20060102_150405")

	sess := session.Must(session.NewSession(
		&aws.Config{
			Region: aws.String("eu-central-1"),
		}))
	s3Client := s3.New(sess)
	s3Key := fmt.Sprintf("%s/cars_%s.json", KeyPrefix, timestamp)
	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("read body error: %w", err)
	}
	bodyReader := bytes.NewReader(bodyBytes)
	_, err = s3Client.PutObject(&s3.PutObjectInput{
		Bucket: aws.String(Bucket),
		Key:    aws.String(s3Key),
		Body:   bodyReader,
	})
	if err != nil {
		return fmt.Errorf("S3 upload error: %w", err)
	}
	slog.Info("Uploaded to S3", "bucket", Bucket, "key", s3Key)
	return nil
}

func main() {
	interval := flag.Duration("interval", 2*time.Minute, "Fetch interval (e.g. 20s, 2m)")
	flag.Parse()

	ticker := time.NewTicker(*interval)
	defer ticker.Stop()

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	slog.Info("Starting data fetcher", "endpoint", CarsEndpoint, "interval", interval.String())
	for {
		select {
		case <-ticker.C:
			if err := fetchAndSave(CarsEndpoint); err != nil {
				slog.Error("Fetch and save failed", "error", err)
			}
		case <-ctx.Done():
			slog.Info("Shutting down gracefully")
			return
		}
	}
}
