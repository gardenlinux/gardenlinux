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
	_, _ = fmt.Fprintf(os.Stderr, "Usage: %s <command> [--option]...\n", filepath.Base(os.Args[0]))
	_, _ = fmt.Fprintf(os.Stderr, "Commands: cname, expand, platform\n")
	_, _ = fmt.Fprintf(os.Stderr, "Options:\n")
	flag.PrintDefaults()
}

func parseCmdLine(args []string) (progName string, cmd string, featDir string, features []string, ignore []string) {
	progName = filepath.Base(args[0])
	flag.Usage = usage
	flag.ErrHelp = nil
	flag.CommandLine = flag.NewFlagSet(args[0], flag.ContinueOnError)

	flag.StringVar(&featDir, "feat-dir", "../features", "Directory of GardenLinux features")
	flag.StringSliceVarP(&ignore, "ignore", "i", nil, "List of feaures to ignore (comma-separated)")
	flag.StringSliceVarP(&features, "features", "f", nil, "List of feaures (comma-separated)")

	var help bool
	flag.BoolVarP(&help, "help", "h", false, "Show this help message")

	err := flag.CommandLine.Parse(args[1:])
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%s: %s\n", progName, err)
		flag.Usage()
		os.Exit(2)
	}
	if help {
		flag.Usage()
		os.Exit(2)
	}

	cmd = flag.Arg(0)
	switch cmd {
	case "cname":
	case "expand":
	case "platform":
	default:
		flag.Usage()
		os.Exit(2)
	}

	return
}

func main() {
	progName, cmd, featDir, features, ignore := parseCmdLine(os.Args)

	allFeatures, err := readFeatures(featDir)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%s: %s\n", progName, err)
		os.Exit(1)
	}

	switch cmd {

	case "cname":
		err = cnameCmd(allFeatures, features, ignore)

	case "expand":
		err = expandCmd(allFeatures, features, ignore)

	case "platform":
		err = platformCmd(allFeatures, features, ignore)

	}

	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%s: %s\n", progName, err)
		os.Exit(1)
	}
}

func expandCmd(allFeatures featureSet, features []string, ignore []string) error {
	features, err := sortFeatures(allFeatures, features, false, false)
	if err != nil {
		return fmt.Errorf("expand: %w", err)
	}

	features, err = expand(allFeatures, features, makeSet(ignore))
	if err != nil {
		return fmt.Errorf("expand: %w", err)
	}

	_, err = sortFeatures(allFeatures, features, false, true)
	if err != nil {
		return fmt.Errorf("expand: %w", err)
	}

	printStrings(features)

	return nil
}

func cnameCmd(allFeatures featureSet, features []string, ignore []string) error {
	ignored := makeSet(ignore)

	expanded, err := expand(allFeatures, features, ignored)
	if err != nil {
		return fmt.Errorf("cname: %w", err)
	}

	_, err = sortFeatures(allFeatures, expanded, false, true)
	if err != nil {
		return fmt.Errorf("cname: %w", err)
	}

	features, err = reduce(allFeatures, features, ignored)
	if err != nil {
		return fmt.Errorf("cname: %w", err)
	}

	features, err = sortFeatures(allFeatures, features, true, false)
	if err != nil {
		return fmt.Errorf("cname: %w", err)
	}

	err = printCname(allFeatures, features)
	if err != nil {
		return fmt.Errorf("cname: %w", err)
	}

	return nil
}

func platformCmd(allFeatures featureSet, features []string, ignore []string) error {
	features, err := expand(allFeatures, features, makeSet(ignore))
	if err != nil {
		return fmt.Errorf("expand: %w", err)
	}

	features, err = sortFeatures(allFeatures, features, false, true)
	if err != nil {
		return fmt.Errorf("expand: %w", err)
	}

	fmt.Println(features[0])
	return nil
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

func makeSet(items []string) set {
	s := make(set)
	for _, i := range items {
		s[i] = struct{}{}
	}
	return s
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

func sortFeatures(allFeatures featureSet, unsorted []string, strict, validatePlatform bool) ([]string, error) {
	var platforms, others, modifiers []string
	for _, f := range unsorted {
		feat, ok := allFeatures[f]
		if !ok {
			return nil, fmt.Errorf("feature %v does not exist", f)
		}

		if feat.Type == "platform" {
			if validatePlatform && len(platforms) > 0 {
				return nil, fmt.Errorf("cannot have multiple platforms: %v and %v", platforms[0], f)
			}
			platforms = append(platforms, f)
		} else if feat.Type == "modifier" {
			modifiers = append(modifiers, f)
		} else {
			others = append(others, f)
		}
	}
	if validatePlatform && len(platforms) == 0 {
		return nil, fmt.Errorf("must have a platform")
	}

	if strict {
		sort.Strings(platforms)
		sort.Strings(others)
		sort.Strings(modifiers)
	}

	sorted := make([]string, len(unsorted))
	n := copy(sorted, platforms)
	n += copy(sorted[n:], others)
	copy(sorted[n:], modifiers)

	return sorted, nil
}

func printCname(allFeatures featureSet, features []string) error {
	for i, f := range features {
		feat, ok := allFeatures[f]
		if !ok {
			return fmt.Errorf("feature %v does not exist", f)
		}

		if feat.Type != "modifier" && i > 0 {
			fmt.Print("-")
		}
		fmt.Printf("%v", f)
	}
	fmt.Println()
	return nil
}

func postorderDFS(g graph, seen set, origin string, allowVertex func(string) bool, processVertex func(string)) error {
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
		v := stack.Top().(string)

		if allowVertex != nil && !allowVertex(v) {
			stack.Pop()
			continue
		}

		hot[v] = struct{}{}
		done := true
		edges := g[v]
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
			delete(hot, v)

			if processVertex != nil {
				processVertex(v)
			}
		}
	}

	return nil
}

func expand(allFeatures featureSet, features []string, ignored set) ([]string, error) {
	gInc := buildInclusionGraph(allFeatures)
	collectedExcl := make(set)
	var expanded []string

	seen := make(set, len(gInc))
	for _, f := range features {
		err := postorderDFS(gInc, seen, f, func(v string) bool {
			_, ok := ignored[v]
			if ok {
				_, _ = fmt.Fprintf(os.Stderr, "WARNING: %v is being ignored\n", v)
			}
			return !ok
		}, func(v string) {
			expanded = append(expanded, v)

			for _, e := range allFeatures[v].Features.Exclude {
				collectedExcl[e] = struct{}{}
			}
		})
		if err != nil {
			return nil, err
		}
	}

	for _, f := range expanded {
		if _, ok := collectedExcl[f]; ok {
			return nil, fmt.Errorf("%v has been excluded by another feature", f)
		}
	}

	return expanded, nil
}

func reduce(allFeatures featureSet, features []string, ignored set) ([]string, error) {
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

		_, ok := ignored[f]
		if ok {
			continue
		}

		minimal[f] = struct{}{}

		err := postorderDFS(gInc, nil, f, func(v string) bool {
			_, ok := ignored[v]
			return !ok
		}, func(v string) {
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
			return nil, err
		}
	}

	for f := range visited {
		if _, ok := collectedExcl[f]; ok {
			return nil, fmt.Errorf("%v has been excluded by another feature", f)
		}
	}

	reduced := make([]string, 0, len(minimal))
	for f := range minimal {
		reduced = append(reduced, f)
	}

	return reduced, nil
}
