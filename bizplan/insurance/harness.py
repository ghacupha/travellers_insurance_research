# SPDX-FileCopyrightText: 2026 ghacupha
# SPDX-License-Identifier: MIT

"""Run lifecycle, input snapshots, and reproducibility manifests."""
from datetime import datetime, timezone, date
from hashlib import sha256
import json
from pathlib import Path
import platform
import shutil
import subprocess
from uuid import uuid4

from .company import Company
from .pipeline import build


def stamp():
    return datetime.now(timezone.utc).isoformat()


def run(config_path, output_dir=None, demo_path=None):
    config_path = Path(config_path).resolve()
    config = json.loads(config_path.read_text())
    if config['schema_version'] != 1:
        raise ValueError('Expected run schema version 1')
    company = Company(**config['company']).validate()
    date.fromisoformat(config['as_of'])
    actuals = (config_path.parent/config['actuals']).resolve()
    if not actuals.is_file():
        raise ValueError(f'Actuals file does not exist: {actuals}')
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid4().hex[:8]
    output = Path(output_dir) if output_dir else Path('output')/run_id
    output.mkdir(parents=True, exist_ok=False)
    manifest = dict(schema_version=1, run_id=run_id, started_at=stamp(),
                    status='running', python=platform.python_version(),
                    company=config['company'], as_of=config['as_of'],
                    inputs={}, code={}, stages=[])
    manifest_path = output/'manifest.json'

    def save():
        temporary = output/'manifest.json.tmp'
        temporary.write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n')
        temporary.replace(manifest_path)

    save()
    try:
        inputs = output/'inputs'
        inputs.mkdir()
        files = {'original_run.json': config_path, 'actuals.json': actuals}
        if demo_path:
            files['synthetic_projection.json'] = Path(demo_path).resolve()
        for name, source in files.items():
            destination = inputs/name
            shutil.copyfile(source, destination)
            manifest['inputs'][name] = dict(original=str(source), snapshot=str(destination.relative_to(output)),
                                           sha256=sha256(destination.read_bytes()).hexdigest())
        replay = dict(config, actuals='actuals.json')
        (inputs/'run.json').write_text(json.dumps(replay, indent=2)+'\n')
        manifest['inputs']['run.json'] = dict(snapshot='inputs/run.json',
                                             sha256=sha256((inputs/'run.json').read_bytes()).hexdigest(),
                                             status='derived_replay_configuration')
        for source in sorted(Path(__file__).parent.glob('*.py')):
            manifest['code'][source.name] = sha256(source.read_bytes()).hexdigest()
        root = Path(__file__).resolve().parents[2]
        try:
            manifest['git_revision'] = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
            manifest['git_dirty'] = bool(subprocess.check_output(
                ['git', 'status', '--porcelain'], cwd=root, text=True, stderr=subprocess.DEVNULL).strip())
        except (OSError, subprocess.CalledProcessError):
            manifest['git_revision'] = None
        manifest['stages'].append(dict(name='snapshot_inputs', status='complete', at=stamp()))
        save()
        build(inputs/'actuals.json', output, config['as_of'],
              inputs/'synthetic_projection.json' if demo_path else None, company)
        manifest['stages'].append(dict(name='validate_compute_render', status='complete', at=stamp()))
        manifest['artifacts'] = {name: sha256((output/name).read_bytes()).hexdigest()
                                 for name in ('research.json', 'research.md')}
        manifest['status'] = 'complete'
    except Exception as exc:
        manifest['status'] = 'failed'
        manifest['error'] = dict(type=type(exc).__name__, message=str(exc))
        raise
    finally:
        manifest['finished_at'] = stamp()
        save()
    return output
