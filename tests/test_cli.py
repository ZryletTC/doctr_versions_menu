"""Test the doctr-versions-menu CLI interface."""
import json
import logging
import platform
import subprocess
import sys
from distutils.dir_util import copy_tree
from pathlib import Path

from click.testing import CliRunner
from pkg_resources import parse_version

import doctr_versions_menu
from doctr_versions_menu.cli import main as doctr_versions_menu_command


def test_version():
    """Test ``doctr-versions-menu --version``."""
    runner = CliRunner()
    result = runner.invoke(doctr_versions_menu_command, ['--version'])
    assert result.exit_code == 0
    normalized_version = str(parse_version(doctr_versions_menu.__version__))
    assert normalized_version in result.output


def test_bad_config():
    """Test ``doctr-versions-menu --config for non-existing config``."""
    runner = CliRunner()
    result = runner.invoke(
        doctr_versions_menu_command, ['--debug', '--config', 'xxx']
    )
    assert result.exit_code != 0
    if sys.platform.startswith('win'):
        # Windows might have slightly different messages
        return
    msg = "Cannot read configuration file: File 'xxx' does not exist"
    if platform.python_version().startswith('3.5'):
        # Python 3.5 hits the IOError earlier, resulting in a different message
        msg = "No such file or directory"
    assert msg in result.stdout


def test_default_run(caplog):
    """Test doctr-versions-menu "default" run."""
    root = Path(__file__).with_suffix('') / 'gh_pages_default'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(doctr_versions_menu_command)
        assert result.exit_code == 0
        assert (cwd / 'index.html').is_file()
        assert (cwd / '.nojekyll').is_file()
        assert (cwd / 'versions.json').is_file()
        assert (cwd / 'versions.py').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['folders'] == ['master', 'v0.1.0', 'v1.0.0']
            assert versions_data['versions'] == ['master', 'v1.0.0', 'v0.1.0']
            assert versions_data['labels'] == {
                'master': 'master',
                'v0.1.0': 'v0.1.0',
                'v1.0.0': 'v1.0.0 (latest)',
            }
            assert 'outdated' in versions_data['warnings']['v0.1.0']
            assert versions_data['latest'] == 'v1.0.0'
            assert versions_data['downloads']['master'] == [
                ['pdf', '/master/master.pdf'],
                ['zip', '/master/master.zip'],
                ['epub', '/master/master.epub'],
            ]
            assert versions_data['downloads']['v1.0.0'] == [
                ['pdf', 'https://host/v1.0.0/v1.0.0.pdf'],
                ['html', 'https://host/v1.0.0/v1.0.0.zip'],
                ['epub', 'https://host/v1.0.0/v1.0.0.epub'],
            ]
        index_html = (cwd / 'index.html').read_text()
        # fmt: off
        assert '<meta http-equiv="Refresh" content="0; url=v1.0.0" />' in index_html
        assert '<p>Go to the <a href="v1.0.0">default documentation</a>.</p>' in index_html
        # fmt: on


