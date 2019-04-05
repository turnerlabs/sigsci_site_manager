workflow "pytest" {
  on = "push"
  resolves = "pytest"
}

action "pytest" {
  uses = "./github/actions/pytest"
}