"""
rewordapp.rewrite.fext
======================

Utilities for inspecting and classifying file name extensions.
"""
import re



COMMON_TLDS = [
    "com", "org", "net", "info", "biz", "xyz", "online", "site",
    "app", "dev", "io", "ai",
    "us", "uk", "ca", "au", "de", "fr", "jp", "cn", "in", "nl", "br",
    "edu", "gov", "mil", "int",
]


COMMON_SUBDOMAINS = [
    # Primary web entry
    "www", "web", "home", "app",

    # API & developer
    "api", "dev", "test", "staging", "beta",
    "docs", "developer", "developers",

    # Authentication & accounts
    "auth", "login", "accounts", "id", "sso",

    # Content & media
    "blog", "news", "media", "static", "cdn", "assets",

    # Admin & support
    "admin", "portal", "support", "help", "status", "dashboard",

    # Mail & communication
    "mail", "smtp", "imap", "pop", "mx", "webmail",

    # Security / infrastructure
    "vpn", "proxy", "gateway", "edge",

    # Language / region (common)
    "en", "fr", "de", "es", "vi", "ja", "zh",
    "us", "uk", "eu", "ca", "jp", "au",
]


class FileExtension:
    TEXT_DATA_EXTENSIONS = {
        # Plain text
        "txt": "text",
        "text": "text",
        "md": "markdown",
        "markdown": "markdown",
        "rst": "restructuredtext",
        "org": "orgmode",
        "tex": "latex",
        "log": "log",

        # Structured data
        "json": "json",
        "yaml": "yaml",
        "yml": "yaml",
        "xml": "xml",
        "toml": "toml",
        "ini": "ini",
        "cfg": "config",
        "conf": "config",
        "csv": "csv",
        "tsv": "tsv",
        "psv": "psv",
        "ndjson": "ndjson",

        # Documentation / markup
        "html": "html",
        "htm": "html",
        "css": "css",
        "man": "manpage",

        # Templates
        "j2": "template",
        "tmpl": "template",
        "template": "template",
        "mustache": "template",
        "hbs": "template",
        "djhtml": "template",
        "textfsm": "template",

        # Programming-adjacent (still text)
        "py": "code",
        "pyi": "code",
        "js": "code",
        "ts": "code",
        "tsx": "code",
        "c": "code",
        "h": "code",
        "cpp": "code",
        "hpp": "code",
        "java": "code",
        "rb": "code",
        "go": "code",
        "rs": "code",
        "sh": "shell",
        "bash": "shell",
        "zsh": "shell",

        # Build / metadata
        "mk": "makefile",
        "sql": "sql",
        "dump": "sqldump",
        "lock": "lockfile",

        # Special text formats
        "diff": "diff",
        "patch": "patch",
        "sha1": "checksum",
        "sha256": "checksum",
        "md5": "checksum",
        "snippet": "snippet",
    }

    PROGRAMMING_EXTENSIONS = {
        # Python
        "py": "python",
        "pyi": "python",
        "pyw": "python",
        "pyx": "cython",
        "pyd": "python-extension",

        # JavaScript / TypeScript
        "js": "javascript",
        "mjs": "javascript-module",
        "cjs": "javascript-commonjs",
        "jsx": "react-jsx",
        "ts": "typescript",
        "tsx": "react-tsx",

        # C / C++
        "c": "c",
        "h": "c-header",
        "cpp": "cpp",
        "cc": "cpp",
        "cxx": "cpp",
        "hpp": "cpp-header",
        "hh": "cpp-header",
        "hxx": "cpp-header",

        # Java
        "java": "java",
        "class": "java-bytecode",
        "jar": "java-archive",

        # Rust
        "rs": "rust",

        # Go
        "go": "go",

        # Ruby
        "rb": "ruby",
        "erb": "ruby-template",
        "rake": "ruby-rakefile",

        # PHP
        "php": "php",
        "php3": "php",
        "php4": "php",
        "php5": "php",
        "phtml": "php-template",

        # Perl
        "pl": "perl",
        "pm": "perl-module",
        "pod": "perl-doc",

        # Shell scripting
        "sh": "shell",
        "bash": "bash",
        "zsh": "zsh",
        "ksh": "korn-shell",
        "csh": "c-shell",
        "tcsh": "tc-shell",

        # Windows scripting
        "bat": "batch",
        "cmd": "batch",
        "ps1": "powershell",
        "psm1": "powershell-module",
        "vbs": "vbscript",
        "wsf": "windows-script-file",

        # Functional languages
        "hs": "haskell",
        "lhs": "haskell-literate",
        "ml": "ocaml",
        "mli": "ocaml-interface",
        "fs": "fsharp",
        "fsi": "fsharp-interface",
        "fsx": "fsharp-script",

        # .NET languages
        "cs": "csharp",
        "vb": "vbnet",

        # R / Data science
        "r": "r",
        "rmd": "r-markdown",
        "ipynb": "jupyter-notebook",

        # Lua / Tcl / Awk / Sed
        "lua": "lua",
        "tcl": "tcl",
        "awk": "awk",
        "sed": "sed",

        # Build systems
        "mk": "makefile",
        "make": "makefile",
        "gradle": "gradle",
        "groovy": "groovy",
        "cmake": "cmake",
        "ninja": "ninja-build",

        # SQL / database scripts
        "sql": "sql",
        "psql": "postgresql-script",
        "mysql": "mysql-script",
    }

    MARKUP_WEB_EXTENSIONS = {
        # HTML & web documents
        "html": "html",
        "htm": "html",
        "xhtml": "html",
        "shtml": "html",
        "dhtml": "html",

        # Stylesheets
        "css": "css",
        "scss": "sass",
        "sass": "sass",
        "less": "less",

        # Web templates / templating engines
        "ejs": "template",
        "pug": "template",
        "jade": "template",
        "hbs": "handlebars",
        "mustache": "mustache",
        "twig": "twig",
        "liquid": "liquid",
        "djhtml": "django-template",
        "jinja": "jinja2",
        "j2": "jinja2",
        "tmpl": "template",
        "template": "template",
        "njk": "nunjucks",

        # Web components / frameworks
        "vue": "vue",
        "svelte": "svelte",
        "astro": "astro",

        # XML-based markup
        "xml": "xml",
        "xsd": "xml-schema",
        "xsl": "xslt",
        "xslt": "xslt",
        "svg": "svg",
        "rss": "rss",
        "atom": "atom",
        "opf": "epub-metadata",
        "plist": "plist",

        # JSON-based web formats
        "json": "json",
        "jsonc": "jsonc",
        "json5": "json5",
        "geojson": "geojson",
        "webmanifest": "web-manifest",
        "manifest": "manifest",
        "map": "source-map",

        # YAML-based web config
        "yaml": "yaml",
        "yml": "yaml",

        # Lightweight markup
        "md": "markdown",
        "markdown": "markdown",
        "mdx": "mdx",
        "rst": "restructuredtext",
        "adoc": "asciidoc",
        "asciidoc": "asciidoc",
    }

    IMAGE_EXTENSIONS = {
        # Common raster formats
        "png": "raster",
        "jpg": "raster",
        "jpeg": "raster",
        "gif": "raster",
        "bmp": "raster",
        "tif": "raster",
        "tiff": "raster",
        "webp": "raster",

        # High‑quality / professional raster
        "psd": "photoshop",
        "psb": "photoshop-large",
        "xcf": "gimp",
        "kra": "krita",
        "exr": "hdr",
        "hdr": "hdr",

        # Vector formats
        "svg": "vector",
        "ai": "illustrator",
        "eps": "eps",
        "pdf": "pdf-vector",  # mixed content but often vector

        # Camera RAW formats
        "cr2": "raw-canon",
        "cr3": "raw-canon",
        "nef": "raw-nikon",
        "arw": "raw-sony",
        "rw2": "raw-panasonic",
        "orf": "raw-olympus",
        "dng": "raw-dng",
        "raf": "raw-fujifilm",

        # Icon & UI formats
        "ico": "icon",
        "icns": "icon-macos",
        "cur": "cursor",
        "ani": "cursor-animated",

        # Scientific / specialized
        "fits": "astronomy",
        "fit": "astronomy",
        "dcm": "dicom",
        "dicom": "dicom",
        "pgm": "netpbm",
        "ppm": "netpbm",
        "pbm": "netpbm",
        "dds": "texture",
        "ktx": "texture",
    }

    AUDIO_EXTENSIONS = {
        # Common compressed audio
        "mp3": "compressed",
        "aac": "compressed",
        "m4a": "compressed",
        "ogg": "compressed",
        "oga": "compressed",
        "opus": "compressed",
        "wma": "compressed",

        # Lossless audio
        "flac": "lossless",
        "alac": "lossless",
        "wav": "lossless",
        "aiff": "lossless",
        "aif": "lossless",
        "aifc": "lossless",

        # High‑resolution / professional formats
        "pcm": "raw-pcm",
        "caf": "apple-caf",
        "dsd": "dsd",
        "dsf": "dsd",
        "dff": "dsd",
        "wv": "wavpack",

        # MIDI & synthesized formats
        "mid": "midi",
        "midi": "midi",
        "kar": "midi-karaoke",
        "rmi": "midi",

        # Tracker / module formats
        "mod": "tracker",
        "xm": "tracker",
        "it": "tracker",
        "s3m": "tracker",

        # Voice / telephony formats
        "amr": "voice",
        "awb": "voice",
        "gsm": "voice",
        "vox": "voice",

        # Streaming / playlist formats
        "m3u": "playlist",
        "m3u8": "playlist",
        "pls": "playlist",
        "xspf": "playlist",

        # Container formats (may contain audio)
        "mp4": "container",
        "m4b": "audiobook",
        "mka": "matroska-audio",
    }

    VIDEO_EXTENSIONS = {
        # Common video formats
        "mp4": "video",
        "m4v": "video",
        "mov": "video",
        "avi": "video",
        "wmv": "video",
        "flv": "video",
        "webm": "video",
        "mkv": "video",

        # MPEG family
        "mpg": "mpeg",
        "mpeg": "mpeg",
        "mpe": "mpeg",
        "mp2": "mpeg",
        "mpv": "mpeg-video",
        "m2v": "mpeg2-video",

        # High-efficiency / modern codecs
        "hevc": "hevc",
        "h265": "hevc",
        "h264": "h264",
        "av1": "av1",

        # Raw / uncompressed
        "yuv": "raw-video",
        "rgb": "raw-video",

        # Professional / broadcast formats
        "mxf": "broadcast",
        "gxf": "broadcast",
        "m2ts": "blu-ray",
        "mts": "avchd",
        "ts": "transport-stream",

        # Apple / QuickTime variants
        "qt": "quicktime",
        "prores": "prores",

        # Camera / device formats
        "3gp": "mobile",
        "3g2": "mobile",
        "mod": "camcorder",
        "tod": "camcorder",

        # Animation formats
        "swf": "flash",
        "fla": "flash-source",

        # Playlist / container helpers
        "m3u8": "playlist",
        "m3u": "playlist",
    }

    ARCHIVE_EXTENSIONS = {
        # ZIP family
        "zip": "zip",
        "zipx": "zip-extended",

        # Tarball families
        "tar": "tar",
        "tgz": "tar-gzip",
        "tbz": "tar-bzip2",
        "tbz2": "tar-bzip2",
        "txz": "tar-xz",
        "tlz": "tar-lzma",
        "tzst": "tar-zstd",

        # Compression formats
        "gz": "gzip",
        "bz": "bzip",
        "bz2": "bzip2",
        "xz": "xz",
        "lz": "lzma",
        "lzma": "lzma",
        "zst": "zstd",
        "br": "brotli",
        "lz4": "lz4",

        # 7‑Zip family
        "7z": "7zip",
        "7zip": "7zip",

        # RAR family
        "rar": "rar",
        "rev": "rar-recovery",

        # ISO / disk images
        "iso": "disk-image",
        "img": "disk-image",
        "dmg": "apple-disk-image",
        "vhd": "virtual-disk",
        "vhdx": "virtual-disk",
        "vmdk": "virtual-disk",

        # Windows cabinet & installers
        "cab": "cabinet",
        "msi": "installer",
        "msp": "installer-patch",

        # Linux package archives
        "deb": "debian-package",
        "rpm": "rpm-package",
        "apk": "alpine-package",

        # Backup formats
        "bak": "backup",
        "old": "backup",
        "orig": "backup",
        "bundle": "bundle",

        # Multi‑part archives
        "part": "multipart",
        "001": "multipart",
        "002": "multipart",
    }

    DOCUMENT_EXTENSIONS = {
        # Office documents (Microsoft)
        "doc": "msword",
        "docx": "msword",
        "dot": "msword-template",
        "dotx": "msword-template",
        "xls": "msexcel",
        "xlsx": "msexcel",
        "xlsm": "msexcel-macro",
        "xlt": "msexcel-template",
        "ppt": "mspowerpoint",
        "pptx": "mspowerpoint",
        "pps": "mspowerpoint-slideshow",
        "ppsx": "mspowerpoint-slideshow",
        "pot": "mspowerpoint-template",
        "potx": "mspowerpoint-template",

        # OpenDocument formats (LibreOffice / OpenOffice)
        "odt": "opendocument-text",
        "ott": "opendocument-text-template",
        "ods": "opendocument-spreadsheet",
        "ots": "opendocument-spreadsheet-template",
        "odp": "opendocument-presentation",
        "otp": "opendocument-presentation-template",

        # Portable formats
        "pdf": "pdf",
        "xps": "xps",
        "oxps": "xps",

        # Rich text formats
        "rtf": "rich-text",
        "rtfd": "rich-text-directory",

        # Plain text variants (documents)
        "txt": "text",
        "text": "text",
        "md": "markdown",
        "markdown": "markdown",
        "rst": "restructuredtext",
        "adoc": "asciidoc",
        "asciidoc": "asciidoc",

        # eBook formats
        "epub": "ebook",
        "mobi": "ebook",
        "azw": "ebook-kindle",
        "azw3": "ebook-kindle",
        "fb2": "ebook-fb2",

        # Note-taking formats
        "one": "onenote",
        "onenote": "onenote",
        "nb": "mathematica-notebook",
        "nbp": "mathematica-player",

        # Document markup formats
        "tex": "latex",
        "ltx": "latex",
        "bib": "bibtex",

        # Data-rich document formats
        "csv": "csv",
        "tsv": "tsv",
        "xml": "xml",
        "json": "json",
        "yaml": "yaml",
        "yml": "yaml",

        # Publishing formats
        "indd": "indesign",
        "idml": "indesign-markup",
        "ps": "postscript",
        "eps": "postscript-eps",

        # Misc document formats
        "msg": "outlook-message",
        "eml": "email",
        "wpd": "wordperfect",
        "pages": "apple-pages",
        "numbers": "apple-numbers",
        "key": "apple-keynote",
    }

    EXECUTABLE_EXTENSIONS = {
        # Windows executables
        "exe": "windows-executable",
        "dll": "windows-library",
        "sys": "windows-system",
        "msi": "windows-installer",
        "msp": "windows-installer-patch",
        "bat": "batch-script",
        "cmd": "batch-script",
        "com": "dos-executable",
        "scr": "windows-screensaver",

        # PowerShell
        "ps1": "powershell-script",
        "psm1": "powershell-module",
        "psd1": "powershell-data",

        # Linux / Unix executables
        # (Note: Linux executables often have *no extension*, but these appear in practice)
        "bin": "linux-binary",
        "run": "linux-installer",
        "out": "compiled-output",
        "so": "shared-library",

        # macOS executables
        "app": "macos-application",
        "pkg": "macos-installer",
        "dylib": "macos-library",
        "bundle": "macos-bundle",

        # WebAssembly
        "wasm": "webassembly",
        "wat": "webassembly-text",

        # Java / JVM
        "jar": "java-archive",
        "war": "java-web-archive",
        "ear": "java-enterprise-archive",
        "class": "java-bytecode",

        # .NET / CLR
        # "dll": "dotnet-library",
        # "exe": "dotnet-executable",

        # Compiled bytecode / VM formats
        "pyc": "python-bytecode",
        "pyo": "python-optimized-bytecode",
        "luac": "lua-bytecode",

        # Firmware / embedded binaries
        "hex": "intel-hex",
        "elf": "elf-binary",
        # "bin": "raw-binary",
        "img": "disk-image",
        "rom": "firmware",
        "iso": "disk-image",

        # Android / mobile
        "apk": "android-package",
        "aab": "android-app-bundle",
        "dex": "dalvik-executable",
        # "so": "android-native-library",

        # iOS
        "ipa": "ios-application",
    }

    CONFIG_SYSTEM_EXTENSIONS = {
        # Generic config files
        "conf": "config",
        "cfg": "config",
        "config": "config",
        "ini": "ini",
        "rc": "run-control",
        "properties": "properties",
        "prop": "properties",

        # Environment / secrets
        "env": "environment",
        "dotenv": "environment",
        "envrc": "environment",

        # YAML / JSON configs
        "yaml": "yaml",
        "yml": "yaml",
        "json": "json",
        "jsonc": "jsonc",

        # Systemd units
        "service": "systemd-unit",
        "socket": "systemd-unit",
        "target": "systemd-unit",
        "timer": "systemd-unit",
        "mount": "systemd-unit",
        "automount": "systemd-unit",
        "path": "systemd-unit",

        # Linux system files
        "fstab": "linux-fstab",
        "modprobe": "linux-modprobe",
        "sysctl": "linux-sysctl",
        "pam": "linux-pam",
        "rules": "udev-rules",

        # Shell configuration
        "bashrc": "shell-config",
        "bash_profile": "shell-config",
        "profile": "shell-config",
        "zshrc": "shell-config",
        "zprofile": "shell-config",
        "cshrc": "shell-config",
        "tcshrc": "shell-config",

        # Hosts / networking
        "hosts": "hosts",
        "resolv": "dns-resolver",
        "network": "network-config",
        "nmconnection": "networkmanager",

        # Package manager configs
        "repo": "repository-config",
        "list": "package-list",
        "sources": "package-sources",

        # macOS system files
        "plist": "plist",
        "strings": "localization-strings",

        # Windows system files
        "reg": "registry",
        "inf": "windows-driver-inf",
        # "ini": "windows-ini",
        "manifest": "windows-manifest",

        # Application configs
        "toml": "toml",
        "lock": "lockfile",
        "editorconfig": "editorconfig",
        "gitattributes": "git-attributes",
        "gitignore": "git-ignore",
        "npmrc": "npm-config",
        "yarnrc": "yarn-config",
        "pylintrc": "pylint-config",
        "flake8": "flake8-config",
        "dockerfile": "dockerfile",
        "dockerignore": "docker-ignore",
        "compose": "docker-compose",
    }

    GIT_EXTENSIONS = {
        "patch": "git-patch",
        "diff": "git-diff",
        "bundle": "git-bundle",
        "rebase": "git-rebase-script",
        "lock": "git-lockfile",
        "pack": "git-packfile",
        "idx": "git-pack-index",
        "keep": "git-pack-keep",
        "bitmap": "git-pack-bitmap",
        "rev": "git-revision-list",
        "commit": "git-commit-object",
        "tree": "git-tree-object",
        "blob": "git-blob-object",
        "tag": "git-tag-object",
    }

    CONTAINER_EXTENSIONS = {
        # Docker / OCI containers
        "tar": "oci-image-tar",  # docker save/export
        "oci": "oci-image-layout",
        "ociarchive": "oci-archive",
        "docker": "docker-image",
        "dockerfile": "dockerfile",  # build recipe, not binary

        # Linux container formats
        "sif": "singularity-image",
        "squashfs": "squashfs-image",
        "sqsh": "squashfs-image",

        # Virtual machine disk images
        "vmdk": "vmware-disk",
        "vdi": "virtualbox-disk",
        "vhd": "virtual-hard-disk",
        "vhdx": "virtual-hard-disk",
        "qcow": "qemu-disk",
        "qcow2": "qemu-disk",
        "img": "disk-image",
        "iso": "disk-image",

        # Application containers / bundles
        "appimage": "linux-appimage",
        "snap": "ubuntu-snap",
        "flatpak": "flatpak-bundle",
        "flatpakref": "flatpak-ref",
        "flatpakrepo": "flatpak-repo",

        # macOS bundles
        "app": "macos-app-bundle",
        "pkg": "macos-installer",
        "dmg": "macos-disk-image",
        "ipa": "ios-app-package",

        # Android packages
        "apk": "android-package",
        "aab": "android-app-bundle",

        # Java archives (container-like)
        "jar": "java-archive",
        "war": "java-web-archive",
        "ear": "java-enterprise-archive",

        # Generic container formats
        "bundle": "bundle",
        "pak": "package",
        "paket": "package",
    }

    DB_EXTENSIONS = {
        # SQLite
        "db": "sqlite",
        "sqlite": "sqlite",
        "sqlite3": "sqlite",
        "db3": "sqlite",
        "sdb": "sqlite",
        "s3db": "sqlite",

        # MySQL / MariaDB
        "frm": "mysql-schema",
        "ibd": "mysql-innodb",
        "myd": "mysql-myisam-data",
        "myi": "mysql-myisam-index",
        "sql": "sql-dump",

        # PostgreSQL
        "psql": "postgres-script",
        "pgsql": "postgres-script",
        "dump": "postgres-dump",
        "backup": "postgres-backup",

        # Microsoft SQL Server
        "mdf": "sqlserver-primary",
        "ndf": "sqlserver-secondary",
        "ldf": "sqlserver-log",
        "bak": "sqlserver-backup",

        # Oracle
        "dbf": "oracle-db-file",
        "ctl": "oracle-control-file",
        "dmp": "oracle-dump",
        "ora": "oracle-config",

        # MongoDB
        "bson": "mongodb-bson",
        "wt": "wiredtiger",
        "ns": "mongodb-namespace",

        # Redis
        "rdb": "redis-dump",
        "aof": "redis-append-log",

        # Cassandra
        # "db": "cassandra-sstable",
        "sst": "cassandra-sstable",
        "crc32": "cassandra-checksum",
        "index": "cassandra-index",
        "summary": "cassandra-summary",
        "toc": "cassandra-table-of-contents",

        # LevelDB / RocksDB
        "ldb": "leveldb",
        # "sst": "rocksdb-sstable",

        # Firebird / InterBase
        "fdb": "firebird",
        "gdb": "interbase",

        # MS Access
        "mdb": "access",
        "accdb": "access",

        # dBase / FoxPro
        # "dbf": "dbase",
        "cdx": "dbase-index",
        "fpt": "foxpro-memo",

        # Paradox
        "px": "paradox-index",
        "xg0": "paradox",
        "val": "paradox",

        # FileMaker
        "fp7": "filemaker",
        "fmp12": "filemaker",

        # Generic / flat-file databases
        "dat": "generic-data",
        "csv": "csv",
        "tsv": "tsv",
        "json": "json",
        "yaml": "yaml",
        "yml": "yaml",
    }

    UNKNOWN_EXTENSIONS = {
        "dat": "generic-data",
        "bin": "binary",
        "raw": "raw-data",
        "pak": "package",
        "bundle": "bundle",
        "res": "resource",
        "rsc": "resource",
        "asset": "game-asset",
        "wad": "game-data",
        "pk3": "game-data",
        "uasset": "unreal-asset",
        "umap": "unreal-map",
        "lvl": "game-level",
        "map": "game-map",
        "sav": "save-file",
        "gcf": "steam-cache",
        "vpk": "valve-package",
        "idx": "index",
        "toc": "table-of-contents",
        "cache": "cache",
        "tmp": "temporary",
        "temp": "temporary",
        "bak": "backup",
        "old": "backup-old",
        "orig": "backup-original",
        "enc": "encrypted",
        "crypt": "encrypted",
        "aes": "encrypted",
        "xor": "obfuscated",
        "lock": "locked",
        "upd": "update",
        "sig": "signature",
        "chk": "checksum",
        "dmp": "dump",
        "zzz": "placeholder",
        "foo": "test",
        "bar": "test",
        "unknown": "unknown",
    }


