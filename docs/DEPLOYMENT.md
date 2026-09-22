# Streamlit deployment

**Deployed and verified on September 21, 2026.**

- App: [Revenue Risk Analyzer](https://anaanya-revenue-risk-analyzer.streamlit.app/)
- Code: [anaanya13/revenue-risk-analyzer](https://github.com/anaanya13/revenue-risk-analyzer)
- Hosting dashboard: [Streamlit Community Cloud](https://share.streamlit.io/)

## Deployment settings

| Setting | Value |
| --- | --- |
| Repository | anaanya13/revenue-risk-analyzer |
| Branch | main |
| Main file | app.py |
| Python selected | 3.12 |
| Dependencies | Root requirements.txt |
| Secrets | None required by this version |

The shared configuration does not force a localhost address. The optional local start script still uses localhost.

## Verification

The hosted browser checks passed: original sample 120 deals and zero issues; alternate headers 12 deals and zero issues; messy sample 12 deals, 11 affected rows, and 11 issues. Both the full standardized CSV and the issue-report CSV downloaded successfully. Earlier local verification has 27 passing automated tests on Python 3.9.13; these are separate from the hosted browser checks.

## Published files

The current app, source modules, requirements, Streamlit configuration, synthetic data, tests, scripts, and current documentation are published. The private local environment, secrets, private uploads, local history, generated START_HERE.html, and archived chat handoff stay local. Git-based publishing respects .gitignore; browser uploads must explicitly select the intended files.

## Future changes

Open the app's saved link to use it. Request changes in this project task. Changes must be published to the connected GitHub main branch before Streamlit updates; editing local files alone does not change the hosted app.

Initial publishing used GitHub's browser interface. This local folder has not been initialized as a Git checkout or configured with push credentials. Future updates can use the same authenticated browser interface, or set up a local Git connection when needed. The deployed app already uses the remote repository.

Official instructions: [Deploy on Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).
