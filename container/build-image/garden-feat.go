package main

import (
	"fmt"
	"github.com/geofffranks/simpleyaml"
	"github.com/geofffranks/spruce"
	flag "github.com/spf13/pflag"
	"gopkg.in/alediaferia/stackgo.v1"
	"gopkg.in/yaml.v2"
	"io/ioutil"
	"os"
	"path/filepath"
	"sort"
	"strconv"
)

func usage() {
	_, _ = fmt.Fprintf(os.Stderr, "Usage: %s <command> [--option]... arg...\n", filepath.Base(os.Args[0]))
	_, _ = fmt.Fprintf(os.Stderr, "Commands:\n" +
		" cname - effective minimum of features equivalent to specified features (ordered)\n" +
		" features - effective maximum of all features (each feature used, no duplicates, ordered)\n\n" +
		" platform - platforms in the featureset\n" +
		" flags - flags in the featureset\n" +
		" elements - all elements of the featureset (including platform because of possible execution order)\n\n" +
		" ignore - ignored elements (no duplicates)\n" +
		" params - debugging output\n\n")
	_, _ = fmt.Fprintf(os.Stderr, "Options:\n")
	flag.PrintDefaults()
}

func parseCmdLine(argv []string) (progName string, cmd string, featDir string, features []string, ignore []string, args []string) {
	progName = filepath.Base(argv[0])
	flag.Usage = usage
	flag.ErrHelp = nil
	flag.CommandLine = flag.NewFlagSet(argv[0], flag.ContinueOnError)

	flag.StringVarP(&featDir, "featureDir", "d", "../features", "Directory of GardenLinux features")
	flag.StringSliceVarP(&ignore, "ignore", "i", nil, "List of feaures to ignore (comma-separated)")
	flag.StringSliceVarP(&features, "features", "f", nil, "List of feaures (comma-separated)")

	var help bool
	flag.BoolVarP(&help, "help", "h", false, "Show this help message")
	// multiplatform support?
	// list elements and flags

	err := flag.CommandLine.Parse(argv[1:])
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
	case "elements":
	case "features":
	case "flags":
	case "ignore":
	case "params":
	case "platform":
	default:
		flag.Usage()
		os.Exit(2)
	}
	args = flag.Args()[1:]

	return
}

func main() {
	progName, cmd, featDir, features, ignore, args := parseCmdLine(os.Args)

	allFeatures, err := readFeatures(featDir, "platform", "element", "flag")
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%s: %s\n", progName, err)
		os.Exit(1)
	}

	switch cmd {

	case "cname":
		err = cnameCmd(allFeatures, features, ignore, args)

	case "elements":
		err = elementsCmd(allFeatures, features, ignore, args)

	case "features":
		err = featuresCmd(allFeatures, features, ignore, args)

	case "flags":
		err = flagsCmd(allFeatures, features, ignore, args)

	case "ignore":
		err = ignoreCmd(allFeatures, features, ignore, args)

	case "params":
		err = paramsCmd(allFeatures, features, ignore, args)

	case "platform":
		err = platformCmd(allFeatures, features, ignore, args)
	}

	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%s: %s\n", progName, err)
		os.Exit(1)
	}
}

