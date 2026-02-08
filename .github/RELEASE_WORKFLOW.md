# Workflow CI/CD Optimisé 🚀

## Vue d'Ensemble

**1 seul workflow actif sur chaque push → 66% d'économie!**

### Workflows Configurés

| Workflow | Déclencheur | Description |
|----------|-------------|-------------|
| **CI/CD Pipeline** | Push sur `main`, PR | ✅ Principal - builds, tests, package |
| **Benchmarks** | Manuel ou release | ⚠️ Performance tests (on-demand) |
| **Documentation** | Manuel ou release | ⚠️ Génération docs (on-demand) |

## 📦 Chaque Push sur Main

À chaque push sur `main`, la CI:
1. ✅ Lint Rust (clippy)
2. ✅ Lint Python (ruff)
3. ✅ Build wheels multi-plateformes
4. ✅ Build source distribution
5. ✅ Run tous les tests
6. ✅ Upload coverage
7. 📦 **Sauvegarde les packages comme artifacts**

**Les packages sont TOUJOURS disponibles dans l'onglet "Actions" → Artifacts**

## 🎯 Créer une Release

### Option 1: Via Tag Git (Recommandé)

```bash
# 1. Créer et pusher un tag
git tag v0.2.0
git push origin v0.2.0

# 2. La CI détecte le tag et:
#    - Build tous les packages
#    - Crée une GitHub release automatique
#    - Attache tous les wheels + sdist
#    - (Optionnel) Publie sur PyPI
```

### Option 2: Manuellement via GitHub

1. Aller sur **Actions** → **CI/CD Pipeline**
2. Cliquer **Run workflow**
3. Cocher **"Create a GitHub release"** ✅
4. Entrer la version (ex: `v0.2.0`)
5. Cliquer **Run workflow**

La CI va:
- Builder tous les packages
- Créer une release GitHub
- Y attacher tous les artefacts

## 🔧 Workflows Manuels

### Lancer les Benchmarks

```bash
# Via GitHub UI:
Actions → Performance Benchmarks → Run workflow

# Ou via gh CLI:
gh workflow run benchmark.yml
```

### Générer la Documentation

```bash
# Via GitHub UI:
Actions → Documentation → Run workflow

# Ou via gh CLI:
gh workflow run docs.yml
```

## 📊 Économies de Coûts

### Avant

```
Push sur main:
  ├─ CI/CD Pipeline       $0.10
  ├─ Benchmarks           $0.08
  └─ Documentation        $0.05
                Total:    $0.23 par push
```

### Maintenant

```
Push sur main:
  └─ CI/CD Pipeline       $0.10 par push

Benchmarks (manuel):      $0.08 quand nécessaire
Documentation (manuel):   $0.05 quand nécessaire
                          ─────────────────────
                Économie: 66% ($0.13 → $0.10)
```

**Sur 50 pushs/mois: $11.50 → $5.00 = $6.50 d'économie/mois!**

## 📥 Télécharger les Packages

### Depuis GitHub Actions

1. Aller sur **Actions**
2. Cliquer sur le workflow run
3. Scroll vers **Artifacts**
4. Télécharger `wheels-*` ou `sdist`

### Depuis une Release

1. Aller sur **Releases**
2. Sélectionner la version
3. Télécharger le wheel pour votre plateforme

## 🎓 Workflow Recommandé

```bash
# Développement normal
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin main
# → CI build automatiquement, packages dans artifacts

# Quand prêt pour release
git tag v0.2.0
git push origin v0.2.0
# → CI crée release + publie packages

# Si besoin de benchmarks
gh workflow run benchmark.yml  # Manuel
```

## ✅ Checklist Avant Release

- [ ] Tous les tests passent en local (`make ci-local`)
- [ ] Version mise à jour dans `Cargo.toml` et `pyproject.toml`
- [ ] CHANGELOG.md mis à jour
- [ ] Commit et push sur `main`
- [ ] Créer et pusher le tag `v0.x.0`
- [ ] Vérifier la release sur GitHub
- [ ] (Optionnel) Tester l'installation: `pip install pyrust==0.x.0`

## 🔍 Vérifier les Artifacts

```bash
# Lister les runs récents
gh run list

# Voir les artifacts d'un run
gh run view <run-id>

# Télécharger un artifact
gh run download <run-id> -n wheels-x86_64-unknown-linux-gnu
```

## 💡 Conseils

1. **Push fréquents sur main** = Packages toujours à jour dans artifacts
2. **Tags pour releases** = Versions officielles avec GitHub release
3. **Benchmarks manuels** = Uniquement quand changements de perf
4. **Docs manuelles** = Régénérer si modifs importantes

---

**Questions?** Voir `.github/CONTRIBUTING.md` pour plus de détails.
