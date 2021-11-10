# Documentation Guide

The ```docs/``` folder contains (technical) documentation for garden linux.


## Folder Structure

**NOTE** You may want to create a new subfolder in ```docs/```
depending on the documentation you are writing.
If you create a new subfolder in ```docs/```, please also add
a short subchapter with a description of the added subfolder below.


### docs/.media
You are encouraged to use diagrams when suitable.
Place your diagram sources in the ```docs/.media``` folder.

### docs/deployment

All markdown files in the subfolder ```docs/deployment``` describes
how to deploy garden linux. Each describes a different platform.



## Creating Diagrams

Preferable use a diagram tool that allows to import/export
diagram source files as text.

* [Mermaid Diagrams](https://mermaid-js.github.io/mermaid/#/)


## Publishing to gardenlinux.io

All markdown files in the ```docs/``` folder are published on the
[gardenlinux.io/documentation](gardenlinux.io/documentation) website.


Check out the [Makefile](https://github.com/gardenlinux/website/blob/master/Makefile)
of the gardenlinux/website for the publishing process.


