"""Test source catalog integrity and provenance."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rfaw.validation.checks import validate_source_catalog, check_no_secrets
from rfaw.config import EVIDENCE_CLASSIFICATIONS


class TestSourceCatalog:
    def test_source_catalog_valid(self):
        """Source catalog should pass validation."""
        errors = validate_source_catalog()
        assert len(errors) == 0, f"Source catalog errors: {errors[:5]}"

    def test_sources_have_urls(self):
        """Every source must have a source_url."""
        import yaml
        from rfaw.config import METADATA_DIR
        with open(METADATA_DIR / "source_catalog.yml") as f:
            catalog = yaml.safe_load(f)
        for s in catalog.get("sources", []):
            assert s.get("source_url"), f"Source {s.get('source_id')} missing URL"

    def test_evidence_classifications_valid(self):
        """All evidence classifications must be from allowed list."""
        import yaml
        from rfaw.config import METADATA_DIR
        with open(METADATA_DIR / "source_catalog.yml") as f:
            catalog = yaml.safe_load(f)
        for s in catalog.get("sources", []):
            ec = s.get("evidence_classification", "")
            assert ec in EVIDENCE_CLASSIFICATIONS, \
                f"Source {s.get('source_id')}: invalid classification '{ec}'"

    def test_observed_not_derived(self):
        """No source should be both observed and derived."""
        import yaml
        from rfaw.config import METADATA_DIR
        with open(METADATA_DIR / "source_catalog.yml") as f:
            catalog = yaml.safe_load(f)
        for s in catalog.get("sources", []):
            assert not (s.get("is_observed") and s.get("is_derived")), \
                f"Source {s.get('source_id')}: cannot be both observed and derived"

    def test_at_least_one_primary_source(self):
        """Should have at least one VERIFIED_PRIMARY source."""
        import yaml
        from rfaw.config import METADATA_DIR
        with open(METADATA_DIR / "source_catalog.yml") as f:
            catalog = yaml.safe_load(f)
        primary = [s for s in catalog.get("sources", []) if s.get("evidence_classification") == "VERIFIED_PRIMARY"]
        assert len(primary) >= 1, "No VERIFIED_PRIMARY sources found"


class TestSecurity:
    def test_no_secrets_in_files(self):
        """No credential patterns in tracked files."""
        errors = check_no_secrets(".")
        assert len(errors) == 0, f"Security issues: {errors}"

    def test_no_token_in_git_config(self):
        """Git config should not contain tokens."""
        import subprocess
        result = subprocess.run(["git", "config", "--local", "--list"],
                               capture_output=True, text=True, cwd=".")
        config = result.stdout
        assert "github_pat_" not in config
        assert "ghp_" not in config
        assert "password=" not in config.lower()

    def test_gitignore_blocks_secrets(self):
        """.gitignore should block .env and credentials."""
        from pathlib import Path
        gitignore = Path(__file__).parent.parent / ".gitignore"
        content = gitignore.read_text()
        assert ".env" in content
        assert "*token*" in content
        assert "*secret*" in content

    def test_no_raw_data_tracked(self):
        """Raw data directory should be gitignored."""
        from pathlib import Path
        gitignore = Path(__file__).parent.parent / ".gitignore"
        content = gitignore.read_text()
        assert "data/raw/*" in content
        assert "data/interim/*" in content
        assert "data/processed/*" in content
