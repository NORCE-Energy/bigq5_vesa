.PHONY: all clean

SHELL:=/bin/bash
SOURCE_FILE:=setup

latex_generated_files=*.aux *.bbl *.blg *.log *.pdf *.fdb_latexmk *.fls

all:
	latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" $(SOURCE_FILE).tex

clean:
	rm -f $(latex_generated_files)
