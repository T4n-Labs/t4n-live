#!/usr/bin/env python3
"""
T4n OS / Void Linux GUI Installer  — v0.0.1 (Alpha Version)
Run as root: sudo python3 installer.py
"""

import os, sys, re, glob, shutil, subprocess, threading
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

# ─── Konstanta ────────────────────────────────────────────────────────────────

TARGETDIR   = "/mnt/target"
LOG_FILE    = "/tmp/t4n-installer.log"
CONF_FILE   = "/tmp/.t4n-installer.conf"
APP_TITLE   = "T4n OS Installer"
APP_VERSION = "0.0.1 (Alpha Version)"

C = {
    "bg"         : "#111827",
    "sidebar"    : "#0d1320",
    "card"       : "#1e2a3a",
    "card2"      : "#162032",
    "accent"     : "#e94560",
    "accent2"    : "#38bdf8",
    "text"       : "#f1f5f9",
    "text_muted" : "#64748b",
    "success"    : "#34d399",
    "warning"    : "#fbbf24",
    "error"      : "#f87171",
    "border"     : "#1e3a5f",
    "input_bg"   : "#0a1628",
    "hover"      : "#1c3050",
    "step_done"  : "#34d399",
    "step_active": "#38bdf8",
    "nm_green"   : "#166534",
    "nm_green_fg": "#86efac",
}

STEPS = [
    ("welcome",   "Selamat Datang"),
    ("locale",    "Bahasa & Waktu"),
    ("keyboard",  "Keyboard"),
    ("network",   "Jaringan"),
    ("disk",      "Partisi Disk"),
    ("account",   "Akun Pengguna"),
    ("login",     "Login & Tampilan"),   # ← BARU
    ("summary",   "Ringkasan"),
    ("install",   "Instalasi"),
    ("done",      "Selesai"),
]

FILESYSTEMS = ["ext4", "ext3", "ext2", "btrfs", "xfs", "f2fs", "vfat", "swap"]

# ─── Backend ──────────────────────────────────────────────────────────────────

