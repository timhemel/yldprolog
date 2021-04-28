# Changelog

This file keeps the most important changes to the project.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed

- The operator \= is now mapped to the built-in neq operator implementation.

### Security

## [1.1.0] - 2021-04-24

### Added

- Support for binary Prolog operators = and /=. Partial support for other binary operators.
- Functors with the same name but different arities work.

### Changed

- Change project structure to a src based Python project.
- Tests now use pytest.
- Extended compiler CLI.
- Better debug output for the compiler via command-line flags.

### Fixed

- Made sure that the antlr runtime dependency version and the used antlr compiler version match.

## [1.0.0] - 2019-10-08

### Added

- rewrite of [YieldProlog](http://yieldprolog.sourceforge.net/).

[Unreleased]: https://github.com/timhemel/yldprolog/compare/1.1.0...HEAD
[1.1.0]: https://github.com/timhemel/yldprolog/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/timhemel/yldprolog/releases/tag/1.0.0