workflow "Test Suite" {
  on = "push"
  resolves = ["pytest", "Check setup.py"]
}

action "pytest" {
  uses = "./.github/actions/pytest"
  args = "python3 setup.py test"
}

action "Check setup.py" {
  uses = "./.github/actions/setuptools"
  args = "python3 setup.py check -ms
}

workflow "Release" {
  on = "release"
  resolves = ["PyPI Upload"]
}

action "Build sdist" {
  needs = ["pytest"]
  uses = "./.github/actions/setuptools"
  args = "python3 setup.py sdist"
}

action "Build bdist_wheel" {
  needs = ["pytest"]
  uses = "./.github/actions/setuptools"
  args = "python3 setup.py bdist_wheel"
}

action "Check dist" {
  needs = ["Build sdist", "Build bdist_wheel"]
  uses = "./.github/actions/setuptools"
  args = "twine check dist/*"
}

action "PyPI Upload" {
  needs = ["Check dist"]
  uses = "./.github/actions/setuptools"
  secrets = ["TWINE_USERNAME", "TWINE_PASSWORD"]
  args = "twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
}