class Backend:

    def __init__(self):
        self.conf = {}
        self.efi_system = os.path.exists("/sys/firmware/efi/systab")
        if self.efi_system:
            bits = self._read("/sys/firmware/efi/fw_platform_size")
            self.efi_target = "i386-efi" if bits.strip() == "32" else "x86_64-efi"
        self._load_conf()

    # ── Config store ───────────────────────────────────────────────────────

    def _load_conf(self):
        if os.path.exists(CONF_FILE):
            with open(CONF_FILE) as f:
                for line in f:
                    parts = line.strip().split(" ", 1)
                    if len(parts) == 2:
                        self.conf[parts[0]] = parts[1]

    def set_option(self, key, value):
        self.conf[key] = str(value)
        lines = []
        if os.path.exists(CONF_FILE):
            with open(CONF_FILE) as f:
                lines = [l for l in f.readlines() if not l.startswith(f"{key} ")]
        lines.append(f"{key} {value}\n")
        with open(CONF_FILE, "w") as f:
            f.writelines(lines)

    def get_option(self, key, default=""):
        return self.conf.get(key, default)

    # ── Utils ──────────────────────────────────────────────────────────────

    def _read(self, path):
        try:
            with open(path) as f: return f.read()
        except Exception: return ""

    def _run(self, cmd, timeout=60, **kw):
        try:
            r = subprocess.run(cmd, shell=isinstance(cmd, str),
                capture_output=True, text=True, timeout=timeout, **kw)
            with open(LOG_FILE, "a") as log:
                log.write(f"\n$ {cmd}\nRC={r.returncode}\n{r.stdout}\n{r.stderr}\n")
            return r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Timeout"
        except Exception as e:
            return 1, "", str(e)

    def _chroot(self, cmd):
        return self._run(f"chroot {TARGETDIR} {cmd}")

    def has_cmd(self, name):
        return shutil.which(name) is not None

    # ── Hardware detection ─────────────────────────────────────────────────

    def get_disks(self):
        disks = []
        patterns = ["/sys/block/hd[a-z]", "/sys/block/[sv]d[a-z]",
                    "/sys/block/xvd[a-z]", "/sys/block/mmcblk[0-9]",
                    "/sys/block/nvme[0-9]n[0-9]"]
        for pat in patterns:
            for dp in glob.glob(pat):
                dev = os.path.basename(dp)
                sectors = int(self._read(f"{dp}/size").strip() or 0)
                sector_sz = int(self._read(f"{dp}/queue/hw_sector_size").strip() or 512)
                gb = round(sectors * sector_sz / 1e9, 1)
                model = self._read(f"{dp}/device/model").strip()
                if gb > 0:
                    disks.append({"dev": f"/dev/{dev}", "size": f"{gb} GB",
                                  "model": model or "Unknown"})
        return disks

    def get_partitions(self, disk):
        dev = os.path.basename(disk)
        parts = []
        for p in sorted(glob.glob(f"/sys/block/{dev}/{dev}*")):
            pn = os.path.basename(p)
            _, out, _ = self._run(f"lsblk -nfr /dev/{pn}")
            cols = out.split()
            fstype = cols[1] if len(cols) > 1 else "unknown"
            _, out2, _ = self._run(f"lsblk -nr /dev/{pn}")
            size = out2.split()[3] if len(out2.split()) > 3 else "?"
            if fstype not in ("iso9660", "crypto_LUKS", "LVM2_member"):
                parts.append({"dev": f"/dev/{pn}", "size": size, "fstype": fstype})
        return parts

    def get_keymaps(self):
        maps = sorted(
            os.path.basename(f).replace(".map.gz", "")
            for f in glob.glob("/usr/share/kbd/keymaps/**/*.map.gz", recursive=True)
        )
        return maps or ["us","uk","de","fr","es","it","pt","dvorak","colemak","id"]

    def get_locales(self):
        locales = []
        try:
            with open("/etc/default/libc-locales") as f:
                for line in f:
                    m = re.match(r"#?([\w_]+\.UTF-8)", line)
                    if m: locales.append(m.group(1))
        except FileNotFoundError:
            pass
        return locales or ["id_ID.UTF-8","en_US.UTF-8","en_GB.UTF-8","ms_MY.UTF-8"]

    def get_timezones(self):
        tz = {}
        for area in ["Africa","America","Antarctica","Arctic","Asia","Atlantic",
                     "Australia","Europe","Indian","Pacific"]:
            locs = sorted(
                os.path.basename(f)
                for f in glob.glob(f"/usr/share/zoneinfo/{area}/*")
                if os.path.isfile(f)
            )
            if locs: tz[area] = locs
        return tz or {"Asia": ["Jakarta","Makassar","Jayapura","Singapore"]}

    # ── NetworkManager helpers ─────────────────────────────────────────────

    def nm_is_running(self):
        rc, _, _ = self._run("nmcli general status", timeout=5)
        return rc == 0

    def nm_get_devices(self):
        """Kembalikan list dict: {name, type, state, connection}."""
        _, out, _ = self._run("nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device")
        devs = []
        for line in out.strip().splitlines():
            parts = line.split(":")
            if len(parts) >= 4:
                devs.append({"name": parts[0], "type": parts[1],
                             "state": parts[2], "connection": parts[3]})
        return devs

    def nm_get_wifi_list(self):
        """Kembalikan list SSID wifi yang tersedia."""
        _, out, _ = self._run("nmcli -t -f SSID,SIGNAL,SECURITY device wifi list", timeout=10)
        networks = []
        seen = set()
        for line in out.strip().splitlines():
            parts = line.split(":")
            if parts and parts[0] and parts[0] not in seen:
                seen.add(parts[0])
                networks.append({
                    "ssid": parts[0],
                    "signal": parts[1] if len(parts) > 1 else "?",
                    "security": parts[2] if len(parts) > 2 else "",
                })
        return networks

    def nm_connect_wifi(self, ssid, password):
        rc, _, err = self._run(f'nmcli device wifi connect "{ssid}" password "{password}"', timeout=30)
        return rc == 0, err

    def nm_connect_dhcp(self, iface):
        rc, _, err = self._run(f"nmcli device connect {iface}", timeout=15)
        return rc == 0, err

    def nm_set_static(self, iface, ip, gw, dns1, dns2=""):
        cmds = [
            f'nmcli con add type ethernet ifname {iface} con-name t4n-static',
            f'nmcli con modify t4n-static ipv4.addresses {ip}',
            f'nmcli con modify t4n-static ipv4.gateway {gw}',
            f'nmcli con modify t4n-static ipv4.dns "{dns1} {dns2}"',
            f'nmcli con modify t4n-static ipv4.method manual',
            f'nmcli con up t4n-static',
        ]
        for cmd in cmds:
            rc, _, err = self._run(cmd, timeout=15)
            if rc != 0:
                return False, err
        return True, ""

    def test_network(self):
        rc, _, _ = self._run(
            "xbps-uhelper fetch https://repo-default.voidlinux.org/current/otime",
            timeout=12)
        return rc == 0

    # ── Partitioner ────────────────────────────────────────────────────────

    def open_gparted(self, disk):
        """Buka GParted GUI."""
        if self.has_cmd("gparted"):
            subprocess.Popen(["gparted", disk])
            return True
        return False

    def open_partitioner(self, disk, tool="cfdisk"):
        for term in ("xterm","gnome-terminal","xfce4-terminal","lxterminal","konsole"):
            if self.has_cmd(term):
                subprocess.Popen([term, "-e", f"{tool} {disk}"])
                return
        os.system(f"{tool} {disk}")

    # ── Format / mount ─────────────────────────────────────────────────────

    def format_partition(self, dev, fstype):
        cmds = {
            "ext4": f"mkfs.ext4 -F {dev}",   "ext3": f"mkfs.ext3 -F {dev}",
            "ext2": f"mkfs.ext2 -F {dev}",   "btrfs": f"mkfs.btrfs -f {dev}",
            "xfs":  f"mkfs.xfs -f {dev}",    "f2fs": f"mkfs.f2fs -f {dev}",
            "vfat": f"mkfs.vfat -F32 {dev}", "swap": f"mkswap {dev}",
        }
        if fstype not in cmds:
            return False, f"Filesystem tidak dikenal: {fstype}"
        rc, _, err = self._run(cmds[fstype])
        return rc == 0, err

    def mount_filesystem(self, dev, fstype, mountpoint):
        target = TARGETDIR + mountpoint
        os.makedirs(target, exist_ok=True)
        if fstype == "swap":
            rc, _, err = self._run(f"swapon {dev}")
        else:
            rc, _, err = self._run(f"mount {dev} {target}")
        return rc == 0, err

    def mount_required_fs(self):
        for fs, src in [("proc","proc"),("sysfs","sysfs"),("devtmpfs","dev")]:
            self._run(f"mount --rbind /{src} {TARGETDIR}/{src}")
        self._run(f"mount --make-rslave {TARGETDIR}/dev")

    def umount_filesystems(self):
        self._run(f"umount -R {TARGETDIR} 2>/dev/null || true")
        self._run("swapoff -a 2>/dev/null || true")

    # ── Install paket ──────────────────────────────────────────────────────

    def install_local(self, callback):
        steps = [
            ("Menyalin sistem dasar dari ISO...",
             f"rsync -aHAX --info=progress2 /run/rootfsbase/ {TARGETDIR}/"),
        ]
        for msg, cmd in steps:
            callback(msg)
            rc, _, err = self._run(cmd, timeout=600)
            if rc != 0: return False, f"{msg} gagal:\n{err}"
        return True, ""

    def install_network(self, mirror, dm, callback):
        repo   = mirror or "https://repo-default.voidlinux.org/current"
        pkgs   = "base-system grub NetworkManager"
        if self.efi_system:
            pkgs += " grub-x86_64-efi efibootmgr"
        # Tambahkan paket display manager
        dm_pkgs = {
            "lightdm": "lightdm lightdm-gtk3-greeter",
            "sddm":    "sddm",
            "gdm":     "gdm",
        }
        if dm in dm_pkgs:
            pkgs += " " + dm_pkgs[dm]
        cmd = (f"XBPS_ARCH=$(xbps-uhelper arch) xbps-install -Sy "
               f"-r {TARGETDIR} --repository={repo} {pkgs}")
        callback(f"Mengunduh dan memasang paket sistem ({pkgs.split()[0]}...)")
        rc, _, err = self._run(cmd, timeout=1200)
        return rc == 0, err

    # ── Post-install config ────────────────────────────────────────────────

    def write_fstab(self, mounts):
        fstab = "# /etc/fstab — T4n OS\n"
        fstab += "tmpfs /tmp tmpfs defaults,nosuid,nodev 0 0\n"
        for dev, fstype, mountpoint in mounts:
            _, out, _ = self._run(f"blkid -s UUID -o value {dev}")
            uuid = out.strip()
            if fstype == "swap":
                fstab += f"UUID={uuid} none swap sw 0 0\n"
            elif uuid:
                dump, pass_ = ("0","1") if mountpoint == "/" else ("0","2")
                fstab += f"UUID={uuid} {mountpoint} {fstype} defaults {dump} {pass_}\n"
        os.makedirs(f"{TARGETDIR}/etc", exist_ok=True)
        with open(f"{TARGETDIR}/etc/fstab", "w") as f:
            f.write(fstab)

    def set_hostname(self):
        hn = self.get_option("HOSTNAME", "t4n")
        with open(f"{TARGETDIR}/etc/hostname", "w") as f:
            f.write(hn + "\n")

    def set_locale(self):
        locale = self.get_option("LOCALE", "en_US.UTF-8")
        os.makedirs(f"{TARGETDIR}/etc", exist_ok=True)
        with open(f"{TARGETDIR}/etc/locale.conf", "w") as f:
            f.write(f"LANG={locale}\n")
        libc = f"{TARGETDIR}/etc/default/libc-locales"
        if os.path.exists(libc):
            self._run(f"sed -i 's|^#{locale}|{locale}|' {libc}")
            self._chroot("xbps-reconfigure -f glibc-locales")

    def set_timezone(self):
        tz = self.get_option("TIMEZONE", "Asia/Jakarta")
        self._run(f"ln -sf /usr/share/zoneinfo/{tz} {TARGETDIR}/etc/localtime")

    def set_keymap(self):
        km = self.get_option("KEYMAP", "us")
        vconsole = f"{TARGETDIR}/etc/vconsole.conf"
        if os.path.exists(vconsole):
            self._run(f"sed -i 's|KEYMAP=.*|KEYMAP={km}|' {vconsole}")
        else:
            self._run(f"sed -i 's|#\\?KEYMAP=.*|KEYMAP={km}|' {TARGETDIR}/etc/rc.conf")

    def set_rootpassword(self):
        pw = self.get_option("ROOTPASSWORD")
        self._run(f'echo "root:{pw}" | chroot {TARGETDIR} chpasswd -c SHA512')

    def set_useraccount(self):
        login  = self.get_option("USERLOGIN")
        name   = self.get_option("USERNAME")
        pw     = self.get_option("USERPASSWORD")
        groups = self.get_option("USERGROUPS", "wheel,audio,video,users,cdrom,kvm")
        if not login: return
        self._chroot(f'useradd -m -G "{groups}" -c "{name}" "{login}"')
        self._run(f'echo "{login}:{pw}" | chroot {TARGETDIR} chpasswd -c SHA512')
        sudoers_d = f"{TARGETDIR}/etc/sudoers.d"
        os.makedirs(sudoers_d, exist_ok=True)
        with open(f"{sudoers_d}/wheel", "w") as f:
            f.write("%wheel ALL=(ALL:ALL) ALL\n")

    # ── [FITUR 1] NetworkManager ───────────────────────────────────────────

    def set_network(self):
        """Aktifkan NetworkManager di sistem target (selalu)."""
        self.enable_service("NetworkManager")
        # Nonaktifkan dhcpcd agar tidak konflik
        dhcpcd_link = f"{TARGETDIR}/etc/runit/runsvdir/default/dhcpcd"
        if os.path.islink(dhcpcd_link):
            os.remove(dhcpcd_link)
        # Tulis konfigurasi NM dasar
        nm_conf = f"{TARGETDIR}/etc/NetworkManager/NetworkManager.conf"
        os.makedirs(os.path.dirname(nm_conf), exist_ok=True)
        with open(nm_conf, "w") as f:
            f.write("[main]\nplugins=keyfile\n\n[keyfile]\n\n[logging]\nlevel=WARN\n")

    # ── [FITUR 4] Display Manager & Auto-login ─────────────────────────────

    def set_display_manager(self, callback):
        """Aktifkan DM atau konfigurasi TTY autologin."""
        dm      = self.get_option("DISPLAY_MANAGER", "none")
        login   = self.get_option("USERLOGIN")
        autologin = self.get_option("AUTOLOGIN", "0") == "1"

        if dm == "tty":
            # Autologin TTY via runit/agetty
            callback("Mengatur autologin TTY...")
            agetty_dir = f"{TARGETDIR}/etc/sv/agetty-tty1"
            conf_path  = f"{agetty_dir}/conf"
            if os.path.exists(agetty_dir):
                with open(conf_path, "w") as f:
                    f.write(f"GETTY_ARGS=\"--autologin {login} --noclear\"\n"
                            f"BAUD_RATE=38400\nTERMINAL_TYPE=linux\n")
            # Pastikan agetty-tty1 aktif
            self.enable_service("agetty-tty1")
            return

        dm_sv = {
            "lightdm": "lightdm",
            "sddm":    "sddm",
            "gdm":     "gdm",
        }
        if dm not in dm_sv:
            return  # "none" — tidak ada DM

        callback(f"Mengaktifkan {dm}...")
        self.enable_service(dm_sv[dm])

        # Konfigurasi autologin per DM
        if autologin and login:
            if dm == "lightdm":
                lgconf = f"{TARGETDIR}/etc/lightdm/lightdm.conf"
                if os.path.exists(lgconf):
                    self._run(f"sed -i 's|#autologin-user=.*|autologin-user={login}|' {lgconf}")
                    self._run(f"sed -i 's|#autologin-user-timeout=.*|autologin-user-timeout=0|' {lgconf}")

            elif dm == "sddm":
                sddm_conf = f"{TARGETDIR}/etc/sddm.conf"
                with open(sddm_conf, "w") as f:
                    f.write(f"[Autologin]\nUser={login}\nSession=default\n")

            elif dm == "gdm":
                gdm_conf = f"{TARGETDIR}/etc/gdm/custom.conf"
                if os.path.exists(gdm_conf):
                    self._run(f"sed -i 's|#AutomaticLoginEnable.*|AutomaticLoginEnable=true|' {gdm_conf}")
                    self._run(f"sed -i 's|#AutomaticLogin=.*|AutomaticLogin={login}|' {gdm_conf}")

    # ── Bootloader ─────────────────────────────────────────────────────────

    def install_bootloader(self, callback):
        dev = self.get_option("BOOTLOADER")
        if not dev or dev == "none": return True, ""
        callback("Memasang GRUB bootloader...")
        self.mount_required_fs()
        args = (f"--target={self.efi_target} --efi-directory=/boot/efi "
                f"--bootloader-id=T4nOS --recheck") if self.efi_system else dev
        rc, _, err = self._chroot(f"grub-install {args}")
        if rc != 0: return False, f"grub-install gagal: {err}"
        callback("Membuat konfigurasi GRUB...")
        rc, _, err = self._chroot("grub-mkconfig -o /boot/grub/grub.cfg")
        if rc != 0: return False, f"grub-mkconfig gagal: {err}"
        return True, ""

    def enable_service(self, name):
        src = f"{TARGETDIR}/etc/sv/{name}"
        dst = f"{TARGETDIR}/etc/runit/runsvdir/default/{name}"
        if os.path.exists(src):
            self._run(f"ln -sf /etc/sv/{name} {dst}")

    def cleanup(self, callback):
        callback("Membersihkan paket sementara...")
        for pkg in ["dialog", "xtools-minimal"]:
            self._run(f"xbps-remove -r {TARGETDIR} -Ry {pkg}")
        callback("Sinkronisasi disk...")
        self._run("sync")

    def self_destruct(self, callback=None):
        """Hapus script installer beserta file sementara langsung dari sistem."""
        script_path = os.path.abspath(sys.argv[0])
        deleted = []
        failed  = []

        for f in [script_path, CONF_FILE]:
            try:
                if os.path.exists(f):
                    os.remove(f)
                    deleted.append(f)
            except Exception as e:
                failed.append(f"{f}: {e}")

        if callback:
            if deleted:
                callback(f"Dihapus: {', '.join(deleted)}")
            if failed:
                callback(f"Gagal hapus: {', '.join(failed)}")


