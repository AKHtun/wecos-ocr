def test_package_import():
    import wecos_ocr
    assert hasattr(wecos_ocr, "__version__")
    assert wecos_ocr.__version__ == "0.1.0"
