# T4n OS Live Image Documentation (English)

> 🇮🇩 [Versi Bahasa Indonesia](../ID/Docs.md) | [← Index](../index.md) | [← README](../../README.md)

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Dependencies](#dependencies)
- [Workflow](#workflow)
- [Script Reference](#script-reference)
- [common/ Configuration](#common-configuration)
- [Kernel Command-line Parameters](#kernel-command-line-parameters)
- [Packer & Container](#packer--container)
- [Release & CI](#release--ci)

## Overview

**t4n-live** is the live image and rootfs generator for **T4n OS**, a Linux distribution based on [Void Linux](https://voidlinux.org/). This repository provides a toolchain for:

- Building bootable live ISO images (USB/CD)
- Building ROOTFS tarballs for chroot-based installation or containers
- Building flash-ready ARM images for embedded devices (Raspberry Pi, Pinebook Pro, etc.)
- Building netboot/PXE tarballs
- Building VM images via Packer (QEMU, VirtualBox, Vagrant)

Default live system credentials: username `t4nos`, password `t4nlabs`.

### Available Scripts

| Script | Description |
|---|---|
| `mklive.sh` | Basic/minimal live ISO generator |
| `mkiso.sh` | Wrapper around `mklive.sh` for full ISOs with `t4n-installer` (i686, x86_64, aarch64) |
| `mkrootfs.sh` | Void Linux rootfs generator for all platforms & architectures |
| `mkplatformfs.sh` | Platform-specific rootfs generator (with kernel, for ARM) |
| `mkimage.sh` | ARM flash-ready image generator (`dd`) |
| `mknet.sh` | Netboot/PXE tarball generator |
| `installer.sh` | T4n OS installer written in Bash |
| `release.sh` | Release automation via GitHub CI |

## Repository Structure

```text
t4n-live/
├── common/
│   ├── cli/                    # Desktop/CLI variant configuration
│   │   ├── .bashrc             # Default shell profile
│   │   ├── config/
│   │   │   ├── lightdm/        # LightDM display manager
│   │   │   │   ├── lightdm-gtk-greeter.conf
│   │   │   │   └── lightdm.conf
│   │   │   └── xbps.d/         # XBPS configuration + glibc repo keys
│   │   ├── grub                # GRUB configuration
│   │   ├── os-release          # OS identity file
│   │   ├── polkit/
│   │   │   └── 20-networkmanager.rules
│   │   ├── resolv.conf         # DNS configuration
│   │   ├── runit/              # runit init system
│   │   │   ├── 1, 2, 3         # runit init stages
│   │   │   ├── core-services/  # Core init scripts (udev, filesystem, swap, etc.)
│   │   │   ├── runsvdir/       # Active services (agetty tty1-6, udevd)
│   │   │   └── shutdown.d/     # Ordered shutdown scripts
│   │   ├── service/
│   │   │   └── pipewire/       # PipeWire audio service setup
│   │   └── sleek/              # T4n OS custom GRUB theme
│   │       ├── icons/          # Distribution icons for the boot menu
│   │       ├── *.pf2           # Poppins & Terminus fonts for GRUB
│   │       └── theme.txt       # GRUB theme definition
│   ├── gui/                    # GUI assets & configuration
│   │   ├── config/
│   │   │   ├── desktop/        # Calamares launcher
│   │   │   ├── etc/            # Calamares, polkit, and udev configuration
│   │   │   └── wallpapers/     # T4n OS wallpapers
│   │   ├── cosmic/             # COSMIC variant (COMING_SOON)
│   │   ├── xfce/               # XFCE assets, configuration, and scripts
│   │   └── xorg.conf.d/
│   │       └── 10-touchpad.conf  # Touchpad configuration (libinput)
│   ├── security/               # Security variant configuration (ON_GOING)
│   └── server/                 # Server variant configuration (coming-soon.md)
├── container/
│   ├── Containerfile           # OCI container image definition
│   └── docker-bake.hcl         # Docker Bake multi-target config
├── data/
│   ├── issue                   # Terminal login banner
│   └── splash.png              # Bootloader splash screen
├── dracut/
│   ├── autoinstaller/          # Automated install module
│   │   ├── autoinstall.cfg
│   │   ├── install.sh
│   │   ├── module-setup.sh
│   │   └── parse-vai-root.sh
│   ├── netmenu/                # Interactive netboot menu module
│   │   ├── module-setup.sh
│   │   └── netmenu.sh
│   └── vmklive/                # Core live system dracut module
│       ├── adduser.sh          # Creates the live user
│       ├── accessibility.sh    # Accessibility setup (espeakup)
│       ├── display-manager-autologin.sh
│       ├── getty-serial.sh     # Serial console setup
│       ├── locale.sh           # Locale setup
│       ├── mtd.sh              # MTD support
│       ├── nomodeset.sh        # Fallback graphics without KMS
│       └── module-setup.sh
├── grub/
│   ├── grub.cfg                # Main GRUB configuration
│   ├── grub_void.cfg.pre       # GRUB pre-config template
│   └── grub_void.cfg.post      # GRUB post-config template
├── isolinux/
│   └── isolinux.cfg.in         # ISOLINUX config template (legacy BIOS)
├── keys/                       # Public keys (.plist) for package verification
├── packer/
│   ├── hcl2/                   # Packer HCL2 build definitions (QEMU, VirtualBox, cloud, Vagrant)
│   ├── http/                   # Preseed/kickstart configs for Packer
│   ├── plugins.pkr.hcl         # Packer plugin declarations
│   └── scripts/                # Post-install provisioning scripts
├── platforms/
│   ├── pinebookpro.sh          # Pinebook Pro platform setup
│   ├── x13s.sh                 # Lenovo X13s (ARM) platform setup
│   └── README.md               # Platform documentation
├── pxelinux.cfg/
│   └── pxelinux.cfg.in         # PXE boot config template
├── vdocs/                      # Project documentation
│   ├── index.md
│   ├── ID/Docs.md
│   └── EN/Docs.md              ← You are here
├── vtools/
│   └── mkxbpskey.sh            # XBPS key generation utility
├── installer.sh                # T4n OS installer (Bash)
├── lib.sh                      # Shared function library
├── mkimage.sh                  # ARM flash-ready image generator
├── mkiso.sh                    # Full live ISO generator
├── mklive.sh                   # Basic live ISO generator
├── mknet.sh                    # Netboot/PXE tarball generator
├── mkplatformfs.sh             # PLATFORMFS generator
├── mkrootfs.sh                 # ROOTFS generator
├── release.sh                  # Release automation via GitHub CI
└── version                     # Release version
```

## Dependencies

> [!WARNING]
> t4n-live is **not guaranteed to work** on distributions other than Void Linux, or inside containers.

| Dependency | Notes |
|---|---|
| `xbps >= 0.45` | Void Linux package manager |
| `bash` | Shell interpreter |
| `liblz4` | lz4 compression for initramfs |
| `xz` | xz compression for initramfs & squashfs (default) |
| `qemu-user-static` | Required for `mkrootfs.sh` when cross-compiling architectures |

## Workflow

### 1. Building a Live ISO

**Full ISO** (recommended — includes `t4n-installer` and additional utilities):

```bash
sudo ./mkiso.sh -a x86_64 -b xfce
```

**Minimal ISO** (CLI only, no installer):

```bash
sudo ./mklive.sh -a x86_64
```

**ISO with extra packages, an overlay, and kernel arguments:**

```bash
sudo ./mkiso.sh -a x86_64 -b xfce -- \
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
sudo ./mkrootfs.sh x86_64
sudo ./mkrootfs.sh aarch64-musl
```

### 3. Building a PLATFORMFS (for ARM)

A PLATFORMFS is a ROOTFS **with a platform-specific kernel**. This step is required before creating an ARM image.

```bash
# Step 1: Build the ROOTFS first
sudo ./mkrootfs.sh aarch64

# Step 2: Build the PLATFORMFS
sudo ./mkplatformfs.sh rpi-aarch64 void-aarch64-ROOTFS-*.tar.xz
```

### 4. Building an ARM Image (Flash-ready)

ARM images contain a complete filesystem layout with 2 partitions (`/boot` and `/`), ready to be written to storage.

```bash
# Step 3: Generate the image
sudo ./mkimage.sh void-rpi-aarch64-PLATFORMFS-*.tar.xz

# Write it to the SD card
dd if=void-rpi-aarch64-*.img of=/dev/sdX bs=4M status=progress
```

> [!WARNING]
> Replace `/dev/sdX` with your actual SD card device. Verify with `lsblk`.

### 5. Building a Netboot Tarball

```bash
sudo ./mknet.sh void-x86_64-ROOTFS-*.tar.xz
```

### 6. Running the Installer

On x86 live images, `installer.sh` is installed as `/usr/bin/t4n-installer` (CLI), and Calamares is available as the GUI installer. Run it as root:

```bash
sudo t4n-installer
```

## Script Reference

### `mklive.sh`

```text
Usage: mklive.sh [options]

Generates a basic live ISO image of T4n OS. This ISO image can be written
to a CD/DVD-ROM or any USB stick.

To generate a more complete live ISO image, use mkiso.sh.

OPTIONS
 -a <arch>          Set XBPS_ARCH in the ISO image
 -b <system-pkg>    Set an alternative base package (default: base-system)
 -r <repo>          Use this XBPS repository. May be specified multiple times
 -c <cachedir>      Use this XBPS cache directory (default: ./xbps-cachedir-<arch>)
 -H <host_cachedir> Use this Host XBPS cache directory (default: ./xbps-cachedir-<host_arch>)
 -k <keymap>        Default keymap to use (default: us)
 -l <locale>        Default locale to use (default: en_US.UTF-8)
 -i <lz4|gzip|bzip2|xz>
                    Compression type for the initramfs image (default: xz)
 -s <gzip|lzo|xz>   Compression type for the squashfs image (default: xz)
 -o <file>          Output file name for the ISO image (default: automatic)
 -p "<pkg> ..."     Install additional packages in the ISO image
 -g "<pkg> ..."     Ignore packages when building the ISO image
 -I <includedir>    Include directory structure under given path in the ROOTFS
 -S "<service> ..." Enable services in the ISO image
 -e <shell>         Default shell of the root user (must be absolute path)
 -C "<arg> ..."     Add additional kernel command line arguments
 -P "<platform> ..." Platforms for aarch64 EFI ISO images (pinebookpro, x13s)
 -T <title>         Modify the bootloader title (default: T4n OS)
 -v linux<version>  Install a custom Linux version (default: linux metapackage)
 -x <script>        Path to a postsetup script to run before generating the initramfs
 -K                 Do not remove builddir
 -h                 Show this help and exit
 -V                 Show version and exit
```

### `mkiso.sh`

```text
Usage: mkiso.sh [options ...] [-- t4n-live options ...]

Wrapper script around mklive.sh for several standard flavors of live images.
Adds t4n-installer and other helpful utilities to the generated images.

OPTIONS
 -a <arch>     Set architecture (or platform) in the image
 -b <variant>  One of base, server, xfce, security, cosmic (COMING SOON). May be
               specified multiple times to build multiple variants (default: base)
 -d <date>     Override the datestamp on the generated image (YYYYMMDD format)
 -t <arch-date-variant>  Equivalent to setting -a, -b, and -d
 -r <repo>     Use this XBPS repository. May be specified multiple times
 -h            Show this help and exit
 -V            Show version and exit

Other options can be passed directly to mklive.sh by specifying them after the --.
```

### `mkrootfs.sh`

```text
Usage: mkrootfs.sh [options] <arch>

Supported architectures:
 i686, i686-musl, x86_64, x86_64-musl,
 armv5tel, armv5tel-musl, armv6l, armv6l-musl, armv7l, armv7l-musl
 aarch64, aarch64-musl,
 mipsel, mipsel-musl,
 ppc, ppc-musl, ppc64le, ppc64le-musl, ppc64, ppc64-musl
 riscv64, riscv64-musl

OPTIONS
 -b <system-pkg>  Set an alternative base-system package (default: base-container-full)
 -c <cachedir>    Set XBPS cache directory (default: ./xbps-cachedir-<arch>)
 -C <file>        Full path to the XBPS configuration file
 -r <repo>        Use this XBPS repository. May be specified multiple times
 -o <file>        Filename to write the ROOTFS to (default: automatic)
 -x <num>         Number of threads to use for image compression (default: dynamic)
 -z <format>      Compression format to use [xz, none] (default: xz)
 -h               Show this help and exit
 -V               Show version and exit
```

### `mkplatformfs.sh`

```text
Usage: mkplatformfs.sh [options] <platform> <rootfs-tarball>

Supported platforms: i686, x86_64, GCP,
                     rpi-armv6l, rpi-armv7l, rpi-aarch64,
                     pinebookpro, pinephone, rock64, rockpro64, asahi

OPTIONS
 -b <system-pkg>  Set an alternative base-system package (default: base-system)
 -c <cachedir>    Set the XBPS cache directory (default: ./xbps-cachedir-<arch>)
 -C <file>        Full path to the XBPS configuration file
 -k <cmd>         Call '<cmd> <ROOTFSPATH>' after building the ROOTFS
 -n               Do not compress the image, instead print out the ROOTFS directory
 -o <file>        Filename to write the PLATFORMFS archive to (default: automatic)
 -p "<pkg> ..."   Additional packages to install into the ROOTFS
 -r <repo>        Use this XBPS repository. May be specified multiple times
 -x <num>         Number of threads to use for image compression (default: dynamic)
 -h               Show this help and exit
 -V               Show version and exit
```

### `mkimage.sh`

```text
Usage: mkimage.sh [options] <platformfs-tarball>

OPTIONS
 -b <fstype>    /boot filesystem type (default: vfat)
 -B <bsize>     /boot filesystem size (default: 256MiB)
 -r <fstype>    / filesystem type (default: ext4)
 -s <totalsize> Total image size (default: 900MiB)
 -o <output>    Image filename (default: guessed automatically)
 -x <num>       Number of threads to use for image compression (default: dynamic)
 -h             Show this help and exit
 -V             Show version and exit

Accepted size suffixes: KiB, MiB, GiB, TiB, EiB.
```

### `mknet.sh`

```text
Usage: mknet.sh [options] <rootfs-tarball>

OPTIONS
 -r <repo>          Use this XBPS repository. May be specified multiple times
 -c <cachedir>      Use this XBPS cache directory (default: )
 -i <lz4|gzip|bzip2|xz>
                    Compression type for the initramfs image (default: xz)
 -o <file>          Output file name for the netboot tarball (default: automatic)
 -K linux<version>  Install a custom Linux version on ISO image (default: linux metapackage)
 -k <keymap>        Default keymap to use (default: us)
 -l <locale>        Default locale to use (default: en_US.UTF-8)
 -C "<arg> ..."     Add additional kernel command line arguments
 -T <title>         Modify the bootloader title (default: Void Linux)
 -S <image>         Set a custom splash image for the bootloader (default: data/splash.png)
 -h                 Show this help and exit
 -V                 Show version and exit
```

## common/ Configuration

The `common/` directory holds system configuration files bundled into the image during the build. It has four sub-directories: `cli/` and `gui/` (active), plus `security/` and `server/` (in development).

### `common/cli/config/lightdm/`

Configuration for **LightDM**, used by desktop variants:

- `lightdm.conf` — Main LightDM configuration (greeter, autologin, session)
- `lightdm-gtk-greeter.conf` — GTK greeter appearance (theme, icons, font)

### `common/cli/config/xbps.d/`

In-image XBPS configuration, including the glibc repository key (`10-glibc.conf`).

### `common/cli/polkit/`

**PolicyKit** rules that let regular users perform selected system operations without a password:

| File | Purpose |
|---|---|
| `20-networkmanager.rules` | Network management for regular users |

The backlight udev rule lives in `common/gui/config/etc/udev/rules.d/30-backlight.rules`.

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
| `99-cleanup.sh` | Clean up lock files and tmp |

**`runsvdir/default/`** — Services enabled by default: `agetty-tty1` through `agetty-tty6`, and `udevd`.

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

The T4n OS custom **GRUB theme** named **Sleek**:

- Image assets for background, selection bar, progress indicator, and slider
- Poppins (14/16/18/48pt) and Terminus (14pt) fonts in `.pf2` format
- `icons/` directory with 60+ Linux distribution icons for multi-boot menus
- `theme.txt` — GRUB theme layout definition

### `common/cli/service/pipewire/`

Setup script for the **PipeWire** service (audio server). Invoked during live environment initialization.

### `common/gui/`

GUI assets and configuration:

- `config/desktop/calamares.desktop` — Calamares launcher on the live desktop
- `config/etc/calamares/` — Calamares configuration (branding, modules, styling)
- `config/etc/polkit-1/rules.d/` and `config/etc/udev/rules.d/` — polkit & udev rules
- `config/wallpapers/` — T4n OS wallpapers
- `xfce/` — XFCE assets, configuration, and scripts
- `xorg.conf.d/10-touchpad.conf` — Touchpad configuration (libinput)
- `cosmic/` — COSMIC variant placeholder

## Kernel Command-line Parameters

| Parameter | Description |
|---|---|
| `live.autologin` | Skip the login screen on `tty1` |
| `live.user=<name>` | Change the non-root username (default: `anon`, password: `voidlinux`) |
| `live.shell=<path>` | Set the default shell for the non-root user |
| `live.accessibility` | Enable the `espeakup` screen reader |
| `console=ttyS0` | Enable a serial console (`ttyS0`, `hvc0`, `hvsi0`) |
| `locale.LANG=<locale>` | Set the `LANG` variable (default: `en_US.UTF-8`) |
| `vconsole.keymap=<keymap>` | Set the console keymap (default: `us`) |

### Example Combinations

```text
# Auto-login as user "jane" with bash shell
live.autologin live.user=jane live.shell=/bin/bash

# Serial console with French keymap
console=ttyS0 vconsole.keymap=fr

# Indonesian language
locale.LANG=id_ID.UTF-8

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
| `hcl2/vagrant/` | Vagrant build definitions (VirtualBox) |
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

## Release & CI

- `release.sh` — release build automation.
- `.github/workflows/gen-images.yml` — image build pipeline on GitHub Actions.
- `.github/workflows/container.yaml` — container image build.
- `keys/` — public keys (`.plist`) for package verification; private keys are not kept in the repository.

---

<div align="center">

[← Back to Index](../index.md) · [Versi Bahasa Indonesia](../ID/Docs.md) · [← README](../../README.md) · Built with ❤️ by [T4n-Labs](https://github.com/T4n-Labs)

</div>
