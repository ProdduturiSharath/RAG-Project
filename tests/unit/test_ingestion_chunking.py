import unittest

from rag_service.domain import DocumentSection, SourceLocation
from rag_service.ingestion import (
    ChunkingConfig,
    DeterministicChunker,
    stable_chunk_id,
    stable_lineage_key,
)


class ChunkingTests(unittest.TestCase):
    def test_windows_keep_overlap_and_stable_ids(self) -> None:
        chunker = DeterministicChunker(
            config=ChunkingConfig(max_tokens=4, overlap_tokens=1, detect_markdown_headings=False)
        )
        sections = [
            DocumentSection(
                text="one two three four five six",
                section_path=("Operations",),
                page_number=3,
                page_metadata={"sheet": "A"},
                source=SourceLocation(uri="manual.pdf"),
            )
        ]

        first = chunker.chunk(sections, document_id="manual", version="v1")
        second = chunker.chunk(sections, document_id="manual", version="v1")

        self.assertEqual([chunk.chunk_id for chunk in first], [chunk.chunk_id for chunk in second])
        self.assertEqual([chunk.text for chunk in first], [
            "one two three four",
            "four five six",
        ])
        self.assertEqual(first[0].page_number, 3)
        self.assertEqual(first[0].page_metadata["sheet"], "A")
        self.assertEqual(
            first[0].chunk_id,
            stable_chunk_id(
                "manual",
                "v1",
                ("Operations",),
                0,
                first[0].text,
                section_id=first[0].section_id,
            ),
        )

    def test_markdown_headings_become_section_paths(self) -> None:
        chunker = DeterministicChunker(max_tokens=20, overlap_tokens=0)
        chunks = chunker.chunk(
            "# Safety\nWear gloves.\n## Storage\nKeep it dry.",
            document_id="manual",
            version="v1",
        )

        self.assertEqual(chunks[0].section_path, ("Safety",))
        self.assertEqual(chunks[1].section_path, ("Safety", "Storage"))

    def test_empty_sections_return_no_chunks(self) -> None:
        chunker = DeterministicChunker(max_tokens=10, overlap_tokens=0)
        self.assertEqual(chunker.chunk([], document_id="empty", version="v1"), ())

    def test_tables_and_code_blocks_stay_whole_and_are_typed(self) -> None:
        chunker = DeterministicChunker(max_tokens=2, overlap_tokens=0)
        chunks = chunker.chunk(
            [
                DocumentSection(
                    text="| Setting | Value |\n| --- | --- |\n| max_wal_senders | 10 |",
                    heading="Configuration",
                    level=1,
                ),
                DocumentSection(
                    text="```sql\nSELECT * FROM pg_stat_activity;\n```",
                    heading="Example",
                    level=1,
                ),
            ],
            document_id="postgres",
            version="17",
        )

        self.assertEqual([chunk.kind for chunk in chunks], ["table", "code"])
        self.assertIn("max_wal_senders", chunks[0].text)
        self.assertIn("pg_stat_activity", chunks[1].text)
        self.assertEqual(
            chunks[0].lineage_key,
            stable_lineage_key("postgres", ("Configuration",), 0),
        )


if __name__ == "__main__":
    unittest.main()
