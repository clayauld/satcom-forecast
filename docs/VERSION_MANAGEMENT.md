# Version Management

This document explains how to manage version numbers in the satcom-forecast project.

## Automated Version Bumping

The project includes automated GitHub Actions workflows that update version numbers when you create a GitHub release. **Important**: The workflows are designed to update versions **before** the release artifacts are created, ensuring the release contains the correct version numbers.

### Available Workflows

#### 1. Pre-Release Version Bump (`.github/workflows/pre-release-version-bump.yml`)
- **Trigger**: When a release is created (published or draft)
- **Action**: Updates version numbers and uploads corrected assets to the release
- **Best for**: Direct releases where you want immediate version updates

#### 2. Draft Release Preparation (`.github/workflows/draft-release-prep.yml`)
- **Trigger**: When a **draft** release is created
- **Action**: Updates version numbers, creates assets, and generates a PR for review
- **Best for**: Controlled releases where you want to review changes before publishing

### How it works

1. **GitHub Actions Workflow**: Automatically runs when you create a release
2. **Trigger**: Release creation event (either published or draft)
3. **Files Updated**: 
   - `pyproject.toml` (line 7)
   - `custom_components/satcom_forecast/manifest.json` (line 4)
4. **Assets**: Creates and uploads release assets with correct version numbers

### Creating a Release

#### Option 1: Draft Release (Recommended for control)

```bash
# Create a draft release first
gh release create v0.0.4 --title "Release v0.0.4" --notes "Release notes here" --draft

# The workflow will:
# 1. Bump version numbers
# 2. Create a PR for review
# 3. Prepare release assets
# 4. Update the draft release

# Review the PR and merge if satisfied
# Then publish the release
gh release edit v0.0.4 --draft=false
```

#### Option 2: Direct Release

```bash
# Create a release directly (will trigger immediate version bump)
gh release create v0.0.4 --title "Release v0.0.4" --notes "Release notes here"
```

#### Using GitHub Web Interface

1. Go to your repository on GitHub
2. Click "Releases" in the right sidebar
3. Click "Create a new release"
4. Choose a tag (e.g., `v0.0.4`)
5. **For draft**: Check "Set as a draft release"
6. Fill in title and description
7. Click "Create release" (draft) or "Publish release"

### What happens automatically

#### For Draft Releases:
1. The workflow triggers when draft is created
2. Extracts the version from your release tag (removes 'v' prefix if present)
3. Updates both version files with the new version
4. Commits and pushes the changes back to the main branch
5. Creates release assets with correct version numbers
6. Uploads assets to the draft release
7. Creates a pull request for review
8. Updates release notes with preparation status

#### For Direct Releases:
1. The workflow triggers when release is published
2. Updates version numbers in both files
3. Commits changes to main branch
4. Creates and uploads corrected release assets
5. Updates release notes

### Version Format

- Use semantic versioning: `X.Y.Z` (e.g., `0.0.4`, `1.2.0`, `2.0.1`)
- Tag format: `vX.Y.Z` (e.g., `v0.0.4`, `v1.2.0`)
- The workflow automatically strips the 'v' prefix

## Manual Version Bumping

If you need to update versions manually, use the provided script:

```bash
# Make the script executable (if not already)
chmod +x scripts/bump_version.py

# Bump to a specific version
python3 scripts/bump_version.py 0.0.4
```

## Current Version

The current version is maintained in two files:
- `pyproject.toml`: `version = "0.0.3"`
- `custom_components/satcom_forecast/manifest.json`: `"version": "0.0.3"`

## Release Workflow Comparison

| Aspect | Draft Release | Direct Release |
|--------|---------------|----------------|
| **Control** | High - review before publishing | Low - immediate publish |
| **Version Timing** | Updated before assets created | Updated and assets replaced |
| **Review Process** | PR created for review | No review process |
| **Asset Quality** | Guaranteed correct versions | Corrected after creation |
| **Best For** | Production releases | Quick releases |

## Troubleshooting

### Workflow doesn't trigger
- Ensure the release is created (not just a tag)
- Check that the tag format is correct (`vX.Y.Z`)
- Verify the workflow files are in `.github/workflows/`

### Version not updated
- Check the GitHub Actions logs for errors
- Ensure the files exist and are writable
- Verify the regex patterns match your file format

### Permission issues
- Ensure the workflow has `contents: write` permission
- Check that the repository allows GitHub Actions to create commits

### Release assets have wrong version
- Use the draft release workflow for better control
- Check that the workflow completed successfully
- Verify the assets were uploaded with the correct version

## Best Practices

1. **Use draft releases** for production releases to review changes
2. **Always use semantic versioning** for meaningful version numbers
3. **Create releases from the main branch** to ensure proper version bumping
4. **Review the generated PR** before merging (draft workflow)
5. **Check release assets** to ensure correct version numbers
6. **Keep release notes** descriptive and helpful for users
7. **Test the workflow** with a draft release first 