# ─── Widget Kustom ────────────────────────────────────────────────────────────

class StyledButton(tk.Button):
    def __init__(self, parent, text, command=None, primary=False,
                 success=False, danger=False, small=False, **kw):
        if primary:
            bg, fg, hbg = C["accent"], "white", "#c4293e"
        elif success:
            bg, fg, hbg = "#166534", C["nm_green_fg"], "#14532d"
        elif danger:
            bg, fg, hbg = "#7f1d1d", C["error"], "#991b1b"
        else:
            bg, fg, hbg = C["card"], C["text"], C["hover"]

        pady = 5 if small else 8
        super().__init__(parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=hbg, activeforeground=fg,
            relief="flat", bd=0, padx=14 if small else 18, pady=pady,
            font=("sans-serif", 9 if small else 10), cursor="hand2", **kw)
        self._bg, self._hbg = bg, hbg
        self.bind("<Enter>", lambda e: self.configure(bg=self._hbg))
        self.bind("<Leave>", lambda e: self.configure(bg=self._bg))


class StyledEntry(tk.Entry):
    def __init__(self, parent, show=None, **kw):
        super().__init__(parent, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["text"], relief="flat",
            font=("monospace", 10), bd=0, show=show, **kw)
        self.configure(highlightthickness=1,
            highlightbackground=C["border"], highlightcolor=C["accent2"])

    def set_error(self, has_error=True):
        self.configure(
            highlightcolor=C["error"] if has_error else C["accent2"],
            highlightbackground=C["error"] if has_error else C["border"])


class RadioCard(tk.Frame):
    def __init__(self, parent, text, subtitle="", icon="",
                 value=None, var=None, **kw):
        super().__init__(parent, bg=C["card"], relief="flat",
            highlightthickness=1, highlightbackground=C["border"], **kw)
        self.value = value
        self.var   = var
        self.configure(cursor="hand2")

        ind = tk.Frame(self, bg=C["card"], width=24)
        ind.pack(side="left", padx=(12, 0), pady=12)
        self.dot = tk.Canvas(ind, width=16, height=16,
            bg=C["card"], highlightthickness=0)
        self.dot.pack()
        self._draw_dot(False)

        if icon:
            tk.Label(self, text=icon, bg=C["card"], fg=C["text"],
                font=("sans-serif", 14)).pack(side="left", padx=6)

        txt_frame = tk.Frame(self, bg=C["card"])
        txt_frame.pack(side="left", padx=8, pady=8, fill="x", expand=True)
        tk.Label(txt_frame, text=text, bg=C["card"], fg=C["text"],
            font=("sans-serif", 10), anchor="w").pack(fill="x")
        if subtitle:
            tk.Label(txt_frame, text=subtitle, bg=C["card"], fg=C["text_muted"],
                font=("sans-serif", 9), anchor="w", wraplength=380).pack(fill="x")

        for w in self.winfo_children() + [self]:
            w.bind("<Button-1>", self._on_click)
        if var:
            var.trace_add("write", lambda *a: self._update())

    def _draw_dot(self, active):
        self.dot.delete("all")
        color = C["accent2"] if active else C["text_muted"]
        self.dot.create_oval(1,1,15,15, outline=color, width=2)
        if active:
            self.dot.create_oval(5,5,11,11, fill=C["accent2"], outline="")

    def _on_click(self, e=None):
        if self.var: self.var.set(self.value)

    def _update(self):
        active = self.var and self.var.get() == self.value
        bg = C["hover"] if active else C["card"]
        hlt = C["accent2"] if active else C["border"]
        self.configure(bg=bg, highlightbackground=hlt)
        self._recolor(self, bg)
        self._draw_dot(active)

    def _recolor(self, widget, bg):
        try: widget.configure(bg=bg)
        except Exception: pass
        for w in widget.winfo_children():
            self._recolor(w, bg)


# ─── BasePage ─────────────────────────────────────────────────────────────────

class BasePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self.B   = app.backend
        self.build()

    def build(self): raise NotImplementedError
    def on_enter(self): pass
    def validate(self): return True

    def label(self, parent, text, size=10, color=None, bold=False, **kw):
        return tk.Label(parent, text=text, bg=parent["bg"],
            fg=color or C["text"],
            font=("sans-serif", size, "bold" if bold else "normal"), **kw)

    def heading(self, parent, title, subtitle=""):
        f = tk.Frame(parent, bg=parent["bg"])
        f.pack(fill="x", pady=(0, 18))
        self.label(f, title, size=17, bold=True).pack(anchor="w")
        if subtitle:
            self.label(f, subtitle, size=10, color=C["text_muted"]).pack(anchor="w", pady=(2,0))
        tk.Frame(f, bg=C["border"], height=1).pack(fill="x", pady=(12,0))
        return f

    def info_box(self, parent, text, kind="info"):
        colors = {
            "info":    ("#0c2d48", C["accent2"]),
            "warn":    ("#451a03", C["warning"]),
            "error":   ("#1c0505", C["error"]),
            "success": ("#052e16", C["success"]),
        }
        bg, fg = colors.get(kind, colors["info"])
        f = tk.Frame(parent, bg=bg,
            highlightthickness=1, highlightbackground=fg)
        f.pack(fill="x", pady=6)
        tk.Label(f, text=text, bg=bg, fg=fg,
            font=("sans-serif", 9), justify="left",
            wraplength=480).pack(anchor="w", padx=12, pady=8)
        return f


# ─── Halaman: Selamat Datang ──────────────────────────────────────────────────

