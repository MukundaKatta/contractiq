"""Tests for clause templates."""

from contractiq.models import ClauseType
from contractiq.templates.standard import CLAUSE_TEMPLATES, get_template, list_templates


class TestTemplates:
    def test_has_at_least_10_templates(self):
        assert len(CLAUSE_TEMPLATES) >= 10

    def test_all_templates_have_required_keys(self):
        for clause_type, template in CLAUSE_TEMPLATES.items():
            assert "name" in template, f"Missing 'name' in {clause_type}"
            assert "description" in template, f"Missing 'description' in {clause_type}"
            assert "template" in template, f"Missing 'template' in {clause_type}"
            assert "key_elements" in template, f"Missing 'key_elements' in {clause_type}"

    def test_get_template_returns_data(self):
        template = get_template(ClauseType.TERMINATION)
        assert template is not None
        assert "template" in template

    def test_get_template_unknown_returns_none(self):
        template = get_template(ClauseType.UNKNOWN)
        assert template is None

    def test_list_templates_returns_all(self):
        templates = list_templates()
        assert len(templates) == len(CLAUSE_TEMPLATES)
        for tmpl in templates:
            assert "clause_type" in tmpl
            assert "name" in tmpl
            assert "description" in tmpl

    def test_template_text_is_substantial(self):
        for clause_type, template in CLAUSE_TEMPLATES.items():
            assert len(template["template"]) > 50, f"Template too short for {clause_type}"

    def test_covers_core_clause_types(self):
        core_types = {
            ClauseType.PARTIES,
            ClauseType.TERM,
            ClauseType.PAYMENT,
            ClauseType.TERMINATION,
            ClauseType.IP,
            ClauseType.CONFIDENTIALITY,
            ClauseType.INDEMNIFICATION,
            ClauseType.LIMITATION_OF_LIABILITY,
            ClauseType.GOVERNING_LAW,
            ClauseType.FORCE_MAJEURE,
        }
        assert core_types.issubset(set(CLAUSE_TEMPLATES.keys()))
