# Changelog

## v1.8.2
- Buttons mode is now only offered in **Tetris** and **Snake** (the other games are better with tilt).
- Tetris with buttons: B = left, A = right, **PWR = rotate** (no pause in this mode), hold A+B = hard drop. A+B no longer rotates, so pieces are not dropped by accident.

## v1.8.1
- **Tilt or buttons**: Meteors, Breakout, Invaders, Slalom, Racing, River, Tetris, Snake and Lunar Lander can now be played with the buttons. A screen asks before the game (your choice is remembered), or pick it once in Settings > Controls (Ask / Tilt / Buttons). Buttons: B = left, A = right (Racing: A+B = nitro, Invaders: auto fire, Tetris: A+B = rotate, hold A+B = drop, Snake: A/B = turn, Lander: A/B = rotate, A+B = thrust).
- **Screen rotation**: Settings > Screen (Normal / Flipped 180 degrees); tilt follows the screen.
- **Emberwood**: original background music (village & forest, crypt, boss), medals (bronze for beating the Ember Golem, silver and gold for fast runs) and a final score; it now appears in Trophies and Stats.
- **Emberwood fixes**: you could get stuck in a tree when entering the forest clearing, and then not leave the village to the right; the river boulder no longer blocks the path.
- **Cardputer / Cardputer-ADV**: screen was rotated 90 degrees (now landscape), Enter/Space now work as A (the language screen could not be validated), Ctrl also works as B. Thanks to the Reddit tester!

## v1.8.0 (beta: played on the StickC Plus2; StickC Plus, StickS3 and Cardputer builds need community testing)
- NEW GAME: **Legend of Emberwood**, a top-down adventure (original hero Kiri). 10 screens: village (merchant, blacksmith, old Magda, Pip, guard), forest (river, waterfall, bridge, clearing, ruins), crypt (torch-lit rooms, spike traps) and the volcanic arena of the **Ember Golem** boss (3 phases: slam + shockwave, fire eruptions, flaming boulders and orbiting shards).
- Tilt to walk, A = sword / talk / open, B = roll (dodge), PWR = pause. Hearts, gems, keys, chests, breakable urns, cuttable tall grass, day/night cycle with fireflies in the forest, dynamic torch lighting in the crypt, auto-save (NVS) with Continue / New game.
- Hand-made 48-colour pixel art (16x24 hero with walk/attack/roll/hurt/victory, 6 animated enemies with particle deaths, articulated 64x64 golem). Art stored as 4-bit / RLE data (~95 KB).

## v1.7.2
- Meteors: new rocky asteroids (lit from top-left, craters) with a fiery tapered trail; violet/blue night sky in Meteors, Invaders and Breakout.

## v1.7.1
- More colourful backgrounds: banded sky, stars, parallax mountains and checker ground (instead of the grey checkerboard).

## v1.7
- New common retro look: strict 8-colour pixel-art palette, pixel fonts everywhere, light checkerboard backgrounds (no more dark screens).
- New first-boot wizard: language, 3-step tilt calibration, **date and time** setup.
- Redesigned main menu; icons redrawn (Daily, 2 Players, Trophies, Stats, Music, Settings). "1-2 Players" is now **"2 Players"**.
- New **Skins** screen with live preview (bird, ship, kayak, lander, snake, ball). The river kayak now uses skins.
- Settings, About, Trophies, Stats, Daily, 2 Players and Music screens restyled; new Game Over screen; point pop-ups ("+10", "OUCH"...) restyled.
- Hidden admin (6 presses of A in About) now has 18 options: unlock/pick skins, skip intro, FPS counter, set medals per game or all, clear records, daily tools, redo setup, plus fun ones (CRT lines, invert colours, rainbow menu, confetti, beep party, secret messages).

## v1.6
- Graphics overhaul: Breakout, Invaders, Stack, Meteors and Maze redrawn (backgrounds, shaded sprites, particles, trails, glow).

## v1.5.1
- Redesigned Daily Challenge screen (game card, tries, streak flame, 7-day chart, pulsing play button).
- Redesigned Trophies screen (progress bar toward the next medal, coloured medal strip, page dots).
- Tetris: tilt is less sensitive (higher threshold, short delay before the first step, slower repeat) so a small tilt moves one square.
- About: M5 button no longer closes the page.

## v1.5
- New **Daily Challenge**: one game and one seed per day (from the built-in clock), 3 tries, best score of the day, day streak and a 7-day history
- New **1-2 Players** mode: play solo to beat your best, or pass the M5 around (same start for both, 1 round or best of 3)
- New **Stats** screen: total play time, games played, favourite game, medals, streak
- New **Difficulty** setting (Easy, Normal, Hard). Easy is practice (no medals), Hard has its own records and medals
- New **Skins** for the hero of Flap Bird, Snake, Meteors, Invaders, Lunar Lander, Breakout, Fish and Maze, unlocked with medals
- New **Volume** setting with 5 levels
- New **Date** setting (used by the Daily Challenge)
- Louder in-game music

## v1.4
- Redrawn **Flap Bird** character (new purple bird with crest, tail and animated wing)
- **New music**: original chiptune tunes with melody and bass for all 15 games
- Fixed **Lunar Lander**: pressing M5 after game over now restarts the game
- New **Trophies** screen: bronze, silver and gold medals for every game, with a banner when you win one
- New **Theme** setting: change the colours of the menu (Auto, Ocean, Sunset, Forest, Sakura, Gold, Mono)
- New **About** page in Settings: version, credits and a QR code to the developer profile

## v1.3
- New games: **Tetris**, **Snake**, **Lunar Lander** (17 games in total)
- Reworked **Flap Bird**: parallax backgrounds, day and night, moving pipes, medals
- Redesigned animated menu
- Quiet chiptune **background music in every game** (setting: Game music)
- Music player now has **25 public domain tunes**
- Tilt controls **adapt automatically** to flat or upright play
- Longer 90s style intro
- Version number shown in Settings
- Hold **A + B** for 1.2 s to go back to the menu (in addition to holding PWR)

## Earlier versions
- First releases with 13 games and apps, tilt controls, saved high scores, battery indicator, brightness and sound settings, English and French

## 1.7.3
- Code cleanup: compiles with no `-Wall` warnings (unused variables, switch defaults, misleading indentation, buffer sizes). Thanks to hiroyukisenshu-commits for the report and patch (#2).
- New ports (first release, simulation-tested): M5StickC Plus, M5StickS3, M5Cardputer.