class WelcomePage(BasePage):
    def build(self):
        header = tk.Frame(self, bg=C["bg"])
        header.pack(fill="x", pady=(28, 18), padx=40)

        logo = tk.Frame(header, bg=C["accent"], width=64, height=64)
        logo.pack(side="left"); logo.pack_propagate(False)
        tk.Label(logo, text="T4", bg=C["accent"], fg="white",
            font=("monospace", 20, "bold")).pack(expand=True)

        tf = tk.Frame(header, bg=C["bg"])
        tf.pack(side="left", padx=16)
        tk.Label(tf, text="T4n OS Installer", bg=C["bg"], fg=C["text"],
            font=("sans-serif", 22, "bold")).pack(anchor="w")
        tk.Label(tf, text=f"Versi {APP_VERSION}  •  Berbasis Void Linux  •  NetworkManager",
            bg=C["bg"], fg=C["text_muted"],
            font=("sans-serif", 10)).pack(anchor="w")

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="x", padx=40)
        tk.Label(body, bg=C["bg"], fg=C["text"], font=("sans-serif", 10),
            justify="left", wraplength=520,
            text=("Selamat datang di T4n OS Installer!\n\n"
                  "Wizard ini akan memandu Anda menginstal T4n OS ke komputer Anda.\n"
                  "Proses instalasi membutuhkan sekitar 10–20 menit.\n\n"
                  "⚠  Pastikan Anda telah membackup data penting sebelum melanjutkan.")
        ).pack(anchor="w")

        cards = tk.Frame(self, bg=C["bg"])
        cards.pack(fill="x", padx=40, pady=20)
        infos = [
            ("🖥", "Minimum",    "RAM 512MB, Disk 8GB"),
            ("🌐", "Jaringan",   "NetworkManager built-in"),
            ("⚡", "Mode Boot",  "EFI" if self.B.efi_system else "BIOS Legacy"),
            ("🎨", "GParted",    "Tersedia" if self.B.has_cmd("gparted") else "Tidak ada"),
        ]
        for icon, title, desc in infos:
            card = tk.Frame(cards, bg=C["card"],
                highlightthickness=1, highlightbackground=C["border"])
            card.pack(side="left", expand=True, fill="x", padx=(0,8))
            tk.Label(card, text=icon, bg=C["card"], font=("sans-serif", 18)).pack(pady=(10,0))
            tk.Label(card, text=title, bg=C["card"], fg=C["text"],
                font=("sans-serif", 9, "bold")).pack()
            tk.Label(card, text=desc, bg=C["card"], fg=C["text_muted"],
                font=("sans-serif", 9), wraplength=120).pack(pady=(2,10))


# ─── Halaman: Locale & Timezone ───────────────────────────────────────────────

class LocalePage(BasePage):
    def build(self):
        cont = tk.Frame(self, bg=C["bg"])
        cont.pack(fill="both", expand=True, padx=40, pady=20)
        self.heading(cont, "Bahasa & Zona Waktu", "Pilih bahasa sistem dan zona waktu Anda.")

        self.label(cont, "Locale sistem", size=9, color=C["text_muted"]).pack(anchor="w")
        self.locale_var = tk.StringVar(value=self.B.get_option("LOCALE","id_ID.UTF-8"))
        ttk.Combobox(cont, textvariable=self.locale_var,
            values=self.B.get_locales(), state="readonly",
            font=("monospace",10)).pack(fill="x", pady=(3,14), ipady=4)

        self.label(cont, "Area", size=9, color=C["text_muted"]).pack(anchor="w")
        self.tz_data = self.B.get_timezones()
        self.area_var = tk.StringVar(value="Asia")
        area_cb = ttk.Combobox(cont, textvariable=self.area_var,
            values=list(self.tz_data.keys()), state="readonly", font=("monospace",10))
        area_cb.pack(fill="x", pady=(3,10), ipady=4)
        area_cb.bind("<<ComboboxSelected>>", self._update_locs)

        self.label(cont, "Kota", size=9, color=C["text_muted"]).pack(anchor="w")
        self.loc_var = tk.StringVar(value="Jakarta")
        self.loc_cb = ttk.Combobox(cont, textvariable=self.loc_var,
            values=self.tz_data.get("Asia",[]), state="readonly", font=("monospace",10))
        self.loc_cb.pack(fill="x", pady=(3,14), ipady=4)

        self.label(cont, "Sumber instalasi", size=9, color=C["text_muted"]).pack(anchor="w")
        self.source_var = tk.StringVar(value=self.B.get_option("SOURCE","local"))
        for val, txt, sub in [
            ("local",   "Lokal (dari ISO)", "Paket sudah ada di media instalasi"),
            ("network", "Jaringan (unduh)", "Unduh paket terbaru dari mirror Void Linux"),
        ]:
            card = RadioCard(cont, txt, sub, value=val, var=self.source_var)
            card.pack(fill="x", pady=3); card._update()

    def _update_locs(self, e=None):
        locs = self.tz_data.get(self.area_var.get(), [])
        self.loc_cb["values"] = locs
        if locs: self.loc_var.set(locs[0])

    def validate(self):
        self.B.set_option("LOCALE",  self.locale_var.get())
        self.B.set_option("TIMEZONE",f"{self.area_var.get()}/{self.loc_var.get()}")
        self.B.set_option("SOURCE",  self.source_var.get())
        return True


# ─── Halaman: Keyboard ────────────────────────────────────────────────────────

class KeyboardPage(BasePage):
    def build(self):
        cont = tk.Frame(self, bg=C["bg"])
        cont.pack(fill="both", expand=True, padx=40, pady=20)
        self.heading(cont, "Layout Keyboard", "Pilih tata letak keyboard Anda.")

        self.label(cont, "Keymap", size=9, color=C["text_muted"]).pack(anchor="w")
        self.km_var = tk.StringVar(value=self.B.get_option("KEYMAP","us"))
        ttk.Combobox(cont, textvariable=self.km_var,
            values=self.B.get_keymaps(), font=("monospace",10)
        ).pack(fill="x", pady=(3,20), ipady=4)

        self.label(cont, "Uji keyboard — ketik sesuatu di sini",
            size=9, color=C["text_muted"]).pack(anchor="w")
        StyledEntry(cont).pack(fill="x", pady=(3,0), ipady=8)

    def validate(self):
        self.B.set_option("KEYMAP", self.km_var.get())
        subprocess.run(["loadkeys", self.km_var.get()], capture_output=True)
        return True


# ─── Halaman: Jaringan (NetworkManager) ──────────────────────────────────────

