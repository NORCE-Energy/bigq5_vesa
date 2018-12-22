.PHONY: all clean docs

SHELL:=/bin/bash
INPUT_PARAMS_FILE:=input_params.json

latex_generated_files=*.aux *.bbl *.blg *.log *.pdf *.fdb_latexmk *.fls

all:
	@if [[ ! -e python/$(INPUT_PARAMS_FILE) ]] ; then \
	   echo "Installing python/$(INPUT_PARAMS_FILE)" ;\
	   cp templates/$(INPUT_PARAMS_FILE) python/ ;\
	else\
	   echo "File python/$(INPUT_PARAMS_FILE) already exists. Will not overwrite." ;\
	fi

docs:
	cd latex/main; latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" main.tex
	cd latex/setup; latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" setup.tex
	cd latex/variogram; \
	  latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" variogram.tex
	cd latex/cholesky; \
	  latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" cholesky.tex
	mkdir -p docs
	mv latex/main/main.pdf docs
	mv latex/setup/setup.pdf docs
	mv latex/variogram/variogram.pdf docs
	mv latex/cholesky/cholesky.pdf docs

clean:
	cd latex/main; rm -f $(latex_generated_files)
	cd latex/setup; rm -f $(latex_generated_files)
	cd latex/variogram; rm -f $(latex_generated_files)
	cd latex/cholesky; rm -f $(latex_generated_files)
