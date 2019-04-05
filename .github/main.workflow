workflow "Run Tests" {
  on = "push"
  resolves = ["pytest"]
}

action "pytest" {
  uses = "./.github/actions/pytest"
  args = "python3 setup.py test"
}