class NetworkPage(BasePage):
    def build(self):
        cont = tk.Frame(self, bg=C["bg"])
        cont.pack(fill="both", expand=True, padx=40, pady=20)
        self.heading(cont, "Konfigurasi Jaringan",
            "Jaringan dikelola oleh NetworkManager (nmcli).")

        # Status NM
        nm_bar = tk.Frame(cont, bg=C["nm_green"] if self.B.nm_is_running() else "#1c0505",
            highlightthickness=1,
            highlightbackground=C["success"] if self.B.nm_is_running() else C["error"])
        nm_bar.pack(fill="x", pady=(0, 12))
        nm_txt = "✓ NetworkManager aktif dan berjalan" if self.B.nm_is_running() \
                 else "✗ NetworkManager tidak ditemukan — jalankan: sv start NetworkManager"
        nm_fg  = C["success"] if self.B.nm_is_running() else C["error"]
        tk.Label(nm_bar, text=nm_txt, bg=nm_bar["bg"], fg=nm_fg,
            font=("sans-serif", 9)).pack(anchor="w", padx=12, pady=7)

        # Pilih tipe koneksi
        self.net_var = tk.StringVar(value=self.B.get_option("NETWORK","nm-dhcp"))
        opts = [
            ("nm-dhcp",   "Ethernet/WiFi Otomatis (DHCP)",
             "NetworkManager otomatis mendeteksi dan mengkoneksikan perangkat jaringan."),
            ("nm-wifi",   "WiFi — masukkan SSID & password",
             "Sambungkan ke jaringan WiFi menggunakan nmcli."),
            ("nm-static", "IP Statis via NetworkManager",
             "Atur IP, gateway, dan DNS secara manual."),
            ("skip",      "Lewati (konfigurasi setelah install)",
             "Atur jaringan setelah instalasi selesai menggunakan nmtui."),
        ]
        for val, txt, sub in opts:
            card = RadioCard(cont, txt, sub, value=val, var=self.net_var)
            card.pack(fill="x", pady=3); card._update()

        self.net_var.trace_add("write", self._toggle_panels)

        # ── Panel WiFi ────────────────────────────────────────────────
        self.wifi_frame = tk.Frame(cont, bg=C["card2"],
            highlightthickness=1, highlightbackground=C["border"])
        self.label(self.wifi_frame, "Jaringan WiFi tersedia",
            size=9, color=C["text_muted"]).pack(anchor="w", padx=12, pady=(10,0))

        wifi_list_frame = tk.Frame(self.wifi_frame, bg=C["card2"])
        wifi_list_frame.pack(fill="x", padx=12, pady=4)
        self.wifi_var = tk.StringVar()
        self.wifi_combo = ttk.Combobox(wifi_list_frame, textvariable=self.wifi_var,
            state="readonly", font=("monospace",10))
        self.wifi_combo.pack(side="left", fill="x", expand=True, ipady=4)
        StyledButton(wifi_list_frame, "🔍 Scan", command=self._scan_wifi,
            small=True).pack(side="left", padx=(6,0))

        self.label(self.wifi_frame, "Password WiFi",
            size=9, color=C["text_muted"]).pack(anchor="w", padx=12, pady=(6,0))
        self.wifi_pass = StyledEntry(self.wifi_frame, show="*")
        self.wifi_pass.pack(fill="x", padx=12, pady=(3,0), ipady=7)

        wifi_btn_row = tk.Frame(self.wifi_frame, bg=C["card2"])
        wifi_btn_row.pack(fill="x", padx=12, pady=8)
        StyledButton(wifi_btn_row, "Sambungkan WiFi",
            command=self._connect_wifi, success=True).pack(side="left")
        self.wifi_status = tk.Label(wifi_btn_row, text="", bg=C["card2"],
            fg=C["text_muted"], font=("sans-serif",9))
        self.wifi_status.pack(side="left", padx=10)

        # ── Panel IP Statis ───────────────────────────────────────────
        self.static_frame = tk.Frame(cont, bg=C["card2"],
            highlightthickness=1, highlightbackground=C["border"])
        tk.Label(self.static_frame, text="Konfigurasi IP Statis",
            bg=C["card2"], fg=C["text"],
            font=("sans-serif", 10, "bold")).pack(anchor="w", padx=12, pady=(10,0))

        self.static_entries = {}
        fields = [("Interface", "eth0"), ("IP Address (CIDR)", "192.168.1.100/24"),
                  ("Gateway",   "192.168.1.1"), ("DNS 1", "8.8.8.8"), ("DNS 2", "8.8.4.4")]
        for lbl, ph in fields:
            row = tk.Frame(self.static_frame, bg=C["card2"])
            row.pack(fill="x", padx=12, pady=3)
            tk.Label(row, text=lbl, bg=C["card2"], fg=C["text_muted"],
                font=("sans-serif",9), width=18, anchor="w").pack(side="left")
            e = StyledEntry(row); e.insert(0, ph)
            e.pack(side="left", fill="x", expand=True, ipady=5)
            self.static_entries[lbl] = e

        static_btn_row = tk.Frame(self.static_frame, bg=C["card2"])
        static_btn_row.pack(fill="x", padx=12, pady=8)
        StyledButton(static_btn_row, "Terapkan IP Statis",
            command=self._apply_static, success=True).pack(side="left")
        self.static_status = tk.Label(static_btn_row, text="", bg=C["card2"],
            fg=C["text_muted"], font=("sans-serif",9))
        self.static_status.pack(side="left", padx=10)

        # ── Tombol uji ────────────────────────────────────────────────
        test_row = tk.Frame(cont, bg=C["bg"])
        test_row.pack(fill="x", pady=10)
        StyledButton(test_row, "Uji Koneksi Internet",
            command=self._test_connection).pack(side="left")
        self.test_status = tk.Label(test_row, text="", bg=C["bg"],
            fg=C["text_muted"], font=("sans-serif",9))
        self.test_status.pack(side="left", padx=10)

        self._toggle_panels()

    def _toggle_panels(self, *a):
        v = self.net_var.get()
        self.wifi_frame.pack_forget()
        self.static_frame.pack_forget()
        if v == "nm-wifi":
            self.wifi_frame.pack(fill="x", pady=6)
        elif v == "nm-static":
            self.static_frame.pack(fill="x", pady=6)

    def _scan_wifi(self):
        self.wifi_status.config(text="Memindai WiFi...")
        def _do():
            nets = self.B.nm_get_wifi_list()
            ssids = [f"{n['ssid']}  ({n['signal']}% {n['security']})" for n in nets]
            self.wifi_combo["values"] = ssids
            if ssids: self.wifi_var.set(ssids[0])
            self.wifi_status.config(text=f"{len(nets)} jaringan ditemukan")
        threading.Thread(target=_do, daemon=True).start()

    def _connect_wifi(self):
        ssid = self.wifi_var.get().split()[0] if self.wifi_var.get() else ""
        pw   = self.wifi_pass.get()
        if not ssid:
            self.wifi_status.config(text="Pilih jaringan WiFi dulu.")
            return
        self.wifi_status.config(text=f"Menyambungkan ke {ssid}...")
        def _do():
            ok, err = self.B.nm_connect_wifi(ssid, pw)
            self.wifi_status.config(
                text=f"✓ Terhubung ke {ssid}" if ok else f"✗ Gagal: {err[:40]}")
        threading.Thread(target=_do, daemon=True).start()

    def _apply_static(self):
        e = self.static_entries
        iface = e["Interface"].get().strip()
        ip    = e["IP Address (CIDR)"].get().strip()
        gw    = e["Gateway"].get().strip()
        dns1  = e["DNS 1"].get().strip()
        dns2  = e["DNS 2"].get().strip()
        self.static_status.config(text="Menerapkan konfigurasi...")
        def _do():
            ok, err = self.B.nm_set_static(iface, ip, gw, dns1, dns2)
            self.static_status.config(
                text="✓ IP statis diterapkan" if ok else f"✗ Gagal: {err[:40]}")
        threading.Thread(target=_do, daemon=True).start()

    def _test_connection(self):
        self.test_status.config(text="Menguji koneksi...")
        def _do():
            ok = self.B.test_network()
            self.test_status.config(
                text="✓ Terhubung ke internet" if ok else "✗ Tidak terhubung ke internet")
        threading.Thread(target=_do, daemon=True).start()

    def validate(self):
        self.B.set_option("NETWORK", self.net_var.get())
        return True


# ─── Halaman: Disk & Partisi (+ GParted) ─────────────────────────────────────

class DiskPage(BasePage):
    def build(self):
        self.mounts = {}
        cont = tk.Frame(self, bg=C["bg"])
        cont.pack(fill="both", expand=True, padx=40, pady=20)
        self.heading(cont, "Disk & Partisi",
            "Buat partisi, lalu tentukan filesystem dan mount point.")

        # Pilih disk
        self.label(cont, "Disk target", size=9, color=C["text_muted"]).pack(anchor="w")
        disks = self.B.get_disks()
        disk_labels = [f"{d['dev']}  —  {d['size']}  {d['model']}" for d in disks]
        self.disk_var = tk.StringVar(value=disk_labels[0] if disk_labels else "")
        disk_cb = ttk.Combobox(cont, textvariable=self.disk_var,
            values=disk_labels, state="readonly", font=("monospace",10))
        disk_cb.pack(fill="x", pady=(3,10), ipady=4)
        disk_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_table())

        # ── [FITUR 2] Tombol Partisi ───────────────────────────────────
        btn_row = tk.Frame(cont, bg=C["bg"])
        btn_row.pack(fill="x", pady=4)

        if self.B.has_cmd("gparted"):
            StyledButton(btn_row, "🎨  GParted (GUI — disarankan)",
                command=self._open_gparted, success=True).pack(side="left", padx=(0,8))

        StyledButton(btn_row, "cfdisk",
            command=lambda: self._open_term("cfdisk")).pack(side="left", padx=(0,6))
        StyledButton(btn_row, "fdisk",
            command=lambda: self._open_term("fdisk")).pack(side="left", padx=(0,6))
        StyledButton(btn_row, "🔄 Muat Ulang Tabel",
            command=self._refresh_table, small=True).pack(side="right")

        if not self.B.has_cmd("gparted"):
            self.info_box(cont,
                "ℹ  GParted tidak terdeteksi. Install dengan: xbps-install gparted\n"
                "    Gunakan cfdisk atau fdisk sebagai alternatif.", "info")

        self.info_box(cont,
            "⚠  Data pada partisi yang diformat akan dihapus permanen.", "warn")

        # Tabel mount point
        self.label(cont, "Konfigurasi mount point & filesystem",
            size=9, color=C["text_muted"]).pack(anchor="w", pady=(10,0))
        tbl = tk.Frame(cont, bg=C["card"],
            highlightthickness=1, highlightbackground=C["border"])
        tbl.pack(fill="x", pady=(4,0))
        for i, h in enumerate(["Partisi","Ukuran","Filesystem","Mount Point","Format?"]):
            tk.Label(tbl, text=h, bg=C["card"], fg=C["text_muted"],
                font=("sans-serif",9,"bold"),
                width=[18,8,12,14,8][i], anchor="w"
            ).grid(row=0, column=i, padx=8, pady=6, sticky="w")
        self.tbl = tbl
        self._refresh_table()

        # Bootloader
        self.label(cont, "Disk bootloader (GRUB)",
            size=9, color=C["text_muted"]).pack(anchor="w", pady=(14,0))
        bl_vals = ["none"] + [d["dev"] for d in disks]
        self.bl_var = tk.StringVar(value=bl_vals[1] if len(bl_vals) > 1 else "none")
        ttk.Combobox(cont, textvariable=self.bl_var, values=bl_vals,
            state="readonly", font=("monospace",10)).pack(fill="x", pady=(3,0), ipady=4)

    def _disk_dev(self):
        raw = self.disk_var.get()
        return raw.split()[0] if raw else ""

    def _open_gparted(self):
        disk = self._disk_dev()
        if disk:
            self.B.open_gparted(disk)
            self.after(3000, self._refresh_table)

    def _open_term(self, tool):
        disk = self._disk_dev()
        if disk:
            self.B.open_partitioner(disk, tool)
            self.after(2000, self._refresh_table)

    def _refresh_table(self):
        for w in self.tbl.grid_slaves():
            if int(w.grid_info()["row"]) > 0: w.destroy()
        disk = self._disk_dev()
        if not disk: return
        parts = self.B.get_partitions(disk)
        if not parts:
            tk.Label(self.tbl, text="Belum ada partisi — buat dulu dengan GParted atau cfdisk.",
                bg=C["card"], fg=C["text_muted"],
                font=("sans-serif",9)).grid(row=1, column=0, columnspan=5, padx=8, pady=10)
            return
        self.mounts.clear()
        for ri, p in enumerate(parts, 1):
            rbg = C["card"] if ri%2==0 else C["hover"]
            tk.Label(self.tbl, text=p["dev"], bg=rbg, fg=C["text"],
                font=("monospace",9), anchor="w", width=18
            ).grid(row=ri, column=0, padx=8, pady=4, sticky="w")
            tk.Label(self.tbl, text=p["size"], bg=rbg, fg=C["text_muted"],
                font=("monospace",9), anchor="w", width=8
            ).grid(row=ri, column=1, padx=8, sticky="w")
            fs_var = tk.StringVar(value=p.get("fstype","ext4"))
            ttk.Combobox(self.tbl, textvariable=fs_var, values=FILESYSTEMS,
                state="readonly", width=10, font=("monospace",9)
            ).grid(row=ri, column=2, padx=8, sticky="w")
            mp_var = tk.StringVar()
            StyledEntry(self.tbl, textvariable=mp_var, width=12
            ).grid(row=ri, column=3, padx=8, ipady=3, sticky="w")
            fmt_var = tk.BooleanVar(value=True)
            tk.Checkbutton(self.tbl, variable=fmt_var,
                bg=rbg, activebackground=rbg, fg=C["text"], selectcolor=C["card"]
            ).grid(row=ri, column=4, padx=8)
            self.mounts[p["dev"]] = (fs_var, mp_var, fmt_var)

    def validate(self):
        disk = self._disk_dev()
        if not disk:
            messagebox.showerror("Error", "Pilih disk terlebih dahulu."); return False
        has_root = any(mp.get().strip() == "/" for _, (_, mp, _) in self.mounts.items())
        if not has_root:
            messagebox.showerror("Error", "Harus ada partisi root (/)."); return False
        self.B.set_option("DISK",       disk)
        self.B.set_option("BOOTLOADER", self.bl_var.get())
        self.app.mounts_config = list(self.mounts.items())
        return True


