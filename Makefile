.PHONY: build fmt check-fmt lint lint-fix codespell

DESTDIR ?=

ALL_SRC_FILES = 'find . -name "*.[ch]" ! -path "./src/libhirte/ini/ini.[ch]" ! -path "./src/libhirte/hashmap/*" ! -path "./src/*/test/**" ! -path "./builddir/**" -print0'

CODESPELL_PARAMS=\
	-S Makefile,imgtype,copy,AUTHORS,bin,.git,CHANGELOG.md,changelog.txt,.cirrus.yml,"*.xz,*.gz,*.tar,*.tgz,*ico,*.png,*.1,*.5,*.orig,*.rej,*.xml,*xsl" \
	-L keypair,flate,uint,iff,od,ERRO

build:
	meson setup builddir
	meson compile -C builddir

test: build
	meson test -C builddir

test-with-valgrind: build
	meson test --wrap='valgrind --leak-check=full --error-exitcode=1' -C builddir

install: build
	meson install -C builddir --destdir "$(DESTDIR)"

fmt:
	eval $(ALL_SRC_FILES) | xargs -0 -I {} clang-format -i --sort-includes {}

check-fmt:
	eval $(ALL_SRC_FILES) | xargs -0 -I {} clang-format  --dry-run -Werror {}

lint-c: build
	# Header config.h is autogenerated during the build, so it needs to be added manually here as a parameter
	eval $(ALL_SRC_FILES) | xargs -0 -I {} clang-tidy --quiet {} -- -I src -I builddir -include config.h

lint-markdown:
	markdownlint-cli2 | echo "markdownlint-cli2 not found, skipping markdown lint"

lint: lint-c lint-markdown

lint-fix:
	eval $(ALL_SRC_FILES) | xargs -0 -I {} clang-tidy --quiet {} --fix -- -I src -I builddir -include config.h

codespell:
	codespell  $(CODESPELL_PARAMS) -w

check-codespell:
	codespell  $(CODESPELL_PARAMS)

clean:
	find . -name \*~ -delete
	find . -name \*# -delete
	meson setup --wipe builddir

distclean: clean
	rm -rf builddir
