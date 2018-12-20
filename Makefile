.PHONY: all clean docs

latex_generated_files=*.aux *.bbl *.blg *.log *.pdf *.fdb_latexmk *.fls

all:
	echo "All"

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
