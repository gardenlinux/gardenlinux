package main

import (
	"fmt"
	flag "github.com/spf13/pflag"
	"gopkg.in/alediaferia/stackgo.v1"
	"gopkg.in/yaml.v2"
	"io/ioutil"
	"os"
	"path/filepath"
	"sort"
)

func usage() {
	_, _ = fmt.Fprintf(os.Stderr, "Usage: %s [--option]... <command> ...\n", filepath.Base(os.Args[0]))
	_, _ = fmt.Fprintf(os.Stderr, "Commands: expand, reduce\n")
	_, _ = fmt.Fprintf(os.Stderr, "Option:\n")
	flag.PrintDefaults()
}

func main() {
	progName := filepath.Base(os.Args[0])
	flag.Usage = usage
	flag.ErrHelp = nil
	flag.CommandLine = flag.NewFlagSet(os.Args[0], flag.ContinueOnError)

	featDirOpt := flag.String("feat-dir", "../features", "Directory of GardenLinux features")
	helpOpt := flag.BoolP("help", "h", false, "Show this help message")

	err := flag.CommandLine.Parse(os.Args[1:])
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%s: %s\n", progName, err)
		flag.Usage()
		os.Exit(2)
	}
	if *helpOpt == true {
		flag.Usage()
		os.Exit(2)
	}

	allFeatures, err := readFeatures(*featDirOpt)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%s: %s\n", progName, err)
		os.Exit(1)
	}

	cmd := flag.Arg(0)
	switch cmd {

	case "expand":
		err = expandCmd(allFeatures, flag.Args()[1:])

	case "reduce":
		err = reduceCmd(allFeatures, flag.Args()[1:])

	default:
		flag.Usage()
		os.Exit(2)
	}

	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%s: %s\n", progName, err)
		os.Exit(1)
	}
}

type feature struct {
	Description string `yaml:"description,omitempty"`
	Type        string `yaml:"type,omitempty"`
	Features    struct {
		Include []string `yaml:"include,omitempty"`
		Exclude []string `yaml:"exclude,omitempty"`
	} `yaml:"features,omitempty"`
}
type featureSet map[string]feature

type graph map[string][]string
type set map[string]struct{}

func buildInclusionGraph(allFeatures featureSet) graph {
	incGraph := make(map[string][]string, len(allFeatures))

	for name, feat := range allFeatures {
		incGraph[name] = feat.Features.Include
	}

	return incGraph
}

func printStrings(strings []string) {
	for i, s := range strings {
		if i > 0 {
			fmt.Print(" ")
		}
		fmt.Printf("%s", s)
	}
	fmt.Println()
}

func readFeatures(featDir string) (featureSet, error) {
	entries, err := ioutil.ReadDir(featDir)
	if err != nil {
		return nil, err
	}

	allFeatures := make(featureSet)
	for _, e := range entries {
		if !e.IsDir() {
			continue
		}

		featData, err := ioutil.ReadFile(filepath.Join(featDir, e.Name(), "info.yaml"))
		if err != nil {
			return nil, err
		}

		var f feature
		err = yaml.Unmarshal(featData, &f)
		if err != nil {
			return nil, err
		}

		allFeatures[e.Name()] = f
	}

	return allFeatures, nil
}

func sortFeatures(allFeatures featureSet, unsorted []string, strict bool) ([]string, error) {
	var platform string
	var others, modifiers []string
	for _, f := range unsorted {
		feat := allFeatures[f]
		if feat.Type == "platform" {
			if platform != "" {
				return nil, fmt.Errorf("cannot have multiple platforms")
			}
			platform = f
		} else if feat.Type == "modifier" {
			modifiers = append(modifiers, f)
		} else {
			others = append(others, f)
		}
	}
	if platform == "" {
		return nil, fmt.Errorf("must have a platform")
	}

	if strict {
		sort.Strings(others)
		sort.Strings(modifiers)
	}

	sorted := make([]string, len(unsorted))
	sorted[0] = platform
	n := copy(sorted[1:], others)
	copy(sorted[n+1:], modifiers)
	return sorted, nil
}

func postorderDFS(g graph, seen set, origin string, processVertex func(string)) error {
	if _, ok := g[origin]; !ok {
		return fmt.Errorf("%v is not part of the graph", origin)
	}

	n := len(g)
	if seen == nil {
		seen = make(set, n)
	}
	if _, ok := seen[origin]; ok {
		return nil
	}

	hot := make(set, n)
	stack := stackgo.NewStack()

	seen[origin] = struct{}{}
	stack.Push(origin)

	for stack.Size() > 0 {
		vertex := stack.Top().(string)
		hot[vertex] = struct{}{}

		done := true
		edges := g[vertex]
		for i := len(edges) - 1; i >= 0; i-- {
			if _, ok := hot[edges[i]]; ok {
				return fmt.Errorf("%v is part of a loop", edges[i])
			}

			if _, ok := seen[edges[i]]; !ok {
				done = false
				seen[edges[i]] = struct{}{}
				stack.Push(edges[i])
			}
		}
		if done {
			stack.Pop()
			delete(hot, vertex)

			if processVertex != nil {
				processVertex(vertex)
			}
		}
	}

	return nil
}

func expandCmd(allFeatures featureSet, features []string) error {
	features, err := sortFeatures(allFeatures, features, false)
	if err != nil {
		return fmt.Errorf("expand: %w", err)
	}

	gInc := buildInclusionGraph(allFeatures)
	collectedExcl := make(set)
	var expanded []string

	seen := make(set, len(gInc))
	for _, f := range features {
		err = postorderDFS(gInc, seen, f, func(v string) {
			expanded = append(expanded, v)

			for _, e := range allFeatures[v].Features.Exclude {
				collectedExcl[e] = struct{}{}
			}
		})
		if err != nil {
			return fmt.Errorf("expand: %w", err)
		}
	}

	for _, f := range expanded {
		if _, ok := collectedExcl[f]; ok {
			return fmt.Errorf("expand: %v has been excluded by another feature", f)
		}
	}

	printStrings(expanded)

	return nil
}

func reduceCmd(allFeatures featureSet, features []string) error {
	features, err := sortFeatures(allFeatures, features, true)
	if err != nil {
		return fmt.Errorf("reduce: %w", err)
	}

	gInc := buildInclusionGraph(allFeatures)
	collectedExcl := make(set)
	visited := make(set)
	minimal := make(set, len(features))

	i := 0
	for i < len(features) {
		if features[i] == "" {
			i++
			continue
		}

		f := features[i]
		i++
		minimal[f] = struct{}{}

		err = postorderDFS(gInc, nil, f, func(v string) {
			if v == f {
				return
			}

			for j, h := range features[i:] {
				if h == v {
					features[i+j] = ""
				}
			}

			delete(minimal, v)

			visited[v] = struct{}{}

			for _, e := range allFeatures[v].Features.Exclude {
				collectedExcl[e] = struct{}{}
			}
		})
		if err != nil {
			return fmt.Errorf("reduce: %w", err)
		}
	}

	for f := range visited {
		if _, ok := collectedExcl[f]; ok {
			return fmt.Errorf("reduce: %v has been excluded by another feature", f)
		}
	}

	reduced := make([]string, 0, len(minimal))
	for f := range minimal {
		reduced = append(reduced, f)
	}
	reduced, err = sortFeatures(allFeatures, reduced, true)
	if err != nil {
		return fmt.Errorf("reduce: %w", err)
	}

	printStrings(reduced)

	return nil
}
