# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
    https://github.com/pyk/starlette-html-stories/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/pyk/starlette-html-stories/releases/tag/v0.1.0
