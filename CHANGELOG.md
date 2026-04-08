# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-04-08

### Added

- `html_stories(...)` lifespan helper for composing stories directly into a
  Starlette app.
- Maintainer dev tooling with Tailwind CSS generation and hot reload support.
- `just dev` and `just build` workflows for local development and release.

### Changed

- Stories now attach routes to the parent Starlette app instead of running as a
  sub-application.
- Story previews now activate through the application lifespan and only run when
  `debug=True`.
- Example application, README, and release flow updated to the new
  lifespan-based integration model.
- Bundled CSS is generated during development and release builds rather than
  committed as a tracked source file.

### Fixed

- Bundled CSS is now rendered without HTML escaping Tailwind syntax.
- Story link generation now respects the configured mount path.

### Removed

- Public `StoriesApp` ASGI sub-application API.

## [0.1.0] - 2026-04-07

### Added

- Initial decorator-first story authoring API with `stories(...)` and
  `@story(...)`.
- Story discovery for `*_stories.py` and `*.stories.py` files in a configured
  directory.
- Story documentation extraction from explicit `docs=`, story function
  docstrings, and leading Python comments.
- `StoriesApp` ASGI sub-application with a story index, JSON story metadata,
  isolated iframe rendering, and story-local route dispatch for HTMX examples.
- `preview_layout` support for wrapping story previews with an application or
  design-system layout.
- Basic example application in `examples/basic`.
- Test coverage for story discovery, mounted story links, story-local routes,
  and preview layouts.

[unreleased]:
    https://github.com/pyk/starlette-html-stories/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/pyk/starlette-html-stories/releases/tag/v0.2.0
[0.1.0]: https://github.com/pyk/starlette-html-stories/releases/tag/v0.1.0