def test_many_releases(caplog):
    """Test doctr-versions-menu run for project with many releases."""
    root = Path(__file__).with_suffix('') / 'gh_pages_many_releases'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(doctr_versions_menu_command)
        assert result.exit_code == 0
        assert (cwd / 'index.html').is_file()
        assert (cwd / '.nojekyll').is_file()
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data == {
                'downloads': {
                    'doc-testing': [],
                    'master': [
                        ['pdf', '/master/master.pdf'],
                        ['zip', '/master/master.zip'],
                        ['epub', '/master/master.epub'],
                    ],
                    'testing': [],
                    'v0.1.0': [
                        ['pdf', '/v0.1.0/v0.1.0.pdf'],
                        ['html', '/v0.1.0/v0.1.0.zip'],
                        ['epub', '/v0.1.0/v0.1.0.epub'],
                    ],
                    'v0.2.0': [
                        ['pdf', '/v0.2.0/v0.2.0.pdf'],
                        ['html', '/v0.2.0/v0.2.0.zip'],
                        ['epub', '/v0.2.0/v0.2.0.epub'],
                    ],
                    'v1.0.0': [
                        ['pdf', 'https://host/v1.0.0/v1.0.0.pdf'],
                        ['html', 'https://host/v1.0.0/v1.0.0.zip'],
                        ['epub', 'https://host/v1.0.0/v1.0.0.epub'],
                    ],
                    'v1.0.0+dev': [],
                    'v1.0.0-dev0': [],
                    'v1.0.0-post1': [
                        ['pdf', 'https://host/v1.0.0/v1.0.0.pdf'],
                        ['html', 'https://host/v1.0.0/v1.0.0.zip'],
                        ['epub', 'https://host/v1.0.0/v1.0.0.epub'],
                    ],
                    'v1.0.0-rc1': [],
                    'v1.1.0-rc1': [],
                },
                'folders': [
                    'doc-testing',
                    'master',
                    'testing',
                    'v0.1.0',
                    'v0.2.0',
                    'v1.0.0',
                    'v1.0.0+dev',
                    'v1.0.0-dev0',
                    'v1.0.0-post1',
                    'v1.0.0-rc1',
                    'v1.1.0-rc1',
                ],
                'labels': {
                    'doc-testing': 'doc-testing',
                    'master': 'master',
                    'testing': 'testing',
                    'v0.1.0': 'v0.1.0',
                    'v0.2.0': 'v0.2.0',
                    'v1.0.0': 'v1.0.0',
                    'v1.0.0+dev': 'v1.0.0+dev',
                    'v1.0.0-dev0': 'v1.0.0-dev0',
                    'v1.0.0-post1': 'v1.0.0-post1 (latest)',
                    'v1.0.0-rc1': 'v1.0.0-rc1',
                    'v1.1.0-rc1': 'v1.1.0-rc1',
                },
                'latest': 'v1.0.0-post1',
                'versions': [
                    'master',
                    'v1.1.0-rc1',
                    'v1.0.0-post1',
                    'v1.0.0+dev',
                    'v1.0.0',
                    'v1.0.0-rc1',
                    'v1.0.0-dev0',
                    'v0.2.0',
                    'v0.1.0',
                    'testing',
                    'doc-testing',
                ],
                'warnings': {
                    'doc-testing': ['unreleased'],
                    'master': ['unreleased'],
                    'testing': ['unreleased'],
                    'v0.1.0': ['outdated'],
                    'v0.2.0': ['outdated'],
                    'v1.0.0': ['outdated'],
                    'v1.0.0+dev': ['outdated', 'unreleased'],
                    'v1.0.0-dev0': ['outdated', 'prereleased'],
                    'v1.0.0-post1': [],
                    'v1.0.0-rc1': ['outdated', 'prereleased'],
                    'v1.1.0-rc1': ['prereleased'],
                },
            }


def test_no_release(caplog):
    """Test doctr-versions-menu for when there is no "latest public release".
    """
    root = Path(__file__).with_suffix('') / 'gh_pages_no_release'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(doctr_versions_menu_command)
        assert result.exit_code == 0
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['latest'] is None
            assert versions_data['warnings'] == {
                'master': ['unreleased'],
                'v1.0.0-rc1': ['prereleased'],
            }
        index_html = (cwd / 'index.html').read_text()
        # fmt: off
        assert '<meta http-equiv="Refresh" content="0; url=master" />' in index_html
        assert '<p>Go to the <a href="master">default documentation</a>.</p>' in index_html
        # fmt: on


def test_custom_index_html(caplog):
    """Test using a custom index.html."""
    root = Path(__file__).with_suffix('') / 'gh_pages_custom_index'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(doctr_versions_menu_command)
        assert result.exit_code == 0
        assert (cwd / 'index.html').is_file()
        assert (cwd / '.nojekyll').is_file()
        assert (cwd / 'versions.json').is_file()
        msg = "This is the index.html for the gh_pages_custom_index test."
        assert msg in (cwd / 'index.html').read_text()
    if sys.platform.startswith('win'):
        # Windows might have slightly different messages
        return
    assert 'Using index.html template from index.html_t' in caplog.messages


def test_custom_downloads_file(caplog):
    """Test using a custom downloads_file."""
    root = Path(__file__).with_suffix('') / 'gh_pages_custom_downloads'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(doctr_versions_menu_command, ['--debug'])
        assert result.exit_code == 0
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['folders'] == ['master', 'v0.1.0', 'v1.0.0']
            assert versions_data['downloads']['master'] == [
                ['pdf', '/master/master.pdf'],
                ['zip', '/master/master.zip'],
            ]
            assert versions_data['downloads']['v1.0.0'] == [
                ['pdf', 'https://host/v1.0.0/v1.0.0.pdf'],
                ['html', 'https://host/v1.0.0/v1.0.0.zip'],
                ['epub', 'https://host/v1.0.0/v1.0.0.epub'],
            ]
    if sys.platform.startswith('win'):
        # Windows might have slightly different messages
        return
    assert 'Processing downloads_file master/downloads.md' in caplog.messages
    assert 'INVALID URL: ./master/master.epub' in caplog.messages


