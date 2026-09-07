"""Regression tests for static Compose validation and exact-source evidence."""

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "validate_repository.py"
SPEC = importlib.util.spec_from_file_location("kyqra_validator", SOURCE)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="kyqra-validator-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def compose_fixture(self):
        source = self.root / "docker-compose.yml"
        source.write_text("services:\n  api:\n    image: example:test\n    env_file: .env\n")
        return source

    def test_static_compose_never_requires_or_creates_runtime_env(self):
        source = self.compose_fixture()
        original = source.read_bytes()
        example = self.root / ".env.example"
        example.write_text("EXAMPLE_ONLY=true\n")
        with patch.object(validator, "run") as execute:
            validator.run_compose_checks(self.root)
        command = execute.call_args.args[0]
        self.assertEqual(command, ["docker", "compose", "--env-file", str(example),
                                   "-f", str(source), "config", "--no-env-resolution", "--quiet"])
        self.assertNotIn("--no-consistency", command)
        self.assertNotIn("--no-interpolate", command)
        self.assertEqual(source.read_bytes(), original)
        self.assertFalse((self.root / ".env").exists())

    def test_compose_without_example_still_validates(self):
        self.compose_fixture()
        with patch.object(validator, "run") as execute:
            validator.run_compose_checks(self.root)
        command = execute.call_args.args[0]
        self.assertNotIn("--env-file", command)
        self.assertIn("--no-env-resolution", command)
        self.assertIn("--quiet", command)

    def test_compose_errors_still_fail_validation(self):
        self.compose_fixture()
        with patch.object(validator.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)):
            with self.assertRaises(validator.ValidationError):
                validator.run_compose_checks(self.root)

    def test_dependency_compose_files_are_not_validated_as_source(self):
        dependency = self.root / "node_modules" / "example"
        dependency.mkdir(parents=True)
        (dependency / "compose.yml").write_text("invalid: example\n")
        with patch.object(validator, "run") as execute:
            validator.run_compose_checks(self.root)
        execute.assert_not_called()

    def test_image_revision_uses_checked_out_head(self):
        (self.root / "Dockerfile").write_text("FROM scratch\n")
        with patch.dict(os.environ, {"SOURCE_SHA": "head-sha", "GITHUB_SHA": "merge-sha", "SKIP_DOCKER_BUILD": "0"}):
            with patch.object(validator, "run") as execute:
                validator.run_docker_builds(self.root, "ci")
        self.assertIn("org.opencontainers.image.revision=head-sha", execute.call_args.args[0])

    def evidence(self, environment):
        output = self.root / "evidence.json"
        with patch.dict(os.environ, environment, clear=True):
            with patch.object(validator.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "tree-sha\n")):
                validator.write_evidence(output, root=self.root, branch="test", mode="ci",
                                         repository_class="service", json_count=0,
                                         yaml_count=0, markdown_count=0)
        return json.loads(output.read_text())

    def test_evidence_identifies_checked_out_head_not_synthetic_merge(self):
        evidence = self.evidence({"SOURCE_SHA": "head-sha", "GITHUB_SHA": "merge-sha"})
        self.assertEqual(evidence["source_sha"], "head-sha")
        self.assertEqual(evidence["source_tree"], "tree-sha")
        self.assertFalse(evidence["runtime_deployment_authorized"])
        self.assertFalse(evidence["external_effects_authorized"])

    def test_evidence_falls_back_for_non_pr_invocations(self):
        self.assertEqual(self.evidence({"GITHUB_SHA": "push-sha"})["source_sha"], "push-sha")


if __name__ == "__main__":
    unittest.main()
