# Convenience wrapper for Linux and macOS.
#
#   make -C assets          build every out-of-date asset
#   make -C assets tikz     the 11 diagrams only
#   make -C assets manim    the 10 clips only
#   make -C assets force    rebuild everything
#   make -C assets check    sizes and durations against the asset spec
#   make -C assets clean    remove build intermediates (not rendered/)
#
# The build itself lives in tools/build_assets.py, which is the single
# implementation and works on Windows too. This file only forwards to it,
# so `make` stays available for muscle memory without the build logic
# existing in two places that can drift apart.
#
# On Windows use tools/build.ps1 (or call the Python script directly).

PY := python
BUILD := ../tools/build_assets.py

.PHONY: all tikz manim force check clean list
all:
	$(PY) $(BUILD)

tikz:
	$(PY) $(BUILD) --tikz

manim:
	$(PY) $(BUILD) --manim

force:
	$(PY) $(BUILD) --force

list:
	$(PY) $(BUILD) --list

check:
	$(PY) ../tools/check_assets.py

clean:
	$(PY) $(BUILD) --clean