# ─── Halaman: Akun Pengguna ──────────────────────────────────────────────────

class AccountPage(BasePage):
    def build(self):
        cont = tk.Frame(self, bg=C["bg"])
        cont.pack(fill="both", expand=True, padx=40, pady=20)
        self.heading(cont, "Buat Akun Pengguna",
            "Akun ini digunakan untuk login ke T4n OS.")

        self.fields  = {}
        self.err_vars = {}

        base_entries = [
            ("fullname", "Nama Lengkap",         "Ahmad Fauzi", "text"),
            ("username", "Nama Pengguna (login)", "ahmadf",      "text"),
            ("hostname", "Nama Komputer",         "t4n-pc",      "text"),
            ("password", "Kata Sandi",            "",            "password"),
            ("confirm",  "Konfirmasi Kata Sandi", "",            "password"),
        ]
        for key, lbl, ph, typ in base_entries:
            ev = tk.StringVar()
            self.err_vars[key] = ev
            row = tk.Frame(cont, bg=C["bg"]); row.pack(fill="x", pady=4)
            tk.Label(row, text=lbl, bg=C["bg"], fg=C["text_muted"],
                font=("sans-serif",9)).pack(anchor="w")
            e = StyledEntry(row, show="*" if typ=="password" else None)
            if ph: e.insert(0, ph)
            e.pack(fill="x", pady=(2,0), ipady=7)
            tk.Label(row, textvariable=ev, bg=C["bg"],
                fg=C["error"], font=("sans-serif",9)).pack(anchor="w")
            self.fields[key] = e

        # ── [FITUR 3] Password root sama/beda ─────────────────────────
        sep = tk.Frame(cont, bg=C["border"], height=1)
        sep.pack(fill="x", pady=10)

        self.same_root_pw = tk.BooleanVar(value=True)
        chk_same = tk.Checkbutton(cont,
            text="Gunakan kata sandi yang sama untuk akun root",
            variable=self.same_root_pw,
            command=self._toggle_root_pw,
            bg=C["bg"], fg=C["text"],
            activebackground=C["bg"], selectcolor=C["card"],
            font=("sans-serif", 10))
        chk_same.pack(anchor="w")

        # Frame root pw (hidden kalau sama)
        self.root_pw_frame = tk.Frame(cont, bg=C["bg"])
        for key, lbl in [("rootpw","Kata Sandi Root"), ("rootpw2","Konfirmasi Kata Sandi Root")]:
            ev = tk.StringVar(); self.err_vars[key] = ev
            r = tk.Frame(self.root_pw_frame, bg=C["bg"]); r.pack(fill="x", pady=4)
            tk.Label(r, text=lbl, bg=C["bg"], fg=C["text_muted"],
                font=("sans-serif",9)).pack(anchor="w")
            e = StyledEntry(r, show="*"); e.pack(fill="x", pady=(2,0), ipady=7)
            tk.Label(r, textvariable=ev, bg=C["bg"],
                fg=C["error"], font=("sans-serif",9)).pack(anchor="w")
            self.fields[key] = e

        self._toggle_root_pw()

        # Grup
        sep2 = tk.Frame(cont, bg=C["border"], height=1)
        sep2.pack(fill="x", pady=10)
        tk.Label(cont, text="Grup pengguna (pisahkan dengan koma)",
            bg=C["bg"], fg=C["text_muted"],
            font=("sans-serif",9)).pack(anchor="w")
        self.groups_entry = StyledEntry(cont)
        self.groups_entry.insert(0, "wheel,audio,video,users,cdrom,kvm,optical")
        self.groups_entry.pack(fill="x", pady=(3,0), ipady=7)

    def _toggle_root_pw(self):
        if self.same_root_pw.get():
            self.root_pw_frame.pack_forget()
        else:
            self.root_pw_frame.pack(fill="x")

    def validate(self):
        f = {k: e.get().strip() for k, e in self.fields.items()}
        errors = {}

        if not f["fullname"]:
            errors["fullname"] = "Nama lengkap wajib diisi."
        if not re.match(r"^[a-z_][a-z0-9_-]{0,31}$", f["username"]):
            errors["username"] = "Harus huruf kecil, boleh angka/underscore, tanpa spasi."
        if not re.match(r"^[a-zA-Z0-9-]{1,63}$", f["hostname"]):
            errors["hostname"] = "Nama komputer tidak valid."
        if len(f["password"]) < 6:
            errors["password"] = "Minimal 6 karakter."
        if f["password"] != f["confirm"]:
            errors["confirm"] = "Kata sandi tidak cocok."

        if not self.same_root_pw.get():
            if len(f.get("rootpw","")) < 6:
                errors["rootpw"] = "Minimal 6 karakter."
            if f.get("rootpw","") != f.get("rootpw2",""):
                errors["rootpw2"] = "Kata sandi root tidak cocok."

        for k, v in self.err_vars.items():
            v.set(errors.get(k, ""))
        for k, e in self.fields.items():
            if hasattr(e, "set_error"):
                e.set_error(k in errors)

        if errors: return False

        self.B.set_option("USERNAME",     f["fullname"])
        self.B.set_option("USERLOGIN",    f["username"])
        self.B.set_option("HOSTNAME",     f["hostname"])
        self.B.set_option("USERPASSWORD", f["password"])

        # [FITUR 3] Tentukan root password
        root_pw = f["password"] if self.same_root_pw.get() else f.get("rootpw","")
        self.B.set_option("ROOTPASSWORD", root_pw)
        self.B.set_option("ROOT_SAME_AS_USER", "1" if self.same_root_pw.get() else "0")
        self.B.set_option("USERGROUPS",   self.groups_entry.get().strip())
        return True


# ─── Halaman: Login & Display Manager ────────────────────────────────────────

