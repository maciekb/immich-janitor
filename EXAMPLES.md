# Przykłady użycia Immich Janitor

## Podstawowe komendy

### 1. Listowanie wszystkich assetów

```bash
uv run immich-janitor list-assets
```

Domyślnie pokazuje pierwszych 100 assetów.

### 2. Listowanie z limitem

```bash
# Pokaż tylko 5 assetów
uv run immich-janitor list-assets --limit 5

# Pokaż 1000 assetów
uv run immich-janitor list-assets --limit 1000

# Bez limitu - pokaż wszystkie (może być wolne dla dużych bibliotek)
uv run immich-janitor list-assets --limit 999999
```

> **Uwaga**: Aplikacja automatycznie pobiera wszystkie assety używając paginacji (1000 assetów na stronę). Bez `--limit` domyślnie pokazuje pierwszych 100.

## Filtrowanie po wzorcu

### 3. Znajdź wszystkie pliki HEIC z iPhone

```bash
uv run immich-janitor list-assets --pattern "IMG_.*\.HEIC"
```

### 4. Znajdź pliki DNG (RAW)

```bash
uv run immich-janitor list-assets --pattern ".*\.dng" --limit 20
```

### 5. Znajdź pliki z konkretną datą w nazwie

```bash
uv run immich-janitor list-assets --pattern "IMG_202411.*"
```

### 6. Znajdź pliki screenshot

```bash
uv run immich-janitor list-assets --pattern "Screenshot.*"
```

## Usuwanie plików

### 7. Dry-run - zobacz co zostałoby usunięte (BEZPIECZNE)

```bash
# Zawsze zacznij od dry-run!
uv run immich-janitor delete-by-pattern "IMG_test.*" --dry-run
```

### 8. Usuń pliki testowe (z potwierdzeniem)

```bash
uv run immich-janitor delete-by-pattern "test_.*"
```

Aplikacja zapyta o potwierdzenie przed usunięciem.

### 9. Usuń pliki bez potwierdzenia (ostrożnie!)

```bash
uv run immich-janitor delete-by-pattern "tmp_.*" --force
```

⚠️ **UWAGA**: Pomiń confirmation prompt - używaj ostrożnie!

## Zaawansowane wzorce regex

### 10. Usuń zdjęcia z konkretnego zakresu numerów

```bash
# Usuń IMG_0100.jpg do IMG_0199.jpg
uv run immich-janitor delete-by-pattern "IMG_01[0-9]{2}\.jpg" --dry-run
```

### 11. Usuń wszystkie pliki JPG z małymi literami

```bash
uv run immich-janitor delete-by-pattern ".*\.jpg$" --dry-run
```

### 12. Usuń pliki zaczynające się od cyfry

```bash
uv run immich-janitor delete-by-pattern "^[0-9].*" --dry-run
```

### 13. Usuń pliki zawierające "duplicate" w nazwie

```bash
uv run immich-janitor delete-by-pattern ".*duplicate.*" --dry-run
```

## Praktyczne scenariusze

### 14. Czyszczenie starych screenshotów

```bash
# Najpierw zobacz co zostanie usunięte
uv run immich-janitor list-assets --pattern "Screenshot_2024.*"

# Potem usuń
uv run immich-janitor delete-by-pattern "Screenshot_2024.*" --dry-run
uv run immich-janitor delete-by-pattern "Screenshot_2024.*"
```

### 15. Usuwanie duplikatów z suffiksem

```bash
# Pliki typu "photo (1).jpg", "photo (2).jpg"
uv run immich-janitor delete-by-pattern ".*\s\([0-9]+\)\.(jpg|png)$" --dry-run
```

### 16. Czyszczenie plików tymczasowych

```bash
uv run immich-janitor delete-by-pattern "^(tmp|temp|test)_.*" --dry-run
```

## Tips & Tricks

### Testowanie wzorców regex przed użyciem

Zawsze używaj `--dry-run` przed właściwym usunięciem:

```bash
# Krok 1: Sprawdź co zostanie znalezione
uv run immich-janitor list-assets --pattern "TWOJ_WZORZEC"

# Krok 2: Dry-run
uv run immich-janitor delete-by-pattern "TWOJ_WZORZEC" --dry-run

# Krok 3: Jeśli wszystko OK, usuń
uv run immich-janitor delete-by-pattern "TWOJ_WZORZEC"
```

### Używanie zmiennych środowiskowych

Jeśli nie chcesz używać pliku .env:

```bash
export IMMICH_API_URL="http://your-server:2283/api"
export IMMICH_API_KEY="your-api-key"

uv run immich-janitor list-assets
```

### Przekazywanie parametrów bezpośrednio

