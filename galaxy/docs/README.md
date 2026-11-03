# ITS-FUN-2-MAP Galaxy wrapper

This directory holds the Galaxy wrapper for ITS-FUN-2-MAP and everything
needed to publish it on the [Galaxy Tool Shed](https://toolshed.g2.bx.psu.edu).

## Where things live

- **Pipeline code:** [museomics/its-fun-2-map](https://github.com/museomics/its-fun-2-map).
  Releases go to PyPI and then Bioconda.
- **Galaxy wrapper:** this fork, [bge-barcoding/its-fun-2-map](https://github.com/bge-barcoding/its-fun-2-map),
  in `galaxy/` only. The upstream repository never contains `galaxy/`, so
  merging upstream changes into this fork does not conflict with it.
- Galaxy installs the **Bioconda package** `its-fun-2-map`; it does not run the
  code in this fork. The wrapper version follows the Bioconda version.

## Files

| File | Purpose |
|---|---|
| `its_fun_2_map.xml` | Tool definition |
| `macros.xml` | Version tokens, requirements and citations |
| `prepare_sheet.py` | Builds the tracking sheet from Galaxy's inputs at run time |
| `.shed.yml` | Tool Shed metadata and the list of files to upload |
| `test-data/` | Inputs for the planemo tests (about 1.4 MB) |
| `docs/` | This README (not uploaded to the Tool Shed) |

## Versioning

The tool version is set in `macros.xml`:

```
<TOOL_VERSION>+galaxy<VERSION_SUFFIX>     e.g. 1.0.0+galaxy0
```

- `@TOOL_VERSION@`: the its-fun-2-map version on Bioconda.
- `@VERSION_SUFFIX@`: the wrapper revision for that version. Reset it to `0`
  whenever `@TOOL_VERSION@` changes.

## Testing locally

From the repository root, with planemo installed in its own conda env:

```bash
planemo lint galaxy/its_fun_2_map.xml
planemo shed_lint --tools galaxy/
```

Before the Bioconda package exists, run the tests against the pipeline's
own conda env, so the `itsfun-*` commands are on `PATH`:

```bash
conda activate its-fun-2-map
/path/to/planemo-env/bin/planemo test --no_dependency_resolution galaxy/its_fun_2_map.xml
```

Once the package is on Bioconda:

```bash
planemo test --conda_auto_install --conda_auto_init galaxy/its_fun_2_map.xml
```

The tests need internet access. Step 2 (`itsfun-refs`) queries NCBI Entrez
for the specimen's lineage, so a test can stall or fail when NCBI is down
(Entrez retries 20 times with 20 s waits). An NCBI API key is optional and is
not used by the tests.

## Test data

`test-data/` holds one specimen and cut-down UNITE references:

| File | Contents |
|---|---|
| `test1_R1.fastq.gz`, `test1_R2.fastq.gz` | 5,672 read pairs from a genome skim of *Pertusaria pertusa* (NCBI taxid 133178), kept because one or both mates map to the specimen's UNITE pseudo-references or its final ITS contig |
| `tracking.csv` | One row for `test1`: ID, taxid and lineage columns (no file paths) |
| `unite_full_subset.fasta` | The 20 pseudo-references `itsfun-refs` selected, from UNITE public release 19.02.2025 |
| `unite_general_subset.fasta` | The 1,565 records hit in BLAST round 1, from `sh_general_release_dynamic_19.02.2025` |
| `uchime_its2_subset.fasta` | The 96 records hit in BLAST round 2a, from the UCHIME reference dataset (2022-10-26) |
| `uchime_its1_subset.fasta` | The 70 records hit in BLAST round 2b, from the same UCHIME release |

UNITE data are licensed CC BY-SA 4.0; cite Abarenkov et al. (2024),
doi:10.1093/nar/gkad1039.

Keep the directory small, because it is uploaded to the Tool Shed with the
wrapper. Never put BLAST index files (`.n*`) in it.

## First-time setup

1. Register a Tool Shed account whose username matches `owner` in
   `.shed.yml`, and create an API key under User → Preferences → Manage API Key.
2. Create the empty Tool Shed repository (the first release uploads the contents):

   ```bash
   cd galaxy
   planemo shed_create --shed_target toolshed --shed_key <API_KEY> --skip_upload .
   ```

3. Add these GitHub secrets (organisation or repository level):
   - `TOOLSHED_API_KEY`: the API key from step 1.
   - `GALAXY_AUTOUPDATE_TOKEN`: a fine-grained GitHub token with write access to
     contents, pull requests and workflows. Without it, the autoupdate PR does
     not run CI and the release tag does not trigger the upload.
4. In this fork's **Actions** settings, enable Actions and disable the workflows
   inherited from upstream (`Tests` and `Publish to PyPI`). They are for the
   upstream repository and should not run here.

## Workflows

| Workflow | Trigger | What it does |
|---|---|---|
| `toolshed_deploy.yml` | Pushes touching `galaxy/**`, and `galaxy-*` tags | Lints and tests on every push; uploads to the Tool Shed only for a `galaxy-*` tag |
| `galaxy_autoupdate.yml` | Daily, or manual | Opens a PR bumping `@TOOL_VERSION@` when Bioconda has a newer its-fun-2-map |
| `galaxy_tag.yml` | `galaxy/macros.xml` changes on `main` | Pushes tag `galaxy-<TOOL_VERSION>+galaxy<VERSION_SUFFIX>` if it does not exist yet |
| `sync_upstream.yml` (optional) | Daily, or manual | Merges museomics `main` into this fork's `main` |

## Releasing

### Wrapper-only change

1. Edit the wrapper files on a branch and open a PR to `main`.
2. Bump `@VERSION_SUFFIX@` in `macros.xml`.
3. Merge. The tag and Tool Shed upload follow automatically.

Changes merged without a suffix bump are not released.

### New its-fun-2-map release

1. Publish a release on museomics/its-fun-2-map. This uploads to PyPI, and
   Bioconda's bot then opens a version bump on the recipe.
2. Once Bioconda has the new version, the daily job here opens a PR on
   `galaxy-autoupdate`.
3. If the release changed any command-line options, update
   `its_fun_2_map.xml` on that branch and merge before the next daily run
   (06:00 UTC). Until it is merged, that run may overwrite the branch.
4. Merge to `main`. The tag and Tool Shed upload follow automatically.