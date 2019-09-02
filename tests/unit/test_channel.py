from ssh2net import SSH2NetChannel


def test__rstrip_all_lines():
    test_input = b"""
some line
another line
one final line
    """
    output = SSH2NetChannel._rstrip_all_lines(test_input)
    for line in output.splitlines():
        assert line[-1] != " "


def test__restructure_output():
    output = "\n\nsomedata\n3560CX#"
    output = SSH2NetChannel._restructure_output(output)
    assert output.splitlines()[0] != ""
    assert output.splitlines()[1] != ""


def test__restructure_output_strip_prompt():
    output = "\n\nsomedata\n3560CX#"
    output = SSH2NetChannel._restructure_output(output, strip_prompt=True)
    assert output.splitlines()[0] != ""
    assert output.splitlines()[-1] != "3560CX#"
