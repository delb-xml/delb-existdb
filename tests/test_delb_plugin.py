import pytest

from delb import Document, FailedDocumentLoading
from delb_existdb import ExistClient
from delb_existdb.exceptions import DelbExistdbConfigError, DelbExistdbWriteError


def test_delete_document(test_client):
    filepath = "delete_document.xml"
    document = Document("<delete/>", existdb_client=test_client)
    document.existdb_store(filepath=filepath)
    document.existdb_delete()
    with pytest.raises(FailedDocumentLoading):
        Document(f"existdb://admin:@localhost:8080/exist/db/tests/{filepath}")


def test_filepath(sample_document):
    assert sample_document.existdb_filepath == "sample.xml"
    sample_document.existdb_filepath = "test.xml"
    assert sample_document.existdb_filepath == "test.xml"


def test_invalid_client(test_client):
    with pytest.raises(DelbExistdbConfigError):
        Document("<foo/>", existdb_client=0)

    document = Document("<foo/>", existdb_client=test_client)
    document.config.existdb.client = 0
    with pytest.raises(DelbExistdbConfigError):
        document.existdb_store(filename="foo.xml")


@pytest.mark.usefixtures("db")
def test_load_document_from_url():
    url = "existdb://admin:@localhost:8080/exist/db/apps/test-data/dada_manifest.xml"
    document = Document(url)

    assert document.source_url == url
    assert isinstance(document.config.existdb.client, ExistClient)
    assert document.existdb_collection == "/"
    assert document.existdb_filepath == "db/apps/test-data/dada_manifest.xml"


def test_load_document_with_client(test_client):
    document = Document("dada_manifest.xml", existdb_client=test_client)
    assert document.config.existdb.client is test_client
    assert document.existdb_collection == "/db/apps/test-data"
    assert document.existdb_filepath == "dada_manifest.xml"


def test_store_document(test_client):
    test_client.root_collection = "/db/apps/"
    document = Document(
        "<test/>",
        existdb_client=test_client,
    )
    document.existdb_store(collection="/test_collection/", filename="new_document.xml")

    document = Document(
        "existdb://admin:@localhost:8080/exist/db/apps/test-data/dada_manifest.xml"
    )
    document.existdb_store(replace_existing=True)
    assert document.existdb_collection == "/"
    assert document.existdb_filepath == "db/apps/test-data/dada_manifest.xml"

    document.existdb_store(
        collection="/another/collection",
        filepath="another_name.xml",
    )
    with pytest.raises(DelbExistdbWriteError):
        document.existdb_store()


@pytest.mark.usefixtures("db")
def test_with_other_extension():
    document = Document("existdb://localhost/exist/db/apps/test-data/dada_manifest.xml")
    assert document.tei_header.title == "Das erste dadaistische Manifest"
    assert document.tei_header.authors == ["Ball, Hugo"]
