"""Build a self-contained local reading artifact. No network or web service."""
from pathlib import Path
import html
import re
from urllib.parse import unquote, urlsplit
import markdown
from markdown.extensions.toc import slugify

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / "README.md", *sorted((ROOT / "docs").glob("[0-9][0-9]-*.md")), ROOT / "VALIDATION.md"]
IDS = {p.resolve(): f"chapter-{i:02d}" for i, p in enumerate(FILES)}


def architecture_svg():
    labels = [
        ("CLOUD / FLEET", "Telemetry, digital twin, release decisions"),
        ("VEHICLE APPLICATIONS", "Advisory, HMI, domain-specific logic"),
        ("DATA / SERVICE ABSTRACTION", "VSS + KUKSA; services via explicit APIs"),
        ("MIDDLEWARE / VEHICLE I-O", "gRPC, SOME-IP, IPC; CAN providers"),
        ("EXECUTION / OS", "Linux or RTOS; process, container, VM"),
        ("HARDWARE", "HPC, zones, MCUs, sensors, actuators"),
    ]
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 600" role="img" aria-labelledby="at ad">',
           '<title id="at">SDV architecture study map</title><desc id="ad">Six architectural layers plus lifecycle, identity, observability, diagnostics and updates across the layers.</desc>',
           '<rect width="900" height="600" rx="18" fill="#0c1526"/>',
           '<style>text{font-family:Segoe UI,Arial,sans-serif;fill:#e8eef9}.label{font-size:17px;font-weight:700}.sub{font-size:15px;fill:#b9c8e0}</style>',
           '<text x="30" y="36" class="label">SDV — ARCHITECTURE STUDY MAP</text>']
    for i, (title, desc) in enumerate(labels):
        y = 58+i*80
        out.extend([f'<rect x="28" y="{y}" width="650" height="66" rx="10" fill="{["#164e63", "#1e3a5f", "#293c67", "#35365e", "#3b3153", "#3b3445"][i]}" stroke="#6783ae"/>',
                    f'<text x="48" y="{y+26}" class="label">{html.escape(title)}</text>',
                    f'<text x="48" y="{y+49}" class="sub">{html.escape(desc)}</text>'])
        if i < len(labels)-1:
            out.append(f'<path d="M350 {y+66} v14" stroke="#81c9e8" stroke-width="3"/>')
    out.extend(['<rect x="704" y="58" width="168" height="466" rx="10" fill="#173c38" stroke="#63c5ac"/>'])
    for j, text in enumerate(["LIFECYCLE", "Identity / ACL", "Logging", "Metrics / health", "Diagnostics", "Updates", "Resource limits"]):
        out.append(f'<text x="720" y="{98+j*53}" class="{ "label" if j==0 else "sub"}">{html.escape(text)}</text>')
    out.extend(['<text x="30" y="565" class="sub">Teaching architecture. Components and boundaries must be selected for each project.</text>', '</svg>'])
    return ''.join(out)


def build():
    sections, navigation = [], []
    for path in FILES:
        raw = path.read_text(encoding="utf-8")
        title = raw.splitlines()[0].lstrip("# ")
        section_id = IDS[path.resolve()]
        md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                               extension_configs={"toc": {"slugify": lambda value, sep, prefix=section_id: prefix+"-"+slugify(value, sep)}})
        rendered = md.convert(raw)

        def rewrite(match):
            href = html.unescape(match.group(1))
            parts = urlsplit(href)
            if parts.scheme or parts.netloc or not parts.path:
                return match.group(0)
            target = (path.parent / unquote(parts.path)).resolve()
            if target in IDS:
                new = "#"+IDS[target]
                if parts.fragment:
                    new += "-"+parts.fragment
            else:
                try:
                    new = target.relative_to(ROOT).as_posix()
                except ValueError:
                    return match.group(0)
                if parts.fragment:
                    new += "#"+parts.fragment
            return 'href="'+html.escape(new, quote=True)+'"'

        rendered = re.sub(r'href="([^"]*)"', rewrite, rendered)
        illustration = architecture_svg() if path.name.startswith("01-") else ""
        if illustration:
            rendered = re.sub(r'(</h1>)', r'\1'+illustration, rendered, count=1)
        navigation.append(f'<a href="#{section_id}">{html.escape(title)}</a>')
        source = path.relative_to(ROOT).as_posix()
        sections.append(f'<section id="{section_id}" data-title="{html.escape(title, quote=True)}"><div class="source">Nguồn Markdown: <a href="{source}">{source}</a></div>{rendered}</section>')
    template = (ROOT / "tools/reader-template.html").read_text(encoding="utf-8")
    output = template.replace("{{NAV}}", '\n'.join(navigation)).replace("{{CONTENT}}", '\n'.join(sections))
    (ROOT / "START_HERE.html").write_text(output, encoding="utf-8")
    (ROOT / "diagrams").mkdir(exist_ok=True)
    (ROOT / "diagrams/01-reference-architecture.svg").write_text(architecture_svg(), encoding="utf-8")
    print(f"Built START_HERE.html: {len(FILES)} sections, {len(output.encode('utf-8')):,} bytes")


if __name__ == "__main__":
    build()