func cnameCmd(allFeatures featureSet, features []string, ignore []string, _ []string) error {
	ignored := makeSet(ignore)

	expanded, _, err := expandFeatures(allFeatures, features, ignored)
	if err != nil {
		return fmt.Errorf("cname: %w", err)
	}

	_, err = sortFeatures(allFeatures, expanded, false, true)
	if err != nil {
		return fmt.Errorf("cname: %w", err)
	}

	features, err = reduceFeatures(allFeatures, features, ignored)
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

func elementsCmd(allFeatures featureSet, features []string, ignore []string, _ []string) error {
	features, err := sortFeatures(allFeatures, features, false, false)
	if err != nil {
		return fmt.Errorf("elements: %w", err)
	}

	features, _, err = expandFeatures(allFeatures, features, makeSet(ignore))
	if err != nil {
		return fmt.Errorf("elements: %w", err)
	}

	_, err = sortFeatures(allFeatures, features, false, true)
	if err != nil {
		return fmt.Errorf("elements: %w", err)
	}

	elements, err := filterByType(allFeatures, features, "platform", "element")
	if err != nil {
		return fmt.Errorf("elements: %w", err)
	}

	err = printStrings(elements...)
	if err != nil {
		return fmt.Errorf("elements: %w", err)
	}

	return nil
}

func featuresCmd(allFeatures featureSet, features []string, ignore []string, _ []string) error {
	features, err := sortFeatures(allFeatures, features, false, false)
	if err != nil {
		return fmt.Errorf("features: %w", err)
	}

	features, _, err = expandFeatures(allFeatures, features, makeSet(ignore))
	if err != nil {
		return fmt.Errorf("features: %w", err)
	}

	_, err = sortFeatures(allFeatures, features, false, true)
	if err != nil {
		return fmt.Errorf("features: %w", err)
	}

	err = printStrings(features...)
	if err != nil {
		return fmt.Errorf("features: %w", err)
	}

	return nil
}

func flagsCmd(allFeatures featureSet, features []string, ignore []string, _ []string) error {
	features, err := sortFeatures(allFeatures, features, false, false)
	if err != nil {
		return fmt.Errorf("flags: %w", err)
	}

	features, _, err = expandFeatures(allFeatures, features, makeSet(ignore))
	if err != nil {
		return fmt.Errorf("flags: %w", err)
	}

	_, err = sortFeatures(allFeatures, features, false, true)
	if err != nil {
		return fmt.Errorf("flags: %w", err)
	}

	flags, err := filterByType(allFeatures, features, "flag")
	if err != nil {
		return fmt.Errorf("flags: %w", err)
	}

	err = printStrings(flags...)
	if err != nil {
		return fmt.Errorf("elements: %w", err)
	}

	return nil
}

func ignoreCmd(allFeatures featureSet, features []string, ignore []string, _ []string) error {
	features, ignoredSet, err := expandFeatures(allFeatures, features, makeSet(ignore))
	if err != nil {
		return fmt.Errorf("ignore: %w", err)
	}

	_, err = sortFeatures(allFeatures, features, false, true)
	if err != nil {
		return fmt.Errorf("ignore: %w", err)
	}

	ignored := make([]string, 0, len(ignoredSet))
	for f := range ignoredSet {
		ignored = append(ignored, f)
	}
	sort.Strings(ignored)

	err = printStrings(ignored...)
	if err != nil {
		return fmt.Errorf("ignore: %w", err)
	}

	return nil
}

func paramsCmd(allFeatures featureSet, features []string, ignore []string, args []string) error {
	features, err := sortFeatures(allFeatures, features, false, false)
	if err != nil {
		return fmt.Errorf("params: %w", err)
	}

	features, _, err = expandFeatures(allFeatures, features, makeSet(ignore))
	if err != nil {
		return fmt.Errorf("params: %w", err)
	}

	_, err = sortFeatures(allFeatures, features, false, true)
	if err != nil {
		return fmt.Errorf("params: %w", err)
	}

	yamls := make([]map[interface{}]interface{}, 0, len(features))
	for _, f := range features {
		yamls = append(yamls, allFeatures[f].yaml)
	}

	mergedYAML, err := spruce.Merge(yamls...)
	if err != nil {
		return fmt.Errorf("params: %w", err)
	}

	e := &spruce.Evaluator{Tree: mergedYAML}
	err = e.Run([]string{"description", "type", "features"}, args)
	if err != nil {
		return fmt.Errorf("params: %w", err)
	}
	mergedYAML = e.Tree

	err = printShellVars(mergedYAML)
	if err != nil {
		return fmt.Errorf("params: %w", err)
	}

	return nil
}

func platformCmd(allFeatures featureSet, features []string, ignore []string, _ []string) error {
	features, _, err := expandFeatures(allFeatures, features, makeSet(ignore))
	if err != nil {
		return fmt.Errorf("platform: %w", err)
	}

	features, err = sortFeatures(allFeatures, features, false, true)
	if err != nil {
		return fmt.Errorf("platform: %w", err)
	}

	err = printStrings(features[0])
	if err != nil {
		return fmt.Errorf("platform: %w", err)
	}

	return nil
}

type feature struct {
	Description string `yaml:"description,omitempty"`
	Type        string `yaml:"type,omitempty"`
	Features    struct {
		Include []string `yaml:"include,omitempty"`
		Exclude []string `yaml:"exclude,omitempty"`
	} `yaml:"features,omitempty"`
	yaml map[interface{}]interface{}
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

func readFeatures(featDir string, types ...string) (featureSet, error) {
	entries, err := ioutil.ReadDir(featDir)
	if err != nil {
		return nil, err
	}

	allFeatures := make(featureSet)
	for _, e := range entries {
		var featFile, featName string
		if e.IsDir() {
			featName = e.Name()
			featFile = filepath.Join(featDir, featName, "info.yaml")
			if _, err = os.Stat(featFile); os.IsNotExist(err) {
				continue
			}
		} else if filepath.Ext(e.Name()) == ".yaml" {
			featName = e.Name()[:len(e.Name())-5]
			featFile = e.Name()
		} else {
			continue
		}

		featData, err := ioutil.ReadFile(featFile)
		if err != nil {
			return nil, err
		}

		var f feature
		err = yaml.Unmarshal(featData, &f)
		if err != nil {
			return nil, err
		}

		accept := false
		for _, t := range types {
			if f.Type == t {
				accept = true
			}
		}
		if !accept {
			return nil, fmt.Errorf("feature %s has unsupported type %s", featName, f.Type)
		}

		y, err := simpleyaml.NewYaml(featData)
		if err != nil {
			return nil, err
		}
		f.yaml, err = y.Map()
		if err != nil {
			return nil, err
		}

		allFeatures[featName] = f
	}

	return allFeatures, nil
}

func sortFeatures(allFeatures featureSet, unsorted []string, strict, validatePlatform bool) ([]string, error) {
	var platforms, others, flags []string
	for _, f := range unsorted {
		feat, ok := allFeatures[f]
		if !ok {
			return nil, fmt.Errorf("feature %s does not exist", f)
		}

		if feat.Type == "platform" {
			if validatePlatform && len(platforms) > 0 {
				return nil, fmt.Errorf("cannot have multiple platforms: %s and %s", platforms[0], f)
			}
			platforms = append(platforms, f)
		} else if feat.Type == "flag" {
			flags = append(flags, f)
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
		sort.Strings(flags)
	}

	sorted := make([]string, len(unsorted))
	n := copy(sorted, platforms)
	n += copy(sorted[n:], others)
	copy(sorted[n:], flags)

	return sorted, nil
}

func filterByType(allFeatures featureSet, features []string, types ...string) ([]string, error) {
	var matching []string

	for _, f := range features {
		feat, ok := allFeatures[f]
		if !ok {
			return nil, fmt.Errorf("feature %s does not exist", f)
		}

		for _, t := range types {
			if feat.Type == t {
				matching = append(matching, f)
			}
		}
	}

	return matching, nil
}

func printStrings(strings ...string) error {
	for i, s := range strings {
		if i > 0 {
			_, err := fmt.Print(",")
			if err != nil {
				return err
			}
		}
		_, err := fmt.Printf("%s", s)
		if err != nil {
			return err
		}
	}
	_, err := fmt.Println()
	if err != nil {
		return err
	}
	return nil
}

func printCname(allFeatures featureSet, features []string) error {
	for i, f := range features {
		feat, ok := allFeatures[f]
		if !ok {
			return fmt.Errorf("feature %s does not exist", f)
		}

		if feat.Type != "flag" && i > 0 {
			_, err := fmt.Print("-")
			if err != nil {
				return err
			}
		}
		_, err := fmt.Printf("%s", f)
		if err != nil {
			return err
		}
	}
	_, err := fmt.Println()
	if err != nil {
		return err
	}
	return nil
}

func printShellVars(root map[interface{}]interface{}) error {
	type prefixNode struct {
		prefix string
		node   interface{}
	}

	stack := stackgo.NewStack()

	stack.Push(prefixNode{"", root})

	for stack.Size() > 0 {
		pn := stack.Pop().(prefixNode)

		switch pn.node.(type) {

		case bool, int, string:
			_, err := fmt.Printf("%s='%v'\n", pn.prefix, pn.node)
			if err != nil {
				return err
			}

		case []interface{}:
			a := pn.node.([]interface{})

			onlyScalars := true
			for _, val := range a {
				switch val.(type) {
				case bool, int, string:
				default:
					onlyScalars = false
				}
			}
			if onlyScalars {
				_, err := fmt.Printf("%s=(", pn.prefix)
				if err != nil {
					return err
				}
				for _, val := range a {
					_, err = fmt.Printf(" '%v'", val)
					if err != nil {
						return err
					}
				}
				_, err = fmt.Println(" )")
				if err != nil {
					return err
				}
				continue
			}

			_, err := fmt.Printf("%s=(", pn.prefix)
			if err != nil {
				return err
			}
			prefixNodes := make([]prefixNode, 0, len(a))
			for i, val := range a {
				prefix := strconv.Itoa(i)
				if m, ok := val.(map[interface{}]interface{}); ok {
					if nameVal, k := m["name"]; k {
						switch nameVal.(type) {
						case bool, int, string:
							prefix = fmt.Sprintf("%v", nameVal)
						}
					}
				}
				if pn.prefix != "" {
					prefix = pn.prefix + "_" + prefix
				}
				_, err = fmt.Printf(" '%s'", prefix)
				if err != nil {
					return err
				}
				prefixNodes = append(prefixNodes, prefixNode{prefix, val})
			}
			_, err = fmt.Println(" )")
			if err != nil {
				return err
			}

			for i := len(prefixNodes) - 1; i >= 0; i-- {
				stack.Push(prefixNodes[i])
			}

		case map[interface{}]interface{}:
			m := pn.node.(map[interface{}]interface{})

			headerPrefix := pn.prefix
			if pn.prefix == "" {
				headerPrefix = "_"
			}
			_, err := fmt.Printf("%s=(", headerPrefix)
			if err != nil {
				return err
			}
			prefixNodes := make([]prefixNode, 0, len(m))
			for key, val := range m {
				prefix := key.(string)
				if pn.prefix != "" {
					prefix = pn.prefix + "_" + prefix
				}
				_, err = fmt.Printf(" '%s'", prefix)
				if err != nil {
					return err
				}
				prefixNodes = append(prefixNodes, prefixNode{prefix, val})
			}
			_, err = fmt.Println(" )")
			if err != nil {
				return err
			}

			for i := len(prefixNodes) - 1; i >= 0; i-- {
				stack.Push(prefixNodes[i])
			}

		}
	}

	return nil
}

func postorderDFS(g graph, seen set, origin string, allowVertex func(string) bool, processVertex func(string)) error {
	if _, ok := g[origin]; !ok {
		return fmt.Errorf("%s is not part of the graph", origin)
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
				return fmt.Errorf("%s is part of a loop", edges[i])
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

func expandFeatures(allFeatures featureSet, features []string, ignored set) ([]string, set, error) {
	gInc := buildInclusionGraph(allFeatures)
	collectedIgn := make(set)
	collectedExcl := make(set)
	var expanded []string

	seen := make(set, len(gInc))
	for _, f := range features {
		err := postorderDFS(gInc, seen, f, func(v string) bool {
			_, ok := ignored[v]
			if ok {
				collectedIgn[v] = struct{}{}
				_, _ = fmt.Fprintf(os.Stderr, "WARNING: %s is being ignored\n", v)
			}
			return !ok
		}, func(v string) {
			expanded = append(expanded, v)

			for _, e := range allFeatures[v].Features.Exclude {
				collectedExcl[e] = struct{}{}
			}
		})
		if err != nil {
			return nil, nil, err
		}
	}

	for _, f := range expanded {
		if _, ok := collectedExcl[f]; ok {
			return nil, nil, fmt.Errorf("%s has been excluded by another feature", f)
		}
	}

	return expanded, collectedIgn, nil
}

func reduceFeatures(allFeatures featureSet, features []string, ignored set) ([]string, error) {
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
			return nil, fmt.Errorf("%s has been excluded by another feature", f)
		}
	}

	reduced := make([]string, 0, len(minimal))
	for f := range minimal {
		reduced = append(reduced, f)
	}

	return reduced, nil
}
