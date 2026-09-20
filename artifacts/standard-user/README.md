# Spore ModAPI Launcher Kit — custom standard-user tools

These are **custom, unofficial binaries** derived from Spore Community's Launcher Kit
`v1.5.12` at commit `93c4ef3fd14c4db020449aa902115b7b5105bb8b`.
They are not official Spore Community release binaries.

Only the Easy Installer and Easy Uninstaller startup behaviour is changed: they retain
their `asInvoker` manifests and never request elevation. They can modify only locations
that the current Windows account can already modify. The ModAPI Launcher is not changed.

## Install

1. Confirm the installed Launcher Kit is version 1.5.12.
2. Back up the two original Easy Installer/Uninstaller executables.
3. Copy only these two files into the existing Launcher Kit directory:
   - `Spore ModAPI Easy Installer.exe`
   - `Spore ModAPI Easy Uninstaller.exe`
4. Keep this artifact directory, including `SHA256SUMS.txt`, somewhere outside the
   Launcher Kit directory so it remains available for later verification.

`ModAPI.Common.dll` and `Newtonsoft.Json.dll` are included as build dependencies and
for reproducibility. A normal v1.5.12 installation already has the matching dependencies;
do not replace unrelated Launcher Kit files unless the installation is incomplete.

## Minimum NTFS permissions

The source writes to the Spore Data directory detected from the registry, the Galactic
Adventures Data directory detected from the registry, and the Launcher Kit installation
directory. The last location contains `InstalledMods.config`, `ModConfigs`, `ModSettings`,
`mLibs`, and sometimes legacy mod DLLs in the directory root. `%APPDATA%\Spore ModAPI
Launcher` is also used by the update checker but is already owned by the signed-in user.

From an Administrator Command Prompt, substitute the exact paths reported by the GOG
installation/Launcher Kit and the standard account name:

```cmd
icacls "<DETECTED SPORE DATA PATH>" /grant "<USERNAME>":(OI)(CI)M /T
icacls "<DETECTED GALACTIC ADVENTURES DATA PATH>" /grant "<USERNAME>":(OI)(CI)M /T
icacls "<LAUNCHER KIT PATH>" /grant "<USERNAME>":(OI)(CI)M /T
```

If the two detected game Data paths are the same, grant that path once. `Modify` is
sufficient; do not grant Full Control. Do not grant the entire GOG installation root
when granting only the detected Data directories is possible.

## Updates and overwrite detection

The existing update check is retained. A Launcher Kit update replaces files in the
Launcher Kit directory and is therefore likely to overwrite these two custom binaries.
Do not disable updates globally. After any Launcher Kit update, run from PowerShell:

```powershell
.\Verify-InstalledBinaries.ps1 -LauncherKitPath "<LAUNCHER KIT PATH>"
```

Exit code 0 means both installed executables match this artifact set; exit code 1 means
one is missing, changed, or overwritten. Rebuilding against a newer upstream release is
safer than copying v1.5.12 binaries over a newer installation.

## Windows test plan

1. Log in to the target standard Windows account.
2. Start Easy Installer and confirm no UAC prompt appears.
3. Install a known-good `.sporemod`; confirm its expected files appear in the detected
   game Data folder and/or Launcher Kit `mLibs` folder.
4. Start Easy Uninstaller and confirm no UAC prompt appears.
5. Remove the test mod and confirm its files are removed.
6. Start Spore through the normal, unmodified ModAPI Launcher and confirm the mod works.
7. Confirm the account still cannot create a file in an unrelated protected location,
   such as `C:\Windows\System32`.
8. Temporarily remove the account's Modify permission from one test Data directory.
   Start each tool and confirm it names the non-writable path and exits without a UAC
   prompt. Restore the intended ACL afterward.

## Reproducible build

The project is .NET Framework 4.8 and includes WPF. macOS does not provide the required
Windows desktop reference/build targets, so the Mac-driven fallback uses the checked-in
GitHub Actions workflow on `windows-2022`.

On Windows (Visual Studio 2022 Build Tools with the .NET desktop workload):

```powershell
pwsh -File scripts/build-standard-user.ps1
```

That script verifies the required commands, restores NuGet packages, builds both Release
projects, copies the executables and runtime DLLs to `artifacts/standard-user`, creates
SHA-256 hashes, and verifies the PE manifests.

From macOS, push the task branch to a GitHub fork so the workflow's push trigger runs,
then download and verify that run with:

```sh
GH_CLI=codex-gh \
STANDARD_USER_BUILD_REPOSITORY="<OWNER>/<FORK>" \
scripts/build-standard-user.sh
```

For a normal user installation of GitHub CLI, omit `GH_CLI=codex-gh`; the script defaults
to `gh`. The script fails if the tools, successful workflow run, executables, hashes, or
`asInvoker` manifests are missing.
