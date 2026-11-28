# AD Arcade v1.9.2

Bug fix release for the Cardputer-ADV and the M5Stack Core.

- **Cardputer / Cardputer-ADV**: Enter, Space and the Go button work again as A, so the language screen and the menus can be validated (#8, thanks @Osamaex, @BadMustard and @Senshu-hiro2). The Go button was read with `digitalRead(0)`, which always returns LOW with Arduino-ESP32 3.x when the pin was not set up with Arduino's `pinMode()`. Button A then stayed "pressed" forever and never fired a new press. The Go button is now read directly, like M5Unified does.
- **M5Stack Core (Basic / Grey / Fire / Core2)**: the screen now uses the normal landscape orientation, with the buttons below the screen (#9, patch by @Senshu-hiro2).

## Downloads
Flash the bin for your device at address `0x0`:
- `AD-Arcade-M5StickCPlus2-v1.9.2.bin`: M5StickC Plus2 (tested)
- `AD-Arcade-M5StickCPlus-v1.9.2.bin`: M5StickC Plus (not tested on a real device yet)
- `AD-Arcade-M5StickS3-v1.9.2.bin`: M5StickS3 (v1.9.1 reported working by a tester)
- `AD-Arcade-M5Cardputer-v1.9.2.bin`: Cardputer and Cardputer-ADV (not tested on a real device yet)
- `AD-Arcade-M5StackCore-v1.9.2.bin`: M5Stack Basic / Grey / Fire (experimental, not tested on a real device yet)

Example: `esptool.py --chip esp32 write_flash 0x0 AD-Arcade-M5StickCPlus2-v1.9.2.bin` (use `--chip esp32s3` for the StickS3 and the Cardputer).
