test: face.mdl lex.py main.py matrix.py mdl.py display.py draw.py gmath.py yacc.py
	python main.py simple_anim.mdl

clean:
	rm -rf __pycache__/ *out parsetab.py
	rm anim/*.p*

clear:
	rm *pyc *out parsetab.py *ppm

main: face.mdl giffer.mdl lex.py main.py matrix.py mdl.py display.py draw.py gmath.py yacc.py
	python main.py giffer.mdl
