"""Graph creation and automatic refresh remain explicit engine-backed workflows."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def test_build_and_watch_have_distinct_discovery_and_real_engine_commands():
    build=(ROOT/'skills/graph-build/SKILL.md').read_text()
    watch=(ROOT/'skills/graph-watch/SKILL.md').read_text()
    assert 'name: graph-build' in build and 'initial indexing' in build
    assert 'solution register --config' in build and '--dry-run --json' in build
    assert 'reconcile --solution <solution-id> --scope full' in build
    assert 'query context --solution' in build and 'supported analyzer' in build
    assert 'name: graph-watch' in watch and 'source files change' in watch
    assert 'axiom-graphd serve' in watch and 'axiom service status' in watch
    assert 'Do not call manual `reconcile`' in watch
    assert 'polling' in watch and 'bounded deadline' in watch
    assert 'Stop only a foreground process started by this skill' in watch
    assert 'Graph refresh does not hot reload the application' in watch


def test_each_host_ships_exact_canonical_build_and_watch_instructions():
    for name in ('graph-build','graph-watch'):
        canonical=(ROOT/'skills'/name/'SKILL.md').read_bytes()
        for package in ('axiom','axiom-agy'):
            assert (ROOT/'plugins'/package/'skills'/name/'SKILL.md').read_bytes()==canonical


def test_published_skills_do_not_carry_internal_tracking_ids():
    for p in (ROOT/'skills').glob('*/SKILL.md'):
        assert not re.search(r'\b(?:ADR-\d{4}|[A-Z]-\d{3}|V2-\d{3})\b',p.read_text()),p
