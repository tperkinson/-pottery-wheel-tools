OPENSCAD ?= openscad
PYTHON ?= python3
PYTHON_B123D ?= $(shell command -v python3.13 >/dev/null 2>&1 && echo python3.13 || echo $(PYTHON))
BUILD_DIR ?= build
CHECK_DIR ?= $(BUILD_DIR)/check

CORE_SWEEP_SCAD := core_mount_system/c_clamp/v1/c_clamp_sweep_reference_v1.scad
PHONE_SCAD := attachments/phone_mount/v1/phone_mount_v1.scad
TRAY_SCAD := attachments/sponge_tray/v1/sponge_tray_v1.scad
CUP_HOLDER_SCAD := attachments/costco_cup_holder/v1/costco_cup_holder_v1.scad
THROWING_WATER_HOLDER_SCAD := attachments/throwing_water_holder/v2/throwing_water_holder_v2.scad
THROWING_TOWEL_HOLDER_SCAD := attachments/throwing_towel_holder/v2/throwing_towel_holder_v2.scad
RADIAL_TOOL_HOLDER_SCAD := attachments/radial_tool_holder/v1/radial_tool_holder_v1.scad
TOOL_SHELF_SCAD := attachments/tool_shelf/v1/tool_shelf_v1.scad
STAMP_TLP_SCAD := attachments/pottery_stamp/v8/pottery_stamp_tlp_v8.scad
STAMP_TLP_B123D_PY := cad/build123d/attachments/pottery_stamp/v8/pottery_stamp_tlp_v8.py
THROWING_WATER_HOLDER_B123D_PY := cad/build123d/attachments/throwing_water_holder/v3/throwing_water_holder_v3.py
TOOL_SHELF_B123D_PY := cad/build123d/attachments/tool_shelf/v2/tool_shelf_v2.py
CUP_HOLDER_B123D_PY := cad/build123d/attachments/costco_cup_holder/v1/costco_cup_holder_v1.py
CHECK_SCADS := $(CORE_SWEEP_SCAD) $(PHONE_SCAD) $(TRAY_SCAD) $(CUP_HOLDER_SCAD) $(THROWING_WATER_HOLDER_SCAD) $(THROWING_TOWEL_HOLDER_SCAD) $(RADIAL_TOOL_HOLDER_SCAD) $(TOOL_SHELF_SCAD) $(STAMP_TLP_SCAD)

CORE_SWEEP_STL := $(BUILD_DIR)/c_clamp_sweep_reference_v1.stl
PHONE_STL := $(BUILD_DIR)/phone_mount_v1.stl
PHONE_SAMPLE_STL := $(BUILD_DIR)/phone_mount_v1_holder_sample.stl
TRAY_STL := $(BUILD_DIR)/sponge_tray_v1.stl
CUP_HOLDER_STL := $(BUILD_DIR)/costco_cup_holder_v1.stl
CUP_HOLDER_SAMPLE_STL := $(BUILD_DIR)/costco_cup_holder_v1_holder_sample.stl
THROWING_WATER_HOLDER_STL := $(BUILD_DIR)/throwing_water_holder_v2.stl
THROWING_WATER_HOLDER_SAMPLE_STL := $(BUILD_DIR)/throwing_water_holder_v2_holder_sample.stl
THROWING_TOWEL_HOLDER_STL := $(BUILD_DIR)/throwing_towel_holder_v2.stl
THROWING_TOWEL_HOLDER_SAMPLE_STL := $(BUILD_DIR)/throwing_towel_holder_v2_holder_sample.stl
RADIAL_TOOL_HOLDER_STL := $(BUILD_DIR)/radial_tool_holder_v1.stl
RADIAL_TOOL_HOLDER_SAMPLE_STL := $(BUILD_DIR)/radial_tool_holder_v1_holder_sample.stl
TOOL_SHELF_STL := $(BUILD_DIR)/tool_shelf_v1.stl
TOOL_SHELF_SAMPLE_STL := $(BUILD_DIR)/tool_shelf_v1_holder_sample.stl
STAMP_TLP_STL := $(BUILD_DIR)/pottery_stamp_tlp_v8.stl
STAMP_TLP_B123D_STL := $(BUILD_DIR)/pottery_stamp_tlp_v8_b123d.stl
THROWING_WATER_HOLDER_B123D_STL := $(BUILD_DIR)/throwing_water_holder_v3_b123d.stl
THROWING_WATER_HOLDER_B123D_HOLDER_ONLY_STL := $(BUILD_DIR)/throwing_water_holder_v3_b123d_holder_only.stl
TOOL_SHELF_B123D_STL := $(BUILD_DIR)/tool_shelf_v2_b123d.stl
TOOL_SHELF_B123D_HOLDER_ONLY_STL := $(BUILD_DIR)/tool_shelf_v2_b123d_holder_only.stl
CUP_HOLDER_B123D_STL := $(BUILD_DIR)/costco_cup_holder_v1_b123d.stl
CUP_HOLDER_B123D_HOLDER_ONLY_STL := $(BUILD_DIR)/costco_cup_holder_v1_b123d_holder_only.stl