def test_custom_suffix(caplog):
    """Test using a custom suffixes for latest versions.

    Also tests the the -c / --config flag.
    """
    root = Path(__file__).with_suffix('') / 'gh_pages_custom_suffix'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(doctr_versions_menu_command, ['-c', 'config'])
        assert result.exit_code == 0
        assert (cwd / 'versions.json').is_file()
        assert not (cwd / 'versions.py').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['labels'] == {
                'master': 'master',
                'v0.1.0': 'v0.1.0',
                'v1.0.0': 'v1.0.0 [latest]',
            }


def test_custom_labels_warnings(caplog):
    """Test custom versions, labels, and warnings."""
    root = Path(__file__).with_suffix('') / 'gh_pages_custom_labels_warnings'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    expected_versions_data = {
        'downloads': {
            'doc-testing': [],
            'master': [],
            'testing': [],
            'v0.1.0': [],
            'v0.2.0': [],
            'v1.0.0': [],
            'v1.0.0+dev': [],
            'v1.0.0-dev0': [],
            'v1.0.0-post1': [],
            'v1.0.0-rc1': [],
            'v1.1.0-rc1': [],
        },
        'folders': [
            'doc-testing',
            'master',
            'testing',
            'v0.1.0',
            'v0.2.0',
            'v1.0.0',
            'v1.0.0+dev',
            'v1.0.0-dev0',
            'v1.0.0-post1',
            'v1.0.0-rc1',
            'v1.1.0-rc1',
        ],
        'labels': {
            'doc-testing': 'doc',
            'master': 'master (latest dev branch)',
            'testing': 'testing',
            'v0.1.0': '0.1.0',
            'v0.2.0': '0.2.0',
            'v1.0.0': '1.0.0 (stable)',
            'v1.0.0+dev': '1.0.0+dev',
            'v1.0.0-dev0': '1.0.0-dev0',
            'v1.0.0-post1': '1.0.0-post1',
            'v1.0.0-rc1': '1.0.0-rc1',
            'v1.1.0-rc1': '1.1.0-rc1',
        },
        'latest': 'v1.0.0',
        'versions': [
            'doc-testing',
            'testing',
            'v0.1.0',
            'v0.2.0',
            'v1.0.0-dev0',
            'v1.0.0-rc1',
            'v1.0.0',
            'v1.0.0+dev',
            'v1.0.0-post1',
            'v1.1.0-rc1',
            'master',
        ],
        'warnings': {
            'doc-testing': ['unreleased'],
            'master': ['unreleased'],
            'testing': ['unreleased'],
            'v0.1.0': ['outdated'],
            'v0.2.0': [],
            'v1.0.0': [],
            'v1.0.0+dev': ['unreleased'],
            'v1.0.0-dev0': [],
            'v1.0.0-post1': ['post'],
            'v1.0.0-rc1': [],
            'v1.1.0-rc1': [],
        },
    }
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(doctr_versions_menu_command)
        assert result.exit_code == 0
        assert (cwd / 'index.html').is_file()
        assert (cwd / '.nojekyll').is_file()
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data == expected_versions_data

    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(
            doctr_versions_menu_command,
            [
                '-c',
                'noconf',
                '--suffix-latest= (stable)',
                '--versions',
                '((<branches> != master), <releases>, master)[::-1]',
                '--no-write-versions-py',
                '--warning',
                'post',
                '<post-releases>',
                '--warning',
                'outdated',
                '(<releases> < 0.2)',
                '--warning',
                'prereleased',
                '',
                '--latest=v1.0.0',
                '--label',
                '<releases>',
                "{{ folder | replace('v', '', 1) }}",
                '--label',
                'doc-testing',
                'doc',
                '--label',
                'master',
                '{{ folder }} (latest dev branch)',
            ],
        )
        assert result.exit_code == 0
        assert (cwd / 'index.html').is_file()
        assert (cwd / '.nojekyll').is_file()
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data == expected_versions_data
