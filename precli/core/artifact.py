# Copyright 2024 Secure Sauce LLC
# SPDX-License-Identifier: BUSL-1.1
import os
from datetime import datetime
from datetime import timezone
from typing import Optional


class Artifact:
    def __init__(self, file_name: str, uri: Optional[str] = None):
        self._file_name = file_name
        # TODO: if uri is None, use file:///
        self._uri = uri
        self._contents = None
        self._encoding = "utf-8"
        self._language = None

        if file_name != "-" and not uri:
            modified_time = os.path.getmtime(file_name)
            self._last_modified = datetime.fromtimestamp(
                modified_time, tz=timezone.utc
            )

    @property
    def file_name(self) -> str:
        """The name of the file."""
        return self._file_name

    @file_name.setter
    def file_name(self, file_name: str):
        """Set the file name"""
        self._file_name = file_name

    @property
    def uri(self) -> Optional[str]:
        """The URI of the artifact."""
        return self._uri

    @uri.setter
    def uri(self, uri: str):
        """Set the artifact URI."""
        self._uri = uri

    @property
    def encoding(self) -> str:
        """The encoding of the file."""
        return self._encoding

    @encoding.setter
    def encoding(self, encoding: str):
        """Set the encoding of the file."""
        self._encoding = encoding

    @property
    def contents(self) -> Optional[str]:
        """The contents of the artifact."""
        return self._contents

    @contents.setter
    def contents(self, contents: str):
        """Set the contents (for typically the file)."""
        self._contents = contents

    @property
    def language(self) -> Optional[str]:
        """The programming language for this artifact."""
        return self._language

    @language.setter
    def language(self, language: str):
        """Set the programming language."""
        self._language = language

    @property
    def last_modified(self) -> datetime:
        """The last modified time in UTC for this artifact."""
        return self._last_modified
