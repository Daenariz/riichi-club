# Git Workflow

- **Nie direkt auf `develop` pushen**
- Immer Feature-Branches verwenden: `git checkout -b feat/...` von `develop`
- Vor Branch-Erstellung: `git fetch origin && git pull origin develop`
- Änderungen über PR nach `develop` mergen
- Wenn Fetch/Pull nicht möglich → Bescheid sagen, nicht forcieren
- Nach Abschluss der Arbeit: alle Änderungen committen **und** pushen