class LoginPage(BasePage):
    """[FITUR 4] Pilih panel login atau autologin TTY."""

    def build(self):
        cont = tk.Frame(self, bg=C["bg"])
        cont.pack(fill="both", expand=True, padx=40, pady=20)
        self.heading(cont, "Panel Login & Tampilan",
            "Pilih bagaimana sistem masuk setelah booting.")

        self.dm_var = tk.StringVar(value=self.B.get_option("DISPLAY_MANAGER","lightdm"))

        dm_opts = [
            ("lightdm", "LightDM",
             "Panel login ringan. Mendukung berbagai DE (XFCE, MATE, Openbox).",
             "🪟"),
            ("sddm",    "SDDM",
             "Panel login modern berbasis QML. Cocok untuk KDE Plasma.",
             "💎"),
            ("gdm",     "GDM",
             "Panel login GNOME. Cocok untuk desktop GNOME.",
             "🌀"),
            ("tty",     "TTY Autologin (tanpa panel grafis)",
             "Langsung masuk ke terminal tanpa memasukkan username/password. "
             "Tidak memerlukan display manager.",
             "⌨"),
            ("none",    "Tanpa Display Manager",
             "Tidak ada panel login. Login manual via TTY, lalu jalankan startx.",
             "🔲"),
        ]
        for val, txt, sub, icon in dm_opts:
            card = RadioCard(cont, txt, sub, icon=icon, value=val, var=self.dm_var)
            card.pack(fill="x", pady=4); card._update()

        # Opsi autologin (muncul untuk DM yang mendukung)
        sep = tk.Frame(cont, bg=C["border"], height=1)
        sep.pack(fill="x", pady=12)

        self.autologin_var = tk.BooleanVar(
            value=self.B.get_option("AUTOLOGIN","0") == "1")

        self.chk_autologin = tk.Checkbutton(cont,
            text="Aktifkan autologin (masuk otomatis tanpa memasukkan kata sandi)",
            variable=self.autologin_var,
            bg=C["bg"], fg=C["text"],
            activebackground=C["bg"], selectcolor=C["card"],
            font=("sans-serif",10))
        self.chk_autologin.pack(anchor="w")

        self.dm_var.trace_add("write", self._toggle_autologin_hint)

        # Info notes
        self.note = tk.Label(cont, text="", bg=C["bg"], fg=C["text_muted"],
            font=("sans-serif",9), wraplength=480, justify="left", anchor="w")
        self.note.pack(anchor="w", pady=(8,0))
        self._toggle_autologin_hint()

    def _toggle_autologin_hint(self, *a):
        dm = self.dm_var.get()
        notes = {
            "lightdm": "LightDM akan diaktifkan sebagai service runit.",
            "sddm":    "SDDM akan diaktifkan sebagai service runit.",
            "gdm":     "GDM akan diaktifkan sebagai service runit.",
            "tty":     ("Mode TTY Autologin: sistem akan langsung masuk ke terminal "
                        "sebagai pengguna yang dibuat, tanpa memasukkan password. "
                        "Opsi autologin di bawah diabaikan untuk mode ini."),
            "none":    ("Tidak ada DM. Gunakan 'startx' secara manual setelah login TTY. "
                        "Cocok untuk pengguna tingkat lanjut."),
        }
        self.note.config(text=notes.get(dm, ""))
        # Nonaktifkan checkbox autologin untuk TTY (sudah otomatis) dan none
        state = "disabled" if dm in ("tty","none") else "normal"
        self.chk_autologin.configure(state=state)

    def validate(self):
        self.B.set_option("DISPLAY_MANAGER", self.dm_var.get())
        self.B.set_option("AUTOLOGIN", "1" if self.autologin_var.get() else "0")
        return True


# ─── Halaman: Ringkasan ───────────────────────────────────────────────────────

class SummaryPage(BasePage):
    def build(self):
        self.cont = tk.Frame(self, bg=C["bg"])
        self.cont.pack(fill="both", expand=True, padx=40, pady=20)

    def on_enter(self):
        for w in self.cont.winfo_children(): w.destroy()
        self.heading(self.cont, "Ringkasan Instalasi",
            "Tinjau semua pengaturan sebelum memulai instalasi.")

        B = self.B
        dm_labels = {"lightdm":"LightDM","sddm":"SDDM","gdm":"GDM",
                     "tty":"TTY Autologin","none":"Tanpa DM"}
        root_label = "Sama dengan pengguna" if B.get_option("ROOT_SAME_AS_USER","0")=="1" \
                     else "Kata sandi berbeda"
        rows = [
            ("Locale",          B.get_option("LOCALE")),
            ("Zona Waktu",      B.get_option("TIMEZONE")),
            ("Keyboard",        B.get_option("KEYMAP")),
            ("Jaringan",        B.get_option("NETWORK")),
            ("Disk",            B.get_option("DISK")),
            ("Bootloader",      B.get_option("BOOTLOADER")),
            ("Sumber",          B.get_option("SOURCE")),
            ("Nama Lengkap",    B.get_option("USERNAME")),
            ("Login",           B.get_option("USERLOGIN")),
            ("Hostname",        B.get_option("HOSTNAME")),
            ("Grup",            B.get_option("USERGROUPS")),
            ("Password Root",   root_label),
            ("Display Manager", dm_labels.get(B.get_option("DISPLAY_MANAGER","none"), "?")),
            ("Autologin",       "Ya" if B.get_option("AUTOLOGIN","0")=="1" else "Tidak"),
        ]
        tbl = tk.Frame(self.cont, bg=C["card"],
            highlightthickness=1, highlightbackground=C["border"])
        tbl.pack(fill="x")
        for i, (k, v) in enumerate(rows):
            rbg = C["card"] if i%2==0 else C["hover"]
            tk.Label(tbl, text=k, bg=rbg, fg=C["text_muted"],
                font=("sans-serif",9), width=20, anchor="w",
                padx=12, pady=7).grid(row=i, column=0, sticky="w")
            tk.Label(tbl, text=v or "—", bg=rbg, fg=C["text"],
                font=("monospace",9), anchor="w",
                padx=12, pady=7).grid(row=i, column=1, sticky="w")

        self.info_box(self.cont,
            "⚠  Klik 'Mulai Instalasi' untuk melanjutkan.\n"
            "    Proses TIDAK bisa dibatalkan — semua data pada partisi yang dipilih akan dihapus.",
            "error")


# ─── Halaman: Instalasi ───────────────────────────────────────────────────────

