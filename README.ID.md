# t4n-live

> 🇮🇩 Bahasa Indonesia | 🇬🇧 [English](./README.md)

## T4n OS — Generator Live Image, Rootfs & Installer

**t4n-live** adalah kumpulan skrip shell untuk membangun live ISO image, rootfs tarball, dan filesystem image berbasis [Void Linux](https://voidlinux.org/), yang dikustomisasi untuk **T4n OS**.

### Kredensial Live System

| Field | Nilai |
|---|---|
| Username | `t4nos` |
| Password | `t4nlabs` |

> 📚 Dokumentasi lengkap tersedia di direktori [`vdocs/`](./vdocs/index.md).

## Struktur Repositori

```text
t4n-live/
├── common/                  # Konfigurasi sistem bersama
│   ├── cli/                 # Varian desktop/CLI: LightDM, Xorg, polkit, runit, tema GRUB
│   ├── gui/                 # Aset GUI: branding Calamares, wallpaper, XFCE
│   ├── security/            # Konfigurasi varian security (dalam pengembangan)
│   └── server/              # Konfigurasi varian server (dalam pengembangan)
├── container/               # Containerfile & Docker Bake (HCL)
├── data/                    # Aset data (splash screen, issue)
├── dracut/                  # Modul dracut (vmklive, autoinstaller, netmenu)
├── grub/                    # Template konfigurasi GRUB
├── isolinux/                # Konfigurasi ISOLINUX (legacy BIOS)
├── keys/                    # Public signing key (.plist)
├── packer/                  # Konfigurasi build Packer (QEMU, VirtualBox, Vagrant)
├── platforms/               # Skrip platform spesifik (pinebookpro, x13s)
├── pxelinux.cfg/            # Konfigurasi boot PXE
├── vdocs/                   # Dokumentasi proyek (ID & EN)
├── vtools/                  # Utilitas tambahan (mkxbpskey.sh)
├── installer.sh             # Installer T4n OS (Bash)
├── lib.sh                   # Library fungsi bersama
├── mkimage.sh               # Generator image ARM siap flash
├── mkiso.sh                 # Generator live ISO lengkap (wrapper)
├── mklive.sh                # Generator live ISO dasar
├── mknet.sh                 # Generator tarball netboot/PXE
├── mkplatformfs.sh          # Generator PLATFORMFS (platform spesifik)
├── mkrootfs.sh              # Generator ROOTFS
├── release.sh               # Otomasi rilis via GitHub CI
└── version                  # Nomor versi rilis
```

## Dependensi

> [!WARNING]
> t4n-live **tidak dijamin berfungsi** pada distribusi selain Void Linux, atau di dalam container.

- `xbps >= 0.45`
- `bash`
- Library kompresi initramfs: `liblz4` (untuk lz4) atau `xz` *(default: `xz`)*
- `qemu-user-static` — dibutuhkan oleh `mkrootfs.sh` untuk build lintas arsitektur

## Skrip Utama

| Skrip | Fungsi |
|---|---|
| `mklive.sh` | Generator live ISO dasar/minimalis |
| `mkiso.sh` | Generator live ISO lengkap dengan `t4n-installer` (i686, x86_64, aarch64) |
| `mkrootfs.sh` | Generator rootfs Void Linux untuk semua platform & arsitektur |
| `mkplatformfs.sh` | Generator rootfs platform-spesifik (dengan kernel, untuk ARM) |
| `mkimage.sh` | Generator image ARM siap-flash (`dd`) |
| `mknet.sh` | Generator tarball netboot/PXE |
| `installer.sh` | Penginstal OS T4n yang ditulis dalam Bash |
| `release.sh` | Otomasi rilis image melalui GitHub CI |

## Mulai Cepat

### Build Live ISO (x86_64, varian xfce)

```bash
sudo ./mkiso.sh -a x86_64 -b xfce
```

Opsi `-b` dapat diulang untuk membangun beberapa varian sekaligus:

```bash
sudo ./mkiso.sh -a x86_64 -b base -b xfce
```

### Build Live ISO dengan paket tambahan

Opsi `mklive.sh` diteruskan setelah `--`:

```bash
sudo ./mkiso.sh -a x86_64 -b xfce -- -p "firefox neovim git" -o T4nOS-xfce.iso
```

### Build Image ARM (Raspberry Pi 4)

```bash
# 1. Build ROOTFS
sudo ./mkrootfs.sh aarch64

# 2. Build PLATFORMFS
sudo ./mkplatformfs.sh rpi-aarch64 void-aarch64-ROOTFS-*.tar.xz

# 3. Generate image siap flash
sudo ./mkimage.sh void-rpi-aarch64-PLATFORMFS-*.tar.xz

# 4. Tulis ke SD card
dd if=void-rpi-aarch64-*.img of=/dev/sdX bs=4M status=progress
```

### Installer

Pada live image x86, `installer.sh` dipasang sebagai `/usr/bin/t4n-installer` (CLI) bersama installer GUI Calamares. Jalankan sebagai root dari sistem live:

```bash
sudo t4n-installer
```

## Varian yang Tersedia (`-b`)

| Varian | Deskripsi |
|---|---|
| `base` | Sistem dasar tanpa DE (default) |
| `xfce` | Desktop XFCE (X11) — otomatis memakai XFCE Wayland pada perangkat asahi |
| `security` | Belum tersedia |
| `server` | Belum tersedia |
| `cosmic` | Belum tersedia |

> [!NOTE]
> Varian `security`, `server`, dan `cosmic` masih dalam pengembangan dan akan berhenti dengan pesan `COMING SOON`.

## Parameter Kernel Command-line

| Parameter | Fungsi |
|---|---|
| `live.autologin` | Lewati layar login di `tty1` |
| `live.user=<nama>` | Ubah username non-root (default: `anon`, password: `voidlinux`) |
| `live.shell=<path>` | Set shell default user non-root |
| `live.accessibility` | Aktifkan screen reader `espeakup` |
| `console=ttyS0` | Aktifkan serial console (`ttyS0`, `hvc0`, `hvsi0`) |
| `locale.LANG=<locale>` | Set locale (default: `en_US.UTF-8`) |
| `vconsole.keymap=<keymap>` | Set keymap console (default: `us`) |

## Dokumentasi

- 📄 [Indeks dokumentasi](./vdocs/index.md)
- 🇮🇩 [Dokumentasi Bahasa Indonesia](./vdocs/ID/Docs.md)
- 🇬🇧 [Documentation in English](./vdocs/EN/Docs.md)

## Lisensi

Lihat file [COPYING](./COPYING) untuk informasi lisensi.

---

<div align="center">

Built with ❤️ by [T4n-Labs](https://github.com/T4n-Labs) · Based on [Void Linux](https://voidlinux.org/)

</div>
