# Developer Tool First-Run Audit Sample

Prepared for public review on 2026-08-01.

## Disclosure

Dockstep CLI is a fictional developer tool created only for this capability sample. This work was not commissioned, reviewed, approved, sponsored, or paid for by any customer. No private product, repository, credential, customer data, production system, or confidential documentation was accessed. The observations and timestamps below are synthetic, internally consistent fixtures that demonstrate the evaluation method.

## Evaluation question

Can a backend developer who has never used Dockstep reach a successful local preview from the public landing page without outside help?

The first value event is defined as a local preview that returns a visible success message. The target is ten minutes or less.

## Synthetic session evidence

| Elapsed time | Action and observation | Evidence class |
|---:|---|---|
| 00:00 | Opened the fictional landing page and looked for a quickstart path. | Navigation |
| 00:38 | Opened Documentation, then selected Getting Started. | Navigation |
| 01:24 | Copied the install command. No supported runtime version appeared beside it. | Documentation |
| 02:11 | Install stopped with `runtime version 3.12 or newer required`. The page had not stated this prerequisite. | Blocking error |
| 03:46 | Searched the documentation and found the runtime requirement in a separate reference page. | Recovery |
| 05:18 | Repeated installation successfully. | Recovery |
| 06:02 | Ran `dockstep preview`. The command returned `configuration file missing` without a file name or example path. | Blocking error |
| 07:31 | Found a configuration example through site search and created `dockstep.yml`. | Recovery |
| 09:14 | Local preview displayed the fictional success message. | First value |

Synthetic time to first value: 9 minutes 14 seconds.

## Scorecard

Each dimension is scored from 1 to 5. A score of 5 means a first-time user can proceed confidently with no material recovery work.

| Dimension | Score | Evidence |
|---|---:|---|
| Starting-path discoverability | 4 | Documentation and Getting Started were visible within two navigation actions. |
| Prerequisite clarity | 2 | The required runtime version appeared only after an installation failure. |
| Error recovery | 2 | The missing configuration error omitted the expected file name and example path. |
| Documentation continuity | 3 | Required information existed, but it was split across separate pages. |
| Time to first value | 3 | The synthetic session met the ten-minute target with two avoidable recovery loops. |

Total: 14 out of 25.

## Prioritized findings

### P1: Runtime prerequisite appears after failure

Impact: A new user can copy the primary install command and fail before learning the supported runtime version.

Evidence: The requirement appeared at 02:11 in the synthetic command output and was found in a separate reference page at 03:46.

Recommendation: Put the minimum supported runtime version directly beside the install command and add a preflight command.

Acceptance check: A new user can identify the required runtime version from the Getting Started page before running installation.

### P1: Configuration error does not identify the required file

Impact: A user who completed installation still cannot start the preview without searching for a separate example.

Evidence: At 06:02 the fictional CLI returned `configuration file missing` without a file name or example path.

Recommendation: Include the expected file name, current search path, and a copyable minimal example in the error output.

Acceptance check: From the error alone, a new user can create the correct file and rerun the command.

### P2: Quickstart is split across three destinations

Impact: Recovery requires switching between Getting Started, runtime reference, and configuration example pages.

Evidence: The synthetic user needed two site searches before reaching first value.

Recommendation: Create one end-to-end quickstart that contains prerequisites, install, minimal configuration, preview, expected output, and recovery links.

Acceptance check: The complete first-value path can be followed from one page with no site search.

## Suggested first experiment

Create one consolidated quickstart and improve the missing-configuration error. Run five fresh first-time evaluations against the revised path. Track completion rate, median time to first value, number of documentation searches, and the step where each unsuccessful session stops.

No conversion or adoption improvement is predicted from this fictional sample. A real product evaluation would require owner-approved scope, a fresh session, dated evidence, and product-specific acceptance criteria.

## Fixed-scope starting service

Developer Tool First-Run Audit: USD 99 or RMB 699.

Starting scope:

1. One public developer tool, API, SDK, CLI, dashboard, or documentation flow.
2. One agreed first-value task.
3. One fresh first-run evaluation using public material or buyer-authorized sanitized access.
4. A timestamped evidence timeline, five-dimension scorecard, up to five prioritized findings, and acceptance checks.
5. Delivery within two business days after complete inputs, confirmed scope, and verified payment.

Excluded from the starting scope: security testing, private repository review, production credentials, personal or regulated data, destructive actions, customer interviews, traffic or conversion guarantees, and implementation of a full product redesign.

[Request the audit in English](https://github.com/stomeonst/launchclear-capability-samples/issues/new?template=developer-onboarding-audit-request.yml) or [用中文提交需求](https://github.com/stomeonst/launchclear-capability-samples/issues/new?template=developer-onboarding-audit-request-zh.yml).
