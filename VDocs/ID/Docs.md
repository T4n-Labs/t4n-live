# Dokumentasi T4n OS Live Image (Bahasa Indonesia)

> 🇬🇧 [English version](../EN/Docs.md) | [← Indeks](../index.md) | [← README](../../README.md)

## Daftar Isi

- [Gambaran Umum](#gambaran-umum)
- [Struktur Repositori](#struktur-repositori)
- [Dependensi](#dependensi)
- [Alur Kerja](#alur-kerja)
- [Referensi Skrip](#referensi-skrip)
- [Konfigurasi common/](#konfigurasi-common)
- [Parameter Kernel Command-line](#parameter-kernel-command-line)
- [Packer & Container](#packer--container)
<!-- - [Rilis & Signing](#rilis--signing) -->

## Gambaran Umum

**t4n-live** adalah generator live image dan rootfs untuk **T4n OS**, sebuah distribusi Linux berbasis [Void Linux](https://voidlinux.org/). Repository ini menyediakan toolchain lengkap untuk:

- Membangun live ISO image yang bisa di-boot dari USB/CD
- Membangun ROOTFS tarball untuk instalasi via chroot
- Membangun image ARM siap-flash untuk perangkat embedded (Raspberry Pi, Pinebook Pro, dll.)
- Membangun tarball netboot/PXE
- Membangun VM image via Packer (QEMU, VirtualBox, Vagrant)

### Skrip yang Tersedia

| Skrip | Fungsi |
|---|---|
| `t4n-live.sh` | Generator live ISO T4n OS (dasar/minimalis) |
| `t4n-iso.sh` | Generator live ISO lengkap dengan `void-installer` |
| `t4n-rootfs.sh` | Generator ROOTFS tarball untuk semua arsitektur |
| `t4n-platformfs.sh` | Generator PLATFORMFS (rootfs + kernel, untuk ARM) |
| `t4n-image.sh` | Generator image ARM siap-flash (`dd`) |
| `t4n-net.sh` | Generator tarball netboot/PXE |
| `installer.sh` | Installer el-cheapo Void Linux/T4n OS untuk x86 |
| `release.sh` | Build & signing image untuk GitHub CI |
| `lib.sh` | Library fungsi bersama (dipakai skrip lain) |

## Struktur Repositori

```
t4n-live/
├── common/
│   ├── cli/                    # Konfigurasi varian desktop/CLI
│   │   ├── config/
│   │   │   └── lightdm/        # Konfigurasi LightDM display manager
│   │   │       ├── lightdm-gtk-greeter.conf
│   │   │       └── lightdm.conf
│   │   ├── grub                # Konfigurasi GRUB bootloader
│   │   ├── os-release          # Identitas OS
│   │   ├── polkit/             # Aturan PolicyKit (autorisasi sistem)
│   │   │   ├── 10-bspwm.rules
│   │   │   ├── 20-networkmanager.rules
│   │   │   └── 30-backlight.rules
│   │   ├── resolv.conf         # Konfigurasi DNS
│   │   ├── runit/              # Init system berbasis runit
│   │   │   ├── 1, 2, 3         # Stage init runit
│   │   │   ├── core-services/  # Skrip init inti (udev, filesystem, swap, dll.)
│   │   │   ├── runsvdir/       # Direktori service aktif
│   │   │   │   ├── default/    # Service default (agetty tty1-6, udevd)
│   │   │   │   └── single/     # Mode single user
│   │   │   └── shutdown.d/     # Skrip shutdown terurut (sv-stop, hwclock, dll.)
│   │   ├── service/
│   │   │   └── pipewire/       # Setup service PipeWire (audio)
│   │   ├── sleek/              # Tema GRUB kustom T4n OS
│   │   │   ├── icons/          # Ikon distribusi untuk bootloader
│   │   │   ├── *.pf2           # Font Poppins & Terminus untuk GRUB
│   │   │   └── theme.txt       # Definisi tema GRUB
│   │   └── xorg.conf.d/
│   │       └── 10-touchpad.conf  # Konfigurasi touchpad (libinput)
│   └── server/
│       └── coming-soon.md      # Konfigurasi server (dalam pengembangan)
├── container/
│   ├── Containerfile           # OCI container image definition
│   └── docker-bake.hcl         # Docker Bake multi-target config
├── data/
│   ├── issue                   # Pesan banner login terminal
│   └── splash.png              # Splash screen bootloader
├── dracut/
│   ├── autoinstaller/          # Modul auto-install (VAI)
│   │   ├── autoinstall.cfg     # Konfigurasi auto-install
│   │   ├── install.sh
│   │   ├── module-setup.sh
│   │   └── parse-vai-root.sh
│   ├── netmenu/                # Modul menu netboot interaktif
│   │   ├── module-setup.sh
│   │   └── netmenu.sh
│   └── vmklive/                # Modul inti live system
│       ├── adduser.sh          # Membuat user live (anon)
│       ├── locale.sh           # Setup locale
│       ├── display-manager-autologin.sh
│       ├── accessibility.sh    # Setup aksesibilitas (espeakup)
│       ├── getty-serial.sh     # Setup serial console
│       ├── nomodeset.sh        # Fallback grafis tanpa KMS
│       └── module-setup.sh
├── grub/
│   ├── grub.cfg                # Konfigurasi GRUB utama
│   ├── grub_void.cfg.pre       # Template pre-config GRUB
│   └── grub_void.cfg.post      # Template post-config GRUB
├── isolinux/
│   └── isolinux.cfg.in         # Template konfigurasi ISOLINUX (legacy BIOS)
├── keys/                       # Public key untuk verifikasi paket
├── packer/
│   ├── hcl2/                   # Packer HCL2 build definitions
│   │   ├── build-cloud-generic.pkr.hcl
│   │   ├── build-vagrant.pkr.hcl
│   │   ├── source-qemu.pkr.hcl
│   │   └── source-virtualbox-ose.pkr.hcl
│   ├── http/                   # Preseed/kickstart config untuk Packer
│   ├── plugins.pkr.hcl         # Deklarasi plugin Packer
│   └── scripts/                # Skrip provisioning post-install
│       ├── cloud.sh
│       └── vagrant.sh
├── platforms/
│   ├── pinebookpro.sh          # Setup platform Pinebook Pro
│   ├── x13s.sh                 # Setup platform Lenovo X13s (ARM)
│   └── README.md               # Dokumentasi platform
├── pxelinux.cfg/
│   └── pxelinux.cfg.in         # Template konfigurasi PXE boot
├── VDocs/                      # Dokumentasi proyek
│   ├── index.md
│   ├── ID/Docs.md              ← Kamu di sini
│   └── EN/Docs.md
├── t4n-live.sh
├── t4n-iso.sh
├── t4n-rootfs.sh
├── t4n-platformfs.sh
├── t4n-image.sh
├── t4n-net.sh
├── installer.sh
├── release.sh
├── lib.sh
└── VNote.md                    # Catatan pengembangan internal
```

## Dependensi

> ⚠️ t4n-live **tidak dijamin berfungsi** pada distribusi selain Void Linux, atau di dalam container.

| Dependensi | Keterangan |
|---|---|
| `xbps >= 0.45` | Package manager Void Linux |
| `bash` | Shell interpreter |
| `liblz4` | Kompresi lz4 untuk initramfs |
| `xz` | Kompresi xz untuk initramfs & squashfs (default) |
| `qemu-user-static` | Diperlukan untuk `t4n-rootfs.sh` saat build cross-architecture |

## Alur Kerja

### 1. Membuat Live ISO

**ISO Lengkap** (disarankan — menyertakan `void-installer` dan utilitas tambahan):

```bash
sudo ./t4n-iso.sh -a x86_64 -b xfce
```

**ISO Dasar** (Base/CLI Only):

```bash
sudo ./t4n-live.sh -a x86_64
```

**ISO dengan paket tambahan dan direktori kustom:**

```bash
sudo ./t4n-iso.sh -a x86_64 -b xfce -- \
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
sudo ./t4n-rootfs.sh x86_64
sudo ./t4n-rootfs.sh aarch64-musl
```

### 3. Membuat PLATFORMFS (untuk ARM)

PLATFORMFS adalah ROOTFS **dengan kernel** yang dikonfigurasi untuk platform spesifik. Langkah ini diperlukan sebelum membuat image ARM.

```bash
# Langkah 1: Buat ROOTFS dulu
sudo ./t4n-rootfs.sh aarch64

# Langkah 2: Buat PLATFORMFS
sudo ./t4n-platformfs.sh rpi-aarch64 void-aarch64-ROOTFS-*.tar.xz
```

### 4. Membuat Image ARM (Siap Flash)

Image ARM berisi layout filesystem lengkap dengan 2 partisi (`/boot` dan `/`) siap di-flash ke storage.

```bash
# Langkah 3: Generate image
sudo ./t4n-image.sh void-rpi-aarch64-PLATFORMFS-*.tar.xz

# Flash ke SD card
dd if=void-rpi-aarch64-*.img of=/dev/sdX bs=4M status=progress
```

> ⚠️ Ganti `/dev/sdX` dengan device SD card yang benar. Cek dengan `lsblk`.

### 5. Membuat Tarball Netboot

```bash
sudo ./t4n-net.sh void-x86_64-ROOTFS-*.tar.xz
```
## Referensi Skrip

### `t4n-live.sh`

```
Usage: t4n-live.sh [options]

OPTIONS
 -a <arch>          Set arsitektur (XBPS_ARCH) pada ISO image
 -b <system-pkg>    Set paket base alternatif (default: base-system)
 -r <repo>          Gunakan XBPS repository ini (bisa diulang)
 -c <cachedir>      Direktori cache XBPS (default: ./xbps-cachedir-<arch>)
 -H <host_cachedir> Direktori cache XBPS host
 -k <keymap>        Keymap default (default: us)
 -l <locale>        Locale default (default: en_US.UTF-8)
 -i <lz4|gzip|bzip2|xz>   Kompresi initramfs (default: xz)
 -s <gzip|lzo|xz>   Kompresi squashfs (default: xz)
 -o <file>          Nama file output ISO (default: otomatis)
 -p "<pkg> ..."     Install paket tambahan di ISO
 -g "<pkg> ..."     Abaikan paket saat build ISO
 -I <includedir>    Sertakan direktori ke dalam ROOTFS
 -S "<service> ..." Aktifkan service di ISO
 -e <shell>         Shell default user root (path absolut)
 -C "<arg> ..."     Tambah argumen kernel command line
 -P "<platform> ..." Platform untuk aarch64 EFI ISO (pinebookpro, x13s)
 -T <title>         Judul bootloader (default: T4n OS)
 -v linux<version>  Versi Linux kustom (default: linux metapackage)
 -x <script>        Path ke postsetup script sebelum generate initramfs
 -K                 Jangan hapus builddir setelah build
 -h                 Tampilkan bantuan
 -V                 Tampilkan versi
```

### `t4n-iso.sh`

```
Usage: t4n-iso.sh [options ...] [-- t4n-live options ...]

OPTIONS
 -a <arch>     Arsitektur atau platform image
 -b <variant>  Varian: base | server | xfce | xfce-wayland (default: base)
               Bisa diulang untuk build beberapa varian sekaligus
 -d <date>     Override datestamp (format: YYYYMMDD)
 -t <arch-date-variant>  Setara dengan -a, -b, -d sekaligus
 -r <repo>     Gunakan XBPS repository ini (bisa diulang)
 -h            Tampilkan bantuan
 -V            Tampilkan versi

Opsi tambahan bisa diteruskan ke t4n-live.sh dengan -- setelah opsi ini.
```

### `t4n-rootfs.sh`

```
Usage: t4n-rootfs.sh [options] <arch>

Arsitektur yang didukung:
  i686, i686-musl, x86_64, x86_64-musl,
  armv5tel, armv5tel-musl, armv6l, armv6l-musl, armv7l, armv7l-musl,
  aarch64, aarch64-musl,
  mipsel, mipsel-musl,
  ppc, ppc-musl, ppc64le, ppc64le-musl, ppc64, ppc64-musl,
  riscv64, riscv64-musl

OPTIONS
 -b <system-pkg>  Paket base-system alternatif (default: base-container-full)
 -c <cachedir>    Direktori cache XBPS
 -C <file>        Path ke file konfigurasi XBPS
 -r <repo>        Gunakan XBPS repository ini (bisa diulang)
 -o <file>        Nama file output ROOTFS (default: otomatis)
 -x <num>         Jumlah thread kompresi (default: dinamis)
 -h               Tampilkan bantuan
 -V               Tampilkan versi
```

### `t4n-platformfs.sh`

```
Usage: t4n-platformfs.sh [options] <platform> <rootfs-tarball>

Platform yang didukung:
  i686, x86_64, GCP,
  rpi-armv6l, rpi-armv7l, rpi-aarch64,
  pinebookpro, pinephone, rock64, rockpro64, asahi

OPTIONS
 -b <system-pkg>  Paket base-system alternatif (default: base-system)
 -c <cachedir>    Direktori cache XBPS
 -C <file>        Path ke file konfigurasi XBPS
 -k <cmd>         Jalankan '<cmd> <ROOTFSPATH>' setelah build selesai
 -n               Jangan kompresi, tampilkan direktori ROOTFS
 -o <file>        Nama file output PLATFORMFS (default: otomatis)
 -p "<pkg> ..."   Paket tambahan untuk diinstall ke ROOTFS
 -r <repo>        Gunakan XBPS repository ini (bisa diulang)
 -x <num>         Jumlah thread kompresi (default: dinamis)
 -h               Tampilkan bantuan
 -V               Tampilkan versi
```

### `t4n-image.sh`

```
Usage: t4n-image.sh [options] <platformfs-tarball>

OPTIONS
 -b <fstype>    Tipe filesystem /boot (default: vfat)
 -B <bsize>     Ukuran /boot (default: 256MiB)
 -r <fstype>    Tipe filesystem / (default: ext4)
 -s <totalsize> Total ukuran image (default: 900MiB)
 -o <file>      Nama file image (default: otomatis)
 -x <num>       Jumlah thread kompresi (default: dinamis)
 -h             Tampilkan bantuan
 -V             Tampilkan versi

Satuan ukuran yang diterima: KiB, MiB, GiB, TiB, EiB
```

### `t4n-net.sh`

```
Usage: t4n-net.sh [options] <rootfs-tarball>

OPTIONS
 -r <repo>          XBPS repository (bisa diulang)
 -c <cachedir>      Direktori cache XBPS
 -i <lz4|gzip|bzip2|xz>   Kompresi initramfs (default: xz)
 -o <file>          Nama file output tarball netboot (default: otomatis)
 -K linux<version>  Versi Linux kustom (default: linux metapackage)
 -k <keymap>        Keymap default (default: us)
 -l <locale>        Locale default (default: en_US.UTF-8)
 -C "<arg> ..."     Argumen kernel command line tambahan
 -T <title>         Judul bootloader (default: Void Linux)
 -S <image>         Splash image kustom (default: data/splash.png)
 -h                 Tampilkan bantuan
 -V                 Tampilkan versi
```

## Konfigurasi common/

Direktori `common/` menyimpan file konfigurasi sistem yang disertakan ke dalam image saat build. Saat ini terdiri dari dua sub-direktori: `cli/` (aktif) dan `server/` (dalam pengembangan).

### `common/cli/config/lightdm/`

Berisi konfigurasi untuk **LightDM** display manager yang digunakan pada varian desktop (xfce, xfce-wayland):

- `lightdm.conf` — Konfigurasi utama LightDM (greeter, autologin, session)
- `lightdm-gtk-greeter.conf` — Konfigurasi tampilan greeter GTK (tema, ikon, font)

### `common/cli/polkit/`

Berisi aturan **PolicyKit** untuk autorisasi operasi sistem tanpa password:

| File | Fungsi |
|---|---|
| `10-bspwm.rules` | Izin untuk window manager BSPWM |
| `20-networkmanager.rules` | Izin manajemen jaringan untuk user biasa |
| `30-backlight.rules` | Izin kontrol kecerahan layar |

### `common/cli/runit/`

Konfigurasi **runit** init system — sistem init yang digunakan Void Linux:

- **Stage 1 (`1`)** — Inisialisasi awal: mount pseudo-filesystem, setup udev, console
- **Stage 2 (`2`)** — Jalankan service daemon via `runsvdir`
- **Stage 3 (`3`)** — Cleanup saat shutdown

**`core-services/`** — Skrip init inti yang dijalankan di stage 1, dieksekusi berurutan berdasarkan prefix angka:

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
| `99-cleanup.sh` | Bersihkan lock file, tmp |

**`runsvdir/default/`** — Service yang aktif secara default:
`agetty-tty1` hingga `agetty-tty6` (login terminal), `udevd`

**`shutdown.d/`** — Skrip shutdown dijalankan berurutan saat sistem mati:

| Skrip | Fungsi |
|---|---|
| `10-sv-stop.sh` | Hentikan semua service runit |
| `20-rc-shutdown.sh` | Jalankan rc.shutdown |
| `30-seedrng.sh` | Simpan entropy seed |
| `40-hwclock.sh` | Sync jam hardware |
| `50-wtmp.sh` | Catat waktu shutdown ke wtmp |
| `60-udev.sh` | Hentikan udev |
| `70-pkill.sh` | Kill semua proses yang tersisa |
| `80-filesystems.sh` | Unmount filesystem |
| `90-kexec.sh` | Eksekusi kexec jika ada |

### `common/cli/sleek/`

Tema **GRUB kustom** T4n OS bernama **Sleek**. Berisi:
- Aset gambar untuk background, selection bar, progress, slider
- Font Poppins (14/16/18/48pt) dan Terminus (14pt) dalam format `.pf2`
- Direktori `icons/` berisi 60+ ikon distribusi Linux untuk multi-boot
- `theme.txt` — definisi layout tema GRUB

### `common/cli/service/pipewire/`

Script setup untuk service **PipeWire** (audio server modern). Dipanggil saat environment live diinisialisasi.

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

```
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

<!-- ## Rilis & Signing

`release.sh` berinteraksi dengan **GitHub Actions** untuk:
1. Memicu build image di CI pipeline
2. Menandatangani image yang dihasilkan dengan key dari direktori `keys/`
3. Mengupload artifact ke GitHub Releases

Key publik untuk verifikasi tersimpan di `keys/` dalam format `.plist`. -->

---

<div align="center">

[← Kembali ke Indeks](../index.md) · [English version](../EN/Docs.md) · Built with ❤️ by [T4n-Labs](https://github.com/T4n-Labs)

</div>
