# t4n-live

> 🇬🇧 English | 🇮🇩 [Bahasa Indonesia](./README.ID.md)

## T4n OS — Live Image, Rootfs & Installer Generator

**t4n-live** is a collection of shell scripts for building live ISO images, rootfs tarballs, and filesystem images based on [Void Linux](https://voidlinux.org/), customized for **T4n OS**.

### Live System Credentials

| Field | Value |
|---|---|
| Username | `t4nos` |
| Password | `t4nlabs` |

> 📚 Full documentation is available in the [`vdocs/`](./vdocs/index.md) directory.

## Repository Structure

```text
t4n-live/
├── common/                  # Shared system configurations
│   ├── cli/                 # Desktop/CLI variant: LightDM, Xorg, polkit, runit, GRUB theme
│   ├── gui/                 # GUI assets: Calamares branding, wallpapers, XFCE
│   ├── security/            # Security variant configuration (in development)
│   └── server/              # Server variant configuration (in development)
├── container/               # Containerfile & Docker Bake (HCL)
├── data/                    # Data assets (splash screen, issue)
├── dracut/                  # Dracut modules (vmklive, autoinstaller, netmenu)
├── grub/                    # GRUB configuration templates
├── isolinux/                # ISOLINUX configuration (legacy BIOS)
├── keys/                    # Public signing keys (.plist)
├── packer/                  # Packer build configuration (QEMU, VirtualBox, Vagrant)
├── platforms/               # Platform-specific scripts (pinebookpro, x13s)
├── pxelinux.cfg/            # PXE boot configuration
├── vdocs/                   # Project documentation (ID & EN)
├── vtools/                  # Additional utilities (mkxbpskey.sh)
├── installer.sh             # T4n OS installer (Bash)
├── lib.sh                   # Shared function library
├── mkimage.sh               # ARM flash-ready image generator
├── mkiso.sh                 # Full live ISO generator (wrapper)
├── mklive.sh                # Basic live ISO generator
├── mknet.sh                 # Netboot/PXE tarball generator
├── mkplatformfs.sh          # Platform-specific PLATFORMFS generator
├── mkrootfs.sh              # ROOTFS generator
├── release.sh               # Release automation via GitHub CI
└── version                  # Release version
```

## Dependencies

> [!WARNING]
> t4n-live is **not guaranteed to work** on distributions other than Void Linux, or inside containers.

- `xbps >= 0.45`
- `bash`
- Initramfs compression library: `liblz4` (for lz4) or `xz` *(default: `xz`)*
- `qemu-user-static` — required by `mkrootfs.sh` for cross-architecture builds

## Main Scripts

| Script | Description |
|---|---|
| `mklive.sh` | Basic/minimal live ISO generator |
| `mkiso.sh` | Full live ISO generator with `t4n-installer` (i686, x86_64, aarch64) |
| `mkrootfs.sh` | Void Linux rootfs generator for all platforms & architectures |
| `mkplatformfs.sh` | Platform-specific rootfs generator (with kernel, for ARM) |
| `mkimage.sh` | ARM flash-ready image generator (`dd`) |
| `mknet.sh` | Netboot/PXE tarball generator |
| `installer.sh` | T4n OS installer written in Bash |
| `release.sh` | Release automation via GitHub CI |

## Quick Start

### Build a Live ISO (x86_64, xfce variant)

```bash
sudo ./mkiso.sh -a x86_64 -b xfce
```

`-b` may be repeated to build several variants at once:

```bash
sudo ./mkiso.sh -a x86_64 -b base -b xfce
```

### Build a Live ISO with extra packages

Options for `mklive.sh` go after `--`:

```bash
sudo ./mkiso.sh -a x86_64 -b xfce -- -p "firefox neovim git" -o T4nOS-xfce.iso
```

### Build an ARM Image (Raspberry Pi 4)

```bash
# 1. Build ROOTFS
sudo ./mkrootfs.sh aarch64

# 2. Build PLATFORMFS
sudo ./mkplatformfs.sh rpi-aarch64 void-aarch64-ROOTFS-*.tar.xz

# 3. Generate the flash-ready image
sudo ./mkimage.sh void-rpi-aarch64-PLATFORMFS-*.tar.xz

# 4. Write it to the SD card
dd if=void-rpi-aarch64-*.img of=/dev/sdX bs=4M status=progress
```

### Installer

On x86 live images, `installer.sh` is installed as `/usr/bin/t4n-installer` (CLI) alongside the Calamares GUI installer. Run it as root from the live system:

```bash
sudo t4n-installer
```

## Available Variants (`-b`)

| Variant | Description |
|---|---|
| `base` | Minimal base system without a DE (default) |
| `xfce` | XFCE desktop (X11) — automatically uses XFCE Wayland on asahi devices |
| `security` | Not yet available |
| `server` | Not yet available |
| `cosmic` | Not yet available |

> [!NOTE]
> `security`, `server`, and `cosmic` are still in development and exit with a `COMING SOON` message.

## Kernel Command-line Parameters

| Parameter | Description |
|---|---|
| `live.autologin` | Skip the login screen on `tty1` |
| `live.user=<name>` | Change the non-root username (default: `anon`, password: `voidlinux`) |
| `live.shell=<path>` | Set the default shell for the non-root user |
| `live.accessibility` | Enable the `espeakup` screen reader |
| `console=ttyS0` | Enable a serial console (`ttyS0`, `hvc0`, `hvsi0`) |
| `locale.LANG=<locale>` | Set the locale (default: `en_US.UTF-8`) |
| `vconsole.keymap=<keymap>` | Set the console keymap (default: `us`) |

## Documentation

- 📄 [Documentation index](./vdocs/index.md)
- 🇬🇧 [English documentation](./vdocs/EN/Docs.md)
- 🇮🇩 [Dokumentasi Bahasa Indonesia](./vdocs/ID/Docs.md)

## License

See the [COPYING](./COPYING) file for license information.

---

<div align="center">

Built with ❤️ by [T4n-Labs](https://github.com/T4n-Labs) · Based on [Void Linux](https://voidlinux.org/)

</div>
