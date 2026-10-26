import pytest

from footballmatch_api.rag.repository import (
    vector_literal,
)


def test_vector_literal() -> None:
    assert vector_literal(
        [1.0, 2.5, -3.0]
    ) == "[1.0,2.5,-3.0]"


def test_vector_literal_accepts_ints() -> None:
    assert vector_literal(
        [1, 2, 3]
    ) == "[1.0,2.0,3.0]"


def test_search_limit_validation() -> None:
    from footballmatch_api.rag.repository import (
        RagRepository,
    )

    repository = RagRepository(
        host="localhost",
        port=5432,
        database="test",
        user="test",
        password="test",
    )

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        repository.semantic_search(
            [0.1, 0.2],
            limit=0,
        )
