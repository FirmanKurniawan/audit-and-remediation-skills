#!/usr/bin/env bash
# Read-only stack fingerprinting for the universal-code-audit skill.
# Prints hints only. Phase 1 must verify every hint by opening the file.
# It never writes, installs, or modifies anything.

set -uo pipefail
ROOT="${1:-.}"
cd "$ROOT" || exit 1

PRUNE='-path ./.git -prune -o -path ./node_modules -prune -o -path ./vendor -prune -o -path ./build -prune -o -path ./dist -prune -o -path ./.gradle -prune -o -path ./Pods -prune -o -path ./target -prune -o'

hit() { # hit <label> <glob-name> [maxdepth]
  local label="$1" name="$2" depth="${3:-4}"
  local found
  found=$(eval find . -maxdepth "$depth" $PRUNE -name "'$name'" -print 2>/dev/null | head -5)
  [ -n "$found" ] && printf '  %-28s %s\n' "$label" "$(echo "$found" | tr '\n' ' ')"
}

echo "=== repository ==="
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf '  %-28s %s\n' "branch" "$(git branch --show-current 2>/dev/null)"
  printf '  %-28s %s\n' "commit" "$(git rev-parse --short HEAD 2>/dev/null)"
  printf '  %-28s %s\n' "dirty files" "$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
else
  echo "  not a git repository"
fi
printf '  %-28s %s\n' "tracked-ish file count" "$(eval find . $PRUNE -type f -print 2>/dev/null | wc -l | tr -d ' ')"

echo
echo "=== primary markers ==="
echo "-- web frontend --"
hit "vite"            "vite.config.*"
hit "webpack"         "webpack.config.*"
hit "next"            "next.config.*"
hit "nuxt"            "nuxt.config.*"
hit "angular"         "angular.json"
hit "svelte"          "svelte.config.*"
hit "astro"           "astro.config.*"
hit "index.html"      "index.html" 3

echo "-- backend / api --"
hit "openapi"         "openapi.*"
hit "graphql schema"  "schema.graphql"
hit "dockerfile"      "Dockerfile"
hit "compose"         "docker-compose*.y*ml"
hit "requirements"    "requirements*.txt"
hit "pyproject"       "pyproject.toml"
hit "go.mod"          "go.mod"
hit "pom.xml"         "pom.xml"
hit "Gemfile"         "Gemfile"
hit "composer"        "composer.json"
hit "csproj"          "*.csproj"

echo "-- mobile --"
hit "android manifest" "AndroidManifest.xml" 6
hit "gradle"           "build.gradle*"
hit "xcodeproj"        "*.xcodeproj" 5
hit "Package.swift"    "Package.swift"
hit "Podfile"          "Podfile"
hit "flutter"          "pubspec.yaml"
hit "capacitor"        "capacitor.config.*"
hit "cordova"          "config.xml" 3
hit "ios privacy"      "PrivacyInfo.xcprivacy" 6

echo "-- desktop --"
hit "tauri"            "tauri.conf.json" 5
hit "electron-builder" "electron-builder.*"
hit "qt project"       "*.pro"
hit "cmake"            "CMakeLists.txt" 3

echo "-- embedded / iot --"
hit "platformio"       "platformio.ini"
hit "zephyr"           "prj.conf"
hit "esp-idf"          "sdkconfig*"
hit "device tree"      "*.dts"
hit "systemd unit"     "*.service" 5

echo "-- data / ml --"
hit "notebooks"        "*.ipynb" 4
hit "dvc"              "dvc.yaml"
hit "mlflow"           "MLproject"
hit "airflow dags"     "dags" 3

echo "-- infra / ci --"
hit "terraform"        "*.tf" 4
hit "helm"             "Chart.yaml"
hit "ansible"          "playbook*.y*ml"
hit "gh actions"       "*.yml" 3
hit "gitlab ci"        ".gitlab-ci.yml"

echo "-- game --"
hit "unity"            "ProjectSettings" 2
hit "unreal"           "*.uproject"
hit "godot"            "project.godot"

echo
echo "=== package.json dependency hints ==="
for pkg in $(eval find . -maxdepth 4 $PRUNE -name package.json -print 2>/dev/null | head -8); do
  echo "  $pkg"
  grep -oE '"(react|react-native|vue|svelte|@angular/core|next|nuxt|electron|@tauri-apps/api|express|fastify|@nestjs/core|koa|@capacitor/core|cordova|three|typescript|jest|vitest|playwright|cypress)"' "$pkg" 2>/dev/null | sort -u | sed 's/^/    /'
done

echo
echo "=== language file counts (top 12) ==="
eval find . $PRUNE -type f -name "'*.*'" -print 2>/dev/null \
  | sed 's/.*\.//' | tr 'A-Z' 'a-z' \
  | grep -E '^(ts|tsx|js|jsx|vue|svelte|py|java|kt|kts|swift|m|mm|c|cc|cpp|h|hpp|rs|go|rb|php|cs|dart|sh|sql|yml|yaml|tf)$' \
  | sort | uniq -c | sort -rn | head -12 | sed 's/^/  /'

echo
echo "=== test & ci presence ==="
for p in test tests __tests__ spec src/test .github/workflows .gitlab-ci.yml Jenkinsfile; do
  [ -e "$p" ] && echo "  present: $p"
done

echo
echo "NOTE: hints only. Phase 1 must confirm each by opening the file."
