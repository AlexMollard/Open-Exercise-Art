# Publishing the gallery on GitHub Pages

The static gallery uses relative catalogue and image URLs, so it works under
the repository's project-site path:

https://alexmollard.github.io/Open-Exercise-Art/

`tools/package_site.py` prepares an allowlisted static bundle containing the
gallery, catalogue, both image formats and licence/provenance files. It verifies
image hashes before copying. Tools, virtual environments, local caches and
uncatalogued files are excluded. No Python dependencies are needed to package it.

```sh
python tools/package_site.py --output .tmp/pages-site
python -m http.server 8000 --bind 127.0.0.1 --directory .tmp/pages-site
```

Choose a fresh output directory for each package; the tool never deletes or
overwrites an existing directory. Test the packaged site locally before deployment.

## Automatic and manual deployment

The `Publish gallery` workflow runs when gallery assets change on `main`, and
can also be run manually with `workflow_dispatch`. It does not run for pull
requests, schedules or releases. All third-party actions are pinned to commit
hashes. The workflow uses a standard Ubuntu runner and deploys the verified
Pages bundle, then removes its temporary artifact. A one-day retention limit is
the fallback if cleanup cannot complete.

GitHub Pages uses the GitHub Actions build type. The owner authorized automatic
Pages deployment for this public repository on 2026-10-14, after confirming that
standard hosted runners are free for public repositories. This exception applies
to Open Exercise Art; it does not change Ironvellum's local-only test policy.
See [GitHub's billing documentation](https://docs.github.com/en/billing/concepts/product-billing/github-actions).
Do not use larger runners or paid hosting services.

To publish manually:

```sh
gh workflow run pages.yml --repo AlexMollard/Open-Exercise-Art --ref main
```

Verify a successful deployment, then open the public URL and check search and
both download formats. Commits that change the published files on `main` also
publish automatically; documentation-only changes outside the bundle do not.
