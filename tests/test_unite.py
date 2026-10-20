"""Tests for UNITE header parsing and taxon lookup helpers in UNITEd."""

import pytest

from its_fun_2_map.UNITEd import (
    get_child_rank,
    get_most_specific_taxon,
    parse_fasta_header,
    search_rank_for_taxon,
)

UNITE_HEADER = ">Fusarium_oxysporum|KX123456|SH1234567.10FU|reps|k__Fungi;p__Ascomycota;c__Sordariomycetes;o__Hypocreales;f__Nectriaceae;g__Fusarium;s__Fusarium_oxysporum"


def test_parse_unite_header():
    parsed = parse_fasta_header(UNITE_HEADER)

    assert parsed["id"] == "Fusarium_oxysporum"
    assert parsed["header"] == UNITE_HEADER.lstrip(">")
    assert parsed["taxonomy"] == {
        "k": "Fungi",
        "p": "Ascomycota",
        "c": "Sordariomycetes",
        "o": "Hypocreales",
        "f": "Nectriaceae",
        "g": "Fusarium",
        "s": "Fusarium_oxysporum",
    }


def test_header_without_taxonomy_returns_none():
    assert parse_fasta_header(">KX123456 some description") is None


@pytest.mark.parametrize("lineage, expected", [
    ({"genus": "Fusarium", "species": "Fusarium oxysporum"}, "Fusarium oxysporum"),
    ({"kingdom": "Fungi", "family": "Nectriaceae"}, "Nectriaceae"),
    ({}, "Unknown"),
])
def test_most_specific_taxon(lineage, expected):
    assert get_most_specific_taxon(lineage) == expected


@pytest.mark.parametrize("parent, child", [
    ("genus", "species"),
    ("kingdom", "phylum"),
    ("species", None),
    ("not_a_rank", None),
])
def test_child_rank(parent, child):
    assert get_child_rank(parent) == child


@pytest.fixture
def unite_index():
    return {
        "genus": {"Fusarium": ["seq_g1"]},
        "species": {"Fusarium_oxysporum": ["seq_s1"]},
    }


def test_search_exact_and_case_insensitive(unite_index):
    assert search_rank_for_taxon(unite_index, "genus", "Fusarium") == ["seq_g1"]
    assert search_rank_for_taxon(unite_index, "genus", "fusarium") == ["seq_g1"]
    assert search_rank_for_taxon(unite_index, "genus", "Aspergillus") is None


def test_search_species_ignores_space_underscore_differences(unite_index):
    assert search_rank_for_taxon(unite_index, "species", "Fusarium oxysporum") == ["seq_s1"]


# ---------------------------------------------------------------------------
# Reference selection (diversity and traverse modes) on a small UNITE-style DB
# ---------------------------------------------------------------------------

import logging
from collections import Counter

from its_fun_2_map.UNITEd import (
    build_unite_taxonomy_index,
    find_sequences_with_diversity,
    find_sequences_with_traverse,
)
from its_fun_2_map.its_a_summary_compiler import n_taxa

TAXONOMY = "k__Fungi;p__Ascomycota;c__Lecanoromycetes;o__Lecanorales;f__Cladoniaceae"
LINEAGE = {
    "kingdom": "Fungi", "phylum": "Ascomycota", "class": "Lecanoromycetes",
    "order": "Lecanorales", "family": "Cladoniaceae", "genus": "Cladonia",
    # NCBI writes species with a space; UNITE uses an underscore
    "species": "Cladonia uncialis",
}


def unite_fasta(entries):
    """UNITE-style FASTA from (accession, genus, species, length) tuples.

    Lengths set the selection order, since longer sequences are taken first.
    """
    return "".join(
        f">{acc}|{TAXONOMY};g__{genus};s__{species}|SH{i}\n{'A' * length}\n"
        for i, (acc, genus, species, length) in enumerate(entries)
    )


def accessions(sequences):
    return [seq["header"].lstrip(">").split("|")[0] for seq in sequences]


