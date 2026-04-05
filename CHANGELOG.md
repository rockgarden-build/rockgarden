## v0.7.1 (2026-04-05)

### Minor / Bug Fixes

- add incremental build support (#92)
- add nav and index sorting options (#91)

## v0.7.0 (2026-04-05)

### Minor / Bug Fixes

- strip comments (#88)
- add highlight support (#87)
- add math support (#86)
- render macro transculsions (#85)
- fix links to fragments (#84)
- add syntax highlighting (#83)
- implement GFM footnotes (#82)
- add GFM task list support (#81)
- fix table spacing when there's no subtitle (#79)
- make nav text consistent w/ body (#78)
- add page heading to properly nest documents (#77)
- nest document headings in llms-full.txt (#76)
- add llms-full.txt generation (#75)
- add optional llms.txt generation (#74)

## v0.6.4 (2026-03-22)

### Minor / Bug Fixes

- add support for multiple URL styles (#72)
  - Note: this change collapses sequential dashes in URLs (`---` becomes `-`). Use `slug` in frontmatter to explicitly override file URL.
- add subtitle support + nav fixes (#71)
- add configurable content padding (#70)

## v0.6.3 (2026-03-20)

### Minor / Bug Fixes

- add auto-index home page when no index present (#66)
- improve build error messages (#65)
- increase main content width and update layout breakpoints (#64)

## v0.6.2 (2026-03-08)

### Minor / Bug Fixes

- extend icon support to custom themes and markdown (#62)
- compute project_root from config directory

## v0.6.1 (2026-03-08)

### Minor / Bug Fixes

- add support for base_path (#60)
- update CLI messages and docs to be consistent (#59)
- add support for static assets (#57)

## v0.6.0 (2026-03-07)

### Features

- upgrade to DaisyUI 5 and Tailwind 4 (#50)

### Minor / Bug Fixes

- add explicit nav links (#48)

## v0.5.3 (2026-03-07)

### Minor / Bug Fixes

- enrich tag index pages (#46)

## v0.5.2 (2026-03-06)

### Minor / Bug Fixes

- add macros support (#43)
- add config validation (#42)

## v0.5.1 (2026-03-02)

### Minor / Bug Fixes

- fix tag index page rendering (#39)

## v0.5.0 (2026-03-02)

### Features

- add collections support (#35)
- switch to Pydantic for modeling (#26)

### Minor / Bug Fixes

- add collection page generation (#36)
- fix media paths (#34)
- add build hooks (#33)
- implement theme export CLI (#31)
- handle static assets
- add default layout system (#30)
- support base URL/ base path (#29)
- implement tag index pages (#28)
- add SEO / meta tags by frontmatter (#27)

## v0.4.11 (2026-03-01)

### Minor / Bug Fixes

- move build info to footer (#25)

## v0.4.10 (2026-03-01)

### Minor / Bug Fixes

- add timezone support (#24)

## v0.4.9 (2026-02-28)

### Minor / Bug Fixes

- add note transclusions and Phase A polish (#21)
- fix HTML escaping in ToC (#20)

## v0.4.8 (2026-02-24)

### Minor / Bug Fixes

- add CSS/JS cache busting

## v0.4.7 (2026-02-24)

### Minor / Bug Fixes

- add build info (#19)
- fix skip-to-content link

## v0.4.6 (2026-02-24)

### Minor / Bug Fixes

- implement remaining Phase A features (#18)

## v0.4.5 (2026-02-11)

### Minor / Bug Fixes

- add callout icons (#17)
- implement table of contents (#16)
- fix callout rendering (#15)
- render single newlines as line breaks (#14)

## v0.4.4 (2026-02-09)

### Minor / Bug Fixes

- bundle JS/CSS (#12)

## v0.4.3 (2026-02-08)

### Minor / Bug Fixes

- fix section/anchor and media link handling (#10)
- re-implement search (#9)
- fix duplicate heading IDs

## v0.4.2 (2026-02-08)

### Minor / Bug Fixes

- add search (#8)
- handle unicode titles (#7)
- show filename in broken link warnings

## v0.4.1 (2026-02-08)

### Minor / Bug Fixes

- add broken link handling (#6)

## v0.4.0 (2026-02-08)

### Minor / Bug Fixes

- sort backlinks (#5)

## v0.3.0 (2026-02-07)

### Features

- implement backlinks

## v0.2.11 (2026-01-25)

### Minor / Bug Fixes

- add theme switching support

## v0.2.10 (2026-01-25)

### Minor / Bug Fixes

- fix site config variable loading
- add DaisyUI theme support

## v0.2.9 (2026-01-21)

### Minor / Bug Fixes

- fix nav labels

## v0.2.8 (2026-01-21)

### Minor / Bug Fixes

- fix build directory from config

## v0.2.7 (2026-01-21)

### Minor / Bug Fixes

- simplify page title calculation

## v0.2.6 (2026-01-21)

- maintenance release

## v0.2.5 (2026-01-21)

### Minor / Bug Fixes

- add init command
- add version to CLI

## v0.2.4 (2026-01-21)

### Minor / Bug Fixes

- add support for other media types
- make nav link to auto indexes configurable
- update nav linking to folders

## v0.2.3 (2026-01-21)

### Minor / Bug Fixes

- allow serve port reuse
- add markdown image handling
- add image embed support
- use DaisyUI nav and update styling
- persist nav expand status
- fix output path
- add clean step
- load site config from source directory
- disable auto_index by default

## v0.2.2 (2026-01-20)

### Minor / Bug Fixes

- use slugs for page URLs
- support clean URLs
- add auto-index override
- add nav sorting
- use frontmatter title
- add support for standard markdown links
- add index pages
- add breadcrumbs

## v0.2.1 (2026-01-20)

### Minor / Bug Fixes

- add serve command
- fix link resolution

## v0.2.0 (2026-01-20)

### Features

- initial rendering implementation

## v0.1.0 (2026-01-18)