.PHONY: help all core attachments stamps stamps_b123d stamp_tlp_b123d throwing_water_holder_b123d throwing_water_holder_b123d_holder_only tool_shelf_b123d tool_shelf_b123d_holder_only cup_holder_b123d cup_holder_b123d_holder_only phone tray cup_holder throwing_water_holder throwing_towel_holder radial_tool_holder tool_shelf check clean

help:
	@echo "Targets:"
	@echo "  make all            Export all primary STLs to $(BUILD_DIR)/"
	@echo "  make core           Export core mount STL(s)"
	@echo "  make attachments    Export phone + tray + cup holder + throwing water holder + radial tool holder STLs"
	@echo "  make stamps         Export stamp STL(s) from SCAD"
	@echo "  make stamps_b123d   Export stamp STL(s) from build123d"
	@echo "  make stamp_tlp_b123d Export pottery stamp TLP v8 STL from build123d"
	@echo "  make throwing_water_holder_b123d Export throwing water holder v3 STL from build123d"
	@echo "  make throwing_water_holder_b123d_holder_only Export holder-only v3 STL from build123d"
	@echo "  make tool_shelf_b123d Export tool shelf v2 STL from build123d"
	@echo "  make tool_shelf_b123d_holder_only Export holder-only tool shelf v2 STL from build123d"
	@echo "  make cup_holder_b123d Export Costco cup holder v1 STL from build123d"
	@echo "  make cup_holder_b123d_holder_only Export holder-only Costco cup holder v1 STL from build123d"
	@echo "                     (Override build123d interpreter with PYTHON_B123D=...)"
	@echo "  make phone          Export phone mount STL + holder-only sample STL"
	@echo "  make tray           Export sponge tray STL"
	@echo "  make cup_holder     Export Costco cup holder STL + holder-only sample STL"
	@echo "  make throwing_water_holder Export throwing water holder STL + holder-only sample STL"
	@echo "  make throwing_towel_holder Export throwing towel holder STL + holder-only sample STL"
	@echo "  make radial_tool_holder Export radial tool holder STL + holder-only sample STL"
	@echo "  make tool_shelf     Export tool shelf STL + holder-only sample STL"
	@echo "  make check          Fast compile checks (CSG) for key SCAD files"
	@echo "  make clean          Remove generated build directory"

all: core attachments stamps

core: $(CORE_SWEEP_STL)

attachments: phone tray cup_holder throwing_water_holder throwing_towel_holder radial_tool_holder tool_shelf

stamps: $(STAMP_TLP_STL)

stamps_b123d: $(STAMP_TLP_B123D_STL)

stamp_tlp_b123d: $(STAMP_TLP_B123D_STL)

throwing_water_holder_b123d: $(THROWING_WATER_HOLDER_B123D_STL)

