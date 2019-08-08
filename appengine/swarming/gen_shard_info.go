// Program to iterate over BotInfo entities and output a series
// of ranges such that the number of entities in each range is
// < count
package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"sort"
	"strings"
	"time"

	"cloud.google.com/go/datastore"
	"google.golang.org/api/iterator"
)

var count = flag.Int("count", 100, "number of items per shard")
var projectID = flag.String("project-id", "chromium-swarm", "project to use for BotInfo query")
var wrapInVar = flag.String("wrap-in-var", "", "if set, wrap results in a python var")

func main() {
	flag.Parse()
	ctx := context.Background()

	// Creates a client.
	client, err := datastore.NewClient(ctx, *projectID)
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}
	defer func() {
		if err := client.Close(); err != nil {
			log.Println(err)
		}
	}()
	ids := dump(ctx, client)
	sort.Strings(ids)
	i := 0
	start := "id:"
	end := "id;" // value lexographically greater than max id
	var lastID string
	if *wrapInVar != "" {
		fmt.Printf("%s = [\n", *wrapInVar)
	}
	for _, id := range ids {
		lastID = id
		i++
		if i == *count {
			// odd format string is so that output
			// passes pylint.
			fmt.Printf("    [%q,\n     %q],\n", start, id)
			start = id
			i = 0
		}
	}
	fmt.Printf("    [%q, %q]\n", lastID, end)
	if *wrapInVar != "" {
		fmt.Printf("]\n")
	}
}

type BotInfo struct {
	Dimensions         []string  `datastore:"dimensions"`
	DimensionsFlat     []string  `datastore:"dimensions_flat"`
	Version            string    `datastore:"version"`
	LeaseID            string    `datastore:"lease_id"`
	TaskName           string    `datastore:"task_name"`
	TaskID             string    `datastore:"task_id"`
	State              []byte    `datastore:"state",json:"-"`
	LeasedIndefinitely bool      `datastore:"leased_indefinitely"`
	MachineType        string    `datastore:"machine_type"`
	ExternalIP         string    `datastore:"external_ip"`
	AuthenticatedAs    string    `datastore:"authenticated_as"`
	LastSeenTS         time.Time `datastore:"last_seen_ts"`
	Quarantined        bool      `datastore:"quarantined"`
	Composite          []int64   `datastore:"composite"`
	MaintenanceMsg     string    `datastore:"maintenance_msg"`
	LeaseExpiration    time.Time `datastore:"lease_expiration_ts"`
	MachineLease       string    `datastore:"machine_lease"`
	FirstSeenTS        time.Time `datastore:"first_seen_ts"`
	IsBusy             bool      `datastore:"is_busy"`
	ID                 string
}

func dump(ctx context.Context, client *datastore.Client) []string {
	// run query, forcing use of index
	q := datastore.NewQuery("BotInfo").Filter("dimensions_flat >", "id:")
	q = q.Filter("dimensions_flat <", "id;")
	iter := client.Run(ctx, q)
	var ids []string
	for {
		var val BotInfo
		_, err := iter.Next(&val)
		if err == iterator.Done {
			break
		}
		if err != nil {
			panic(err)
		}
		for _, dimension := range val.DimensionsFlat {
			if strings.HasPrefix(dimension, "id:") {
				ids = append(ids, dimension)
				break
			}
		}
	}
	return ids
}
