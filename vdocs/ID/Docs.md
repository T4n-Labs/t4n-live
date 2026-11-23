# Dokumentasi T4n OS Live Image (Bahasa Indonesia)

> 🇬🇧 [English version](../EN/Docs.md) | [← Indeks](../index.md) | [← README](../../README.ID.md)

## Daftar Isi

- [Gambaran Umum](#gambaran-umum)
- [Struktur Repositori](#struktur-repositori)
- [Dependensi](#dependensi)
- [Alur Kerja](#alur-kerja)
- [Referensi Skrip](#referensi-skrip)
- [Konfigurasi common/](#konfigurasi-common)
- [Parameter Kernel Command-line](#parameter-kernel-command-line)
- [Packer & Container](#packer--container)
- [Rilis & CI](#rilis--ci)

## Gambaran Umum

**t4n-live** adalah generator live image dan rootfs untuk **T4n OS**, sebuah distribusi Linux berbasis [Void Linux](https://voidlinux.org/). Repositori ini menyediakan toolchain untuk:

- Membangun live ISO image yang bisa di-boot dari USB/CD
- Membangun ROOTFS tarball untuk instalasi via chroot atau container
- Membangun image ARM siap-flash untuk perangkat embedded (Raspberry Pi, Pinebook Pro, dll.)
- Membangun tarball netboot/PXE
- Membangun VM image via Packer (QEMU, VirtualBox, Vagrant)

Kredensial default live system: username `t4nos`, password `t4nlabs`.

### Skrip yang Tersedia

| Skrip | Fungsi |
|---|---|
| `mklive.sh` | Generator live ISO dasar/minimalis |
| `mkiso.sh` | Wrapper `mklive.sh` untuk ISO lengkap dengan `t4n-installer` (i686, x86_64, aarch64) |
| `mkrootfs.sh` | Generator rootfs Void Linux untuk semua platform & arsitektur |
| `mkplatformfs.sh` | Generator rootfs platform-spesifik (dengan kernel, untuk ARM) |
| `mkimage.sh` | Generator image ARM siap-flash (`dd`) |
| `mknet.sh` | Generator tarball netboot/PXE |
| `installer.sh` | Penginstal OS T4n yang ditulis dalam Bash |
| `release.sh` | Otomasi build dan rilis image melalui GitHub CI |

## Struktur Repositori

```text
t4n-live/
├── common/
│   ├── cli/                    # Konfigurasi varian desktop/CLI
│   │   ├── .bashrc             # Shell profile default
│   │   ├── config/
│   │   │   ├── lightdm/        # LightDM display manager
│   │   │   │   ├── lightdm-gtk-greeter.conf
│   │   │   │   └── lightdm.conf
│   │   │   └── xbps.d/         # Konfigurasi XBPS + key repo glibc
│   │   ├── grub                # Konfigurasi GRUB
│   │   ├── os-release          # Identitas OS
│   │   ├── polkit/
│   │   │   └── 20-networkmanager.rules
│   │   ├── resolv.conf         # Konfigurasi DNS
│   │   ├── runit/              # Init system runit
│   │   │   ├── 1, 2, 3         # Stage init runit
│   │   │   ├── core-services/  # Skrip init inti (udev, filesystem, swap, dll.)
│   │   │   ├── runsvdir/       # Direktori service aktif (agetty tty1-6, udevd)
│   │   │   └── shutdown.d/     # Skrip shutdown terurut
│   │   ├── service/
│   │   │   └── pipewire/       # Setup service PipeWire (audio)
│   │   └── sleek/              # Tema GRUB kustom T4n OS
│   │       ├── icons/          # Ikon distribusi untuk menu boot
│   │       ├── *.pf2           # Font Poppins & Terminus untuk GRUB
│   │       └── theme.txt       # Definisi tema GRUB
│   ├── gui/                    # Aset & konfigurasi GUI
│   │   ├── config/
│   │   │   ├── desktop/        # Launcher Calamares
│   │   │   ├── etc/            # Konfigurasi Calamares, polkit, udev
│   │   │   └── wallpapers/     # Wallpaper T4n OS
│   │   ├── cosmic/             # Varian COSMIC (COMING_SOON)
│   │   ├── xfce/               # Aset, konfigurasi, dan skrip XFCE
│   │   └── xorg.conf.d/
│   │       └── 10-touchpad.conf  # Konfigurasi touchpad (libinput)
│   ├── security/               # Konfigurasi varian security (ON_GOING)
│   └── server/                 # Konfigurasi varian server (coming-soon.md)
├── container/
│   ├── Containerfile           # OCI container image definition
│   └── docker-bake.hcl         # Docker Bake multi-target config
├── data/
│   ├── issue                   # Banner login terminal
│   └── splash.png              # Splash screen bootloader
├── dracut/
│   ├── autoinstaller/          # Modul auto-install
│   │   ├── autoinstall.cfg
│   │   ├── install.sh
│   │   ├── module-setup.sh
│   │   └── parse-vai-root.sh
│   ├── netmenu/                # Modul menu netboot interaktif
│   │   ├── module-setup.sh
│   │   └── netmenu.sh
│   └── vmklive/                # Modul inti live system
│       ├── adduser.sh          # Membuat user live
│       ├── accessibility.sh    # Setup aksesibilitas (espeakup)
│       ├── display-manager-autologin.sh
│       ├── getty-serial.sh     # Setup serial console
│       ├── locale.sh           # Setup locale
│       ├── mtd.sh              # Dukungan MTD
│       ├── nomodeset.sh        # Fallback grafis tanpa KMS
│       └── module-setup.sh
├── grub/
│   ├── grub.cfg                # Konfigurasi GRUB utama
│   ├── grub_void.cfg.pre       # Template pre-config GRUB
│   └── grub_void.cfg.post      # Template post-config GRUB
├── isolinux/
│   └── isolinux.cfg.in         # Template konfigurasi ISOLINUX (legacy BIOS)
├── keys/                       # Public key (.plist) untuk verifikasi paket
├── packer/
│   ├── hcl2/                   # Definisi build Packer HCL2 (QEMU, VirtualBox, cloud, Vagrant)
│   ├── http/                   # Preseed/kickstart untuk Packer
│   ├── plugins.pkr.hcl         # Deklarasi plugin Packer
│   └── scripts/                # Skrip provisioning post-install
├── platforms/
│   ├── pinebookpro.sh          # Setup platform Pinebook Pro
│   ├── x13s.sh                 # Setup platform Lenovo X13s (ARM)
│   └── README.md               # Dokumentasi platform
├── pxelinux.cfg/
│   └── pxelinux.cfg.in         # Template konfigurasi PXE boot
├── vdocs/                      # Dokumentasi proyek
│   ├── index.md
│   ├── ID/Docs.md              ← Kamu di sini
│   └── EN/Docs.md
├── vtools/
│   └── mkxbpskey.sh            # Utilitas pembuat key XBPS
├── installer.sh                # Installer T4n OS (Bash)
├── lib.sh                      # Library fungsi bersama
├── mkimage.sh                  # Generator image ARM siap flash
├── mkiso.sh                    # Generator live ISO lengkap
├── mklive.sh                   # Generator live ISO dasar
├── mknet.sh                    # Generator tarball netboot/PXE
├── mkplatformfs.sh             # Generator PLATFORMFS
├── mkrootfs.sh                 # Generator ROOTFS
├── release.sh                  # Otomasi rilis GitHub CI
└── version                     # Nomor versi rilis
```

## Dependensi

> [!WARNING]
> t4n-live **tidak dijamin berfungsi** pada distribusi selain Void Linux, atau di dalam container.

| Dependensi | Keterangan |
|---|---|
| `xbps >= 0.45` | Package manager Void Linux |
| `bash` | Shell interpreter |
| `liblz4` | Kompresi lz4 untuk initramfs |
| `xz` | Kompresi xz untuk initramfs & squashfs (default) |
| `qemu-user-static` | Diperlukan untuk `mkrootfs.sh` saat build cross-architecture |

## Alur Kerja

### 1. Membuat Live ISO

**ISO lengkap** (rekomendasi — menyertakan `t4n-installer` dan utilitas tambahan):

```bash
sudo ./mkiso.sh -a x86_64 -b xfce
```

**ISO dasar** (CLI only, tanpa installer):

```bash
sudo ./mklive.sh -a x86_64
```

**ISO dengan paket tambahan, overlay, dan argumen kernel:**

```bash
sudo ./mkiso.sh -a x86_64 -b xfce -- \
  -p "firefox neovim git htop" \
  -I ./my-overlay/ \
  -C "live.autologin live.shell=/bin/bash" \
  -o T4nOS-xfce-custom.iso
```

### 2. Membuat ROOTFS Tarball

ROOTFS berisi sistem Void Linux dasar **tanpa kernel**. Berguna untuk:

- [Instalasi via chroot](https://docs.voidlinux.org/installation/guides/chroot.html)
- [Container & chroot environments](https://docs.voidlinux.org/config/containers-and-vms/chroot.html)

```bash
sudo ./mkrootfs.sh x86_64
sudo ./mkrootfs.sh aarch64-musl
```

### 3. Membuat PLATFORMFS (untuk ARM)

PLATFORMFS adalah ROOTFS **dengan kernel** yang dikonfigurasi untuk platform spesifik. Langkah ini diperlukan sebelum membuat image ARM.

```bash
# Langkah 1: Buat ROOTFS dulu
sudo ./mkrootfs.sh aarch64

# Langkah 2: Buat PLATFORMFS
sudo ./mkplatformfs.sh rpi-aarch64 void-aarch64-ROOTFS-*.tar.xz
```

### 4. Membuat Image ARM (Siap Flash)

Image ARM berisi layout filesystem dengan 2 partisi (`/boot` dan `/`), siap ditulis ke storage.

```bash
# Langkah 3: Generate image
sudo ./mkimage.sh void-rpi-aarch64-PLATFORMFS-*.tar.xz

# Flash ke SD card
dd if=void-rpi-aarch64-*.img of=/dev/sdX bs=4M status=progress
```

> [!WARNING]
> Ganti `/dev/sdX` dengan device SD card yang benar. Cek dengan `lsblk`.

### 5. Membuat Tarball Netboot

```bash
sudo ./mknet.sh void-x86_64-ROOTFS-*.tar.xz
```

### 6. Menjalankan Installer

Pada live image x86, `installer.sh` disalin menjadi `/usr/bin/t4n-installer` (CLI) dan Calamares tersedia sebagai installer GUI. Jalankan sebagai root:

```bash
sudo t4n-installer
```

## Referensi Skrip

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

## Konfigurasi common/

Direktori `common/` menyimpan file konfigurasi sistem yang disertakan ke dalam image saat build. Terdiri dari empat sub-direktori: `cli/` dan `gui/` (aktif), serta `security/` dan `server/` (dalam pengembangan).

### `common/cli/config/lightdm/`

Konfigurasi **LightDM** untuk varian desktop:

- `lightdm.conf` — Konfigurasi utama LightDM (greeter, autologin, session)
- `lightdm-gtk-greeter.conf` — Tampilan greeter GTK (tema, ikon, font)

### `common/cli/config/xbps.d/`

Konfigurasi XBPS di dalam image, termasuk key repository glibc (`10-glibc.conf`).

### `common/cli/polkit/`

Aturan **PolicyKit** agar user biasa dapat melakukan operasi sistem tertentu tanpa password:

| File | Fungsi |
|---|---|
| `20-networkmanager.rules` | Izin manajemen jaringan untuk user biasa |

Aturan udev untuk backlight berada di `common/gui/config/etc/udev/rules.d/30-backlight.rules`.

### `common/cli/runit/`

Konfigurasi **runit** init system — sistem init yang digunakan Void Linux:

- **Stage 1 (`1`)** — Inisialisasi awal: mount pseudo-filesystem, setup udev, console
- **Stage 2 (`2`)** — Jalankan service daemon via `runsvdir`
- **Stage 3 (`3`)** — Cleanup saat shutdown

**`core-services/`** — Skrip init inti yang dijalankan di stage 1, berurutan berdasarkan prefix angka:

| Skrip | Fungsi |
|---|---|
| `00-pseudofs.sh` | Mount proc, sys, dev, devpts |
| `01-static-devnodes.sh` | Buat device node statis |
| `02-kmods.sh` | Load kernel modules |
| `02-udev.sh` | Mulai udev daemon |
| `03-console-setup.sh` | Setup font & keymap console |
| `03-filesystems.sh` | Mount filesystem dari fstab |
| `04-swap.sh` | Aktifkan swap |
| `05-misc.sh` | Setup hostname, loopback, waktu |
| `08-sysctl.sh` | Terapkan parameter sysctl |
| `98-sbin-merge.sh` | Merge /sbin ke /usr/bin |
| `99-cleanup.sh` | Bersihkan lock file dan tmp |

**`runsvdir/default/`** — Service aktif secara default: `agetty-tty1` hingga `agetty-tty6`, dan `udevd`.

**`shutdown.d/`** — Skrip shutdown berurutan saat sistem dimatikan:

| Skrip | Fungsi |
|---|---|
| `10-sv-stop.sh` | Hentikan semua service runit |
| `20-rc-shutdown.sh` | Jalankan rc.shutdown |
| `30-seedrng.sh` | Simpan entropy seed |
| `40-hwclock.sh` | Sinkronisasi jam hardware |
| `50-wtmp.sh` | Catat waktu shutdown ke wtmp |
| `60-udev.sh` | Hentikan udev |
| `70-pkill.sh` | Kill proses yang tersisa |
| `80-filesystems.sh` | Unmount filesystem |
| `90-kexec.sh` | Eksekusi kexec jika ada |

### `common/cli/sleek/`

Tema **GRUB kustom** T4n OS bernama **Sleek**:

- Aset gambar untuk background, selection bar, progress, dan slider
- Font Poppins (14/16/18/48pt) dan Terminus (14pt) dalam format `.pf2`
- Direktori `icons/` berisi 60+ ikon distribusi Linux untuk multi-boot
- `theme.txt` — definisi layout tema GRUB

### `common/cli/service/pipewire/`

Script setup untuk service **PipeWire** (audio server). Dipanggil saat environment live diinisialisasi.

### `common/gui/`

Aset dan konfigurasi GUI:

- `config/desktop/calamares.desktop` — Launcher Calamares di desktop live
- `config/etc/calamares/` — Konfigurasi Calamares (branding, modul, tampilan)
- `config/etc/polkit-1/rules.d/` dan `config/etc/udev/rules.d/` — Aturan polkit & udev
- `config/wallpapers/` — Wallpaper T4n OS
- `xfce/` — Aset, konfigurasi, dan skrip XFCE
- `xorg.conf.d/10-touchpad.conf` — Konfigurasi touchpad (libinput)
- `cosmic/` — Placeholder varian COSMIC

## Parameter Kernel Command-line

| Parameter | Fungsi |
|---|---|
| `live.autologin` | Skip login screen di `tty1` |
| `live.user=<nama>` | Ubah username non-root (default: `anon`, password: `voidlinux`) |
| `live.shell=<path>` | Set shell default user non-root di environment live |
| `live.accessibility` | Aktifkan screen reader `espeakup` |
| `console=ttyS0` | Aktifkan agetty di serial console (`ttyS0`, `hvc0`, `hvsi0`) |
| `locale.LANG=<locale>` | Set variabel LANG (default: `en_US.UTF-8`) |
| `vconsole.keymap=<keymap>` | Set keymap console (default: `us`) |

### Contoh Kombinasi

```text
# Login otomatis user "upi" dengan bash
live.autologin live.user=upi live.shell=/bin/bash

# Serial console + keymap Prancis
console=ttyS0 vconsole.keymap=fr

# Bahasa Indonesia
locale.LANG=id_ID.UTF-8

# Aktifkan aksesibilitas
live.accessibility live.autologin
```

## Packer & Container

### Packer

Direktori `packer/` berisi konfigurasi [HashiCorp Packer](https://www.packer.io/) untuk membangun VM image secara otomatis:

| File | Fungsi |
|---|---|
| `hcl2/source-qemu.pkr.hcl` | Source QEMU/KVM untuk build VM |
| `hcl2/source-virtualbox-ose.pkr.hcl` | Source VirtualBox OSE |
| `hcl2/build-cloud-generic.pkr.hcl` | Build cloud-generic image |
| `hcl2/build-vagrant.pkr.hcl` | Build Vagrant box |
| `hcl2/vagrant/` | Definisi build Vagrant (VirtualBox) |
| `plugins.pkr.hcl` | Deklarasi plugin yang dibutuhkan |
| `http/*.cfg` | File preseed/kickstart untuk auto-install |
| `scripts/cloud.sh` | Provisioning untuk cloud image |
| `scripts/vagrant.sh` | Provisioning untuk Vagrant box |

```bash
# Install plugin Packer
packer init packer/plugins.pkr.hcl

# Build QEMU image
packer build packer/hcl2/source-qemu.pkr.hcl
```

### Container

```bash
# Build container image
podman build -f container/Containerfile -t t4n-live:latest

# Atau dengan Docker Bake
docker buildx bake -f container/docker-bake.hcl
```

## Rilis & CI

- `release.sh` — otomasi build dan rilis image.
- `.github/workflows/gen-images.yml` — pipeline build image di GitHub Actions.
- `.github/workflows/container.yaml` — build container image.
- `keys/` — public key (`.plist`) untuk verifikasi paket; key privat tidak disimpan di repositori.

---

<div align="center">

[← Kembali ke Indeks](../index.md) · [English version](../EN/Docs.md) · [← README](../../README.ID.md) · Built with ❤️ by [T4n-Labs](https://github.com/T4n-Labs)

</div>