throwing_water_holder_b123d_holder_only: $(THROWING_WATER_HOLDER_B123D_HOLDER_ONLY_STL)

tool_shelf_b123d: $(TOOL_SHELF_B123D_STL)

tool_shelf_b123d_holder_only: $(TOOL_SHELF_B123D_HOLDER_ONLY_STL)

cup_holder_b123d: $(CUP_HOLDER_B123D_STL)

cup_holder_b123d_holder_only: $(CUP_HOLDER_B123D_HOLDER_ONLY_STL)

phone: $(PHONE_STL) $(PHONE_SAMPLE_STL)

tray: $(TRAY_STL)

cup_holder: $(CUP_HOLDER_STL) $(CUP_HOLDER_SAMPLE_STL)

throwing_water_holder: $(THROWING_WATER_HOLDER_STL) $(THROWING_WATER_HOLDER_SAMPLE_STL)

throwing_towel_holder: $(THROWING_TOWEL_HOLDER_STL) $(THROWING_TOWEL_HOLDER_SAMPLE_STL)

radial_tool_holder: $(RADIAL_TOOL_HOLDER_STL) $(RADIAL_TOOL_HOLDER_SAMPLE_STL)

tool_shelf: $(TOOL_SHELF_STL) $(TOOL_SHELF_SAMPLE_STL)

check: | $(CHECK_DIR)
	@set -e; \
	for f in $(CHECK_SCADS); do \
		out="$(CHECK_DIR)/$$(basename "$${f%.scad}").stl"; \
		echo "CHECK $$f"; \
		$(OPENSCAD) -D '$$fn=24' -o "$$out" "$$f"; \
	done; \
	echo "CHECK attachments/phone_mount/v1/phone_mount_v1.scad (holder-only mode)"; \
	$(OPENSCAD) -D '$$fn=24' -D render_holder_only=true -o "$(CHECK_DIR)/phone_mount_v1_holder_sample.stl" "$(PHONE_SCAD)"; \
	echo "CHECK attachments/costco_cup_holder/v1/costco_cup_holder_v1.scad (holder-only mode)"; \
	$(OPENSCAD) -D '$$fn=24' -D render_holder_only=true -o "$(CHECK_DIR)/costco_cup_holder_v1_holder_sample.stl" "$(CUP_HOLDER_SCAD)"; \
	echo "CHECK attachments/throwing_water_holder/v2/throwing_water_holder_v2.scad (holder-only mode)"; \
	$(OPENSCAD) -D '$$fn=24' -D render_holder_only=true -o "$(CHECK_DIR)/throwing_water_holder_v2_holder_sample.stl" "$(THROWING_WATER_HOLDER_SCAD)"; \
	echo "CHECK attachments/throwing_towel_holder/v2/throwing_towel_holder_v2.scad (holder-only mode)"; \
	$(OPENSCAD) -D '$$fn=24' -D render_holder_only=true -o "$(CHECK_DIR)/throwing_towel_holder_v2_holder_sample.stl" "$(THROWING_TOWEL_HOLDER_SCAD)"; \
	echo "CHECK attachments/radial_tool_holder/v1/radial_tool_holder_v1.scad (holder-only mode)"; \
	$(OPENSCAD) -D '$$fn=24' -D render_holder_only=true -o "$(CHECK_DIR)/radial_tool_holder_v1_holder_sample.stl" "$(RADIAL_TOOL_HOLDER_SCAD)"; \
	echo "CHECK attachments/tool_shelf/v1/tool_shelf_v1.scad (holder-only mode)"; \
	$(OPENSCAD) -D '$$fn=24' -D render_holder_only=true -o "$(CHECK_DIR)/tool_shelf_v1_holder_sample.stl" "$(TOOL_SHELF_SCAD)"; \
	echo "All checks passed."

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(CHECK_DIR):
	@mkdir -p $(CHECK_DIR)

