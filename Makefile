# NAME: Ricardo Kuchimpos,Jesse Catalan
# EMAIL: rkuchimpos@gmail.com,jessecatalan77@gmail.com
# ID: 704827423,204785152

lab3b: lab3b.py
	ln -s lab3b.py lab3b

.PHONY: clean
clean:
	rm -rf lab3b
	rm -rf lab3b-704827423.tar.gz

.PHONY: dist
dist:
	tar czf lab3b-704827423.tar.gz lab3b.py Makefile README
