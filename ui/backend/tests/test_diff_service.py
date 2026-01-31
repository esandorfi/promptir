"""Tests for diff service logic."""

from backend.services.diff_service import compute_diff


class TestComputeDiff:
    """Tests for compute_diff function."""

    def test_diff_between_versions(self, temp_dir):
        """Should compute diff between two versions."""
        prompts_dir = temp_dir / "prompts" / "my_prompt"
        prompts_dir.mkdir(parents=True)

        # Version 1
        (prompts_dir / "v1.md").write_text("""---
{
  "id": "my_prompt",
  "version": "v1",
  "variables": ["question"]
}
---
# system
Hello v1""")

        # Version 2
        (prompts_dir / "v2.md").write_text("""---
{
  "id": "my_prompt",
  "version": "v2",
  "variables": ["question", "context"]
}
---
# system
Hello v2""")

        result = compute_diff(str(temp_dir / "prompts"), "my_prompt", "v1", "v2")

        assert result is not None
        frontmatter_diff, template_diff = result

        # Should show variable change
        assert "context" in frontmatter_diff

        # Should show template change
        assert "v1" in template_diff
        assert "v2" in template_diff

    def test_diff_nonexistent_version(self, temp_dir):
        """Should return None when version doesn't exist."""
        prompts_dir = temp_dir / "prompts" / "my_prompt"
        prompts_dir.mkdir(parents=True)
        (prompts_dir / "v1.md").write_text("content")

        result = compute_diff(str(temp_dir / "prompts"), "my_prompt", "v1", "v99")
        assert result is None

    def test_diff_identical_versions(self, temp_dir):
        """Should show empty diff for identical content."""
        prompts_dir = temp_dir / "prompts" / "my_prompt"
        prompts_dir.mkdir(parents=True)

        content = """---
{"id": "my_prompt", "version": "v1"}
---
# system
Same content"""

        (prompts_dir / "v1.md").write_text(content)
        (prompts_dir / "v2.md").write_text(content.replace("v1", "v2"))

        result = compute_diff(str(temp_dir / "prompts"), "my_prompt", "v1", "v2")
        assert result is not None
        # Only version field changed in frontmatter
        _frontmatter_diff, template_diff = result
        assert template_diff == ""  # Template is identical