```bash
uv run immich-janitor \
  --api-url "http://localhost:2283/api" \
  --api-key "your-key" \
  list-assets --limit 10
```

## Częste wzorce regex

```regex
# Wszystkie zdjęcia JPG
.*\.jpg$

# Wszystkie zdjęcia JPG i PNG
.*\.(jpg|png)$

# Pliki z iPhone (IMG_XXXX)
^IMG_[0-9]{4}\.(jpg|heic|png)$

# Pliki z datą w formacie YYYYMMDD
.*[0-9]{8}.*

# Pliki zaczynające się od konkretnego prefiksu
^MyPrefix.*

# Pliki zawierające "old" lub "backup"
.*(old|backup).*

# Wszystkie pliki video
.*\.(mp4|mov|avi)$
```

## Bezpieczeństwo

1. **Zawsze rób backup przed masowym usuwaniem**
2. **Zawsze używaj `--dry-run` najpierw**
3. **Testuj wzorce na małej liczbie plików**
4. **Sprawdź dwukrotnie wzorzec regex**
5. **Immich ma kosz - usunięte pliki można odzyskać przez jakiś czas**

## Pomoc

```bash
# Ogólna pomoc
uv run immich-janitor --help

# Pomoc dla konkretnej komendy
uv run immich-janitor list-assets --help
uv run immich-janitor delete-by-pattern --help
```

---

## 🆕 NEW FEATURES (v0.2.0)

### Statistics Commands

#### View library overview
```bash
uv run immich-janitor stats overview
```

Shows:
- Total assets count and size
- Images vs videos breakdown  
- Favorites, archived, trashed counts
- Date range and average uploads per day

#### Breakdown by file type
```bash
uv run immich-janitor stats by-type
```

Lists all file extensions with counts, percentages, and sizes.

#### Timeline view
```bash
# Group by month (default)
uv run immich-janitor stats by-date

# Group by year
uv run immich-janitor stats by-date --group-by year

# Group by day
uv run immich-janitor stats by-date --group-by day
```

---

### Duplicate Management

#### Find duplicates
```bash
uv run immich-janitor duplicates find
```

Shows:
- Number of duplicate groups
- Assets in each group
- Potential space savings

#### Delete duplicates (keep oldest)
```bash
# Dry run first!
uv run immich-janitor duplicates delete --keep oldest --dry-run

# Actually delete
uv run immich-janitor duplicates delete --keep oldest
```

#### Delete duplicates (keep newest or largest)
```bash
# Keep newest file
uv run immich-janitor duplicates delete --keep newest

# Keep largest resolution
uv run immich-janitor duplicates delete --keep largest
```

---

### Trash Management

#### List trashed assets
```bash
# All trashed assets
uv run immich-janitor trash list

# Only assets deleted more than 30 days ago
uv run immich-janitor trash list --older-than 30d
```

#### Restore from trash
```bash
# Restore specific pattern
uv run immich-janitor trash restore --pattern "IMG_2024.*"

# Restore all
uv run immich-janitor trash restore --all

# Dry run
uv run immich-janitor trash restore --all --dry-run
```

#### Empty trash (permanent deletion!)
```bash
# Empty trash older than 60 days
uv run immich-janitor trash empty --older-than 60d

# Empty entire trash (⚠️ DANGEROUS!)
uv run immich-janitor trash empty --all

# Always test with dry-run first!
uv run immich-janitor trash empty --all --dry-run
```

#### Trash statistics
```bash
uv run immich-janitor trash stats
```

---

### Real-World Workflows

#### Monthly cleanup routine
```bash
# 1. Check what's in trash
uv run immich-janitor trash stats

# 2. Empty old trash (60+ days)
uv run immich-janitor trash empty --older-than 60d

# 3. Find and remove duplicates
uv run immich-janitor duplicates find
uv run immich-janitor duplicates delete --keep oldest --dry-run
uv run immich-janitor duplicates delete --keep oldest

# 4. Check library stats
uv run immich-janitor stats overview
```

#### Before/after migration analysis
```bash
# Before migration
uv run immich-janitor stats overview > before.txt
uv run immich-janitor stats by-type >> before.txt

# After migration  
uv run immich-janitor stats overview > after.txt
uv run immich-janitor stats by-type >> after.txt

# Compare files to see what changed
diff before.txt after.txt
```

#### Find and clean up test uploads
```bash
# Find test files
uv run immich-janitor list-assets --pattern "test.*"

# Delete them (with confirmation)
uv run immich-janitor delete-by-pattern "test.*"

# They go to trash - you can restore if needed
uv run immich-janitor trash list

# Or permanently delete after verifying
uv run immich-janitor trash empty --all
```

