"""Regression tests for static Compose validation and exact-source evidence."""

import importlib.util
import json
import os
import shutil
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

    def test_static_compose_uses_only_isolated_example_fixture(self):
        source = self.compose_fixture()
        original = source.read_bytes()
        example = self.root / ".env.example"
        example.write_text("EXAMPLE_ONLY=true\n")
        directories = []
        def inspect(command, *, cwd, timeout):
            directories.append(cwd)
            self.assertNotEqual(cwd, self.root)
            self.assertEqual((cwd / source.name).read_bytes(), original)
            self.assertEqual((cwd / ".env").read_bytes(), example.read_bytes())
            self.assertEqual(command, ["docker", "compose", "--project-name", "kyqra-ci-validation",
                                       "--env-file", str(cwd / ".env"), "-f", str(cwd / source.name),
                                       "config", "--quiet"])
            self.assertFalse((self.root / ".env").exists())
        with patch.object(validator, "run", side_effect=inspect):
            validator.run_compose_checks(self.root)
        self.assertEqual(source.read_bytes(), original)
        self.assertTrue(directories)
        self.assertTrue(all(not directory.exists() for directory in directories))
        self.assertFalse((self.root / ".env").exists())

    def test_compose_without_example_does_not_invent_runtime_values(self):
        self.compose_fixture()
        def inspect(command, *, cwd, timeout):
            self.assertNotIn("--env-file", command)
            self.assertFalse((cwd / ".env").exists())
            self.assertIn("--quiet", command)
        with patch.object(validator, "run", side_effect=inspect) as execute:
            validator.run_compose_checks(self.root)
        execute.assert_called_once()

    def test_compose_errors_still_fail_and_cleanup_fixtures(self):
        self.compose_fixture()
        (self.root / ".env.example").write_text("EXAMPLE_ONLY=true\n")
        directories = []
        def reject(command, *, cwd, **kwargs):
            directories.append(cwd)
            return subprocess.CompletedProcess(command, 1)
        with patch.object(validator.subprocess, "run", side_effect=reject):
            with self.assertRaises(validator.ValidationError):
                validator.run_compose_checks(self.root)
        self.assertTrue(all(not directory.exists() for directory in directories))
        self.assertFalse((self.root / ".env").exists())

    def test_existing_runtime_env_is_never_copied_or_modified(self):
        self.compose_fixture()
        runtime = self.root / ".env"
        runtime.write_text("DO_NOT_COPY=runtime-sentinel\n")
        (self.root / ".env.example").write_text("EXAMPLE_ONLY=true\n")
        def inspect(command, *, cwd, timeout):
            self.assertNotIn("runtime-sentinel", (cwd / ".env").read_text())
        with patch.object(validator, "run", side_effect=inspect):
            validator.run_compose_checks(self.root)
        self.assertEqual(runtime.read_text(), "DO_NOT_COPY=runtime-sentinel\n")

    @unittest.skipUnless(shutil.which("docker"), "Docker CLI is exercised by Required CI")
    def test_real_compose_accepts_required_env_with_isolated_example(self):
        self.compose_fixture()
        (self.root / ".env.example").write_text("EXAMPLE_ONLY=true\n")
        validator.run_compose_checks(self.root)
        self.assertFalse((self.root / ".env").exists())

    @unittest.skipUnless(shutil.which("docker"), "Docker CLI is exercised by Required CI")
    def test_real_compose_rejects_inconsistent_model(self):
        (self.root / "compose.yaml").write_text(
            "services:\n  api:\n    image: example:test\n    networks: [undefined-network]\n")
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
