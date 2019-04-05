workflow "Run Tests" {
  on = "push"
  resolves = ["pytest"]
}

action "pytest" {
  uses = "./.github/actions/pytest"
  args = ""
}