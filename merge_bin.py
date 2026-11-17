# Produit un .bin unique a flasher a l'adresse 0x0 (bootloader + partitions + boot_app0 + appli)
Import("env")
import os, sys

def merge_bin(source, target, env):
    build = env.subst("$BUILD_DIR")
    pio = env.PioPlatform()
    fw = os.path.join(build, "firmware.bin")
    boot = os.path.join(build, "bootloader.bin")
    part = os.path.join(build, "partitions.bin")
    boot_app0 = os.path.join(pio.get_package_dir("framework-arduinoespressif32"),
                             "tools", "partitions", "boot_app0.bin")
    esptool = os.path.join(pio.get_package_dir("tool-esptoolpy"), "esptool.py")
    name = env.GetProjectOption("custom_bin_name", "AD-Arcade")
    chip = env.GetProjectOption("custom_chip", "esp32")
    flash = env.GetProjectOption("custom_flash", "8MB")
    bootaddr = "0x1000" if chip in ("esp32", "esp32s2") else "0x0"
    out = os.path.join(env.subst("$PROJECT_DIR"), name + ".bin")
    cmd = [env.subst("$PYTHONEXE"), esptool, "--chip", chip, "merge_bin", "-o", out,
           "--flash_mode", "dio", "--flash_freq", "40m", "--flash_size", flash,
           bootaddr, boot, "0x8000", part, "0xe000", boot_app0, "0x10000", fw]
    env.Execute(" ".join('"%s"' % c for c in cmd))
    print("=> BIN FINAL :", out)

env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", merge_bin)