@pytest.fixture
def small_genus_index(write_file):
    # Too few Cladonia sequences to fill 20 slots, so the search also climbs
    # to family level, where genus Cladonia is one of the child taxa.
    fasta = write_file("unite_small.fasta", unite_fasta([
        ("U1", "Cladonia", "Cladonia_uncialis", 44),
        ("U2", "Cladonia", "Cladonia_uncialis", 43),
        ("U3", "Cladonia", "Cladonia_uncialis", 42),
        ("U4", "Cladonia", "Cladonia_uncialis", 41),
        ("R1", "Cladonia", "Cladonia_rangiferina", 36),
        ("S1", "Cladonia", "Cladonia_sp", 31),
        ("A1", "Cladonia", "Cladonia_arbuscula", 30),
        ("E1", "Cladina", "Cladina_stellaris", 29),
        ("P1", "Pycnothelia", "Pycnothelia_papillaria", 28),
    ]))
    return build_unite_taxonomy_index(str(fasta), logging.getLogger("test"), keep_all_sequences=True)


@pytest.fixture
def large_genus_index(write_file):
    # More Cladonia species than remaining slots (1 slot each, in file order),
    # with the target species first so it would get a slot if not excluded.
    entries = [(f"U{i}", "Cladonia", "Cladonia_uncialis", 60 - i) for i in range(6)]
    entries += [(f"X{i:02d}", "Cladonia", f"Cladonia_species{i:02d}", 40) for i in range(30)]
    fasta = write_file("unite_large.fasta", unite_fasta(entries))
    return build_unite_taxonomy_index(str(fasta), logging.getLogger("test"), keep_all_sequences=True)


def test_diversity_never_selects_a_sequence_twice(small_genus_index):
    seqs, _ = find_sequences_with_diversity(
        LINEAGE, small_genus_index, "genus", 20, logging.getLogger("test"), traverse_limit="family"
    )

    accs = accessions(seqs)
    assert [a for a, c in Counter(accs).items() if c > 1] == []
    # Every one of the 9 available sequences is used exactly once
    assert sorted(accs) == ["A1", "E1", "P1", "R1", "S1", "U1", "U2", "U3", "U4"]


def test_target_species_is_labelled_with_the_unite_name(small_genus_index):
    seqs, _ = find_sequences_with_diversity(
        LINEAGE, small_genus_index, "genus", 20, logging.getLogger("test"), traverse_limit="family"
    )

    targets = [s for s in seqs if s.get("target_species_match")]
    assert len(targets) == 4  # up to 25% of 20 = 5 allowed, but only 4 exist
    assert {s["diversity_source_taxon"] for s in targets} == {"Cladonia_uncialis"}
    # No non-target entry is labelled as the target species
    others = [s for s in seqs if not s.get("target_species_match")]
    assert "Cladonia_uncialis" not in {s["diversity_source_taxon"] for s in others}


def test_n_taxa_on_selected_labels(small_genus_index):
    seqs, _ = find_sequences_with_diversity(
        LINEAGE, small_genus_index, "genus", 20, logging.getLogger("test"), traverse_limit="family"
    )
    taxa = ";".join(s["diversity_source_taxon"] for s in seqs)

    # Cladonia_uncialis, _rangiferina, _sp, _arbuscula + genera Cladina, Pycnothelia.
    # Genus Cladonia has no unselected sequences left, so it adds nothing.
    assert n_taxa(taxa) == 6


def test_large_genus_excludes_target_species_from_child_slots(large_genus_index):
    seqs, _ = find_sequences_with_diversity(
        LINEAGE, large_genus_index, "genus", 20, logging.getLogger("test"), traverse_limit="family"
    )

    accs = accessions(seqs)
    labels = [s["diversity_source_taxon"] for s in seqs]
    assert len(seqs) == 20
    assert len(set(accs)) == 20
    # 5 target matches (25% of 20), then 15 distinct other species
    assert labels.count("Cladonia_uncialis") == 5
    assert len(set(labels)) == 16


def test_traverse_does_not_retake_species_sequences_at_genus_level(small_genus_index):
    seqs, _ = find_sequences_with_traverse(
        LINEAGE, small_genus_index, "species", 7, logging.getLogger("test"), "genus"
    )

    accs = accessions(seqs)
    assert len(accs) == len(set(accs))
    # 4 species-level sequences, then the 3 longest *other* Cladonia sequences
    assert sorted(accs) == ["A1", "R1", "S1", "U1", "U2", "U3", "U4"]
