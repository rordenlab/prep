#!/usr/bin/env python3
"""Rebuild this GitHub Pages site from fastprep sample outputs: each <name>_out keeps only its sub-*.html
report and sub-*/figures/*.png (no NIfTI, surfaces or confounds). Usage: python3 sync.py [fastprep_dir]"""
import html, re, shutil, sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else '/Users/chris/src/fastprep')
HERE = Path(__file__).resolve().parent
ABOUT = {  # one line per sample dataset
    'rhyming': 'Siemens 3T, multiband BOLD, phasediff fieldmap',
    'me': 'Siemens 3T, 3-echo BOLD with phase (MEDIC)',
    'ds004958': 'OpenNeuro ds004958: Prisma, multiband rest, AP/PA PEPOLAR (sucor)',
    'ds001796': 'OpenNeuro ds001796: Prisma, multiband rest, phasediff fieldmap',
    'motor3T': 'Siemens 3T: PEPOLAR pair acquired with one polarity, phasediff, and MEDIC runs',
    'motor7T': 'Siemens 7T Terra.X: MP2RAGE (UNI-DEN), four 1 mm 3D-EPI runs, no fieldmap',
}

rows = []
for out in sorted(SRC.glob('*_out')):
    name = out.name[:-4]
    dst = HERE / name
    shutil.rmtree(dst, ignore_errors=True)
    for report in sorted(out.glob('sub-*.html')):
        sub = report.stem
        shutil.copytree(out / sub / 'figures', dst / sub / 'figures')
        shutil.copy2(report, dst / report.name)
        page = report.read_text()
        t = re.search(r'End-to-end time</dt><dd>([0-9.]+ s)', page)
        sdc = re.findall(r'SDC: ([^;<]+)', page)
        rows.append(f'<tr><td><a href="{name}/{report.name}">{html.escape(name)}</a></td><td>{html.escape(sub)}</td>'
                    f'<td>{html.escape(ABOUT.get(name, ""))}</td><td class="n">{t.group(1) if t else ""}</td>'
                    f'<td>{"<br>".join(html.escape(s) for s in sdc)}</td></tr>')

(HERE / 'index.html').write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>fastprep samples</title><style>
:root{{color-scheme:light dark;--bg:#fff;--fg:#1d1d1f;--mut:#6e6e73;--line:#d2d2d7;--acc:#c0392b}}
@media(prefers-color-scheme:dark){{:root{{--bg:#161618;--fg:#f2f2f7;--mut:#a1a1a6;--line:#3a3a3d;--acc:#ff6b5a}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
main{{max-width:1040px;margin:auto;padding:24px 16px 48px}}h1{{font-size:1.6em;margin:0 0 4px}}p{{color:var(--mut)}}
a{{color:var(--acc)}}.wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:.92em}}
th,td{{padding:6px 8px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}}
th{{color:var(--mut);font-weight:500}}.n{{text-align:right;white-space:nowrap}}
</style></head><body><main><h1>fastprep sample reports</h1>
<p>Preprocessing reports (QC figures and methods) from fastprep, a lean fMRIPrep-style pipeline still under
development. Figures only: no imaging data are shared here.</p>
<div class="wrap"><table><tr><th>Dataset</th><th>Subject</th><th>About</th><th class="n">Time</th><th>Distortion correction per run</th></tr>
{"".join(rows)}</table></div></main></body></html>
''')
(HERE / '.nojekyll').touch()  # serve files as-is
print(f'{len(rows)} reports')
