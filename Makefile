OPENSCAD ?= openscad
BUILD_DIR ?= build
CHECK_DIR ?= $(BUILD_DIR)/check

CORE_SWEEP_SCAD := core_mount_system/c_clamp/v1/c_clamp_sweep_reference_v1.scad
PHONE_SCAD := attachments/phone_mount/v1/phone_mount_v1.scad
TRAY_SCAD := attachments/sponge_tray/v1/sponge_tray_v1.scad
STAMP_TLP_SCAD := attachments/pottery_stamp/v8/pottery_stamp_tlp_v8.scad
CHECK_SCADS := $(CORE_SWEEP_SCAD) $(PHONE_SCAD) $(TRAY_SCAD) $(STAMP_TLP_SCAD)

CORE_SWEEP_STL := $(BUILD_DIR)/c_clamp_sweep_reference_v1.stl
PHONE_STL := $(BUILD_DIR)/phone_mount_v1.stl
PHONE_SAMPLE_STL := $(BUILD_DIR)/phone_mount_v1_holder_sample.stl
TRAY_STL := $(BUILD_DIR)/sponge_tray_v1.stl
STAMP_TLP_STL := $(BUILD_DIR)/pottery_stamp_tlp_v8.stl

.PHONY: help all core attachments stamps phone tray check clean

help:
	@echo "Targets:"
	@echo "  make all            Export all primary STLs to $(BUILD_DIR)/"
	@echo "  make core           Export core mount STL(s)"
	@echo "  make attachments    Export phone + tray STLs"
	@echo "  make stamps         Export stamp STL(s) from SCAD"
	@echo "  make phone          Export phone mount STL + holder-only sample STL"
	@echo "  make tray           Export sponge tray STL"
	@echo "  make check          Fast compile checks (CSG) for key SCAD files"
	@echo "  make clean          Remove generated build directory"

all: core attachments stamps

core: $(CORE_SWEEP_STL)

attachments: phone tray

stamps: $(STAMP_TLP_STL)

phone: $(PHONE_STL) $(PHONE_SAMPLE_STL)

tray: $(TRAY_STL)

check: | $(CHECK_DIR)
	@set -e; \
	for f in $(CHECK_SCADS); do \
		out="$(CHECK_DIR)/$$(basename "$${f%.scad}").stl"; \
		echo "CHECK $$f"; \
		$(OPENSCAD) -D '$$fn=24' -o "$$out" "$$f"; \
	done; \
	echo "CHECK attachments/phone_mount/v1/phone_mount_v1.scad (holder-only mode)"; \
	$(OPENSCAD) -D '$$fn=24' -D render_holder_only=true -o "$(CHECK_DIR)/phone_mount_v1_holder_sample.stl" "$(PHONE_SCAD)"; \
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

$(STAMP_TLP_STL): $(STAMP_TLP_SCAD) | $(BUILD_DIR)
	$(OPENSCAD) -o $@ $<

clean:
	rm -rf $(BUILD_DIR)
