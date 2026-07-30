# Free Lab Release Design

## Goal

Turn the public fixed-fixture lab into a one-click ZIP download for buyers who
do not use Git, while preserving the paid Pipeline Kit release as GitHub's
latest release.

## Approaches considered

1. **Dedicated non-latest GitHub release — selected.** It provides a stable
   direct asset URL, release notes, checksums, and download metadata without
   adding binaries to git history.
2. Commit the ZIP to the repository. This makes the link simple but permanently
   bloats history and lets the archive drift from its source.
3. Link GitHub's automatic repository source ZIP. This contains unrelated paid
   product evidence, documentation, and assets, and does not present a clean
   buyer command.

## Release identity

- Tag: `free-lab-v1.0.0`
- Title: `Free Resume Lab v1.0.0`
- Asset: `Free_Resume_Lab_v1.0.0.zip`
- The release is explicitly not marked as GitHub's latest release.
- Existing paid Pipeline Kit `v1.0.1` remains the latest release.

## Archive contract

The ZIP contains exactly:

```text
free-lab/README.md
free-lab/run_demo.py
free-lab/run_demo.ps1
free-lab/input.csv
free-lab/fixtures/product_a.html
free-lab/fixtures/product_b.html
free-lab/test_offline_lab.py
```

Generated `output/`, bytecode, repository documentation, product assets, and
paid source are excluded.

After extraction, the buyer command remains:

```text
python free-lab/run_demo.py
```

## Packaging and verification

`free-lab/package_release.py` uses only the Python standard library. It creates
the archive with stable entry names, rejects any unexpected entry, extracts the
archive into a temporary directory, runs the buyer command, and requires exit
zero plus all five proof lines.

The release process records archive size and SHA-256. The root README shows the
direct download link, checksum, exact command, and narrow commercial boundary.

## Public release notes

Release notes state that this is a free, fixed-fixture proof, not the paid
configurable Pipeline Kit or a performance claim for arbitrary websites. They
list Python 3.10+, no network use during execution, and no third-party package.

## Gumroad handoff

Only after the GitHub asset is public and a fresh download passes extraction and
execution will the Gumroad purchase Content and public description be updated
from the repository-folder link to the direct release asset. The existing v1.0
paid ZIP, price, and other products remain unchanged.

## Failure handling

If the tag or release already exists, stop and inspect it rather than
overwriting. If the public asset hash differs from the local artifact, do not
update Gumroad. A failed public buyer command leaves the repository-folder link
as the current fallback.

## License boundary

This release changes no license. It packages the already-public lab for download
convenience and does not publish the Field Manual PDF or Pipeline Kit source.
