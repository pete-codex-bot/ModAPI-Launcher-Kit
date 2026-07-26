---
title: Game Crashes
description: If your game freezes or crashes (i.e. "SPORE Galactic Adventures has stopped responding"), it may be due to a bug in the game itself, or due to a mod. See the page on Improving Game Stability for general recommendations that may help fix some crashes. You can ask for help when troubleshooting other crashes.
---
If your game freezes or crashes (i.e. "SPORE Galactic Adventures has stopped responding"), it may be due to a bug in the game itself, or due to a mod.

---

## Fixing/reducing common crashes
See [Improving Game Stability](improving-stability) for general recommendations that may help fix some crashes.

---

## Crashes when mods are installed
If you encounter crashes at startup, or at *specific* points in the game, it may be due to a bug in a mod. Try uninstalling mods (aside from SporeCrashFix) using the Easy Uninstaller and see if the crash persists. You may need to use trial and error to figure out which mod is causing the crash. In particular, ensure that you do not have any [outdated mods](outdated-mods).

If you have identified which mod is causing the crash, you will need to contact the developer of that mod to report it. Mod developers can generally be contacted on Discord or GitHub.

## Crashes when no mods (except SporeCrashFix) are installed
For crashes that occur even when SporeCrashFix is the only installed mod, it may be a bug in the game itself, or due to corrupted user data.

### Startup crashes
For crashes that occur *every time* you start the game, *before* you reach the galaxy menu, the most common cause is corrupted or invalid user data.

To temporarily remove this data:
- Open your Documents folder. Rename the `My Spore Creations` folder by appending the current date at the end, for example `My Spore Creations - 2026/09/07`.
- Press Win+R and type in `%appdata%`. Rename the `Spore` folder by appending the current date at the end, for example `Spore - 2026/09/07`.
After renaming both folders, launch the game via the ModAPI Launcher. If the game no longer crashes, it means there is a problem with your user data. Please [ask for further help](/support) and indicate that you have completed these steps.

The game will re-create these folders on startup. To restore your data, first delete the newly re-created folders, then rename both original folders back to their original names.

### Other crashes
Crashes that occur while playing, assuming that no mods (except SporeCrashFix) are installed, are often due to bugs in the game.

Crashes that occur at random, and cannot be easily reproduced, are generally difficult to identify and fix. However, if the cause can be identified, mod developers may be able to add a fix for the crash in SporeCrashFix.

To help resolve crashes, please follow these steps:
- Check all [common troubleshooting steps](/support).
- Ensure that the only installed mod is SporeCrashFix.
- Collect the following information:
  - If you can reproduce the crash, note the steps needed to do so.
  - If you cannot reproduce the crash, note where or when the crash occurs, in as much detail as possible.
  - A support info file:
    - Press Win+R and type in `notepad "%appdata%\Spore ModAPI Launcher\support.info"`
    - A notepad window will open, copy and send the full contents of this file.
    - *If you get a prompt "Cannot find the file", make sure the Launcher Kit is up-to-date.*
  - The game's exception report:
    - Open the folder where Spore Galactic Adventures is installed, look in the `SporebinEP1` folder, and send the most recent exception report file
    - *Privacy note: This file includes your Windows username - you may open the file in notepad and edit it to remove this name*
- [Ask for help](/support) and include the above information.