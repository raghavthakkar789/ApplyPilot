import hashlib
import os
import secrets
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from applypilot.domain.documents.document_limits import LIMITS


class UploadTooLargeError(ValueError):
    pass


@dataclass(frozen=True)
class StagedUpload:
    path: Path
    byte_length: int
    sha256: str


class DocumentStorageService:
    directories = ("originals", "extracted", "temporary", "quarantine", "trash")

    def __init__(self, root: str) -> None:
        self.root = Path(root).resolve()
        self._prepare()

    def _prepare(self) -> None:
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.root, 0o700)
        for name in self.directories:
            directory = self.root / name
            directory.mkdir(mode=0o700, exist_ok=True)
            if directory.is_symlink():
                raise RuntimeError("Document storage directories cannot be symbolic links")
            os.chmod(directory, 0o700)

    async def stage(self, upload: UploadFile) -> StagedUpload:
        name = f"{secrets.token_hex(24)}.upload"
        path = self._safe_path("temporary", name)
        digest = hashlib.sha256()
        size = 0
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as destination:
                while chunk := await upload.read(64 * 1024):
                    size += len(chunk)
                    if size > LIMITS.upload_bytes:
                        raise UploadTooLargeError("The upload exceeds the 10 MiB limit.")
                    digest.update(chunk)
                    destination.write(chunk)
                destination.flush()
                os.fsync(destination.fileno())
            return StagedUpload(path=path, byte_length=size, sha256=digest.hexdigest())
        except Exception:
            path.unlink(missing_ok=True)
            raise
        finally:
            await upload.close()

    def finalize(self, staged: Path, storage_key: str) -> Path:
        destination = self._safe_path("originals", storage_key)
        os.replace(staged, destination)
        os.chmod(destination, 0o600)
        return destination

    def discard(self, staged: Path) -> None:
        staged.unlink(missing_ok=True)

    def original_path(self, storage_key: str) -> Path:
        return self._safe_path("originals", storage_key)

    def move_to_trash(self, storage_key: str) -> None:
        source = self._safe_path("originals", storage_key)
        destination = self._safe_path("trash", storage_key)
        if source.exists():
            os.replace(source, destination)

    def restore_from_trash(self, storage_key: str) -> None:
        source = self._safe_path("trash", storage_key)
        destination = self._safe_path("originals", storage_key)
        if source.exists():
            os.replace(source, destination)

    def permanently_delete(self, storage_key: str) -> None:
        for directory in ("originals", "trash", "extracted"):
            self._safe_path(directory, storage_key).unlink(missing_ok=True)

    def _safe_path(self, directory: str, name: str) -> Path:
        if not name or "/" in name or "\\" in name or name in {".", ".."}:
            raise ValueError("Invalid internal storage key")
        parent = (self.root / directory).resolve()
        candidate = parent / name
        if candidate.parent != parent:
            raise ValueError("Invalid storage location")
        return candidate
