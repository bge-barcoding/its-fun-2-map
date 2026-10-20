# ITS-FUN-2-MAP: final summary CSV column definitions

The final summary is written by `itsfun-summary` (step 9) to:

```
<OUTPUT_BASE>/final_results_dir/merged_summary_<YYYYMMDD>.csv
```

(or the name given with `--output`). 

> The file contains **one row per sample**.

> **Missing values** are written as empty cells. A value is missing when a step did not run for that sample, did not apply (e.g. ITS1 columns for a sample with no ITS1 hit), or reported `NA`.

> **Units:** lengths are in base pairs (bp). Rates and GC content are fractions (0–1) unless stated otherwise.

---

## Column definitions
| Column | Step | Definition |
|---|---|---|
| `ID` | User input | Sample ID, from the `--column_name` column of the tracking sheet. Every step's CSV is joined on this value. |
| `trimmed_before_total_reads` | Read QC | Raw reads (R1 + R2) before trimming/filtering. |
| `trimmed_before_total_bases` | Read QC | Raw bases before trimming/filtering. |
| `trimmed_before_q30_rate` | Read QC | Fraction of raw bases with Phred quality ≥ 30. |
| `trimmed_after_total_reads` | Read QC | Reads (R1 + R2) remaining after trimming, filtering and deduplication. |
| `trimmed_after_total_bases` | Read QC | Bases remaining after trimming/filtering. |
| `trimmed_after_q30_rate` | Read QC | Fraction of remaining bases with Phred quality ≥ 30. |
| `trimmed_after_read1_mean_length` | Read QC | Mean length of R1 reads after trimming (bp). |
| `trimmed_after_read2_mean_length` | Read QC | Mean length of R2 reads after trimming (bp). |
| `trimmed_after_gc_content` | Read QC | GC fraction of the remaining reads. |
| `trimmed_duplication_rate` | Read QC | Duplication rate estimated by fastp (fraction). |
| `merged_after_total_reads` | Read QC | Reads reported by fastp after the merge step. |
| `merged_after_total_bases` | Read QC | Bases reported after the merge step. |
| `merged_after_q30_rate` | Read QC | Fraction of bases with Phred quality ≥ 30 after the merge step. |
| `merged_after_read1_mean_length` | Read QC | Mean read length after the merge step (bp). In merge mode this is the mean length of the merged reads. |
| `merged_after_gc_content` | Read QC | GC fraction after the merge step. |
| `merged_passed_filter_reads` | Read QC | Reads that passed fastp's filters in the merge run. |
| `merged_duplication_rate` | Read QC | Duplication rate estimated by fastp in the merge run (fraction). |
| `UNITEd_searched_taxid` | Reference retrieval | NCBI taxid of the sample, determined from the taxonomy in tracking sheet. |
| `UNITEd_searched_taxa` | Reference retrieval | Most specific taxon name in that taxid's NCBI lineage (species if available, else genus, family, ...). |
| `UNITEd_number` | Reference retrieval | Number of UNITE reference sequences written to the sample's `{ID}_seed.fasta` (pseudo-references used for read baiting). |
| `UNITEd_n_unique_taxa` | Reference retrieval | Number of distinct taxon labels among those references. |
| `UNITEd_taxa` | Reference retrieval | `;`-separated taxon label of each reference. |
| `UNITEd_min_length` | Reference retrieval | Shortest reference sequence (bp). |
| `UNITEd_max_length` | Reference retrieval | Longest reference sequence (bp). |
| `UNITEd_avg_length` | Reference retrieval | Mean reference sequence length (bp). |
| `mapping_n_reads` | Read baiting | Number of merged reads mapped to the sample's pseudo-references. |
| `mapping_perc` | Read baiting | Percentage of merged reads mapped. |
| `assembly_method` | Contig assembly | Assembly attempt that succeeded: `INITIAL` (SPAdes on mapped merged reads, k = 21,33,55), `FALLBACK1` (mapped merged reads, k = 21) or `FALLBACK2` (merged + unmerged reads, k = 21). `FAIL` if all three failed. |
| `assembly_status` | Contig assembly | `PASS` if SPAdes produced a non-empty `scaffolds.fasta`, else `FAIL`. |
| `assembly_n_scaffolds` | Contig assembly | Number of scaffolds in `scaffolds.fasta`. |
| `assembly_mean_scaffold_length` | Contig assembly | Mean scaffold length (bp). |
| `assembly_n50` | Contig assembly | Scaffold N50 (bp): the length L such that scaffolds of length ≥ L make up at least half of the total assembly length. |
| `blast_round1_found_taxon` | BLASTn round 1 | The expected taxon name that was found among the hits: the species if any hit matched it, otherwise the genus, otherwise family. |
| `blast_round1_n_contigs_in` | BLASTn round 1 | Number of contigs in the sample's assembly (`scaffolds.fasta`), i.e. the contigs queried. |
| `blast_round1_n_contigs_hits` | BLASTn round 1 | Number of distinct contigs with a hit to the found taxon. |
| `blast_round1_hit_taxonomy` | BLASTn round 1 | Full UNITE taxonomy string of the first matching hit. |
| `blast_round1_correct_taxonomy` | BLASTn round 1 | `PASS` / `FAIL`. As run by `run_pipeline.sh`: `PASS` if at least one contig has a hit to the expected species, genus or family. |
| `blast_its2_n_contigs_in` / `blast_its1_n_contigs_in` | BLASTn round 2 (ITS2/ITS1) | Number of contigs in the sample's full assembly. |
| `blast_its2_n_contigs_hits` / `blast_its1_n_contigs_hits` | BLASTn round 2 (ITS2/ITS1) | Number of contigs whose filtered hits match the expected taxon: 1 for a `PASS`; 0 or >1 for a `FAIL`. |
| `blast_its2_hit_taxonomy` / `blast_its1_hit_taxonomy` | BLASTn round 2 (ITS2/ITS1) | Full UNITE taxonomy string of the hit that supported the `PASS`. |
| `blast_its2_correct_taxonomy` / `blast_its1_correct_taxonomy` | BLASTn round 2 (ITS2/ITS1) | `PASS` if exactly one contig matches the expected family. If the family is missing from the tracking sheet or absent from the hits, the genus is used instead. When several contigs match, the check narrows to genus, then species, to find a single contig. Otherwise `FAIL`. |
| `extraction_ITS1` | Primer extarction | `YES` if the ITS1 region (primers ITS1 → ITS2) was extracted, else `NO`. |
| `extraction_ITS2` | Primer extarction | `YES` if the ITS2 region (primers ITS3 → ITS4) was extracted, else `NO`. |
| `extraction_ITS_complete` | Primer extarction | `YES` if the full ITS region (primers ITS1 → ITS4) was extracted, else `NO`. |
| `same_contig` | ITS1/ITS2 conig comparison | `YES` if the ITS1 and ITS2 hits are on the same contig, `NO` if on different contigs. |
| `overlapping_coords` | ITS1/ITS2 conig comparison | Only when `same_contig` is `YES`: `YES` if the ITS1 and ITS2 hit coordinate ranges on that contig overlap, `NO` if they are separate. |
| `decision_description` | Final decision | Human-readable outcome (see figure below). |
| `Final_outcome` | Final decision | `PASS` (a contig is reported as an ITS sequence for the sample) or `FAIL`. |
| `Final_contig_desc` | Final decision | What the final contig represents: `complete_ITS_region`, `putative_ITS_region` or `ITS2`. Empty on `FAIL`. Also used in the output FASTA file name. |
| `Final_contig` | Final decision | Absolute path to the FASTA chosen for the sample (see table). `PASS` FASTAs are copied, with renamed headers, to `final_results_dir/pass_fastas/`. The "manual curation" FASTAs go to `final_results_dir/manual_verification/`. |

## Final decision tree
<img width="872" height="844" alt="image" src="https://github.com/user-attachments/assets/15945c5d-6493-4897-8630-c8fb9613b94d" />
