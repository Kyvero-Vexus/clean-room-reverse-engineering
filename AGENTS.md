# AGENTS.md

## Contributing via Pull Requests

Use this flow for all contributions.

1. **Sync first**: start from the latest `master`.
2. **Create a branch**: use a descriptive name like `feat/<topic>` or `fix/<topic>`.
3. **Implement + verify**: keep changes focused; run tests/lint before opening a PR.
4. **Commit clearly**: use concise, descriptive commit messages.
5. **Push your branch**: never push directly to `master`.
6. **Open a Pull Request** against `master` with:
   - a clear summary of what changed
   - test/verification notes
   - linked issues (if applicable)
7. **Address review feedback** and keep the branch updated until merge.

### Quick PR commands (GitHub CLI)

```bash
git checkout master
git pull --ff-only
git checkout -b feat/my-change
# make changes, run tests
git add -A
git commit -m "feat: describe change"
git push -u origin feat/my-change
gh pr create --base master --fill
```
