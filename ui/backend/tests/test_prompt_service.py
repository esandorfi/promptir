"""Tests for prompt service logic."""

import json

from backend.services.prompt_service import (
    get_includes,
    list_prompt_files,
    load_manifest,
    load_prompt_source,
    parse_prompt_content,
    save_prompt_source,
)


class TestParsePromptContent:
    """Tests for parse_prompt_content function."""

    def test_valid_frontmatter(self):
        """Should parse valid JSON frontmatter."""
        content = """---
{
  "id": "test",
  "version": "v1"
}
---
# system
Hello"""
        fm, body = parse_prompt_content(content)
        assert fm is not None
        assert fm["id"] == "test"
        assert fm["version"] == "v1"
        assert "# system" in body

    def test_no_frontmatter(self):
        """Should handle content without frontmatter."""
        content = "# system\nHello"
        fm, body = parse_prompt_content(content)
        assert fm is None
        assert body == content

    def test_invalid_json_frontmatter(self):
        """Should handle invalid JSON in frontmatter."""
        content = """---
{invalid json}
---
# system"""
        fm, _body = parse_prompt_content(content)
        assert fm is None

    def test_unclosed_frontmatter(self):
        """Should handle unclosed frontmatter."""
        content = """---
{"id": "test"}
# system"""
        fm, _body = parse_prompt_content(content)
        assert fm is None


class TestLoadManifest:
    """Tests for load_manifest function."""

    def test_load_existing_manifest(self, temp_dir):
        """Should load existing manifest file."""
        manifest_path = temp_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps({"schema_version": 1, "prompts": [{"id": "test", "version": "v1"}]})
        )

        result = load_manifest(str(manifest_path))
        assert result is not None
        assert result["schema_version"] == 1
        assert len(result["prompts"]) == 1

    def test_load_nonexistent_manifest(self, temp_dir):
        """Should return None for nonexistent manifest."""
        result = load_manifest(str(temp_dir / "nonexistent.json"))
        assert result is None


class TestLoadPromptSource:
    """Tests for load_prompt_source function."""

    def test_load_existing_prompt(self, temp_dir, sample_prompt_content):
        """Should load existing prompt source."""
        prompts_dir = temp_dir / "prompts" / "my_prompt"
        prompts_dir.mkdir(parents=True)
        (prompts_dir / "v1.md").write_text(sample_prompt_content)

        result = load_prompt_source(str(temp_dir / "prompts"), "my_prompt", "v1")
        assert result is not None
        assert result.id == "my_prompt"
        assert result.version == "v1"
        assert "test_prompt" in result.content  # From frontmatter

    def test_load_nonexistent_prompt(self, temp_dir):
        """Should return None for nonexistent prompt."""
        result = load_prompt_source(str(temp_dir), "nonexistent", "v1")
        assert result is None

    def test_load_include(self, temp_dir):
        """Should load from _includes directory."""
        includes_dir = temp_dir / "prompts" / "_includes" / "policy"
        includes_dir.mkdir(parents=True)
        (includes_dir / "v1.md").write_text("Policy content")

        result = load_prompt_source(str(temp_dir / "prompts"), "policy", "v1")
        assert result is not None
        assert "Policy content" in result.content


class TestSavePromptSource:
    """Tests for save_prompt_source function."""

    def test_save_new_prompt(self, temp_dir):
        """Should create new prompt file."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        result = save_prompt_source(str(prompts_dir), "new_prompt", "v1", "# system\nHello")

        assert result is not None
        assert result.id == "new_prompt"
        assert (prompts_dir / "new_prompt" / "v1.md").exists()

    def test_save_overwrites_existing(self, temp_dir):
        """Should overwrite existing prompt."""
        prompts_dir = temp_dir / "prompts" / "existing"
        prompts_dir.mkdir(parents=True)
        (prompts_dir / "v1.md").write_text("old content")

        result = save_prompt_source(str(temp_dir / "prompts"), "existing", "v1", "new content")

        assert result is not None
        assert (temp_dir / "prompts" / "existing" / "v1.md").read_text() == "new content"


class TestListPromptFiles:
    """Tests for list_prompt_files function."""

    def test_list_prompts(self, temp_dir, sample_prompt_content):
        """Should list all prompt files."""
        prompts_dir = temp_dir / "prompts"

        # Create multiple prompts
        for name in ["prompt_a", "prompt_b"]:
            d = prompts_dir / name
            d.mkdir(parents=True)
            (d / "v1.md").write_text(sample_prompt_content)

        result = list_prompt_files(str(prompts_dir))
        assert len(result) == 2
        ids = {p.id for p in result}
        assert "prompt_a" in ids
        assert "prompt_b" in ids

    def test_excludes_includes_directory(self, temp_dir, sample_prompt_content):
        """Should exclude _includes directory."""
        prompts_dir = temp_dir / "prompts"

        # Regular prompt
        (prompts_dir / "prompt_a").mkdir(parents=True)
        (prompts_dir / "prompt_a" / "v1.md").write_text(sample_prompt_content)

        # Include (should be excluded)
        (prompts_dir / "_includes" / "policy").mkdir(parents=True)
        (prompts_dir / "_includes" / "policy" / "v1.md").write_text(sample_prompt_content)

        result = list_prompt_files(str(prompts_dir))
        assert len(result) == 1
        assert result[0].id == "prompt_a"

    def test_empty_directory(self, temp_dir):
        """Should return empty list for empty directory."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        result = list_prompt_files(str(prompts_dir))
        assert result == []


class TestGetIncludes:
    """Tests for get_includes function."""

    def test_get_includes(self, temp_dir, sample_prompt_content):
        """Should list include files."""
        includes_dir = temp_dir / "prompts" / "_includes"

        for name in ["policy", "rules"]:
            d = includes_dir / name
            d.mkdir(parents=True)
            (d / "v1.md").write_text(sample_prompt_content)

        result = get_includes(str(temp_dir / "prompts"))
        assert len(result) == 2

    def test_no_includes_directory(self, temp_dir):
        """Should return empty list when no _includes."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()

        result = get_includes(str(prompts_dir))
        assert result == []
