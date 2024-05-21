# Copyright 2024 Secure Sauce LLC
import datetime
import io
import logging
import os
import pathlib
import re
import sys
import traceback

from pygments import lexers
from rich import progress

from precli.core.artifact import Artifact
from precli.core.level import Level
from precli.core.metrics import Metrics
from precli.core.result import Result
from precli.core.tool import Tool


LOG = logging.getLogger(__name__)
PROGRESS_THRESHOLD = 50


class Run:
    def __init__(
        self, tool: Tool, parsers: dict, artifacts: list[Artifact], debug
    ):
        self._tool = tool
        self._parsers = parsers
        self._artifacts = artifacts
        self._init_logger(debug)
        self._start_time = None
        self._endt_time = None

    def _init_logger(self, log_level=logging.INFO):
        """Initialize the logger.

        :param debug: Whether to enable debug mode
        :return: An instantiated logging instance
        """
        LOG.handlers = []
        logging.captureWarnings(True)
        LOG.setLevel(log_level)
        handler = logging.StreamHandler(sys.stderr)
        LOG.addHandler(handler)
        LOG.debug("logging initialized")

    @property
    def tool(self) -> Tool:
        """Get the tool associated with this run."""
        return self._tool

    def _get_file_encoding(self, file_path):
        with open(file_path, "rb") as f:
            first_two_lines = f.readline() + f.readline()

        encoding_match = re.search(rb"coding[:=]\s*([-\w.]+)", first_two_lines)
        if encoding_match:
            encoding = encoding_match.group(1).decode("ascii")
        else:
            encoding = "utf-8"
        return encoding

    def invoke(self):
        """Invokes a run"""
        self._start_time = datetime.datetime.now(datetime.UTC)

        # if we have problems with a file, we'll remove it from the file_list
        # and add it to the skipped list instead
        new_artifacts = list(self._artifacts)
        files_skipped = []
        if (
            len(self._artifacts) > PROGRESS_THRESHOLD
            and LOG.getEffectiveLevel() <= logging.INFO
        ):
            artifacts = progress.track(
                self._artifacts, description="Analyzing..."
            )
        else:
            artifacts = self._artifacts

        results = []
        lines = 0
        for artifact in artifacts:
            try:
                if artifact.file_name == "-":
                    open_fd = os.fdopen(sys.stdin.fileno(), "rb", 0)
                    fdata = io.BytesIO(open_fd.read())
                    artifact.file_name = "<stdin>"
                    artifact.contents = fdata.read()
                else:
                    encoding = self._get_file_encoding(artifact.file_name)
                    artifact.encoding = encoding
                    with open(artifact.file_name, "rb") as f:
                        lines += sum(1 for _ in f)
                    with open(artifact.file_name, "rb") as f:
                        artifact.contents = f.read()
                results += self.parse_file(
                    artifact, new_artifacts, files_skipped
                )
            except OSError as e:
                files_skipped.append((artifact.file_name, e.strerror))
                new_artifacts.remove(artifact)

        self._metrics = Metrics(
            files=len(new_artifacts),
            files_skipped=len(files_skipped),
            lines=lines,
            errors=sum(result.level == Level.ERROR for result in results),
            warnings=sum(result.level == Level.WARNING for result in results),
            notes=sum(result.level == Level.NOTE for result in results),
        )
        self._results = results
        self._end_time = datetime.datetime.now(datetime.UTC)

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    def parse_file(
        self,
        artifact: Artifact,
        new_artifacts: list,
        files_skipped: list,
    ) -> list[Result]:
        try:
            if artifact.file_name == "<stdin>":
                lxr = lexers.guess_lexer(artifact.contents)
                artifact.language = lxr.aliases[0] if lxr.aliases else lxr.name
                parser = self._parsers.get(artifact.language)
            else:
                file_extension = pathlib.Path(artifact.file_name).suffix
                parser = next(
                    (
                        p
                        for p in self._parsers.values()
                        if file_extension in p.file_extensions()
                    ),
                    None,
                )

            if parser is not None:
                LOG.debug(f"Working on file: {artifact.file_name}")
                artifact.language = parser.lexer
                return parser.parse(artifact)
        except KeyboardInterrupt:
            sys.exit(2)
        except SyntaxError as e:
            print(
                f"Syntax error while parsing file. ({e.filename}, "
                f"line {e.lineno})",
                file=sys.stderr,
            )
            files_skipped.append((artifact.file_name, e))
            new_artifacts.remove(artifact)
        except Exception as e:
            LOG.error(
                f"Exception occurred when executing rules against "
                f'{artifact.file_name}. Run "precli --debug '
                f'{artifact.file_name}" to see the full traceback.'
            )
            files_skipped.append(
                (artifact.file_name, "Exception while parsing file")
            )
            new_artifacts.remove(artifact)
            LOG.debug(f"  Exception string: {e}")
            LOG.debug(f"  Exception traceback: {traceback.format_exc()}")
        return []

    @property
    def results(self) -> list[Result]:
        """Get the list of results."""
        return self._results

    @property
    def metrics(self) -> list[Result]:
        """Get the list of results."""
        return self._metrics
