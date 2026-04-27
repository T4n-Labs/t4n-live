# T4n OS Live Image Documentation (English)

> 🇮🇩 [Versi Bahasa Indonesia](../ID/Docs.md) | [← Index](../index.md) | [← README](../../README.md)

---

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Dependencies](#dependencies)
- [Workflow](#workflow)
- [Script Reference](#script-reference)
- [common/ Configuration](#common-configuration)
- [Kernel Command-line Parameters](#kernel-command-line-parameters)
- [Packer & Container](#packer--container)
<!-- - [Release & Signing](#release--signing) -->

## Overview

**t4n-live** is the live image and rootfs generator for **T4n OS**, a Linux distribution based on [Void Linux](https://voidlinux.org/). This repository provides a complete toolchain for:

- Building bootable live ISO images (USB/CD)
- Building ROOTFS tarballs for chroot-based installation
- Building flash-ready ARM images for embedded devices (Raspberry Pi, Pinebook Pro, etc.)
- Building netboot/PXE tarballs
- Building VM images via Packer (QEMU, VirtualBox, Vagrant)

### Available Scripts

| Script | Description |
|---|---|
| `t4n-live.sh` | Basic/minimal T4n OS live ISO generator |
| `t4n-iso.sh` | Full live ISO generator with `void-installer` |
| `t4n-rootfs.sh` | ROOTFS tarball generator for all architectures |
| `t4n-platformfs.sh` | Platform-specific PLATFORMFS generator (rootfs + kernel, for ARM) |
| `t4n-image.sh` | ARM flash-ready image generator (`dd`) |
| `t4n-net.sh` | Netboot/PXE tarball generator |
| `installer.sh` | El-cheapo Void Linux/T4n OS installer for x86 |
| `release.sh` | Build & signing images for GitHub CI |
| `lib.sh` | Shared function library (used by other scripts) |

---

## Repository Structure

```
t4n-live/
├── common/
│   ├── cli/                    # Desktop/CLI variant configurations
│   │   ├── config/
│   │   │   └── lightdm/        # LightDM display manager configuration
│   │   │       ├── lightdm-gtk-greeter.conf
│   │   │       └── lightdm.conf
│   │   ├── grub                # GRUB bootloader configuration
│   │   ├── os-release          # OS identity file
│   │   ├── polkit/             # PolicyKit rules (system authorization)
│   │   │   ├── 10-bspwm.rules
│   │   │   ├── 20-networkmanager.rules
│   │   │   └── 30-backlight.rules
│   │   ├── resolv.conf         # DNS configuration
│   │   ├── runit/              # runit-based init system
│   │   │   ├── 1, 2, 3         # runit init stages
│   │   │   ├── core-services/  # Core init scripts (udev, filesystem, swap, etc.)
│   │   │   ├── runsvdir/       # Active service directories
│   │   │   │   ├── default/    # Default services (agetty tty1-6, udevd)
│   │   │   │   └── single/     # Single-user mode
│   │   │   └── shutdown.d/     # Ordered shutdown scripts
│   │   ├── service/
│   │   │   └── pipewire/       # PipeWire audio service setup
│   │   ├── sleek/              # T4n OS custom GRUB theme
│   │   │   ├── icons/          # Distribution icons for bootloader
│   │   │   ├── *.pf2           # Poppins & Terminus fonts for GRUB
│   │   │   └── theme.txt       # GRUB theme definition
│   │   └── xorg.conf.d/
│   │       └── 10-touchpad.conf  # Touchpad configuration (libinput)
│   └── server/
│       └── coming-soon.md      # Server configurations (in development)
├── container/
│   ├── Containerfile           # OCI container image definition
│   └── docker-bake.hcl         # Docker Bake multi-target config
├── data/
│   ├── issue                   # Terminal login banner message
│   └── splash.png              # Bootloader splash screen
├── dracut/
│   ├── autoinstaller/          # Automated install module (VAI)
│   │   ├── autoinstall.cfg
│   │   ├── install.sh
│   │   ├── module-setup.sh
│   │   └── parse-vai-root.sh
│   ├── netmenu/                # Interactive netboot menu module
│   │   ├── module-setup.sh
│   │   └── netmenu.sh
│   └── vmklive/                # Core live system dracut module
│       ├── adduser.sh          # Creates live user (anon)
│       ├── locale.sh           # Locale setup
│       ├── display-manager-autologin.sh
│       ├── accessibility.sh    # Accessibility setup (espeakup)
│       ├── getty-serial.sh     # Serial console setup
│       ├── nomodeset.sh        # Fallback graphics without KMS
│       └── module-setup.sh
├── grub/
│   ├── grub.cfg                # Main GRUB configuration
│   ├── grub_void.cfg.pre       # GRUB pre-config template
│   └── grub_void.cfg.post      # GRUB post-config template
├── isolinux/
│   └── isolinux.cfg.in         # ISOLINUX config template (legacy BIOS)
├── keys/                       # Public keys for package verification
├── packer/
│   ├── hcl2/                   # Packer HCL2 build definitions
│   │   ├── build-cloud-generic.pkr.hcl
│   │   ├── build-vagrant.pkr.hcl
│   │   ├── source-qemu.pkr.hcl
│   │   └── source-virtualbox-ose.pkr.hcl
│   ├── http/                   # Preseed/kickstart configs for Packer
│   ├── plugins.pkr.hcl         # Packer plugin declarations
│   └── scripts/                # Post-install provisioning scripts
│       ├── cloud.sh
│       └── vagrant.sh
├── platforms/
│   ├── pinebookpro.sh          # Pinebook Pro platform setup
│   ├── x13s.sh                 # Lenovo X13s (ARM) platform setup
│   └── README.md               # Platform documentation
├── pxelinux.cfg/
│   └── pxelinux.cfg.in         # PXE boot config template
├── VDocs/                      # Project documentation
│   ├── index.md
│   ├── ID/Docs.md
│   └── EN/Docs.md              ← You are here
├── t4n-live.sh
├── t4n-iso.sh
├── t4n-rootfs.sh
├── t4n-platformfs.sh
├── t4n-image.sh
├── t4n-net.sh
├── installer.sh
├── release.sh
├── lib.sh
└── VNote.md                    # Internal development notes
```

## Dependencies

> ⚠️ t4n-live is **not guaranteed to work** on distributions other than Void Linux, or inside containers.

| Dependency | Notes |
|---|---|
| `xbps >= 0.45` | Void Linux package manager |
| `bash` | Shell interpreter |
| `liblz4` | lz4 compression for initramfs |
| `xz` | xz compression for initramfs & squashfs (default) |
| `qemu-user-static` | Required for `t4n-rootfs.sh` when cross-compiling architectures |

## Workflow

### 1. Building a Live ISO

**Full ISO** (recommended — includes `void-installer` and additional utilities):

```bash
sudo ./t4n-iso.sh -a x86_64 -b xfce
```

**Minimal ISO** (no installer):

```bash
sudo ./t4n-live.sh -a x86_64
```

**ISO with extra packages and a custom overlay:**

```bash
sudo ./t4n-iso.sh -a x86_64 -b xfce -- \
  -p "firefox neovim git htop" \
  -I ./my-overlay/ \
  -C "live.autologin live.shell=/bin/bash" \
  -o T4nOS-xfce-custom.iso
```

### 2. Building a ROOTFS Tarball

A ROOTFS contains a basic Void Linux root filesystem **without a kernel**. Useful for:
- [Chroot-based installation](https://docs.voidlinux.org/installation/guides/chroot.html)
- [Container & chroot environments](https://docs.voidlinux.org/config/containers-and-vms/chroot.html)

```bash
sudo ./t4n-rootfs.sh x86_64
sudo ./t4n-rootfs.sh aarch64-musl
```

### 3. Building a PLATFORMFS (for ARM)

A PLATFORMFS is a ROOTFS **with a platform-specific kernel**. This step is required before creating an ARM image.

```bash
# Step 1: Build the ROOTFS first
sudo ./t4n-rootfs.sh aarch64

# Step 2: Build the PLATFORMFS
sudo ./t4n-platformfs.sh rpi-aarch64 void-aarch64-ROOTFS-*.tar.xz
```

### 4. Building an ARM Image (Flash-ready)

ARM images contain a complete filesystem layout with 2 partitions (`/boot` and `/`), ready to be flashed to storage.

```bash
# Step 3: Generate the image
sudo ./t4n-image.sh void-rpi-aarch64-PLATFORMFS-*.tar.xz

# Flash to SD card
dd if=void-rpi-aarch64-*.img of=/dev/sdX bs=4M status=progress
```

> ⚠️ Replace `/dev/sdX` with your actual SD card device. Verify with `lsblk`.

### 5. Building a Netboot Tarball

```bash
sudo ./t4n-net.sh void-x86_64-ROOTFS-*.tar.xz
```

## Script Reference

### `t4n-live.sh`

```
Usage: t4n-live.sh [options]

OPTIONS
 -a <arch>          Set XBPS_ARCH in the ISO image
 -b <system-pkg>    Set an alternative base package (default: base-system)
 -r <repo>          Use this XBPS repository (may be specified multiple times)
 -c <cachedir>      XBPS cache directory (default: ./xbps-cachedir-<arch>)
 -H <host_cachedir> Host XBPS cache directory
 -k <keymap>        Default keymap (default: us)
 -l <locale>        Default locale (default: en_US.UTF-8)
 -i <lz4|gzip|bzip2|xz>   Initramfs compression type (default: xz)
 -s <gzip|lzo|xz>   Squashfs compression type (default: xz)
 -o <file>          Output ISO file name (default: automatic)
 -p "<pkg> ..."     Install additional packages in the ISO
 -g "<pkg> ..."     Ignore packages when building the ISO
 -I <includedir>    Include directory into the ROOTFS
 -S "<service> ..." Enable services in the ISO
 -e <shell>         Default shell for root user (absolute path)
 -C "<arg> ..."     Additional kernel command line arguments
 -P "<platform> ..." Platforms for aarch64 EFI ISO (pinebookpro, x13s)
 -T <title>         Bootloader title (default: T4n OS)
 -v linux<version>  Custom Linux version (default: linux metapackage)
 -x <script>        Path to postsetup script before generating initramfs
 -K                 Do not remove builddir after build
 -h                 Show help and exit
 -V                 Show version and exit
```

### `t4n-iso.sh`

```
Usage: t4n-iso.sh [options ...] [-- t4n-live options ...]

OPTIONS
 -a <arch>     Architecture or platform for the image
 -b <variant>  Variant: base | server | xfce | xfce-wayland (default: base)
               May be specified multiple times to build multiple variants
 -d <date>     Override datestamp (format: YYYYMMDD)
 -t <arch-date-variant>  Equivalent to setting -a, -b, and -d
 -r <repo>     Use this XBPS repository (may be specified multiple times)
 -h            Show help and exit
 -V            Show version and exit

Additional options can be passed to t4n-live.sh by appending them after --.
```


### `t4n-rootfs.sh`

```
Usage: t4n-rootfs.sh [options] <arch>

Supported architectures:
  i686, i686-musl, x86_64, x86_64-musl,
  armv5tel, armv5tel-musl, armv6l, armv6l-musl, armv7l, armv7l-musl,
  aarch64, aarch64-musl,
  mipsel, mipsel-musl,
  ppc, ppc-musl, ppc64le, ppc64le-musl, ppc64, ppc64-musl,
  riscv64, riscv64-musl

OPTIONS
 -b <system-pkg>  Alternative base-system package (default: base-container-full)
 -c <cachedir>    XBPS cache directory
 -C <file>        Full path to the XBPS configuration file
 -r <repo>        Use this XBPS repository (may be specified multiple times)
 -o <file>        ROOTFS output filename (default: automatic)
 -x <num>         Number of compression threads (default: dynamic)
 -h               Show help and exit
 -V               Show version and exit
```

### `t4n-platformfs.sh`

```
Usage: t4n-platformfs.sh [options] <platform> <rootfs-tarball>

Supported platforms:
  i686, x86_64, GCP,
  rpi-armv6l, rpi-armv7l, rpi-aarch64,
  pinebookpro, pinephone, rock64, rockpro64, asahi

OPTIONS
 -b <system-pkg>  Alternative base-system package (default: base-system)
 -c <cachedir>    XBPS cache directory
 -C <file>        Full path to the XBPS configuration file
 -k <cmd>         Run '<cmd> <ROOTFSPATH>' after the build completes
 -n               Do not compress; print the ROOTFS directory instead
 -o <file>        PLATFORMFS archive output filename (default: automatic)
 -p "<pkg> ..."   Additional packages to install into the ROOTFS
 -r <repo>        Use this XBPS repository (may be specified multiple times)
 -x <num>         Number of compression threads (default: dynamic)
 -h               Show help and exit
 -V               Show version and exit
```

### `t4n-image.sh`

```
Usage: t4n-image.sh [options] <platformfs-tarball>

OPTIONS
 -b <fstype>    /boot filesystem type (default: vfat)
 -B <bsize>     /boot filesystem size (default: 256MiB)
 -r <fstype>    / filesystem type (default: ext4)
 -s <totalsize> Total image size (default: 900MiB)
 -o <file>      Image filename (default: automatic)
 -x <num>       Number of compression threads (default: dynamic)
 -h             Show help and exit
 -V             Show version and exit

Accepted size suffixes: KiB, MiB, GiB, TiB, EiB
```

### `t4n-net.sh`

```
Usage: t4n-net.sh [options] <rootfs-tarball>

OPTIONS
 -r <repo>          XBPS repository (may be specified multiple times)
 -c <cachedir>      XBPS cache directory
 -i <lz4|gzip|bzip2|xz>   Initramfs compression type (default: xz)
 -o <file>          Netboot tarball output filename (default: automatic)
 -K linux<version>  Custom Linux version (default: linux metapackage)
 -k <keymap>        Default keymap (default: us)
 -l <locale>        Default locale (default: en_US.UTF-8)
 -C "<arg> ..."     Additional kernel command line arguments
 -T <title>         Bootloader title (default: Void Linux)
 -S <image>         Custom splash image (default: data/splash.png)
 -h                 Show help and exit
 -V                 Show version and exit
```

## common/ Configuration

The `common/` directory holds system configuration files that are bundled into the image during the build. It currently has two sub-directories: `cli/` (active) and `server/` (in development).

### `common/cli/config/lightdm/`

Contains configuration for the **LightDM** display manager used in desktop variants (xfce, xfce-wayland):

- `lightdm.conf` — Main LightDM configuration (greeter, autologin, session)
- `lightdm-gtk-greeter.conf` — GTK greeter appearance (theme, icons, font)

### `common/cli/polkit/`

**PolicyKit** rules that allow regular users to perform system operations without a password:

| File | Purpose |
|---|---|
| `10-bspwm.rules` | Permissions for BSPWM window manager |
| `20-networkmanager.rules` | Network management for regular users |
| `30-backlight.rules` | Screen brightness control |

### `common/cli/runit/`

**runit** init system configuration — Void Linux's init system:

- **Stage 1 (`1`)** — Early init: mount pseudo-filesystems, set up udev, configure console
- **Stage 2 (`2`)** — Run service daemons via `runsvdir`
- **Stage 3 (`3`)** — Cleanup on shutdown

**`core-services/`** — Core init scripts run in stage 1, executed in numeric prefix order:

| Script | Purpose |
|---|---|
| `00-pseudofs.sh` | Mount proc, sys, dev, devpts |
| `01-static-devnodes.sh` | Create static device nodes |
| `02-kmods.sh` | Load kernel modules |
| `02-udev.sh` | Start udev daemon |
| `03-console-setup.sh` | Set up console font & keymap |
| `03-filesystems.sh` | Mount filesystems from fstab |
| `04-swap.sh` | Activate swap |
| `05-misc.sh` | Set hostname, loopback, time |
| `08-sysctl.sh` | Apply sysctl parameters |
| `98-sbin-merge.sh` | Merge /sbin into /usr/bin |
| `99-cleanup.sh` | Clean up lock files, tmp |

**`runsvdir/default/`** — Services enabled by default:
`agetty-tty1` through `agetty-tty6` (login terminals), `udevd`

**`shutdown.d/`** — Shutdown scripts run in order when the system powers off:

| Script | Purpose |
|---|---|
| `10-sv-stop.sh` | Stop all runit services |
| `20-rc-shutdown.sh` | Run rc.shutdown |
| `30-seedrng.sh` | Save entropy seed |
| `40-hwclock.sh` | Sync hardware clock |
| `50-wtmp.sh` | Record shutdown time to wtmp |
| `60-udev.sh` | Stop udev |
| `70-pkill.sh` | Kill remaining processes |
| `80-filesystems.sh` | Unmount filesystems |
| `90-kexec.sh` | Execute kexec if present |

### `common/cli/sleek/`

The T4n OS custom **GRUB theme** named **Sleek**. Contains:
- Image assets for background, selection bar, progress indicator, slider
- Poppins (14/16/18/48pt) and Terminus (14pt) fonts in `.pf2` format
- `icons/` directory with 60+ Linux distribution icons for multi-boot menus
- `theme.txt` — GRUB theme layout definition

### `common/cli/service/pipewire/`

Setup script for the **PipeWire** service (modern audio server). Invoked during live environment initialization.

## Kernel Command-line Parameters

| Parameter | Description |
|---|---|
| `live.autologin` | Skip the login screen on `tty1` |
| `live.user=<name>` | Change non-root username (default: `anon`, password: `voidlinux`) |
| `live.shell=<path>` | Set the default shell for the non-root user in the live environment |
| `live.accessibility` | Enable `espeakup` screen reader |
| `console=ttyS0` | Enable agetty on serial console (`ttyS0`, `hvc0`, `hvsi0`) |
| `locale.LANG=<locale>` | Set the LANG variable (default: `en_US.UTF-8`) |
| `vconsole.keymap=<keymap>` | Set the console keymap (default: `us`) |

### Example Combinations

```
# Auto-login as user "jane" with bash shell
live.autologin live.user=jane live.shell=/bin/bash

# Serial console with French keymap
console=ttyS0 vconsole.keymap=fr

# Canadian French language
locale.LANG=fr_CA.UTF-8

# Enable accessibility with auto-login
live.accessibility live.autologin
```

## Packer & Container

### Packer

The `packer/` directory contains [HashiCorp Packer](https://www.packer.io/) configurations for automatically building VM images:

| File | Purpose |
|---|---|
| `hcl2/source-qemu.pkr.hcl` | QEMU/KVM source for VM builds |
| `hcl2/source-virtualbox-ose.pkr.hcl` | VirtualBox OSE source |
| `hcl2/build-cloud-generic.pkr.hcl` | Cloud-generic image build |
| `hcl2/build-vagrant.pkr.hcl` | Vagrant box build |
| `plugins.pkr.hcl` | Required plugin declarations |
| `http/*.cfg` | Preseed/kickstart files for auto-install |
| `scripts/cloud.sh` | Cloud image provisioning |
| `scripts/vagrant.sh` | Vagrant box provisioning |

```bash
# Install Packer plugins
packer init packer/plugins.pkr.hcl

# Build a QEMU image
packer build packer/hcl2/source-qemu.pkr.hcl
```

### Container

```bash
# Build the container image
podman build -f container/Containerfile -t t4n-live:latest

# Or with Docker Bake
docker buildx bake -f container/docker-bake.hcl
```

<!-- ## Release & Signing

`release.sh` interacts with **GitHub Actions** to:
1. Trigger image builds in the CI pipeline
2. Sign the generated images using keys from the `keys/` directory
3. Upload build artifacts to GitHub Releases

Public keys for verification are stored in `keys/` in `.plist` format. -->

---

<div align="center">

[← Back to Index](../index.md) · [Versi Bahasa Indonesia](../ID/Docs.md) · Built with ❤️ by [T4n-Labs](https://github.com/T4n-Labs)

</div>
