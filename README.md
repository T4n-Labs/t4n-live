# t4n-live

> 🇮🇩 [Bahasa Indonesia](#bahasa-indonesia) | 🇬🇧 [English](#english)

<a name="bahasa-indonesia"></a>
# 🇮🇩 Bahasa Indonesia

## T4n OS — Generator Live Image, Rootfs & Installer

**t4n-live** adalah kumpulan skrip shell untuk membangun live ISO image, rootfs tarball, dan filesystem image berbasis [Void Linux](https://voidlinux.org/) yang dikustomisasi untuk **T4n OS**.

> 📚 Dokumentasi lengkap tersedia di direktori [`VDocs/`](./VDocs/index.md)

## Struktur Repositori

```
t4n-live/
├── common/              # Konfigurasi sistem bersama (CLI & Server)
│   ├── cli/             # Konfigurasi untuk varian desktop/CLI
│   │   ├── config/      # LightDM, xorg, dll.
│   │   ├── grub/        # Konfigurasi GRUB
│   │   ├── polkit/      # Aturan PolicyKit
│   │   ├── runit/       # Init system (runit stage 1/2/3, services)
│   │   ├── service/     # Setup service tambahan (pipewire, dll.)
│   │   ├── sleek/       # Tema GRUB kustom T4n OS
│   │   └── xorg.conf.d/ # Konfigurasi Xorg
│   └── server/          # Konfigurasi untuk varian server (coming soon)
├── container/           # Containerfile & Docker Bake HCL
├── data/                # Aset data (splash screen, issue)
├── dracut/              # Modul dracut (vmklive, autoinstaller, netmenu)
├── grub/                # Template konfigurasi GRUB
├── isolinux/            # Konfigurasi bootloader ISOLINUX (legacy BIOS)
├── keys/                # Signing keys
├── packer/              # Build config Packer (QEMU, VirtualBox, Vagrant)
├── platforms/           # Skrip platform-spesifik (pinebookpro, x13s)
├── pxelinux.cfg/        # Konfigurasi PXE boot
├── VDocs/               # Dokumentasi proyek (ID & EN)
│   ├── index.md         # Indeks dokumentasi
│   ├── ID/Docs.md       # Dokumentasi Bahasa Indonesia
│   └── EN/Docs.md       # Dokumentasi English
├── t4n-live.sh          # Generator live ISO dasar
├── t4n-iso.sh           # Generator live ISO lengkap (wrapper)
├── t4n-rootfs.sh        # Generator ROOTFS tarball
├── t4n-platformfs.sh    # Generator PLATFORMFS (platform-spesifik)
├── t4n-image.sh         # Generator image ARM (dd-ready)
├── t4n-net.sh           # Generator tarball netboot
├── installer.sh         # Installer el-cheapo x86
├── release.sh           # Skrip rilis & signing (GitHub CI)
├── lib.sh               # Library fungsi bersama
└── VNote.md             # Catatan pengembangan
```

## Dependensi

> ⚠️ t4n-live **tidak dijamin berfungsi** pada distribusi selain Void Linux, atau di dalam container.

- `xbps >= 0.45`
- `bash`
- Library kompresi initramfs: `liblz4` (untuk lz4) atau `xz` *(default: xz)*
- `qemu-user-static` — dibutuhkan untuk `t4n-rootfs.sh` (cross-arch build)

## Skrip Utama

| Skrip | Fungsi |
|---|---|
| `t4n-live.sh` | Generator live ISO T4n OS (dasar/minimalis) |
| `t4n-iso.sh` | Generator live ISO lengkap dengan `void-installer` (i686, x86\_64, aarch64) |
| `t4n-rootfs.sh` | Generator rootfs Void Linux untuk semua platform & arsitektur |
| `t4n-platformfs.sh` | Generator rootfs platform-spesifik (dengan kernel, untuk ARM) |
| `t4n-image.sh` | Generator image ARM siap-flash (`dd`) |
| `t4n-net.sh` | Generator tarball netboot/PXE |
| `installer.sh` | Installer el-cheapo Void Linux/T4n OS untuk x86 |
| `release.sh` | Berinteraksi dengan GitHub CI untuk build & signing rilis |

## Quick Start

### Build Live ISO (x86\_64, varian xfce)

```bash
sudo ./t4n-iso.sh -a x86_64 -b xfce
```

### Build Live ISO dengan paket tambahan

```bash
sudo ./t4n-iso.sh -a x86_64 -b xfce -- -p "firefox neovim git" -o T4nOS-xfce.iso
```

### Build Image ARM (Raspberry Pi 4)

```bash
# 1. Build ROOTFS
sudo ./t4n-rootfs.sh aarch64

# 2. Build PLATFORMFS
sudo ./t4n-platformfs.sh rpi-aarch64 void-aarch64-ROOTFS-*.tar.xz

# 3. Generate image siap flash
sudo ./t4n-image.sh void-aarch64-ROOTFS-*.tar.xz
```

### Varian yang Tersedia (`-b`)

| Varian | Deskripsi |
|---|---|
| `base` | Sistem dasar tanpa DE |
| `server` | Varian server headless |
| `xfce` | Desktop XFCE (X11) |
| `xfce-wayland` | Desktop XFCE (Wayland) |

[!Note!] : Varian Server Belum Tersedia

## Parameter Kernel Command-line

| Parameter | Fungsi |
|---|---|
| `live.autologin` | Skip login screen di `tty1` |
| `live.user=<nama>` | Ubah username non-root (default: `anon`, password: `voidlinux`) |
| `live.shell=<path>` | Set shell default user non-root |
| `live.accessibility` | Aktifkan screen reader `espeakup` |
| `console=ttyS0` | Aktifkan serial console (`ttyS0`, `hvc0`, `hvsi0`) |
| `locale.LANG=<locale>` | Set locale (default: `en_US.UTF-8`) |
| `vconsole.keymap=<keymap>` | Set keymap console (default: `us`) |

## Dokumentasi

Dokumentasi lengkap tersedia di direktori **VDocs**:

- 📄 [Indeks Dokumentasi](./VDocs/index.md)
- 🇮🇩 [Dokumentasi Bahasa Indonesia](./VDocs/ID/Docs.md)
- 🇬🇧 [Documentation in English](./VDocs/EN/Docs.md)

## Lisensi

Lihat file [COPYING](./COPYING) untuk informasi lisensi.

<a name="english"></a>
# 🇬🇧 English

## T4n OS — Live Image, Rootfs & Installer Generator

**t4n-live** is a collection of shell scripts for building live ISO images, rootfs tarballs, and filesystem images based on [Void Linux](https://voidlinux.org/), customized for **T4n OS**.

> 📚 Full documentation is available in the [`VDocs/`](./VDocs/index.md) directory.

## Repository Structure

```
t4n-live/
├── common/              # Shared system configurations (CLI & Server)
│   ├── cli/             # Configurations for desktop/CLI variants
│   │   ├── config/      # LightDM, xorg, etc.
│   │   ├── grub/        # GRUB configuration
│   │   ├── polkit/      # PolicyKit rules
│   │   ├── runit/       # Init system (runit stage 1/2/3, services)
│   │   ├── service/     # Additional service setup (pipewire, etc.)
│   │   ├── sleek/       # T4n OS custom GRUB theme
│   │   └── xorg.conf.d/ # Xorg configuration
│   └── server/          # Server variant configurations (coming soon)
├── container/           # Containerfile & Docker Bake HCL
├── data/                # Data assets (splash screen, issue)
├── dracut/              # Dracut modules (vmklive, autoinstaller, netmenu)
├── grub/                # GRUB configuration templates
├── isolinux/            # ISOLINUX bootloader config (legacy BIOS)
├── keys/                # Signing keys
├── packer/              # Packer build configs (QEMU, VirtualBox, Vagrant)
├── platforms/           # Platform-specific scripts (pinebookpro, x13s)
├── pxelinux.cfg/        # PXE boot configuration
├── VDocs/               # Project documentation (ID & EN)
│   ├── index.md         # Documentation index
│   ├── ID/Docs.md       # Indonesian documentation
│   └── EN/Docs.md       # English documentation
├── t4n-live.sh          # Basic live ISO generator
├── t4n-iso.sh           # Full live ISO generator (wrapper)
├── t4n-rootfs.sh        # ROOTFS tarball generator
├── t4n-platformfs.sh    # Platform-specific PLATFORMFS generator
├── t4n-image.sh         # ARM image generator (dd-ready)
├── t4n-net.sh           # Netboot tarball generator
├── installer.sh         # El-cheapo x86 installer
├── release.sh           # Release & signing script (GitHub CI)
├── lib.sh               # Shared function library
└── VNote.md             # Development notes
```

## Dependencies

> ⚠️ t4n-live is **not guaranteed to work** on distributions other than Void Linux, or inside containers.

- `xbps >= 0.45`
- `bash`
- Initramfs compression library: `liblz4` (for lz4) or `xz` *(default: xz)*
- `qemu-user-static` — required for `t4n-rootfs.sh` (cross-architecture builds)

## Main Scripts

| Script | Description |
|---|---|
| `t4n-live.sh` | Basic/minimal T4n OS live ISO generator |
| `t4n-iso.sh` | Full live ISO generator with `void-installer` (i686, x86\_64, aarch64) |
| `t4n-rootfs.sh` | Void Linux rootfs generator for all platforms & architectures |
| `t4n-platformfs.sh` | Platform-specific rootfs generator (with kernel, for ARM) |
| `t4n-image.sh` | ARM flash-ready image generator (`dd`) |
| `t4n-net.sh` | Netboot/PXE tarball generator |
| `installer.sh` | El-cheapo Void Linux/T4n OS installer for x86 |
| `release.sh` | Interacts with GitHub CI to build & sign release images |

## Quick Start

### Build a Live ISO (x86\_64, xfce variant)

```bash
sudo ./t4n-iso.sh -a x86_64 -b xfce
```

### Build a Live ISO with extra packages

```bash
sudo ./t4n-iso.sh -a x86_64 -b xfce -- -p "firefox neovim git" -o T4nOS-xfce.iso
```

### Build an ARM Image (Raspberry Pi 4)

```bash
# 1. Build ROOTFS
sudo ./t4n-rootfs.sh aarch64

# 2. Build PLATFORMFS
sudo ./t4n-platformfs.sh rpi-aarch64 void-aarch64-ROOTFS-*.tar.xz

# 3. Generate flash-ready image
sudo ./t4n-image.sh void-rpi-aarch64-PLATFORMFS-*.tar.xz
```

### Available Variants (`-b`)

| Variant | Description |
|---|---|
| `base` | Minimal base system without a DE |
| `server` | Headless server variant |
| `xfce` | XFCE desktop (X11) |
| `xfce-wayland` | XFCE desktop (Wayland) |

[!Note!] : Server Variant Not Yet Available

## Kernel Command-line Parameters

| Parameter | Description |
|---|---|
| `live.autologin` | Skip login screen on `tty1` |
| `live.user=<name>` | Change non-root username (default: `anon`, password: `voidlinux`) |
| `live.shell=<path>` | Set the default shell for the non-root user |
| `live.accessibility` | Enable `espeakup` screen reader |
| `console=ttyS0` | Enable serial console (`ttyS0`, `hvc0`, `hvsi0`) |
| `locale.LANG=<locale>` | Set locale (default: `en_US.UTF-8`) |
| `vconsole.keymap=<keymap>` | Set console keymap (default: `us`) |

## Documentation

Full documentation is available in the **VDocs** directory:

- 📄 [Documentation Index](./VDocs/index.md)
- 🇮🇩 [Dokumentasi Bahasa Indonesia](./VDocs/ID/Docs.md)
- 🇬🇧 [Documentation in English](./VDocs/EN/Docs.md)

## License

See the [COPYING](./COPYING) file for license information.

---

<div align="center">

Built with ❤️ by [T4n-Labs](https://github.com/T4n-Labs) · Based on [Void Linux](https://voidlinux.org/)

</div>
