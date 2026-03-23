#!/usr/bin/env python3
"""Evidence bundle automation for CRRE clean-room cycles.

Generates per-cycle evidence bundles (spec/test/traceability/compliance snapshots)
suitable for legal-process review and audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_bundle_artifacts(bundle_dir: Path) -> list[dict]:
    """Collect artifacts from bundle directory."""
    artifacts = []
    for f in bundle_dir.iterdir():
        if f.is_file() and not f.name.endswith(".sha256"):
            try:
                sha256 = compute_sha256(f)
                artifacts.append({
                    "path": str(f.name),
                    "sha256": sha256,
                    "size": f.stat().st_size,
                })
            except Exception as e:
                print(f"Warning: could not hash {f}: {e}", file=sys.stderr)
    return artifacts


def verify_bundle(bundle_dir: Path, require: list[str] | None = None) -> dict:
    """Verify bundle has required artifacts."""
    require = require or ["spec", "test", "traceability", "contamination", "score"]
    
    artifacts = collect_bundle_artifacts(bundle_dir)
    artifact_names = [a["path"].lower() for a in artifacts]
    
    missing = []
    for req in require:
        found = any(req.lower() in name for name in artifact_names)
        if not found:
            missing.append(req)
    
    return {
        "bundle_dir": str(bundle_dir),
        "artifacts": artifacts,
        "required": require,
        "missing": missing,
        "valid": len(missing) == 0,
    }


def finalize_bundle(bundle_dir: Path, write_checksums: bool = False) -> dict:
    """Finalize bundle by generating checksums."""
    bundle_dir = bundle_dir.resolve()
    if not bundle_dir.exists():
        return {"status": "error", "error": f"Bundle directory does not exist: {bundle_dir}"}
    
    artifacts = collect_bundle_artifacts(bundle_dir)
    
    if write_checksums:
        checksums_path = bundle_dir / "checksums.sha256"
        with open(checksums_path, "w") as f:
            for a in artifacts:
                f.write(f"{a['sha256']}  {bundle_dir / a['path']}\n")
        
        # Add checksums file itself to artifacts
        artifacts.append({
            "path": "checksums.sha256",
            "sha256": compute_sha256(checksums_path),
            "size": checksums_path.stat().st_size,
        })
    
    manifest = {
        "bundle_dir": str(bundle_dir),
        "timestamp": datetime.now().isoformat(),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    
    # Write manifest
    manifest_path = bundle_dir / f"bundle-manifest-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    return {
        "status": "ok",
        "bundle_dir": str(bundle_dir),
        "artifacts": len(artifacts),
        "checksums": str(bundle_dir / "checksums.sha256") if write_checksums else None,
        "manifest": str(manifest_path),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Evidence bundle automation")
    subparsers = ap.add_subparsers(dest="command", required=True)
    
    # verify command
    verify_parser = subparsers.add_parser("verify", help="Verify bundle has required artifacts")
    verify_parser.add_argument("--bundle", required=True, help="Bundle directory path")
    verify_parser.add_argument("--require", nargs="+", help="Required artifact types")
    
    # finalize command
    finalize_parser = subparsers.add_parser("finalize", help="Finalize bundle with checksums")
    finalize_parser.add_argument("--bundle", required=True, help="Bundle directory path")
    finalize_parser.add_argument("--write-checksums", action="store_true", 
                                  help="Write checksums.sha256 file")
    
    # collect command
    collect_parser = subparsers.add_parser("collect", help="Collect artifacts from bundle")
    collect_parser.add_argument("--bundle", required=True, help="Bundle directory path")
    
    args = ap.parse_args()
    
    bundle_dir = Path(args.bundle)
    
    if args.command == "verify":
        result = verify_bundle(bundle_dir, args.require)
        print(json.dumps(result, indent=2))
        return 0 if result["valid"] else 1
    
    elif args.command == "finalize":
        result = finalize_bundle(bundle_dir, args.write_checksums)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "ok" else 1
    
    elif args.command == "collect":
        artifacts = collect_bundle_artifacts(bundle_dir)
        print(json.dumps({"artifacts": artifacts}, indent=2))
        return 0
    
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
