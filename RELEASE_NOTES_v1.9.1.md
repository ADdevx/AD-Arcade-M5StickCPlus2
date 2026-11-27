# AD Arcade v1.9.1

Bug fix release: Cardputer Arduino IDE builds, experimental M5Stack Core support, Tetris on StickS3, random number fix.

- **Cardputer / Cardputer-ADV**: building with the Arduino IDE now works. The Cardputer board is detected automatically (`ARDUINO_M5STACK_CARDPUTER` / `ARDUINO_M5STACK_CARDPUTER_ADV`), so the keyboard is read and Enter/Space validate the language screen (#8, thanks @BadMustard and @Senshu-hiro2). An empty `src/src.ino` lets the `src` folder open directly in the Arduino IDE.
- **M5Stack Core (Basic / Grey / Fire), experimental**: new build `AD-Arcade-M5StackCore`. Button C acts as PWR, and the 240x135 game image is centered on the 320x240 screen (#9). Not tested on a real device yet: feedback welcome.
- **Portability**: every PWR button read now goes through one macro, `BTN_PWR` in `common.h` (#9).
- **Tetris with buttons**: a quick tap on A+B now rotates (for the StickS3, where PWR cannot be read). Holding A+B still hard drops (#6).
- **Bug fixes**: the random number helper could not return negative values. Because of this, Emberwood enemies could get a huge speed when changing direction, a charging enemy aimed at a random angle, and some particles in Pocket Siege, Emberwood and Music flew off screen. Chrome Dino no longer paints the whole display white (only its game area).
- Compiles with no warnings under `-Wall -Wextra`.

## Downloads
Flash the bin for your device at address `0x0`:
- `AD-Arcade-M5StickCPlus2-v1.9.1.bin`: M5StickC Plus2 (tested)
- `AD-Arcade-M5StickCPlus-v1.9.1.bin`: M5StickC Plus (not tested on a real device yet)
- `AD-Arcade-M5StickS3-v1.9.1.bin`: M5StickS3 (not tested on a real device yet)
- `AD-Arcade-M5Cardputer-v1.9.1.bin`: Cardputer and Cardputer-ADV (not tested on a real device yet)
- `AD-Arcade-M5StackCore-v1.9.1.bin`: M5Stack Basic / Grey / Fire (experimental, not tested on a real device yet)

Example: `esptool.py --chip esp32 write_flash 0x0 AD-Arcade-M5StickCPlus2-v1.9.1.bin` (use `--chip esp32s3` for the StickS3 and the Cardputer).
