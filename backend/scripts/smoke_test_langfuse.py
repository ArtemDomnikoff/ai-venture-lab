from __future__ import annotations

from app.observability import get_langfuse, is_langfuse_enabled


def main() -> None:
    if not is_langfuse_enabled():
        print("Langfuse is not configured.")
        print("Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in .env")
        return

    langfuse = get_langfuse()

    if langfuse is None:
        raise RuntimeError("Langfuse client was not created")

    if not langfuse.auth_check():
        raise RuntimeError("Langfuse authentication failed")

    print("Langfuse authentication: OK")

    langfuse.flush()


if __name__ == "__main__":
    main()