$(CORE_SWEEP_STL): $(CORE_SWEEP_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -o $@ $<

$(PHONE_STL): $(PHONE_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -o $@ $<

$(PHONE_SAMPLE_STL): $(PHONE_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -D render_holder_only=true -o $@ $<

$(TRAY_STL): $(TRAY_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -o $@ $<

$(CUP_HOLDER_STL): $(CUP_HOLDER_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -o $@ $<

$(CUP_HOLDER_SAMPLE_STL): $(CUP_HOLDER_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -D render_holder_only=true -o $@ $<

$(THROWING_WATER_HOLDER_STL): $(THROWING_WATER_HOLDER_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -o $@ $<

$(THROWING_WATER_HOLDER_SAMPLE_STL): $(THROWING_WATER_HOLDER_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -D render_holder_only=true -o $@ $<

$(THROWING_TOWEL_HOLDER_STL): $(THROWING_TOWEL_HOLDER_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -o $@ $<

$(THROWING_TOWEL_HOLDER_SAMPLE_STL): $(THROWING_TOWEL_HOLDER_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -D render_holder_only=true -o $@ $<

$(RADIAL_TOOL_HOLDER_STL): $(RADIAL_TOOL_HOLDER_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -o $@ $<

$(RADIAL_TOOL_HOLDER_SAMPLE_STL): $(RADIAL_TOOL_HOLDER_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -D render_holder_only=true -o $@ $<

$(TOOL_SHELF_STL): $(TOOL_SHELF_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -o $@ $<

$(TOOL_SHELF_SAMPLE_STL): $(TOOL_SHELF_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -D render_holder_only=true -o $@ $<

$(STAMP_TLP_STL): $(STAMP_TLP_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -o $@ $<

$(STAMP_TLP_B123D_STL): $(STAMP_TLP_B123D_PY) | $(BUILD_DIR)
	XDG_CACHE_HOME=$(CURDIR)/.cache $(PYTHON_B123D) $(STAMP_TLP_B123D_PY) --output $@

$(THROWING_WATER_HOLDER_B123D_STL): $(THROWING_WATER_HOLDER_B123D_PY) | $(BUILD_DIR)
	XDG_CACHE_HOME=$(CURDIR)/.cache $(PYTHON_B123D) $(THROWING_WATER_HOLDER_B123D_PY) --export --output $@

$(THROWING_WATER_HOLDER_B123D_HOLDER_ONLY_STL): $(THROWING_WATER_HOLDER_B123D_PY) | $(BUILD_DIR)
	XDG_CACHE_HOME=$(CURDIR)/.cache $(PYTHON_B123D) $(THROWING_WATER_HOLDER_B123D_PY) --holder-only --export --output $@

$(TOOL_SHELF_B123D_STL): $(TOOL_SHELF_B123D_PY) | $(BUILD_DIR)
	XDG_CACHE_HOME=$(CURDIR)/.cache $(PYTHON_B123D) $(TOOL_SHELF_B123D_PY) --export --output $@

$(TOOL_SHELF_B123D_HOLDER_ONLY_STL): $(TOOL_SHELF_B123D_PY) | $(BUILD_DIR)
	XDG_CACHE_HOME=$(CURDIR)/.cache $(PYTHON_B123D) $(TOOL_SHELF_B123D_PY) --holder-only --export --output $@

$(CUP_HOLDER_B123D_STL): $(CUP_HOLDER_B123D_PY) | $(BUILD_DIR)
	XDG_CACHE_HOME=$(CURDIR)/.cache $(PYTHON_B123D) $(CUP_HOLDER_B123D_PY) --export --output $@

$(CUP_HOLDER_B123D_HOLDER_ONLY_STL): $(CUP_HOLDER_B123D_PY) | $(BUILD_DIR)
	XDG_CACHE_HOME=$(CURDIR)/.cache $(PYTHON_B123D) $(CUP_HOLDER_B123D_PY) --holder-only --export --output $@

clean:
	rm -rf $(BUILD_DIR)