class InstallPage(BasePage):
    def build(self):
        cont = tk.Frame(self, bg=C["bg"])
        cont.pack(fill="both", expand=True, padx=40, pady=20)
        self.heading(cont, "Menginstal T4n OS...",
            "Jangan matikan komputer selama proses ini.")

        self.overall_var = tk.DoubleVar(value=0)
        self.msg_var     = tk.StringVar(value="Mempersiapkan...")
        tk.Label(cont, textvariable=self.msg_var, bg=C["bg"], fg=C["text"],
            font=("sans-serif",10)).pack(anchor="w", pady=(0,4))

        style = ttk.Style()
        style.configure("T4n.Horizontal.TProgressbar",
            troughcolor=C["input_bg"], background=C["accent2"], thickness=18)
        ttk.Progressbar(cont, variable=self.overall_var, maximum=100,
            style="T4n.Horizontal.TProgressbar").pack(fill="x")
        self.pct_lbl = tk.Label(cont, text="0%", bg=C["bg"],
            fg=C["text_muted"], font=("sans-serif",9), anchor="e")
        self.pct_lbl.pack(anchor="e", pady=(2,0))

        tk.Label(cont, text="Log instalasi:", bg=C["bg"],
            fg=C["text_muted"], font=("sans-serif",9)).pack(anchor="w", pady=(14,4))
        log_outer = tk.Frame(cont, bg=C["input_bg"],
            highlightthickness=1, highlightbackground=C["border"])
        log_outer.pack(fill="both", expand=True)
        self.log = tk.Text(log_outer, bg=C["input_bg"], fg="#86efac",
            font=("monospace",9), state="disabled", wrap="word",
            relief="flat", bd=0, padx=8, pady=8)
        sb = ttk.Scrollbar(log_outer, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True)
        self._started = False

    def on_enter(self):
        if not self._started:
            self._started = True
            self.app.set_nav_enabled(False)
            threading.Thread(target=self._run, daemon=True).start()

    def _log(self, msg):
        def _d():
            self.log.configure(state="normal")
            self.log.insert("end", f"[*] {msg}\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.after(0, _d)

    def _prog(self, pct, msg=None):
        def _d():
            self.overall_var.set(pct)
            self.pct_lbl.configure(text=f"{int(pct)}%")
            if msg: self.msg_var.set(msg)
        self.after(0, _d)

    def _run(self):
        B = self.B
        try:
            os.makedirs(TARGETDIR, exist_ok=True)

            self._prog(5, "Memformat dan mount partisi...")
            mounts_sorted = sorted(
                getattr(self.app, "mounts_config", []),
                key=lambda x: len(x[1][1].get().strip()))
            fstab_entries = []
            for dev, (fs_var, mp_var, fmt_var) in mounts_sorted:
                fs = fs_var.get(); mp = mp_var.get().strip(); do_fmt = fmt_var.get()
                if not mp: continue
                if do_fmt:
                    self._log(f"Format {dev} → {fs}...")
                    ok, err = B.format_partition(dev, fs)
                    if not ok: raise RuntimeError(f"Format {dev} gagal: {err}")
                self._log(f"Mount {dev} → {TARGETDIR}{mp}")
                ok, err = B.mount_filesystem(dev, fs, mp)
                if not ok and fs != "swap":
                    raise RuntimeError(f"Mount {dev} gagal: {err}")
                fstab_entries.append((dev, fs, mp))

            self._prog(15, "Memasang paket sistem...")
            source = B.get_option("SOURCE","local")
            dm     = B.get_option("DISPLAY_MANAGER","none")
            if source == "local":
                ok, err = B.install_local(lambda m: (self._log(m),
                    self._prog(min(self.overall_var.get()+4, 55), m)))
            else:
                ok, err = B.install_network(
                    B.get_option("MIRROR",""), dm,
                    lambda m: (self._log(m),
                        self._prog(min(self.overall_var.get()+3, 55), m)))
            if not ok: raise RuntimeError(f"Instalasi paket gagal:\n{err}")

            steps = [
                (60, "Menulis /etc/fstab...",        lambda: B.write_fstab(fstab_entries)),
                (64, "Mengatur keymap...",            B.set_keymap),
                (67, "Mengatur locale...",            B.set_locale),
                (70, "Mengatur timezone...",          B.set_timezone),
                (73, "Mengatur hostname...",          B.set_hostname),
                (76, "Mengatur password root...",     B.set_rootpassword),
                (79, "Membuat akun pengguna...",      B.set_useraccount),
                (82, "Mengaktifkan NetworkManager...",B.set_network),
            ]
            for pct, msg, fn in steps:
                self._prog(pct, msg); self._log(msg); fn()

            self._prog(85, "Memasang bootloader...")
            ok, err = B.install_bootloader(self._log)
            if not ok: self._log(f"PERINGATAN: {err}")

            self._prog(90, "Mengatur display manager & login...")
            self._log("Mengatur display manager & autologin...")
            B.set_display_manager(self._log)

            self._prog(94, "Mengaktifkan service...")
            for svc in ["dbus", "NetworkManager"]:
                B.enable_service(svc)

            self._prog(97, "Membersihkan...")
            B.cleanup(self._log)

            self._prog(99, "Unmount filesystem...")
            B.umount_filesystems()

            self._prog(100, "✓ Instalasi selesai!")
            self._log("✓ T4n OS berhasil diinstal!")

            # ── Self-destruct: hapus script & config sementara ──────────────
            self._prog(100, "Menghapus script installer dari sistem...")
            B.self_destruct(self._log)

            self.after(800, self.app.go_next)

        except Exception as e:
            err_msg = str(e)
            self._log(f"ERROR: {err_msg}")
            self._prog(0, "Instalasi gagal!")
            self.after(0, lambda m=err_msg: messagebox.showerror(
                "Instalasi Gagal", f"{m}\n\nLog: {LOG_FILE}"))
            self.after(0, lambda: self.app.set_nav_enabled(True))


# ─── Halaman: Selesai ─────────────────────────────────────────────────────────

class DonePage(BasePage):
    def build(self):
        cont = tk.Frame(self, bg=C["bg"])
        cont.pack(fill="both", expand=True, padx=40, pady=40)

        icon = tk.Frame(cont, bg=C["success"], width=72, height=72)
        icon.pack(); icon.pack_propagate(False)
        tk.Label(icon, text="✓", bg=C["success"], fg="white",
            font=("sans-serif", 28, "bold")).pack(expand=True)

        tk.Label(cont, text="Instalasi Selesai!", bg=C["bg"], fg=C["text"],
            font=("sans-serif", 22, "bold")).pack(pady=(20,6))
        tk.Label(cont, bg=C["bg"], fg=C["text_muted"],
            font=("sans-serif",10), justify="center", wraplength=440,
            text=("T4n OS berhasil diinstal ke komputer Anda.\n"
                  "Lepas media instalasi, lalu restart untuk mulai menggunakan T4n OS.")
        ).pack(pady=(0,20))

        btn_row = tk.Frame(cont, bg=C["bg"])
        btn_row.pack()
        StyledButton(btn_row, "Restart Sekarang",
            command=lambda: os.system("shutdown -r now"),
            primary=True).pack(side="left", padx=8, ipadx=10, ipady=4)
        StyledButton(btn_row, "Keluar ke Desktop",
            command=lambda: sys.exit(0)).pack(side="left", padx=8, ipadx=10, ipady=4)


# ─── Aplikasi Utama ───────────────────────────────────────────────────────────

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("940x620")
        self.minsize(860, 560)
        self.configure(bg=C["bg"])
        self.resizable(True, True)

        self._apply_ttk_style()
        self.backend       = Backend()
        self.mounts_config = []
        self.step_index    = 0
        self._build_ui()
        self._show_step(0)

    def _apply_ttk_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TCombobox",
            fieldbackground=C["input_bg"], background=C["card"],
            foreground=C["text"], selectbackground=C["card"],
            arrowcolor=C["text"], bordercolor=C["border"])
        s.map("TCombobox",
            fieldbackground=[("readonly", C["input_bg"])],
            foreground=[("readonly", C["text"])])
        s.configure("TScrollbar",
            background=C["card"], troughcolor=C["input_bg"],
            arrowcolor=C["text_muted"])

    def _build_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=C["sidebar"], width=210)
        self.sidebar.pack(side="left", fill="y"); self.sidebar.pack_propagate(False)

        logo = tk.Frame(self.sidebar, bg=C["accent"], height=54)
        logo.pack(fill="x")
        tk.Label(logo, text="  T4n OS Installer",
            bg=C["accent"], fg="white",
            font=("monospace", 11, "bold"), anchor="w").pack(fill="x", padx=8, expand=True)

        self.step_btns = []
        for i, (_, label) in enumerate(STEPS):
            btn = tk.Label(self.sidebar,
                text=f"  {i+1:02d}  {label}",
                bg=C["sidebar"], fg=C["text_muted"],
                font=("sans-serif",9), anchor="w", pady=7, padx=4)
            btn.pack(fill="x")
            self.step_btns.append(btn)

        # Main
        main = tk.Frame(self, bg=C["bg"])
        main.pack(side="left", fill="both", expand=True)

        self.page_cont = tk.Frame(main, bg=C["bg"])
        self.page_cont.pack(fill="both", expand=True)

        tk.Frame(main, bg=C["border"], height=1).pack(fill="x", side="bottom")
        nav = tk.Frame(main, bg=C["sidebar"], height=56)
        nav.pack(fill="x", side="bottom"); nav.pack_propagate(False)

        self.btn_back = StyledButton(nav, "← Kembali", command=self.go_back)
        self.btn_back.pack(side="left", padx=16, pady=10)
        self.next_lbl = tk.StringVar(value="Lanjut →")
        self.btn_next = StyledButton(nav, "", command=self.go_next, primary=True)
        self.btn_next.configure(textvariable=self.next_lbl)
        self.btn_next.pack(side="right", padx=16, pady=10, ipadx=8)

        # Buat halaman
        page_classes = [
            WelcomePage, LocalePage, KeyboardPage, NetworkPage,
            DiskPage, AccountPage, LoginPage, SummaryPage,
            InstallPage, DonePage,
        ]
        self.pages = []
        for cls in page_classes:
            p = cls(self.page_cont, self)
            p.place(relwidth=1, relheight=1)
            self.pages.append(p)

    def _show_step(self, idx):
        for i, btn in enumerate(self.step_btns):
            if i < idx:
                btn.configure(bg=C["sidebar"], fg=C["step_done"],
                    font=("sans-serif",9,"normal"))
            elif i == idx:
                btn.configure(bg=C["card"], fg=C["step_active"],
                    font=("sans-serif",9,"bold"))
            else:
                btn.configure(bg=C["sidebar"], fg=C["text_muted"],
                    font=("sans-serif",9,"normal"))

        page = self.pages[idx]
        page.lift(); page.on_enter()

        sid = STEPS[idx][0]
        if sid == "done":
            self.btn_next.pack_forget(); self.btn_back.pack_forget()
        elif sid == "install":
            self.btn_next.pack_forget(); self.btn_back.pack_forget()
        else:
            self.next_lbl.set("Mulai Instalasi ▶" if sid=="summary" else "Lanjut →")
            self.btn_next.pack(side="right", padx=16, pady=10, ipadx=8)
            self.btn_back.pack(side="left", padx=16, pady=10)

        self.btn_back.configure(state="normal" if idx > 0 else "disabled")

    def go_next(self):
        page = self.pages[self.step_index]
        if page and not page.validate(): return
        ni = self.step_index + 1
        if ni < len(self.pages):
            self.step_index = ni
            self._show_step(ni)

    def go_back(self):
        pi = self.step_index - 1
        if pi >= 0:
            self.step_index = pi
            self._show_step(pi)

    def set_nav_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.btn_next.configure(state=state)
        self.btn_back.configure(state=state)


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    if os.geteuid() != 0:
        print("ERROR: Installer harus dijalankan sebagai root!")
        print("       sudo python3 installer.py")
        sys.exit(1)
    open(LOG_FILE, "w").close()
    app = InstallerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