def is_known_extension(ext: str) -> bool:
    """Return True if the extension exists in any *_EXTENSIONS mapping."""
    ext = ext.lower().lstrip(".")

    for attr in dir(FileExtension):
        if attr.endswith("_EXTENSIONS"):
            mapping = getattr(FileExtension, attr)
            if isinstance(mapping, dict) and ext in mapping:
                return True

    return False


def has_known_extension(value: str) -> bool:
    """Return True if the filename or extension is recognized."""
    if "." in value:
        _, ext = value.rsplit(".", 1)
        return is_known_extension(ext)

    return is_known_extension(value)


def is_valid_hostname(host: str) -> bool:
    """Return True if the hostname matches a basic DNS-style pattern."""
    pattern = r"(?i)([a-z][a-z0-9-]+[.])+[a-z][a-z0-9-]+"
    return bool(re.fullmatch(pattern, host))


def has_common_tld(host: str) -> bool:
    """Return True if the hostname ends with a known TLD."""
    if not is_valid_hostname(host):
        return False

    _, tld = host.rsplit(".", 1)
    return tld.lower() in {t.lower() for t in COMMON_TLDS}


def has_common_subdomain(host: str) -> bool:
    """Return True if the hostname begins with a known subdomain."""
    if not has_common_tld(host):
        return False

    if host.count(".") < 2:
        return False

    subdomain, _ = host.split(".", 1)

    for prefix in COMMON_SUBDOMAINS:
        pattern = fr"(?i){prefix}[a-z0-9]*"
        if re.fullmatch(pattern, subdomain):
            return True

    return False