from pathlib import Path


project = 'doctr-versions-menu test'

extensions = [
    'doctr_versions_menu',
]

templates_path = [str(Path(__file__).parent / '_templates')]
# temlates_path entries are supposed to be relative to the the configuration
# directory, but for some reason this is not working (maybe a bug in
# sphinx.testing?). Thus, we set an absolute path here.

doctr_versions_menu_conf = dict(
    github_project_url="https://github.com/goerz/doctr_versions_menu",
    my_var="custom variable",
    badge_only=False,
)
