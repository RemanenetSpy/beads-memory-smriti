"""
beads-memory-smriti — Pack compatibility tests.

Verifies:
  1. pack.toml exists and declares schema = 2.
  2. The smriti-memory skill has valid Gas City SKILL frontmatter
     (name and description fields present).
  3. The smriti-anchor template fragment exists.
  4. The template fragment references the required Smriti FastMCP
     endpoint (preflight call contract).
"""

from __future__ import annotations

import pathlib
import re
import unittest

PACK_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (PACK_ROOT / rel).read_text(encoding="utf-8")


class PackManifestTests(unittest.TestCase):
    def test_pack_toml_exists(self) -> None:
        self.assertTrue((PACK_ROOT / "pack.toml").exists())

    def test_schema_version(self) -> None:
        content = _read("pack.toml")
        self.assertIn("schema = 2", content)

    def test_pack_name(self) -> None:
        content = _read("pack.toml")
        self.assertIn('name = "smriti"', content)

    def test_gc_import_declared(self) -> None:
        content = _read("pack.toml")
        self.assertIn("[imports.gc]", content)


class SkillFrontmatterTests(unittest.TestCase):
    SKILL_PATH = "skills/smriti-memory/SKILL.md"

    def _frontmatter(self) -> str:
        content = _read(self.SKILL_PATH)
        match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        self.assertIsNotNone(match, "SKILL.md must contain a YAML frontmatter block")
        return match.group(1)

    def test_skill_exists(self) -> None:
        self.assertTrue((PACK_ROOT / self.SKILL_PATH).exists())

    def test_name_field(self) -> None:
        fm = self._frontmatter()
        self.assertIn("name:", fm)
        self.assertIn("smriti-memory", fm)

    def test_description_field(self) -> None:
        fm = self._frontmatter()
        self.assertIn("description:", fm)

    def test_fastmcp_endpoint_documented(self) -> None:
        content = _read(self.SKILL_PATH)
        self.assertIn("spy9191-chronos-api-backend.hf.space", content)

    def test_preflight_endpoint_documented(self) -> None:
        content = _read(self.SKILL_PATH)
        self.assertIn("/v1/events/active", content)

    def test_ingest_endpoint_documented(self) -> None:
        content = _read(self.SKILL_PATH)
        self.assertIn("/v1/events/ingest", content)

    def test_supersession_endpoint_documented(self) -> None:
        content = _read(self.SKILL_PATH)
        self.assertIn("/v1/events/supersession-check", content)


class TemplatFragmentTests(unittest.TestCase):
    FRAGMENT_PATH = "template-fragments/smriti-anchor.template.md"

    def test_fragment_exists(self) -> None:
        self.assertTrue((PACK_ROOT / self.FRAGMENT_PATH).exists())

    def test_preflight_call_present(self) -> None:
        content = _read(self.FRAGMENT_PATH)
        self.assertIn("/v1/events/active", content)

    def test_context_char_invariant_documented(self) -> None:
        content = _read(self.FRAGMENT_PATH)
        self.assertIn("2,000", content)

    def test_ingest_call_present(self) -> None:
        content = _read(self.FRAGMENT_PATH)
        self.assertIn("/v1/events/ingest", content)

    def test_valid_to_null_invariant(self) -> None:
        content = _read(self.FRAGMENT_PATH)
        self.assertIn("valid_to", content)

    def test_api_key_env_var_referenced(self) -> None:
        content = _read(self.FRAGMENT_PATH)
        self.assertIn("SMRITI_API_KEY", content)


if __name__ == "__main__":
    unittest.main()
